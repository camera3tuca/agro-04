import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

# ===================================================================
# CONFIGURAÇÕES E CREDENCIAIS
# ===================================================================
FINNHUB_API_KEY = "d4uouchr01qnm7pnasq0d4uouchr01qnm7pnasqg"
NEWS_API_KEY = "ec7100fa90ef4e3f9a69a914050dd736"
BRAPI_TOKEN = "iExnKM1xcbQcYL3cNPhPQ3"

st.set_page_config(
    page_title="🌾 Agro Tracker Pro - Sistema Completo",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
.main {padding: 0rem 1rem;}
.stMetric {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
           color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
.stMetric label {color: white !important; font-weight: 600;}
.stMetric [data-testid="stMetricValue"] {color: white !important;}
h1 {color: #2e7d32; text-align: center; font-size: 2.5rem; font-weight: 700;}
.positive {color: #00c853; font-weight: bold;}
.negative {color: #d32f2f; font-weight: bold;}
.news-card {background: #f8f9fa; padding: 15px; border-radius: 10px; 
            margin: 10px 0; border-left: 4px solid #667eea;}
</style>
""", unsafe_allow_html=True)

# ===================================================================
# BASE DE DADOS DO AGRONEGÓCIO
# ===================================================================
ATIVOS_AGRO = {
    "Ações BR": {
        'BEEF3.SA': 'Minerva Foods', 'MRFG3.SA': 'Marfrig', 'JBSS3.SA': 'JBS',
        'BRFS3.SA': 'BRF', 'ABEV3.SA': 'Ambev', 'MDIA3.SA': 'M. Dias Branco',
        'SMTO3.SA': 'São Martinho', 'SOJA3.SA': 'Boa Safra', 'RAIZ4.SA': 'Raízen',
        'CSAN3.SA': 'Cosan', 'SUZB3.SA': 'Suzano', 'KLBN11.SA': 'Klabin',
        'SLCE3.SA': 'SLC Agrícola', 'AGRO3.SA': 'BrasilAgro'
    },
    "BDRs Internacionais": {
        'DE': 'Deere & Company', 'AGCO': 'AGCO Corp', 'ADM': 'Archer Daniels',
        'BG': 'Bunge', 'MOS': 'Mosaic', 'NTR': 'Nutrien', 'CTVA': 'Corteva'
    },
    "FIAGROs": {
        'AGRX11.SA': 'Exes Araguaia', 'BBGO11.SA': 'BB Crédito',
        'FARM11.SA': 'Santa Fé', 'GCRA11.SA': 'Galápagos', 'KNCA11.SA': 'Kinea',
        'RURA11.SA': 'Itaú Asset', 'SNAG11.SA': 'Suno Agro', 'XPCA11.SA': 'XP Crédito'
    }
}

# ===================================================================
# FUNÇÕES DE API
# ===================================================================
@st.cache_data(ttl=300)
def get_brapi_quote(ticker):
    """Obtém cotação via Brapi"""
    try:
        symbol = ticker.replace('.SA', '')
        url = f"https://brapi.dev/api/quote/{symbol}?token={BRAPI_TOKEN}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0]
    except Exception as e:
        st.warning(f"Erro Brapi {ticker}: {e}")
    return None

@st.cache_data(ttl=600)
def get_news_agro():
    """Obtém notícias do agronegócio"""
    try:
        url = f"https://newsapi.org/v2/everything?q=agronegócio OR agricultura OR JBS OR commodities&language=pt&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('articles', [])[:5]
    except:
        pass
    return []

@st.cache_data(ttl=300)
def get_finnhub_sentiment(symbol):
    """Obtém sentimento via Finnhub"""
    try:
        url = f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('sentiment', {})
    except:
        pass
    return None

# ===================================================================
# ANÁLISE TÉCNICA
# ===================================================================
def calculate_technical_indicators(df):
    """Calcula indicadores técnicos"""
    if df is None or len(df) < 50:
        return None
    
    try:
        ind = {}
        ind['SMA_20'] = SMAIndicator(df['Close'], 20).sma_indicator()
        ind['SMA_50'] = SMAIndicator(df['Close'], 50).sma_indicator()
        ind['SMA_200'] = SMAIndicator(df['Close'], 200).sma_indicator()
        
        macd = MACD(df['Close'])
        ind['MACD'] = macd.macd()
        ind['MACD_signal'] = macd.macd_signal()
        ind['MACD_hist'] = macd.macd_diff()
        
        ind['RSI'] = RSIIndicator(df['Close'], 14).rsi()
        
        bb = BollingerBands(df['Close'], 20, 2)
        ind['BB_upper'] = bb.bollinger_hband()
        ind['BB_lower'] = bb.bollinger_lband()
        ind['BB_middle'] = bb.bollinger_mavg()
        
        ind['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
        
        return ind
    except:
        return None

def analyze_trend(df, indicators):
    """Analisa tendência"""
    if not indicators:
        return {'trend': 'NEUTRO', 'score': 0, 'signals': []}
    
    try:
        price = df['Close'].iloc[-1]
        sma20 = indicators['SMA_20'].iloc[-1]
        sma50 = indicators['SMA_50'].iloc[-1]
        sma200 = indicators['SMA_200'].iloc[-1]
        
        score = 0
        signals = []
        
        if price > sma20:
            score += 1
            signals.append("✓ Preço > SMA20")
        if price > sma50:
            score += 2
            signals.append("✓ Preço > SMA50")
        if price > sma200:
            score += 3
            signals.append("✓ Preço > SMA200")
        if sma50 > sma200:
            score += 2
            signals.append("✓ Golden Cross")
        
        if score >= 5:
            trend = '🟢 ALTA FORTE'
        elif score >= 3:
            trend = '🟢 ALTA'
        elif score >= 1:
            trend = '🟡 ALTA FRACA'
        elif score >= -1:
            trend = '⚪ NEUTRO'
        else:
            trend = '🔴 BAIXA'
        
        return {'trend': trend, 'score': score, 'signals': signals}
    except:
        return {'trend': 'NEUTRO', 'score': 0, 'signals': []}

def calculate_score(df, indicators):
    """Calcula score técnico (0-100)"""
    if not indicators:
        return 50, "⚪ NEUTRO"
    
    try:
        trend = analyze_trend(df, indicators)
        rsi = indicators['RSI'].iloc[-1]
        macd = indicators['MACD'].iloc[-1]
        signal = indicators['MACD_signal'].iloc[-1]
        
        score = 50 + (trend['score'] * 4)
        
        if rsi < 30:
            score += 10
        elif rsi > 70:
            score -= 10
        
        if macd > signal:
            score += 5
        else:
            score -= 5
        
        score = max(0, min(100, score))
        
        if score >= 75:
            classification = "🟢 COMPRA FORTE"
        elif score >= 60:
            classification = "🟢 COMPRA"
        elif score >= 55:
            classification = "🟡 COMPRA FRACA"
        elif score >= 45:
            classification = "⚪ NEUTRO"
        elif score >= 40:
            classification = "🟡 VENDA FRACA"
        elif score >= 25:
            classification = "🔴 VENDA"
        else:
            classification = "🔴 VENDA FORTE"
        
        return round(score, 1), classification
    except:
        return 50, "⚪ NEUTRO"

# ===================================================================
# INTERFACE PRINCIPAL
# ===================================================================
st.title("🌾 Agro Tracker Pro - Sistema Completo de Análise")
st.markdown("### 📊 Monitoramento em Tempo Real | Análise Técnica + Fundamentalista + Notícias")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Configurações")
categoria = st.sidebar.selectbox("Categoria:", list(ATIVOS_AGRO.keys()))
ativos = st.sidebar.multiselect(
    "Selecione Ativos:",
    options=list(ATIVOS_AGRO[categoria].keys()),
    default=list(ATIVOS_AGRO[categoria].keys())[:3],
    format_func=lambda x: ATIVOS_AGRO[categoria][x]
)
periodo = st.sidebar.selectbox("Período:", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)
auto_refresh = st.sidebar.checkbox("🔄 Auto-atualizar (60s)", False)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dados via:** Brapi, Yahoo Finance, NewsAPI, Finnhub")
st.sidebar.caption(f"⏰ Atualizado: {datetime.now().strftime('%H:%M:%S')}")

# ===================================================================
# SEÇÃO DE NOTÍCIAS
# ===================================================================
with st.expander("📰 Últimas Notícias do Agronegócio", expanded=False):
    news = get_news_agro()
    if news:
        for article in news:
            st.markdown(f"""
            <div class='news-card'>
                <h4 style='margin:0; color:#667eea;'>{article.get('title', 'Sem título')}</h4>
                <p style='margin:5px 0; font-size:0.9em; color:#666;'>
                    🗓️ {article.get('publishedAt', '')[:10]} | 📰 {article.get('source', {}).get('name', 'Fonte')}
                </p>
                <p style='margin:5px 0;'>{article.get('description', '')[:200]}...</p>
                <a href='{article.get('url', '#')}' target='_blank' style='color:#667eea;'>Ler mais →</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma notícia disponível no momento.")

st.markdown("---")

# ===================================================================
# DASHBOARD DE ATIVOS
# ===================================================================
if ativos:
    # Panorama Geral
    st.subheader(f"📊 Panorama Geral - {categoria}")
    cols = st.columns(min(4, len(ativos)))
    
    for idx, ticker in enumerate(ativos[:8]):
        with cols[idx % len(cols)]:
            try:
                # Dados via Brapi
                brapi_data = get_brapi_quote(ticker)
                
                if brapi_data:
                    price = brapi_data.get('regularMarketPrice', 0)
                    change = brapi_data.get('regularMarketChangePercent', 0)
                    
                    st.metric(
                        label=ATIVOS_AGRO[categoria][ticker],
                        value=f"R$ {price:.2f}",
                        delta=f"{change:+.2f}%"
                    )
                else:
                    # Fallback para YFinance
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='1d')
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                        change = ((price - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
                        st.metric(
                            label=ATIVOS_AGRO[categoria][ticker],
                            value=f"R$ {price:.2f}",
                            delta=f"{change:+.2f}%"
                        )
            except:
                st.metric(label=ATIVOS_AGRO[categoria][ticker], value="N/D")
    
    st.markdown("---")
    
    # Abas de Análise
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Análise Técnica", "📊 Gráficos", "📉 Comparativo", "📋 Resumo"])
    
    with tab1:
        st.subheader("🔍 Análise Técnica Detalhada")
        
        for ticker in ativos:
            with st.expander(f"📊 {ATIVOS_AGRO[categoria][ticker]} ({ticker})", expanded=True):
                try:
                    stock = yf.Ticker(ticker)
                    df = stock.history(period=periodo)
                    
                    if df.empty:
                        st.warning("Dados indisponíveis")
                        continue
                    
                    indicators = calculate_technical_indicators(df)
                    
                    if indicators:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        price = df['Close'].iloc[-1]
                        change = ((price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                        rsi = indicators['RSI'].iloc[-1]
                        score, classification = calculate_score(df, indicators)
                        
                        with col1:
                            st.metric("Preço Atual", f"R$ {price:.2f}", f"{change:+.2f}%")
                        with col2:
                            st.metric("RSI (14)", f"{rsi:.1f}")
                        with col3:
                            st.metric("Score Técnico", f"{score}/100")
                        with col4:
                            st.metric("Recomendação", classification)
                        
                        trend = analyze_trend(df, indicators)
                        st.markdown(f"**Tendência:** {trend['trend']}")
                        st.markdown("**Sinais:**")
                        for signal in trend['signals']:
                            st.markdown(f"- {signal}")
                        
                        # Sentimento (se disponível)
                        if not ticker.endswith('.SA'):
                            sentiment = get_finnhub_sentiment(ticker)
                            if sentiment:
                                st.markdown(f"**Sentimento Finnhub:** {sentiment}")
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    with tab2:
        st.subheader("📈 Gráficos de Preços")
        
        for ticker in ativos:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period=periodo)
                
                if df.empty:
                    continue
                
                indicators = calculate_technical_indicators(df)
                
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.5, 0.25, 0.25],
                    subplot_titles=(f"{ATIVOS_AGRO[categoria][ticker]}", "MACD", "RSI")
                )
                
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'], name="Preço"
                ), row=1, col=1)
                
                if indicators:
                    # SMAs
                    fig.add_trace(go.Scatter(x=df.index, y=indicators['SMA_20'], 
                                           name="SMA20", line=dict(color='orange', width=1)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=indicators['SMA_50'], 
                                           name="SMA50", line=dict(color='blue', width=1)), row=1, col=1)
                    
                    # MACD
                    fig.add_trace(go.Scatter(x=df.index, y=indicators['MACD'], 
                                           name="MACD", line=dict(color='blue')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=indicators['MACD_signal'], 
                                           name="Signal", line=dict(color='red')), row=2, col=1)
                    
                    # RSI
                    fig.add_trace(go.Scatter(x=df.index, y=indicators['RSI'], 
                                           name="RSI", line=dict(color='purple')), row=3, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
                
                fig.update_layout(height=800, showlegend=True, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao gerar gráfico: {e}")
    
    with tab3:
        st.subheader("📉 Comparativo de Desempenho")
        
        fig = go.Figure()
        for ticker in ativos:
            try:
                df = yf.Ticker(ticker).history(period=periodo)
                if not df.empty:
                    normalized = (df['Close'] / df['Close'].iloc[0]) * 100
                    fig.add_trace(go.Scatter(
                        x=df.index, y=normalized,
                        mode='lines', name=ATIVOS_AGRO[categoria][ticker]
                    ))
            except:
                pass
        
        fig.update_layout(
            title="Desempenho Relativo (Base 100)",
            yaxis_title="Índice", height=600,
            template="plotly_white", hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("📋 Tabela Resumo")
        
        dados = []
        for ticker in ativos:
            try:
                brapi = get_brapi_quote(ticker)
                df = yf.Ticker(ticker).history(period=periodo)
                
                if brapi:
                    price = brapi.get('regularMarketPrice', 0)
                    change = brapi.get('regularMarketChangePercent', 0)
                elif not df.empty:
                    price = df['Close'].iloc[-1]
                    change = ((price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                else:
                    continue
                
                indicators = calculate_technical_indicators(df)
                score, classification = calculate_score(df, indicators) if indicators else (50, "NEUTRO")
                
                dados.append({
                    "Ativo": ATIVOS_AGRO[categoria][ticker],
                    "Código": ticker.replace('.SA', ''),
                    "Preço (R$)": f"{price:.2f}",
                    "Var (%)": f"{change:+.2f}",
                    "Score": score,
                    "Recomendação": classification
                })
            except:
                pass
        
        if dados:
            df_resumo = pd.DataFrame(dados)
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)
            
            csv = df_resumo.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv,
                f"agro_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

else:
    st.warning("⚠️ Selecione ativos na barra lateral")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🌾 Agro Tracker Pro</strong> | Desenvolvido com Brapi, Yahoo Finance, NewsAPI e Finnhub</p>
    <p>⚠️ <em>Sistema educacional. Não constitui recomendação de investimento.</em></p>
</div>
""", unsafe_allow_html=True)

if auto_refresh:
    time.sleep(60)
    st.rerun()

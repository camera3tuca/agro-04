import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================
BRAPI_TOKEN = "iExnKM1xcbQcYL3cNPhPQ3"
NEWS_API_KEY = "ec7100fa90ef4e3f9a69a914050dd736"
FINNHUB_API_KEY = "d4uouchr01qnm7pnasq0d4uouchr01qnm7pnasqg"

st.set_page_config(
    page_title="🌾 Agro Tracker Pro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
.main {padding: 0rem 1rem;}
.stMetric {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; padding: 15px; border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.stMetric label {color: white !important; font-weight: 600;}
.stMetric [data-testid="stMetricValue"] {color: white !important; font-size: 1.3rem;}
h1 {color: #2e7d32; text-align: center; font-size: 2.2rem;}
.category-header {
    background: linear-gradient(90deg, #2e7d32, #66bb6a);
    color: white; padding: 15px; border-radius: 10px;
    font-size: 1.5rem; font-weight: bold; margin: 20px 0;
    text-align: center;
}
.opportunity-badge {
    display: inline-block; padding: 5px 15px;
    border-radius: 20px; font-weight: bold;
    font-size: 0.9rem; margin: 5px;
}
.buy-strong {background: #00c853; color: white;}
.buy {background: #69f0ae; color: #1b5e20;}
.neutral {background: #ffd54f; color: #f57f17;}
.sell {background: #ff8a80; color: #b71c1c;}
</style>
""", unsafe_allow_html=True)

# ===================================================================
# BASE DE DADOS
# ===================================================================
ATIVOS = {
    "Ações Brasileiras": {
        'BEEF3': 'Minerva Foods', 'MRFG3': 'Marfrig', 'JBSS3': 'JBS',
        'BRFS3': 'BRF', 'ABEV3': 'Ambev', 'MDIA3': 'M. Dias Branco',
        'SMTO3': 'São Martinho', 'SOJA3': 'Boa Safra', 'RAIZ4': 'Raízen',
        'CSAN3': 'Cosan', 'SUZB3': 'Suzano', 'KLBN11': 'Klabin',
        'SLCE3': 'SLC Agrícola', 'AGRO3': 'BrasilAgro', 'CAML3': 'Camil',
        'TTEN3': 'Três Tentos', 'JALL3': 'Jalles Machado', 'KEPL3': 'Kepler Weber'
    },
    "BDRs Internacionais": {
        'A1DM34': 'Archer Daniels (ADM)', 'B1UN34': 'Bunge',
        'D1EE34': 'Deere & Company', 'A1GC34': 'AGCO Corp',
        'M1OS34': 'Mosaic', 'N1TR34': 'Nutrien', 'C1TV34': 'Corteva'
    },
    "FIAGROs": {
        'AGRX11': 'Exes Araguaia', 'BBGO11': 'BB Crédito',
        'FARM11': 'Santa Fé', 'GCRA11': 'Galápagos',
        'KNCA11': 'Kinea', 'RURA11': 'Itaú Asset',
        'SNAG11': 'Suno Agro', 'XPCA11': 'XP Crédito'
    }
}

# ===================================================================
# FUNÇÕES DE API
# ===================================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_brapi_quote(ticker):
    """Obtém cotação via Brapi"""
    try:
        url = f"https://brapi.dev/api/quote/{ticker}?range=1mo&interval=1d&fundamental=true&token={BRAPI_TOKEN}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                # Converte dados históricos para DataFrame
                if 'historicalDataPrice' in result:
                    hist_data = result['historicalDataPrice']
                    if hist_data:
                        df = pd.DataFrame(hist_data)
                        df['date'] = pd.to_datetime(df['date'], unit='s')
                        df = df.set_index('date')
                        df = df.rename(columns={
                            'open': 'Open', 'high': 'High',
                            'low': 'Low', 'close': 'Close',
                            'volume': 'Volume'
                        })
                        return result, df
                return result, None
    except Exception as e:
        st.warning(f"⚠️ Brapi falhou para {ticker}: {str(e)[:50]}")
    return None, None

@st.cache_data(ttl=300, show_spinner=False)
def get_yfinance_data(ticker, period='1mo'):
    """Fallback para YFinance"""
    try:
        # Adiciona .SA apenas para ações brasileiras e FIAGROs
        symbol = f"{ticker}.SA" if not any(x in ticker for x in ['34', 'BDR']) else ticker
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        if not df.empty:
            info = stock.info
            return info, df
    except Exception as e:
        pass
    return None, None

@st.cache_data(ttl=600, show_spinner=False)
def get_news():
    """Obtém notícias"""
    try:
        url = f"https://newsapi.org/v2/everything?q=(agronegócio OR agricultura OR JBS OR Marfrig OR commodities) AND Brasil&language=pt&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('articles', [])
    except:
        pass
    return []

# ===================================================================
# ANÁLISE TÉCNICA
# ===================================================================
def calculate_indicators(df):
    """Calcula indicadores técnicos"""
    if df is None or len(df) < 20:
        return None
    
    try:
        ind = {}
        ind['SMA_20'] = SMAIndicator(df['Close'], 20).sma_indicator()
        ind['SMA_50'] = SMAIndicator(df['Close'], min(50, len(df))).sma_indicator()
        ind['RSI'] = RSIIndicator(df['Close'], 14).rsi()
        
        macd = MACD(df['Close'])
        ind['MACD'] = macd.macd()
        ind['MACD_signal'] = macd.macd_signal()
        
        bb = BollingerBands(df['Close'], 20, 2)
        ind['BB_upper'] = bb.bollinger_hband()
        ind['BB_lower'] = bb.bollinger_lband()
        
        return ind
    except:
        return None

def calculate_opportunity_score(df, indicators, brapi_data=None):
    """Calcula score de oportunidade (0-100)"""
    if df is None or indicators is None:
        return 50, "⚪ NEUTRO", []
    
    try:
        score = 50
        signals = []
        
        price = df['Close'].iloc[-1]
        
        # RSI (peso 25)
        rsi = indicators['RSI'].iloc[-1]
        if rsi < 30:
            score += 25
            signals.append(f"✓ RSI Sobrevendido ({rsi:.0f})")
        elif rsi < 40:
            score += 15
            signals.append(f"✓ RSI Baixo ({rsi:.0f})")
        elif rsi > 70:
            score -= 25
            signals.append(f"✗ RSI Sobrecomprado ({rsi:.0f})")
        elif rsi > 60:
            score -= 10
        
        # Tendência (peso 25)
        if len(indicators['SMA_20']) > 0 and len(indicators['SMA_50']) > 0:
            sma20 = indicators['SMA_20'].iloc[-1]
            sma50 = indicators['SMA_50'].iloc[-1]
            
            if price > sma20 and price > sma50:
                score += 15
                signals.append("✓ Tendência de Alta")
            elif price > sma20:
                score += 10
                signals.append("✓ Acima SMA20")
            elif price < sma20 and price < sma50:
                score -= 15
                signals.append("✗ Tendência de Baixa")
        
        # MACD (peso 20)
        macd = indicators['MACD'].iloc[-1]
        signal = indicators['MACD_signal'].iloc[-1]
        if macd > signal:
            score += 20
            signals.append("✓ MACD Positivo")
        else:
            score -= 10
        
        # Bollinger Bands (peso 15)
        bb_lower = indicators['BB_lower'].iloc[-1]
        bb_upper = indicators['BB_upper'].iloc[-1]
        
        if price <= bb_lower:
            score += 15
            signals.append("✓ Preço na Banda Inferior")
        elif price >= bb_upper:
            score -= 15
            signals.append("✗ Preço na Banda Superior")
        
        # Variação recente (peso 15)
        var = ((price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        if var < -10:
            score += 15
            signals.append(f"✓ Queda recente ({var:.1f}%)")
        elif var < -5:
            score += 10
        elif var > 10:
            score -= 10
        
        score = max(0, min(100, score))
        
        # Classificação
        if score >= 75:
            classification = "🟢 COMPRA FORTE"
        elif score >= 60:
            classification = "🟢 COMPRA"
        elif score >= 50:
            classification = "🟡 COMPRA FRACA"
        elif score >= 40:
            classification = "⚪ NEUTRO"
        elif score >= 25:
            classification = "🟡 VENDA FRACA"
        else:
            classification = "🔴 VENDA"
        
        return round(score, 1), classification, signals
    
    except Exception as e:
        return 50, "⚪ NEUTRO", []

# ===================================================================
# INTERFACE
# ===================================================================
st.title("🌾 Agro Tracker Pro - Sistema Completo")
st.markdown("### 📊 Monitoramento Automático | Classificado por Oportunidade de Compra")

# Sidebar
st.sidebar.header("⚙️ Configurações")
auto_refresh = st.sidebar.checkbox("🔄 Auto-atualizar (2 min)", False)
show_charts = st.sidebar.checkbox("📈 Mostrar Gráficos", True)
min_score = st.sidebar.slider("Score Mínimo para Exibir", 0, 100, 0)

st.sidebar.markdown("---")
st.sidebar.info(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.caption("📡 Dados: Brapi + Yahoo Finance")

# Notícias
with st.expander("📰 Últimas Notícias do Agronegócio", expanded=False):
    news = get_news()
    if news:
        for article in news:
            st.markdown(f"""
            <div style='background:#f8f9fa; padding:15px; border-radius:10px; margin:10px 0; border-left:4px solid #2e7d32;'>
                <h4 style='margin:0; color:#2e7d32;'>{article.get('title', '')}</h4>
                <p style='margin:5px 0; font-size:0.85em; color:#666;'>
                    📅 {article.get('publishedAt', '')[:10]} | {article.get('source', {}).get('name', '')}
                </p>
                <a href='{article.get('url', '#')}' target='_blank' style='color:#2e7d32;'>Ler mais →</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Notícias indisponíveis no momento")

st.markdown("---")

# ===================================================================
# PROCESSAMENTO DE DADOS
# ===================================================================
all_data = []

with st.spinner("🔄 Coletando dados de todos os ativos..."):
    progress_bar = st.progress(0)
    total_ativos = sum(len(ativos) for ativos in ATIVOS.values())
    current = 0
    
    for categoria, ativos in ATIVOS.items():
        for ticker, nome in ativos.items():
            current += 1
            progress_bar.progress(current / total_ativos)
            
            try:
                # Tenta Brapi primeiro
                brapi_data, df_brapi = get_brapi_quote(ticker)
                
                if brapi_data and df_brapi is not None and not df_brapi.empty:
                    price = brapi_data.get('regularMarketPrice', 0)
                    change = brapi_data.get('regularMarketChangePercent', 0)
                    df = df_brapi
                else:
                    # Fallback YFinance
                    info, df = get_yfinance_data(ticker, '1mo')
                    if df is not None and not df.empty:
                        price = df['Close'].iloc[-1]
                        change = ((price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                        brapi_data = None
                    else:
                        continue
                
                # Calcula indicadores
                indicators = calculate_indicators(df)
                if indicators:
                    score, classification, signals = calculate_opportunity_score(df, indicators, brapi_data)
                    
                    rsi = indicators['RSI'].iloc[-1] if 'RSI' in indicators else None
                    
                    all_data.append({
                        'Categoria': categoria,
                        'Ticker': ticker,
                        'Nome': nome,
                        'Preço': price,
                        'Variação (%)': change,
                        'RSI': rsi,
                        'Score': score,
                        'Classificação': classification,
                        'Sinais': signals,
                        'DataFrame': df,
                        'Indicadores': indicators
                    })
            
            except Exception as e:
                continue
    
    progress_bar.empty()

# Ordena por score (maior primeiro)
all_data.sort(key=lambda x: x['Score'], reverse=True)

# Filtra por score mínimo
all_data_filtered = [d for d in all_data if d['Score'] >= min_score]

# ===================================================================
# EXIBIÇÃO DOS RESULTADOS
# ===================================================================
if not all_data_filtered:
    st.warning("⚠️ Nenhum ativo encontrado com os critérios selecionados")
else:
    st.success(f"✅ {len(all_data_filtered)} ativos analisados com sucesso!")
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    scores = [d['Score'] for d in all_data_filtered]
    compras = len([d for d in all_data_filtered if d['Score'] >= 60])
    vendas = len([d for d in all_data_filtered if d['Score'] < 40])
    neutros = len(all_data_filtered) - compras - vendas
    
    with col1:
        st.metric("Score Médio", f"{np.mean(scores):.1f}/100")
    with col2:
        st.metric("🟢 Oportunidades Compra", compras)
    with col3:
        st.metric("⚪ Neutros", neutros)
    with col4:
        st.metric("🔴 Evitar", vendas)
    
    st.markdown("---")
    
    # Por categoria
    for categoria in ATIVOS.keys():
        categoria_data = [d for d in all_data_filtered if d['Categoria'] == categoria]
        
        if not categoria_data:
            continue
        
        st.markdown(f"<div class='category-header'>📊 {categoria} ({len(categoria_data)} ativos)</div>", 
                   unsafe_allow_html=True)
        
        # Grid de cards
        cols_per_row = 3
        for i in range(0, len(categoria_data), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(categoria_data):
                    data = categoria_data[i + j]
                    
                    with col:
                        # Card
                        badge_class = "buy-strong" if data['Score'] >= 75 else \
                                    "buy" if data['Score'] >= 60 else \
                                    "neutral" if data['Score'] >= 40 else "sell"
                        
                        st.markdown(f"""
                        <div style='background:white; padding:15px; border-radius:10px; 
                                    box-shadow:0 2px 8px rgba(0,0,0,0.1); margin:10px 0;'>
                            <h4 style='margin:0; color:#2e7d32;'>{data['Nome']}</h4>
                            <p style='margin:5px 0; color:#666; font-size:0.9em;'>{data['Ticker']}</p>
                            <div class='opportunity-badge {badge_class}'>
                                Score: {data['Score']}/100
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.metric(
                            label="Preço",
                            value=f"R$ {data['Preço']:.2f}",
                            delta=f"{data['Variação (%)']:+.2f}%"
                        )
                        
                        if data['RSI']:
                            rsi_color = "🟢" if data['RSI'] < 40 else "🔴" if data['RSI'] > 60 else "🟡"
                            st.metric(label="RSI", value=f"{rsi_color} {data['RSI']:.0f}")
                        
                        st.markdown(f"**{data['Classificação']}**")
                        
                        with st.expander("📋 Sinais Detectados"):
                            for signal in data['Sinais']:
                                st.markdown(f"- {signal}")
                        
                        # Gráfico
                        if show_charts and data['DataFrame'] is not None:
                            with st.expander("📈 Gráfico"):
                                df = data['DataFrame']
                                ind = data['Indicadores']
                                
                                fig = go.Figure()
                                
                                fig.add_trace(go.Candlestick(
                                    x=df.index, open=df['Open'], high=df['High'],
                                    low=df['Low'], close=df['Close'], name="Preço"
                                ))
                                
                                if ind and 'SMA_20' in ind:
                                    fig.add_trace(go.Scatter(
                                        x=df.index, y=ind['SMA_20'],
                                        name="SMA20", line=dict(color='orange', width=1)
                                    ))
                                
                                fig.update_layout(
                                    height=300, showlegend=False,
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    xaxis_rangeslider_visible=False
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
    
    # Tabela resumo
    st.subheader("📋 Tabela Consolidada")
    
    df_resumo = pd.DataFrame([{
        'Categoria': d['Categoria'],
        'Ticker': d['Ticker'],
        'Nome': d['Nome'],
        'Preço (R$)': f"{d['Preço']:.2f}",
        'Var (%)': f"{d['Variação (%)']:+.2f}",
        'RSI': f"{d['RSI']:.0f}" if d['RSI'] else "N/D",
        'Score': d['Score'],
        'Recomendação': d['Classificação']
    } for d in all_data_filtered])
    
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)
    
    # Download
    csv = df_resumo.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        f"agro_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#666;'>
    <p><strong>🌾 Agro Tracker Pro</strong> | Dados: Brapi + Yahoo Finance + NewsAPI</p>
    <p>⚠️ <em>Sistema educacional. Não constitui recomendação de investimento.</em></p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    time.sleep(120)
    st.rerun()

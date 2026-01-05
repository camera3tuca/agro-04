import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================
BRAPI_TOKEN = "iExnKM1xcbQcYL3cNPhPQ3"
NEWS_API_KEY = "ec7100fa90ef4e3f9a69a914050dd736"

st.set_page_config(
    page_title="🌾 Agro Tracker Pro",
    page_icon="🌾",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.stMetric {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important; padding: 15px; border-radius: 10px;
}
.stMetric label, .stMetric [data-testid="stMetricValue"] {color: white !important;}
h1 {color: #2e7d32; text-align: center;}
.cat-header {
    background: linear-gradient(90deg, #2e7d32, #66bb6a);
    color: white; padding: 12px; border-radius: 8px;
    font-size: 1.3rem; font-weight: bold; margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# ===================================================================
# BASE DE DADOS COMPLETA
# ===================================================================
ATIVOS = {
    "Ações BR": {
        'BEEF3': 'Minerva Foods',
        'MRFG3': 'Marfrig',
        'JBSS3': 'JBS',
        'BRFS3': 'BRF',
        'ABEV3': 'Ambev',
        'MDIA3': 'M. Dias Branco',
        'SMTO3': 'São Martinho',
        'SOJA3': 'Boa Safra',
        'RAIZ4': 'Raízen',
        'CSAN3': 'Cosan',
        'SUZB3': 'Suzano',
        'KLBN11': 'Klabin',
        'SLCE3': 'SLC Agrícola',
        'AGRO3': 'BrasilAgro',
        'CAML3': 'Camil',
        'TTEN3': 'Três Tentos',
        'JALL3': 'Jalles Machado',
        'KEPL3': 'Kepler Weber'
    },
    "BDRs": {
        'A1DM34': 'Archer Daniels',
        'B1UN34': 'Bunge',
        'D1EE34': 'Deere',
        'A1GC34': 'AGCO',
        'M1OS34': 'Mosaic',
        'N1TR34': 'Nutrien',
        'C1TV34': 'Corteva'
    },
    "FIAGROs": {
        'AGRX11': 'Exes Araguaia',
        'BBGO11': 'BB Crédito',
        'FARM11': 'Santa Fé',
        'GCRA11': 'Galápagos',
        'KNCA11': 'Kinea',
        'RURA11': 'Itaú Asset',
        'SNAG11': 'Suno Agro',
        'XPCA11': 'XP Crédito'
    }
}

# ===================================================================
# FUNÇÕES
# ===================================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_brapi_data(ticker):
    """Obtém dados via Brapi"""
    try:
        url = f"https://brapi.dev/api/quote/{ticker}?range=1mo&interval=1d&token={BRAPI_TOKEN}"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if 'results' in data and data['results']:
                return data['results'][0]
    except:
        pass
    return None

@st.cache_data(ttl=600, show_spinner=False)
def get_news():
    """Obtém notícias"""
    try:
        url = f"https://newsapi.org/v2/everything?q=agronegócio OR agricultura&language=pt&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            return resp.json().get('articles', [])
    except:
        pass
    return []

def calculate_score(data):
    """Calcula score de oportunidade simplificado"""
    if not data:
        return 50, "⚪ NEUTRO"
    
    try:
        score = 50
        
        # Variação
        change = data.get('regularMarketChangePercent', 0)
        if change < -5:
            score += 20
        elif change < -2:
            score += 10
        elif change > 5:
            score -= 15
        elif change > 2:
            score -= 10
        
        # Volume vs média
        volume = data.get('regularMarketVolume', 0)
        avg_volume = data.get('averageDailyVolume10Day', 1)
        if avg_volume > 0:
            vol_ratio = volume / avg_volume
            if vol_ratio > 1.5:
                score += 10
            elif vol_ratio < 0.5:
                score -= 5
        
        # Preço vs máxima/mínima 52 semanas
        price = data.get('regularMarketPrice', 0)
        high52 = data.get('fiftyTwoWeekHigh', price)
        low52 = data.get('fiftyTwoWeekLow', price)
        
        if high52 > low52:
            position = (price - low52) / (high52 - low52)
            if position < 0.3:  # Perto da mínima
                score += 20
            elif position > 0.7:  # Perto da máxima
                score -= 15
        
        score = max(0, min(100, score))
        
        if score >= 70:
            return score, "🟢 COMPRA FORTE"
        elif score >= 55:
            return score, "🟢 COMPRA"
        elif score >= 45:
            return score, "⚪ NEUTRO"
        elif score >= 30:
            return score, "🟡 VENDA FRACA"
        else:
            return score, "🔴 VENDA"
    
    except:
        return 50, "⚪ NEUTRO"

# ===================================================================
# INTERFACE
# ===================================================================
st.title("🌾 Agro Tracker Pro - Sistema Completo de Análise")
st.markdown("### 📊 Monitoramento em Tempo Real | Análise Técnica + Fundamentalista + Notícias")

# Sidebar
st.sidebar.header("⚙️ Configurações")
st.sidebar.caption(f"⏰ Atualizado: {datetime.now().strftime('%H:%M:%S')}")
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (60s)", False)
st.sidebar.markdown("---")
st.sidebar.info("💡 Dados via Brapi + NewsAPI")

# Notícias
with st.expander("📰 Últimas Notícias do Agronegócio", expanded=False):
    news = get_news()
    if news:
        for article in news:
            st.markdown(f"""
            **{article.get('title', 'Sem título')}**  
            📅 {article.get('publishedAt', '')[:10]} | {article.get('source', {}).get('name', '')}  
            [Ler mais →]({article.get('url', '#')})
            """)
            st.markdown("---")
    else:
        st.info("Notícias indisponíveis")

st.markdown("---")

# ===================================================================
# COLETA E PROCESSAMENTO
# ===================================================================
all_results = []

progress = st.progress(0)
status = st.empty()

total = sum(len(v) for v in ATIVOS.values())
count = 0

for categoria, ativos in ATIVOS.items():
    for ticker, nome in ativos.items():
        count += 1
        progress.progress(count / total)
        status.text(f"Processando {ticker}... ({count}/{total})")
        
        data = get_brapi_data(ticker)
        
        if data:
            score, classification = calculate_score(data)
            
            all_results.append({
                'Categoria': categoria,
                'Ticker': ticker,
                'Nome': nome,
                'Preço': data.get('regularMarketPrice', 0),
                'Variação': data.get('regularMarketChangePercent', 0),
                'Volume': data.get('regularMarketVolume', 0),
                'Score': score,
                'Classificação': classification,
                'Data': data
            })
        
        time.sleep(0.1)  # Rate limiting

progress.empty()
status.empty()

# Ordenar por score
all_results.sort(key=lambda x: x['Score'], reverse=True)

# ===================================================================
# EXIBIÇÃO
# ===================================================================
if not all_results:
    st.error("❌ Nenhum dado disponível no momento")
else:
    st.success(f"✅ {len(all_results)} ativos analisados!")
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    scores = [r['Score'] for r in all_results]
    compras = len([r for r in all_results if r['Score'] >= 55])
    vendas = len([r for r in all_results if r['Score'] < 45])
    
    with col1:
        st.metric("Score Médio", f"{sum(scores)/len(scores):.1f}/100")
    with col2:
        st.metric("🟢 Compras", compras)
    with col3:
        st.metric("⚪ Neutros", len(all_results) - compras - vendas)
    with col4:
        st.metric("🔴 Vendas", vendas)
    
    st.markdown("---")
    
    # Por Categoria
    for categoria in ATIVOS.keys():
        cat_data = [r for r in all_results if r['Categoria'] == categoria]
        
        if not cat_data:
            continue
        
        st.markdown(f"<div class='cat-header'>📊 {categoria} ({len(cat_data)} ativos)</div>", 
                   unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, result in enumerate(cat_data):
            with cols[idx % 3]:
                # Cor do card
                if result['Score'] >= 70:
                    color = "#00c853"
                elif result['Score'] >= 55:
                    color = "#69f0ae"
                elif result['Score'] >= 45:
                    color = "#ffd54f"
                else:
                    color = "#ff8a80"
                
                st.markdown(f"""
                <div style='background:white; padding:15px; border-radius:10px; 
                            border-left:5px solid {color}; box-shadow:0 2px 8px rgba(0,0,0,0.1);'>
                    <h4 style='margin:0; color:#2e7d32;'>{result['Nome']}</h4>
                    <p style='margin:5px 0; color:#666;'>{result['Ticker']}</p>
                    <div style='background:{color}; color:white; padding:8px; 
                                border-radius:20px; text-align:center; font-weight:bold;'>
                        Score: {result['Score']}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.metric(
                    "Preço",
                    f"R$ {result['Preço']:.2f}",
                    f"{result['Variação']:+.2f}%"
                )
                
                st.markdown(f"**{result['Classificação']}**")
                
                # Gráfico mini
                with st.expander("📈 Ver Gráfico"):
                    hist = result['Data'].get('historicalDataPrice', [])
                    if hist and len(hist) > 0:
                        df_hist = pd.DataFrame(hist)
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=list(range(len(df_hist))),
                            y=df_hist['close'],
                            mode='lines',
                            name='Preço',
                            line=dict(color=color, width=2)
                        ))
                        
                        fig.update_layout(
                            height=200,
                            margin=dict(l=0, r=0, t=0, b=0),
                            showlegend=False,
                            xaxis_visible=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Histórico indisponível")
        
        st.markdown("---")
    
    # Tabela Resumo
    st.subheader("📋 Tabela Consolidada")
    
    df_table = pd.DataFrame([{
        'Categoria': r['Categoria'],
        'Ticker': r['Ticker'],
        'Nome': r['Nome'],
        'Preço (R$)': f"{r['Preço']:.2f}",
        'Var (%)': f"{r['Variação']:+.2f}",
        'Score': r['Score'],
        'Recomendação': r['Classificação']
    } for r in all_results])
    
    st.dataframe(df_table, use_container_width=True, hide_index=True)
    
    # Download
    csv = df_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Baixar CSV",
        csv,
        f"agro_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#666;'>
    <p><strong>🌾 Agro Tracker Pro</strong> | Desenvolvido com Brapi + NewsAPI</p>
    <p>⚠️ Sistema educacional. Não constitui recomendação de investimento.</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    time.sleep(60)
    st.rerun()

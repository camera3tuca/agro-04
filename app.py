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

# CSS PROFISSIONAL
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {font-family: 'Inter', sans-serif;}

.main {background: linear-gradient(180deg, #f8fdf9 0%, #ffffff 100%); padding: 1rem;}

h1 {
    background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    text-align: center;
    margin-bottom: 0.5rem !important;
}

.subtitle {
    text-align: center;
    color: #5f6368;
    font-size: 1.1rem;
    margin-bottom: 2rem;
    font-weight: 500;
}

.stats-container {
    display: flex;
    gap: 15px;
    margin: 25px 0;
    flex-wrap: wrap;
}

.stat-card {
    flex: 1;
    min-width: 200px;
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid #e8eaed;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.stat-label {
    font-size: 0.85rem;
    color: #5f6368;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #202124;
    line-height: 1;
}

.stat-icon {
    font-size: 2rem;
    margin-bottom: 10px;
}

.category-section {
    background: white;
    padding: 30px;
    border-radius: 20px;
    margin: 30px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid #e8eaed;
}

.category-header {
    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
    color: white;
    padding: 18px 25px;
    border-radius: 12px;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 25px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 15px rgba(26,115,232,0.3);
}

.asset-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 25px;
    border-radius: 16px;
    border: 2px solid #e8eaed;
    margin: 15px 0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.asset-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
    background: var(--border-color);
}

.asset-card:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    border-color: var(--border-color);
}

.asset-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #202124;
    margin-bottom: 5px;
}

.asset-ticker {
    font-size: 0.9rem;
    color: #5f6368;
    font-weight: 600;
    background: #f1f3f4;
    padding: 4px 12px;
    border-radius: 8px;
    display: inline-block;
    margin-bottom: 15px;
}

.score-badge {
    display: inline-block;
    padding: 12px 24px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 15px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.score-strong-buy {background: linear-gradient(135deg, #00c853 0%, #00e676 100%); color: white;}
.score-buy {background: linear-gradient(135deg, #69f0ae 0%, #76ff03 100%); color: #1b5e20;}
.score-neutral {background: linear-gradient(135deg, #ffd54f 0%, #ffeb3b 100%); color: #f57f17;}
.score-sell {background: linear-gradient(135deg, #ff8a80 0%, #ff5252 100%); color: white;}

.price-container {
    display: flex;
    align-items: center;
    gap: 15px;
    margin: 15px 0;
}

.price-value {
    font-size: 2rem;
    font-weight: 800;
    color: #202124;
}

.price-change {
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1rem;
}

.price-up {background: #c8e6c9; color: #2e7d32;}
.price-down {background: #ffcdd2; color: #c62828;}

.news-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border-left: 4px solid #1a73e8;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
}

.news-card:hover {
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    transform: translateX(5px);
}

.news-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #202124;
    margin-bottom: 8px;
    line-height: 1.4;
}

.news-meta {
    font-size: 0.85rem;
    color: #5f6368;
    margin-bottom: 10px;
}

.sidebar-header {
    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(26,115,232,0.3);
}

.sidebar-info {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    border-left: 4px solid #34a853;
    margin: 15px 0;
}

.stButton>button {
    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(26,115,232,0.3);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(26,115,232,0.4);
}

.progress-container {
    background: white;
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ===================================================================
# BASE DE DADOS
# ===================================================================
ATIVOS = {
    "💼 Ações Brasileiras": {
        'BEEF3': 'Minerva Foods', 'MRFG3': 'Marfrig', 'JBSS3': 'JBS',
        'BRFS3': 'BRF', 'ABEV3': 'Ambev', 'MDIA3': 'M. Dias Branco',
        'SMTO3': 'São Martinho', 'SOJA3': 'Boa Safra', 'RAIZ4': 'Raízen',
        'CSAN3': 'Cosan', 'SUZB3': 'Suzano', 'KLBN11': 'Klabin',
        'SLCE3': 'SLC Agrícola', 'AGRO3': 'BrasilAgro', 'CAML3': 'Camil',
        'TTEN3': 'Três Tentos', 'JALL3': 'Jalles Machado', 'KEPL3': 'Kepler Weber'
    },
    "🌎 BDRs Internacionais": {
        'A1DM34': 'Archer Daniels', 'B1UN34': 'Bunge', 'D1EE34': 'Deere',
        'A1GC34': 'AGCO', 'M1OS34': 'Mosaic', 'N1TR34': 'Nutrien', 'C1TV34': 'Corteva'
    },
    "🏦 FIAGROs": {
        'AGRX11': 'Exes Araguaia', 'BBGO11': 'BB Crédito', 'FARM11': 'Santa Fé',
        'GCRA11': 'Galápagos', 'KNCA11': 'Kinea', 'RURA11': 'Itaú Asset',
        'SNAG11': 'Suno Agro', 'XPCA11': 'XP Crédito'
    }
}

# ===================================================================
# FUNÇÕES
# ===================================================================
@st.cache_data(ttl=180, show_spinner=False)
def get_brapi_data(ticker):
    """Obtém dados via Brapi com retry"""
    for attempt in range(3):
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?range=3mo&interval=1d&token={BRAPI_TOKEN}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if 'results' in data and data['results']:
                    return data['results'][0]
            time.sleep(0.5 * attempt)
        except:
            time.sleep(0.5 * attempt)
    return None

@st.cache_data(ttl=600, show_spinner=False)
def get_news():
    try:
        url = f"https://newsapi.org/v2/everything?q=agronegócio OR agro OR agricultura&language=pt&sortBy=publishedAt&pageSize=4&apiKey={NEWS_API_KEY}"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            return resp.json().get('articles', [])
    except:
        pass
    return []

def calculate_score(data):
    if not data:
        return 50, "⚪ NEUTRO"
    
    score = 50
    price = data.get('regularMarketPrice', 0)
    change = data.get('regularMarketChangePercent', 0)
    
    # Variação (peso 30)
    if change < -7:
        score += 30
    elif change < -4:
        score += 20
    elif change < -2:
        score += 10
    elif change > 7:
        score -= 25
    elif change > 4:
        score -= 15
    
    # Posição 52 semanas (peso 30)
    high52 = data.get('fiftyTwoWeekHigh', price)
    low52 = data.get('fiftyTwoWeekLow', price)
    
    if high52 > low52 and price > 0:
        position = (price - low52) / (high52 - low52)
        if position < 0.25:
            score += 30
        elif position < 0.4:
            score += 20
        elif position > 0.75:
            score -= 25
        elif position > 0.6:
            score -= 15
    
    # Volume (peso 20)
    volume = data.get('regularMarketVolume', 0)
    avg_volume = data.get('averageDailyVolume10Day', 1)
    if avg_volume > 0:
        vol_ratio = volume / avg_volume
        if vol_ratio > 2:
            score += 20
        elif vol_ratio > 1.3:
            score += 10
        elif vol_ratio < 0.5:
            score -= 10
    
    score = max(0, min(100, score))
    
    if score >= 75:
        return score, "🟢 COMPRA FORTE"
    elif score >= 60:
        return score, "🟢 COMPRA"
    elif score >= 45:
        return score, "⚪ NEUTRO"
    else:
        return score, "🔴 VENDA"

# ===================================================================
# INTERFACE
# ===================================================================
st.markdown("<h1>🌾 Agro Tracker Pro</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sistema Inteligente de Análise de Investimentos no Agronegócio</div>", 
           unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("<div class='sidebar-header'><h2 style='margin:0; color:white;'>⚙️ Configurações</h2></div>", 
               unsafe_allow_html=True)
    
    auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", False)
    show_graphs = st.checkbox("📈 Mostrar Gráficos", True)
    
    st.markdown("<div class='sidebar-info'>", unsafe_allow_html=True)
    st.markdown(f"**⏰ Atualizado:** {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("**📡 Fonte:** Brapi + NewsAPI")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**💡 Legenda de Scores:**")
    st.markdown("🟢 75-100: Compra Forte")
    st.markdown("🟢 60-74: Compra")
    st.markdown("⚪ 45-59: Neutro")
    st.markdown("🔴 0-44: Venda")

# NOTÍCIAS
with st.expander("📰 Últimas Notícias do Agronegócio", expanded=False):
    news = get_news()
    if news:
        for article in news:
            st.markdown(f"""
            <div class='news-card'>
                <div class='news-title'>{article.get('title', 'Sem título')}</div>
                <div class='news-meta'>
                    📅 {article.get('publishedAt', '')[:10]} | 
                    📰 {article.get('source', {}).get('name', 'Fonte desconhecida')}
                </div>
                <a href='{article.get('url', '#')}' target='_blank' 
                   style='color:#1a73e8; font-weight:600;'>Ler notícia completa →</a>
            </div>
            """, unsafe_allow_html=True)

# COLETA DE DADOS
all_results = []

progress_container = st.container()
with progress_container:
    st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
    st.markdown("### 🔄 Coletando Dados dos Ativos...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = sum(len(v) for v in ATIVOS.values())
    count = 0
    
    for categoria, ativos in ATIVOS.items():
        for ticker, nome in ativos.items():
            count += 1
            progress_bar.progress(count / total)
            status_text.markdown(f"**Processando:** {nome} ({ticker}) - {count}/{total}")
            
            data = get_brapi_data(ticker)
            
            if data and data.get('regularMarketPrice'):
                score, classification = calculate_score(data)
                
                all_results.append({
                    'Categoria': categoria,
                    'Ticker': ticker,
                    'Nome': nome,
                    'Preço': data.get('regularMarketPrice', 0),
                    'Variação': data.get('regularMarketChangePercent', 0),
                    'Score': score,
                    'Classificação': classification,
                    'Data': data
                })
            
            time.sleep(0.15)
    
    st.markdown("</div>", unsafe_allow_html=True)

progress_container.empty()

# ORDENAR
all_results.sort(key=lambda x: x['Score'], reverse=True)

# ESTATÍSTICAS
if all_results:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #00c853 0%, #69f0ae 100%); 
                color: white; padding: 20px; border-radius: 16px; text-align: center; 
                margin: 30px 0; box-shadow: 0 6px 25px rgba(0,200,83,0.3);'>
        <h2 style='margin:0; font-size: 2rem;'>✅ {len(all_results)} Ativos Analisados com Sucesso!</h2>
    </div>
    """, unsafe_allow_html=True)
    
    scores = [r['Score'] for r in all_results]
    compras = len([r for r in all_results if r['Score'] >= 60])
    neutros = len([r for r in all_results if 45 <= r['Score'] < 60])
    vendas = len([r for r in all_results if r['Score'] < 45])
    
    st.markdown("<div class='stats-container'>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-icon'>📊</div>
            <div class='stat-label'>Score Médio</div>
            <div class='stat-value' style='color:#1a73e8;'>{sum(scores)/len(scores):.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-icon'>🟢</div>
            <div class='stat-label'>Oportunidades</div>
            <div class='stat-value' style='color:#00c853;'>{compras}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-icon'>⚪</div>
            <div class='stat-label'>Neutros</div>
            <div class='stat-value' style='color:#fbc02d;'>{neutros}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-icon'>🔴</div>
            <div class='stat-label'>Evitar</div>
            <div class='stat-value' style='color:#d32f2f;'>{vendas}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # POR CATEGORIA
    for categoria in ATIVOS.keys():
        cat_data = [r for r in all_results if r['Categoria'] == categoria]
        
        if not cat_data:
            continue
        
        st.markdown("<div class='category-section'>", unsafe_allow_html=True)
        st.markdown(f"<div class='category-header'>{categoria} <span style='opacity:0.8;'>({len(cat_data)} ativos)</span></div>", 
                   unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, result in enumerate(cat_data):
            with cols[idx % 3]:
                # Cor baseada no score
                if result['Score'] >= 75:
                    border_color = "#00c853"
                    badge_class = "score-strong-buy"
                elif result['Score'] >= 60:
                    border_color = "#69f0ae"
                    badge_class = "score-buy"
                elif result['Score'] >= 45:
                    border_color = "#ffd54f"
                    badge_class = "score-neutral"
                else:
                    border_color = "#ff8a80"
                    badge_class = "score-sell"
                
                change_class = "price-up" if result['Variação'] >= 0 else "price-down"
                
                st.markdown(f"""
                <div class='asset-card' style='--border-color: {border_color};'>
                    <div class='asset-name'>{result['Nome']}</div>
                    <div class='asset-ticker'>{result['Ticker']}</div>
                    
                    <div class='price-container'>
                        <div class='price-value'>R$ {result['Preço']:.2f}</div>
                        <div class='price-change {change_class}'>
                            {result['Variação']:+.2f}%
                        </div>
                    </div>
                    
                    <div class='score-badge {badge_class}'>
                        Score: {result['Score']:.0f}/100
                    </div>
                    
                    <div style='margin-top: 15px; font-size: 1.1rem; font-weight: 600;'>
                        {result['Classificação']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if show_graphs:
                    with st.expander("📈 Ver Histórico"):
                        hist = result['Data'].get('historicalDataPrice', [])
                        if hist and len(hist) > 5:
                            df = pd.DataFrame(hist)
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=list(range(len(df))),
                                y=df['close'],
                                fill='tozeroy',
                                fillcolor=f'rgba({int(border_color[1:3], 16)},{int(border_color[3:5], 16)},{int(border_color[5:7], 16)},0.2)',
                                line=dict(color=border_color, width=3),
                                name='Preço'
                            ))
                            
                            fig.update_layout(
                                height=200,
                                margin=dict(l=0, r=0, t=10, b=0),
                                showlegend=False,
                                xaxis_visible=False,
                                yaxis_visible=False,
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # TABELA
    st.markdown("### 📋 Tabela Consolidada")
    
    df_table = pd.DataFrame([{
        'Categoria': r['Categoria'],
        'Nome': r['Nome'],
        'Ticker': r['Ticker'],
        'Preço': f"R$ {r['Preço']:.2f}",
        'Variação': f"{r['Variação']:+.2f}%",
        'Score': f"{r['Score']:.0f}/100",
        'Recomendação': r['Classificação']
    } for r in all_results])
    
    st.dataframe(df_table, use_container_width=True, hide_index=True)
    
    csv = df_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Baixar Relatório Completo (CSV)",
        csv,
        f"agro_tracker_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv"
    )

else:
    st.error("❌ Nenhum ativo foi processado. Verifique a conexão com a API.")

# FOOTER
st.markdown("---")
st.markdown("""
<div style='text-align:center; padding: 30px; color:#5f6368;'>
    <p style='font-size: 1.1rem; font-weight: 600;'>🌾 Agro Tracker Pro</p>
    <p>Desenvolvido com Brapi API + NewsAPI | Dados em tempo real</p>
    <p style='font-size: 0.9rem; opacity: 0.7;'>⚠️ Sistema educacional. Não constitui recomendação de investimento.</p>
</div>
""", unsafe_allow_html=True)

if auto_refresh:
    time.sleep(60)
    st.rerun()

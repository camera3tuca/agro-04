import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# CONFIGURAÇÕES
BRAPI_TOKEN = "iExnKM1xcbQcYL3cNPhPQ3"
NEWS_API_KEY = "ec7100fa90ef4e3f9a69a914050dd736"

st.set_page_config(page_title="🌾 Agro Tracker Pro", page_icon="🌾", layout="wide")

# CSS PROFISSIONAL
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
* {font-family: 'Inter', sans-serif;}
.main {background: linear-gradient(180deg, #f0f8f0 0%, #ffffff 100%); padding: 1rem;}
h1 {
    background: linear-gradient(135deg, #1b5e20 0%, #4caf50 50%, #81c784 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem !important;
    font-weight: 900 !important;
    text-align: center;
    margin-bottom: 0 !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle {
    text-align: center;
    color: #424242;
    font-size: 1.2rem;
    margin: 10px 0 30px 0;
    font-weight: 500;
}
.success-banner {
    background: linear-gradient(135deg, #00c853 0%, #69f0ae 100%);
    color: white;
    padding: 25px;
    border-radius: 16px;
    text-align: center;
    font-size: 1.8rem;
    font-weight: 800;
    margin: 25px 0;
    box-shadow: 0 8px 30px rgba(0,200,83,0.4);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% {transform: scale(1);}
    50% {transform: scale(1.02);}
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin: 30px 0;
}
.stat-card {
    background: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.1);
    border: 2px solid #e0e0e0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: var(--color);
}
.stat-card:hover {
    transform: translateY(-10px) scale(1.03);
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}
.stat-icon {
    font-size: 3rem;
    margin-bottom: 15px;
    display: block;
}
.stat-label {
    font-size: 0.9rem;
    color: #757575;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.stat-value {
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1;
    color: var(--color);
}
.cat-section {
    background: white;
    padding: 35px;
    border-radius: 24px;
    margin: 35px 0;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08);
    border: 2px solid #e8eaed;
}
.cat-header {
    background: linear-gradient(135deg, #1565c0 0%, #1976d2 50%, #42a5f5 100%);
    color: white;
    padding: 22px 30px;
    border-radius: 16px;
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 6px 20px rgba(21,101,192,0.35);
}
.asset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin-top: 20px;
}
.asset-card {
    background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
    padding: 28px;
    border-radius: 18px;
    border-left: 8px solid var(--color);
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}
.asset-card:hover {
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    border-left-width: 12px;
}
.asset-name {
    font-size: 1.4rem;
    font-weight: 800;
    color: #212121;
    margin-bottom: 8px;
    line-height: 1.3;
}
.asset-ticker {
    font-size: 0.95rem;
    color: #616161;
    font-weight: 700;
    background: #f5f5f5;
    padding: 6px 14px;
    border-radius: 10px;
    display: inline-block;
    margin-bottom: 15px;
    border: 1px solid #e0e0e0;
}
.price-container {
    margin: 18px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}
.price-big {
    font-size: 2.3rem;
    font-weight: 900;
    color: #1a237e;
}
.price-change {
    padding: 10px 18px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 1.1rem;
}
.price-up {background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%); color: #1b5e20; border: 2px solid #81c784;}
.price-down {background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%); color: #b71c1c; border: 2px solid #e57373;}
.score-badge {
    padding: 14px 28px;
    border-radius: 30px;
    font-weight: 800;
    font-size: 1.2rem;
    display: inline-block;
    margin: 12px 0;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}
.score-buy-strong {
    background: linear-gradient(135deg, #00c853 0%, #00e676 50%, #69f0ae 100%);
    color: white;
}
.score-buy {
    background: linear-gradient(135deg, #76ff03 0%, #b2ff59 100%);
    color: #1b5e20;
}
.score-neutral {
    background: linear-gradient(135deg, #ffd54f 0%, #ffeb3b 50%, #fff176 100%);
    color: #f57c00;
}
.score-sell {
    background: linear-gradient(135deg, #ff5252 0%, #ff1744 50%, #ff8a80 100%);
    color: white;
}
.recomm-text {
    margin-top: 12px;
    font-weight: 700;
    font-size: 1.15rem;
    padding: 8px 0;
}
.news-card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    border-left: 5px solid #1976d2;
    margin: 14px 0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    transition: all 0.3s;
}
.news-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    transform: translateX(8px);
    border-left-width: 8px;
}
.news-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #212121;
    margin-bottom: 10px;
    line-height: 1.4;
}
.news-meta {
    font-size: 0.88rem;
    color: #757575;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# BASE DE DADOS
ATIVOS = {
    "💼 Ações Brasileiras": {
        'BEEF3': 'Minerva Foods', 'MRFG3': 'Marfrig', 'JBSS3': 'JBS', 'BRFS3': 'BRF',
        'ABEV3': 'Ambev', 'MDIA3': 'M. Dias Branco', 'SMTO3': 'São Martinho',
        'SOJA3': 'Boa Safra', 'RAIZ4': 'Raízen', 'CSAN3': 'Cosan', 'SUZB3': 'Suzano',
        'KLBN11': 'Klabin', 'SLCE3': 'SLC Agrícola', 'AGRO3': 'BrasilAgro',
        'CAML3': 'Camil', 'TTEN3': 'Três Tentos', 'JALL3': 'Jalles Machado', 'KEPL3': 'Kepler Weber'
    },
    "🌎 BDRs Internacionais": {
        'A1DM34': 'Archer Daniels', 'B1UN34': 'Bunge', 'D1EE34': 'Deere', 'A1GC34': 'AGCO',
        'M1OS34': 'Mosaic', 'N1TR34': 'Nutrien', 'C1TV34': 'Corteva'
    },
    "🏦 FIAGROs": {
        'AGRX11': 'Exes Araguaia', 'BBGO11': 'BB Crédito', 'FARM11': 'Santa Fé',
        'GCRA11': 'Galápagos', 'KNCA11': 'Kinea', 'RURA11': 'Itaú Asset',
        'SNAG11': 'Suno Agro', 'XPCA11': 'XP Crédito'
    }
}

@st.cache_data(ttl=180, show_spinner=False)
def get_brapi(ticker):
    for attempt in range(3):
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?range=3mo&interval=1d&token={BRAPI_TOKEN}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                d = r.json()
                if 'results' in d and d['results']:
                    return d['results'][0]
            time.sleep(0.5 * attempt)
        except:
            time.sleep(0.5 * attempt)
    return None

@st.cache_data(ttl=600, show_spinner=False)
def get_news():
    try:
        url = f"https://newsapi.org/v2/everything?q=agronegócio OR agricultura OR commodities&language=pt&sortBy=publishedAt&pageSize=4&apiKey={NEWS_API_KEY}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json().get('articles', [])
    except:
        pass
    return []

def calc_score(data):
    if not data:
        return 50, "⚪ NEUTRO"
    
    score = 50
    price = data.get('regularMarketPrice', 0)
    change = data.get('regularMarketChangePercent', 0)
    
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
    
    high52 = data.get('fiftyTwoWeekHigh', price)
    low52 = data.get('fiftyTwoWeekLow', price)
    
    if high52 > low52 and price > 0:
        pos = (price - low52) / (high52 - low52)
        if pos < 0.25:
            score += 30
        elif pos < 0.4:
            score += 20
        elif pos > 0.75:
            score -= 25
        elif pos > 0.6:
            score -= 15
    
    vol = data.get('regularMarketVolume', 0)
    avg = data.get('averageDailyVolume10Day', 1)
    if avg > 0:
        ratio = vol / avg
        if ratio > 2:
            score += 20
        elif ratio > 1.3:
            score += 10
        elif ratio < 0.5:
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

# INTERFACE
st.markdown("<h1>🌾 Agro Tracker Pro</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sistema Inteligente de Análise de Investimentos • Dados em Tempo Real</div>", 
           unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    auto = st.checkbox("🔄 Auto-refresh (60s)", False)
    graphs = st.checkbox("📈 Mostrar Gráficos", True)
    st.markdown("---")
    st.caption(f"⏰ **Atualizado:** {datetime.now().strftime('%H:%M:%S')}")
    st.info("📡 **Fonte:** Brapi + NewsAPI")
    st.markdown("---")
    st.markdown("**💡 Legenda de Scores:**")
    st.markdown("🟢 **75-100** • Compra Forte")
    st.markdown("🟢 **60-74** • Compra")
    st.markdown("⚪ **45-59** • Neutro")
    st.markdown("🔴 **0-44** • Venda")

with st.expander("📰 Últimas Notícias do Agronegócio", expanded=False):
    news = get_news()
    if news:
        for a in news:
            st.markdown(f"""
            <div class='news-card'>
                <div class='news-title'>{a.get('title', 'Sem título')}</div>
                <div class='news-meta'>📅 {a.get('publishedAt', '')[:10]} | 📰 {a.get('source', {}).get('name', 'Fonte')}</div>
                <a href='{a.get('url', '#')}' target='_blank' style='color:#1976d2; font-weight:700;'>Ler notícia completa →</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Notícias temporariamente indisponíveis")

results = []
prog = st.progress(0)
status = st.empty()

total = sum(len(v) for v in ATIVOS.values())
cnt = 0

for cat, ativos in ATIVOS.items():
    for tick, nome in ativos.items():
        cnt += 1
        prog.progress(cnt / total)
        status.markdown(f"**Processando:** {nome} • {cnt}/{total}")
        
        data = get_brapi(tick)
        
        if data and data.get('regularMarketPrice'):
            score, classif = calc_score(data)
            
            results.append({
                'Cat': cat,
                'Ticker': tick,
                'Nome': nome,
                'Preço': data.get('regularMarketPrice', 0),
                'Var': data.get('regularMarketChangePercent', 0),
                'Score': score,
                'Class': classif,
                'Data': data
            })
        
        time.sleep(0.15)

prog.empty()
status.empty()

results.sort(key=lambda x: x['Score'], reverse=True)

if results:
    st.markdown(f"""
    <div class='success-banner'>
        ✅ {len(results)} ATIVOS ANALISADOS COM SUCESSO!
    </div>
    """, unsafe_allow_html=True)
    
    scores = [r['Score'] for r in results]
    compras = len([r for r in results if r['Score'] >= 60])
    neutros = len([r for r in results if 45 <= r['Score'] < 60])
    vendas = len([r for r in results if r['Score'] < 45])
    
    st.markdown("<div class='stats-grid'>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class='stat-card' style='--color:#1976d2;'>
            <span class='stat-icon'>📊</span>
            <div class='stat-label'>Score Médio</div>
            <div class='stat-value' style='--color:#1976d2;'>{sum(scores)/len(scores):.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class='stat-card' style='--color:#00c853;'>
            <span class='stat-icon'>🟢</span>
            <div class='stat-label'>Compras</div>
            <div class='stat-value' style='--color:#00c853;'>{compras}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"""
        <div class='stat-card' style='--color:#fbc02d;'>
            <span class='stat-icon'>⚪</span>
            <div class='stat-label'>Neutros</div>
            <div class='stat-value' style='--color:#fbc02d;'>{neutros}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"""
        <div class='stat-card' style='--color:#d32f2f;'>
            <span class='stat-icon'>🔴</span>
            <div class='stat-label'>Vendas</div>
            <div class='stat-value' style='--color:#d32f2f;'>{vendas}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    for cat in ATIVOS.keys():
        cat_data = [r for r in results if r['Cat'] == cat]
        
        if not cat_data:
            continue
        
        st.markdown("<div class='cat-section'>", unsafe_allow_html=True)
        st.markdown(f"<div class='cat-header'><span>{cat}</span><span style='opacity:0.9;'>• {len(cat_data)} ativos</span></div>", 
                   unsafe_allow_html=True)
        
        st.markdown("<div class='asset-grid'>", unsafe_allow_html=True)
        
        for r in cat_data:
            if r['Score'] >= 75:
                color = "#00c853"
                badge = "score-buy-strong"
            elif r['Score'] >= 60:
                color = "#76ff03"
                badge = "score-buy"
            elif r['Score'] >= 45:
                color = "#ffd54f"
                badge = "score-neutral"
            else:
                color = "#ff5252"
                badge = "score-sell"
            
            change_class = "price-up" if r['Var'] >= 0 else "price-down"
            
            st.markdown(f"""
            <div class='asset-card' style='--color: {color};'>
                <div class='asset-name'>{r['Nome']}</div>
                <div class='asset-ticker'>{r['Ticker']}</div>
                <div class='price-container'>
                    <span class='price-big'>R$ {r['Preço']:.2f}</span>
                    <span class='price-change {change_class}'>{r['Var']:+.2f}%</span>
                </div>
                <div class='score-badge {badge}'>
                    Score: {r['Score']:.0f}/100
                </div>
                <div class='recomm-text'>{r['Class']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        if graphs:
            with st.expander(f"📈 Ver Gráficos de {cat}", expanded=False):
                cols = st.columns(3)
                for idx, r in enumerate(cat_data):
                    with cols[idx % 3]:
                        hist = r['Data'].get('historicalDataPrice', [])
                        if hist and len(hist) > 5:
                            df = pd.DataFrame(hist)
                            
                            if r['Score'] >= 75:
                                color = "#00c853"
                            elif r['Score'] >= 60:
                                color = "#76ff03"
                            elif r['Score'] >= 45:
                                color = "#ffd54f"
                            else:
                                color = "#ff5252"
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=list(range(len(df))),
                                y=df['close'],
                                fill='tozeroy',
                                line=dict(color=color, width=3),
                                name=r['Nome']
                            ))
                            
                            fig.update_layout(
                                title=f"{r['Nome']} ({r['Ticker']})",
                                height=250,
                                margin=dict(l=0, r=0, t=30, b=0),
                                showlegend=False,
                                xaxis_visible=False,
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📋 Tabela Consolidada • Ranking Completo")
    
    df = pd.DataFrame([{
        'Categoria': r['Cat'],
        'Nome': r['Nome'],
        'Ticker': r['Ticker'],
        'Preço': f"R$ {r['Preço']:.2f}",
        'Variação': f"{r['Var']:+.2f}%",
        'Score': f"{r['Score']:.0f}/100",
        'Recomendação': r['Class']
    } for r in results])
    
    st.dataframe(df, use_container_width=True, hide_index=True, height=600)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Baixar Relatório Completo (CSV)",
        csv,
        f"agro_tracker_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
        use_container_width=True
    )
else:
    st.error("❌ Nenhum ativo foi processado. Verifique a conexão.")

st.markdown("---")
st.markdown("""
<div style='text-align:center; padding:30px; color:#616161;'>
    <p style='font-size:1.3rem; font-weight:700; margin-bottom:10px;'>🌾 Agro Tracker Pro</p>
    <p style='font-size:1rem;'>Desenvolvido com Brapi API + NewsAPI • Dados em tempo real</p>
    <p style='font-size:0.9rem; color:#9e9e9e; margin-top:10px;'>⚠️ Sistema educacional • Não constitui recomendação de investimento</p>
</div>
""", unsafe_allow_html=True)

if auto:
    time.sleep(60)
    st.rerun()

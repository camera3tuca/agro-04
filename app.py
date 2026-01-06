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

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
* {font-family: 'Inter', sans-serif;}
.main {background: linear-gradient(180deg, #f8fdf9 0%, #ffffff 100%);}
h1 {background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important; font-weight: 800 !important; text-align: center;}
.subtitle {text-align: center; color: #5f6368; font-size: 1.1rem; margin-bottom: 2rem;}
.stat-card {background: white; padding: 25px; border-radius: 16px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 10px;}
.stat-card:hover {transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0,0,0,0.12);}
.stat-label {font-size: 0.85rem; color: #5f6368; font-weight: 600; 
             text-transform: uppercase; letter-spacing: 0.5px;}
.stat-value {font-size: 2.5rem; font-weight: 800; color: #202124;}
.cat-header {background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
             color: white; padding: 18px 25px; border-radius: 12px; font-size: 1.4rem;
             font-weight: 700; margin: 25px 0; box-shadow: 0 4px 15px rgba(26,115,232,0.3);}
.asset-card {background: white; padding: 25px; border-radius: 16px;
             border-left: 6px solid var(--color); margin: 15px 0;
             box-shadow: 0 2px 15px rgba(0,0,0,0.08); transition: all 0.3s;}
.asset-card:hover {transform: scale(1.02); box-shadow: 0 8px 25px rgba(0,0,0,0.15);}
.asset-name {font-size: 1.3rem; font-weight: 700; color: #202124; margin-bottom: 5px;}
.asset-ticker {font-size: 0.9rem; color: #5f6368; font-weight: 600;
               background: #f1f3f4; padding: 4px 12px; border-radius: 8px;
               display: inline-block; margin-bottom: 10px;}
.price-big {font-size: 2rem; font-weight: 800; color: #202124;}
.price-change {padding: 8px 16px; border-radius: 8px; font-weight: 700;
               display: inline-block; margin-left: 10px;}
.price-up {background: #c8e6c9; color: #2e7d32;}
.price-down {background: #ffcdd2; color: #c62828;}
.score-badge {padding: 12px 24px; border-radius: 25px; font-weight: 700;
              font-size: 1.1rem; margin: 10px 0; display: inline-block;
              box-shadow: 0 4px 15px rgba(0,0,0,0.2);}
.score-buy-strong {background: linear-gradient(135deg, #00c853 0%, #00e676 100%); color: white;}
.score-buy {background: linear-gradient(135deg, #69f0ae 0%, #76ff03 100%); color: #1b5e20;}
.score-neutral {background: linear-gradient(135deg, #ffd54f 0%, #ffeb3b 100%); color: #f57f17;}
.score-sell {background: linear-gradient(135deg, #ff8a80 0%, #ff5252 100%); color: white;}
.news-card {background: white; padding: 20px; border-radius: 12px;
            border-left: 4px solid #1a73e8; margin: 12px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: all 0.3s;}
.news-card:hover {box-shadow: 0 4px 15px rgba(0,0,0,0.12); transform: translateX(5px);}
</style>
""", unsafe_allow_html=True)

# BASE DE DADOS
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
        url = f"https://newsapi.org/v2/everything?q=agronegócio&language=pt&sortBy=publishedAt&pageSize=4&apiKey={NEWS_API_KEY}"
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
st.markdown("<div class='subtitle'>Sistema Inteligente de Análise de Investimentos no Agronegócio</div>", 
           unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    auto = st.checkbox("🔄 Auto-refresh (60s)", False)
    graphs = st.checkbox("📈 Gráficos", True)
    st.markdown("---")
    st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    st.info("📡 Brapi + NewsAPI")
    st.markdown("**💡 Scores:**")
    st.markdown("🟢 75-100: Compra Forte")
    st.markdown("🟢 60-74: Compra")
    st.markdown("⚪ 45-59: Neutro")
    st.markdown("🔴 0-44: Venda")

with st.expander("📰 Notícias do Agronegócio", expanded=False):
    news = get_news()
    if news:
        for a in news:
            st.markdown(f"""
            <div class='news-card'>
                <strong>{a.get('title', '')}</strong><br>
                <small>📅 {a.get('publishedAt', '')[:10]} | {a.get('source', {}).get('name', '')}</small><br>
                <a href='{a.get('url', '#')}' target='_blank'>Ler →</a>
            </div>
            """, unsafe_allow_html=True)

results = []
prog = st.progress(0)
status = st.empty()

total = sum(len(v) for v in ATIVOS.values())
cnt = 0

for cat, ativos in ATIVOS.items():
    for tick, nome in ativos.items():
        cnt += 1
        prog.progress(cnt / total)
        status.text(f"Processando {nome} ({cnt}/{total})")
        
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
    st.success(f"✅ {len(results)} ativos analisados!")
    
    scores = [r['Score'] for r in results]
    compras = len([r for r in results if r['Score'] >= 60])
    neutros = len([r for r in results if 45 <= r['Score'] < 60])
    vendas = len([r for r in results if r['Score'] < 45])
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-label'>📊 Score Médio</div>
            <div class='stat-value' style='color:#1a73e8;'>{sum(scores)/len(scores):.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-label'>🟢 Compras</div>
            <div class='stat-value' style='color:#00c853;'>{compras}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-label'>⚪ Neutros</div>
            <div class='stat-value' style='color:#fbc02d;'>{neutros}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-label'>🔴 Vendas</div>
            <div class='stat-value' style='color:#d32f2f;'>{vendas}</div>
        </div>
        """, unsafe_allow_html=True)
    
    for cat in ATIVOS.keys():
        cat_data = [r for r in results if r['Cat'] == cat]
        
        if not cat_data:
            continue
        
        st.markdown(f"<div class='cat-header'>{cat} ({len(cat_data)} ativos)</div>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, r in enumerate(cat_data):
            with cols[idx % 3]:
                if r['Score'] >= 75:
                    color = "#00c853"
                    badge = "score-buy-strong"
                elif r['Score'] >= 60:
                    color = "#69f0ae"
                    badge = "score-buy"
                elif r['Score'] >= 45:
                    color = "#ffd54f"
                    badge = "score-neutral"
                else:
                    color = "#ff8a80"
                    badge = "score-sell"
                
                change_class = "price-up" if r['Var'] >= 0 else "price-down"
                
                st.markdown(f"""
                <div class='asset-card' style='--color: {color};'>
                    <div class='asset-name'>{r['Nome']}</div>
                    <div class='asset-ticker'>{r['Ticker']}</div>
                    <div>
                        <span class='price-big'>R$ {r['Preço']:.2f}</span>
                        <span class='price-change {change_class}'>{r['Var']:+.2f}%</span>
                    </div>
                    <div class='score-badge {badge}'>Score: {r['Score']:.0f}/100</div>
                    <div style='margin-top:10px; font-weight:600; font-size:1.05rem;'>{r['Class']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if graphs:
                    with st.expander("📈 Histórico"):
                        hist = r['Data'].get('historicalDataPrice', [])
                        if hist and len(hist) > 5:
                            df = pd.DataFrame(hist)
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=list(range(len(df))),
                                y=df['close'],
                                fill='tozeroy',
                                line=dict(color=color, width=3)
                            ))
                            
                            fig.update_layout(
                                height=200,
                                margin=dict(l=0, r=0, t=0, b=0),
                                showlegend=False,
                                xaxis_visible=False,
                                yaxis_visible=False
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Tabela Consolidada")
    
    df = pd.DataFrame([{
        'Categoria': r['Cat'],
        'Nome': r['Nome'],
        'Ticker': r['Ticker'],
        'Preço': f"R$ {r['Preço']:.2f}",
        'Var (%)': f"{r['Var']:+.2f}",
        'Score': f"{r['Score']:.0f}/100",
        'Recomendação': r['Class']
    } for r in results])
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Baixar CSV",
        csv,
        f"agro_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv"
    )
else:
    st.error("❌ Nenhum ativo processado")

st.markdown("---")
st.markdown("""
<div style='text-align:center; padding:20px; color:#666;'>
    <strong>🌾 Agro Tracker Pro</strong><br>
    Brapi + NewsAPI | Dados em tempo real<br>
    <small>⚠️ Sistema educacional</small>
</div>
""", unsafe_allow_html=True)

if auto:
    time.sleep(60)
    st.rerun()

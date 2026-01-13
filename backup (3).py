import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

BRAPI_TOKEN = "iExnKM1xcbQcYL3cNPhPQ3"
NEWS_API_KEY = "ec7100fa90ef4e3f9a69a914050dd736"

st.set_page_config(page_title="Agro Tracker Pro", page_icon="🌾", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
* {font-family: 'Inter', sans-serif;}
.main {background: linear-gradient(180deg, #f0f8f0, #ffffff);}
h1 {background: linear-gradient(135deg, #1b5e20, #4caf50, #81c784);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 3rem !important; font-weight: 900 !important; text-align: center;}
.subtitle {text-align: center; color: #424242; font-size: 1.2rem; margin-bottom: 30px;}
.success {background: linear-gradient(135deg, #00c853, #69f0ae); color: white;
          padding: 25px; border-radius: 16px; text-align: center; font-size: 1.8rem;
          font-weight: 800; margin: 25px 0; box-shadow: 0 8px 30px rgba(0,200,83,0.4);}
.stat {background: white; padding: 30px; border-radius: 20px;
       box-shadow: 0 6px 25px rgba(0,0,0,0.1); margin: 10px; transition: all 0.3s;}
.stat:hover {transform: translateY(-8px); box-shadow: 0 12px 40px rgba(0,0,0,0.15);}
.stat-icon {font-size: 3rem; display: block; margin-bottom: 10px;}
.stat-label {font-size: 0.9rem; color: #757575; font-weight: 700; text-transform: uppercase;}
.stat-value {font-size: 3.5rem; font-weight: 900;}
.cat {background: linear-gradient(135deg, #1565c0, #42a5f5); color: white;
     padding: 22px 30px; border-radius: 16px; font-size: 1.6rem; font-weight: 800;
     margin: 30px 0 20px 0; box-shadow: 0 6px 20px rgba(21,101,192,0.35);}
.card {background: white; padding: 28px; border-radius: 18px; margin: 15px 0;
       box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: all 0.3s;}
.card:hover {transform: translateY(-8px) scale(1.02); box-shadow: 0 12px 35px rgba(0,0,0,0.15);}
.name {font-size: 1.4rem; font-weight: 800; color: #212121; margin-bottom: 8px;}
.ticker {font-size: 0.95rem; color: #616161; font-weight: 700; background: #f5f5f5;
         padding: 6px 14px; border-radius: 10px; display: inline-block; margin-bottom: 15px;}
.price {font-size: 2.3rem; font-weight: 900; color: #1a237e;}
.change {padding: 10px 18px; border-radius: 12px; font-weight: 800;
         font-size: 1.1rem; margin-left: 10px;}
.up {background: #c8e6c9; color: #1b5e20;}
.down {background: #ffcdd2; color: #b71c1c;}
.badge {padding: 14px 28px; border-radius: 30px; font-weight: 800; font-size: 1.2rem;
        display: inline-block; margin: 12px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.25);}
.buy-strong {background: linear-gradient(135deg, #00c853, #69f0ae); color: white;}
.buy {background: linear-gradient(135deg, #76ff03, #b2ff59); color: #1b5e20;}
.neutral {background: linear-gradient(135deg, #ffd54f, #fff176); color: #f57c00;}
.sell {background: linear-gradient(135deg, #ff5252, #ff8a80); color: white;}
.news {background: white; padding: 22px; border-radius: 14px; border-left: 5px solid #1976d2;
       margin: 14px 0; box-shadow: 0 3px 12px rgba(0,0,0,0.08); transition: all 0.3s;}
.news:hover {box-shadow: 0 6px 20px rgba(0,0,0,0.12); transform: translateX(8px);}
</style>
""", unsafe_allow_html=True)

ATIVOS = {
    "Ações BR": {
        'BEEF3': 'Minerva', 'MRFG3': 'Marfrig', 'JBSS3': 'JBS', 'BRFS3': 'BRF',
        'ABEV3': 'Ambev', 'MDIA3': 'M. Dias Branco', 'SMTO3': 'São Martinho',
        'SOJA3': 'Boa Safra', 'RAIZ4': 'Raízen', 'CSAN3': 'Cosan', 'SUZB3': 'Suzano',
        'KLBN11': 'Klabin', 'SLCE3': 'SLC Agrícola', 'AGRO3': 'BrasilAgro',
        'CAML3': 'Camil', 'TTEN3': 'Três Tentos', 'JALL3': 'Jalles Machado', 'KEPL3': 'Kepler Weber'
    },
    "BDRs": {
        'A1DM34': 'Archer Daniels', 'B1UN34': 'Bunge', 'D1EE34': 'Deere', 'A1GC34': 'AGCO',
        'M1OS34': 'Mosaic', 'N1TR34': 'Nutrien', 'C1TV34': 'Corteva'
    },
    "FIAGROs": {
        'AGRX11': 'Exes Araguaia', 'BBGO11': 'BB Crédito', 'FARM11': 'Santa Fé',
        'GCRA11': 'Galápagos', 'KNCA11': 'Kinea', 'RURA11': 'Itaú Asset',
        'SNAG11': 'Suno Agro', 'XPCA11': 'XP Crédito'
    }
}

def get_brapi(ticker):
    for i in range(3):
        try:
            url = f"https://brapi.dev/api/quote/{ticker}?range=3mo&interval=1d&token={BRAPI_TOKEN}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                d = r.json()
                if 'results' in d and d['results']:
                    return d['results'][0]
            time.sleep(0.5 * i)
        except:
            time.sleep(0.5 * i)
    return None

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
        return 50, "NEUTRO"
    
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
        return score, "COMPRA FORTE"
    elif score >= 60:
        return score, "COMPRA"
    elif score >= 45:
        return score, "NEUTRO"
    else:
        return score, "VENDA"

st.markdown("<h1>🌾 Agro Tracker Pro</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sistema Inteligente de Análise de Investimentos</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Configurações")
    auto = st.checkbox("Auto-refresh (60s)", False)
    graphs = st.checkbox("Gráficos", True)
    st.markdown("---")
    st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    st.info("📡 Brapi + NewsAPI")
    st.markdown("**Scores:**")
    st.markdown("🟢 75-100: Compra Forte")
    st.markdown("🟢 60-74: Compra")
    st.markdown("⚪ 45-59: Neutro")
    st.markdown("🔴 0-44: Venda")

with st.expander("📰 Notícias", expanded=False):
    news = get_news()
    for a in news:
        t = a.get('title', 'Sem título')
        d = a.get('publishedAt', '')[:10]
        s = a.get('source', {}).get('name', 'Fonte')
        u = a.get('url', '#')
        st.markdown(f"<div class='news'><strong>{t}</strong><br><small>📅 {d} | {s}</small><br><a href='{u}' target='_blank'>Ler →</a></div>", unsafe_allow_html=True)

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
    st.markdown(f"<div class='success'>✅ {len(results)} ATIVOS ANALISADOS!</div>", unsafe_allow_html=True)
    
    scores = [r['Score'] for r in results]
    compras = len([r for r in results if r['Score'] >= 60])
    neutros = len([r for r in results if 45 <= r['Score'] < 60])
    vendas = len([r for r in results if r['Score'] < 45])
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"<div class='stat'><span class='stat-icon'>📊</span><div class='stat-label'>Score Médio</div><div class='stat-value' style='color:#1976d2;'>{sum(scores)/len(scores):.0f}</div></div>", unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"<div class='stat'><span class='stat-icon'>🟢</span><div class='stat-label'>Compras</div><div class='stat-value' style='color:#00c853;'>{compras}</div></div>", unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"<div class='stat'><span class='stat-icon'>⚪</span><div class='stat-label'>Neutros</div><div class='stat-value' style='color:#fbc02d;'>{neutros}</div></div>", unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"<div class='stat'><span class='stat-icon'>🔴</span><div class='stat-label'>Vendas</div><div class='stat-value' style='color:#d32f2f;'>{vendas}</div></div>", unsafe_allow_html=True)
    
    for cat in ATIVOS.keys():
        cat_data = [r for r in results if r['Cat'] == cat]
        
        if not cat_data:
            continue
        
        st.markdown(f"<div class='cat'>💼 {cat} • {len(cat_data)} ativos</div>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, r in enumerate(cat_data):
            with cols[idx % 3]:
                if r['Score'] >= 75:
                    color = "#00c853"
                    badge = "buy-strong"
                elif r['Score'] >= 60:
                    color = "#76ff03"
                    badge = "buy"
                elif r['Score'] >= 45:
                    color = "#ffd54f"
                    badge = "neutral"
                else:
                    color = "#ff5252"
                    badge = "sell"
                
                ch_class = "up" if r['Var'] >= 0 else "down"
                
                st.markdown(f"<div class='card' style='border-left:8px solid {color};'><div class='name'>{r['Nome']}</div><div class='ticker'>{r['Ticker']}</div><div><span class='price'>R$ {r['Preço']:.2f}</span><span class='change {ch_class}'>{r['Var']:+.2f}%</span></div><div class='badge {badge}'>Score: {r['Score']:.0f}/100</div><div style='margin-top:10px; font-weight:700; font-size:1.1rem;'>🟢 {r['Class']}</div></div>", unsafe_allow_html=True)
                
                if graphs:
                    with st.expander("📈 Gráfico"):
                        hist = r['Data'].get('historicalDataPrice', [])
                        if hist and len(hist) > 5:
                            df = pd.DataFrame(hist)
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=list(range(len(df))), y=df['close'], fill='tozeroy', line=dict(color=color, width=3)))
                            fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, xaxis_visible=False, yaxis_visible=False)
                            
                            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Tabela Completa")
    
    df = pd.DataFrame([{
        'Cat': r['Cat'], 'Nome': r['Nome'], 'Ticker': r['Ticker'],
        'Preço': f"R$ {r['Preço']:.2f}", 'Var': f"{r['Var']:+.2f}%",
        'Score': f"{r['Score']:.0f}/100", 'Rec': r['Class']
    } for r in results])
    
    st.dataframe(df, use_container_width=True, hide_index=True, height=600)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, f"agro_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv", use_container_width=True)
else:
    st.error("❌ Nenhum ativo processado")

st.markdown("---")
st.markdown("<div style='text-align:center; padding:30px; color:#616161;'><p style='font-size:1.3rem; font-weight:700;'>🌾 Agro Tracker Pro</p><p>Brapi + NewsAPI</p><p style='font-size:0.9rem; color:#9e9e9e;'>⚠️ Sistema educacional</p></div>", unsafe_allow_html=True)

if auto:
    time.sleep(60)
    st.rerun()

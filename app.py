"""
AGRO MONITOR PRO v2.0
Sistema Profissional de Monitoramento do Agronegócio
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Imports dos módulos
from modules.database import AgroDatabase
from modules.technical_analysis import TechnicalAnalysisEngine
from modules.fundamental_analysis import FundamentalAnalysisEngine
from modules.news_analysis import NewsAnalysisEngine
from modules.monitoring_system import AgroMonitoringSystem
from modules.cache_manager import CacheManager
from modules.scheduler import SchedulerManager

# Configuração da Página
st.set_page_config(
    page_title="🌾 Agro Monitor Pro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .metric-card { background: white; padding: 20px; border-radius: 10px; 
                   box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }
    .big-title { font-size: 42px; font-weight: bold; color: #2c3e50; 
                 text-align: center; margin-bottom: 10px; }
    .subtitle { font-size: 18px; color: #7f8c8d; text-align: center; margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Inicialização do Sistema
@st.cache_resource
def initialize_system():
    """Inicializa o sistema com cache"""
    try:
        if hasattr(st, 'secrets'):
            finnhub_key = st.secrets.get("FINNHUB_API_KEY", "")
            news_key = st.secrets.get("NEWS_API_KEY", "")
            brapi_token = st.secrets.get("BRAPI_API_TOKEN", "")
        else:
            finnhub_key = ""
            news_key = ""
            brapi_token = ""
        
        system = AgroMonitoringSystem(finnhub_key, news_key, brapi_token)
        cache_manager = CacheManager()
        scheduler = SchedulerManager()
        
        return system, cache_manager, scheduler
    except Exception as e:
        st.error(f"Erro ao inicializar sistema: {e}")
        return None, None, None

system, cache_manager, scheduler = initialize_system()

# Funções Auxiliares
def get_score_color(score: float) -> str:
    """Retorna classe CSS baseada no score"""
    if score >= 70:
        return "score-high"
    elif score >= 50:
        return "score-medium"
    else:
        return "score-low"

def create_gauge_chart(score: float, title: str) -> go.Figure:
    """Cria gráfico de gauge (velocímetro)"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': '#ffcccc'},
                {'range': [40, 60], 'color': '#fff9cc'},
                {'range': [60, 100], 'color': '#ccffcc'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 75}
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

@st.cache_data(ttl=3600)
def load_analysis_data(ticker: str) -> Optional[Dict]:
    """Carrega dados de análise com cache"""
    try:
        cached_data = cache_manager.get_cached_analysis(ticker)
        if cached_data:
            return cached_data
        
        analysis = system.analyze_asset(ticker)
        if analysis:
            cache_manager.save_analysis(ticker, analysis)
        return analysis
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# SIDEBAR
with st.sidebar:
    st.markdown("# 🌾 Agro Monitor Pro")
    st.markdown("---")
    
    menu = st.radio(
        "📍 Navegação",
        ["🏠 Dashboard", "📊 Análise Individual", "🔍 Scanner", 
         "📈 Comparador", "📰 Notícias", "⚙️ Configurações"]
    )
    
    st.markdown("---")
    st.markdown("### 👤 Perfil")
    perfil = st.selectbox("Selecione", ["🛡️ Conservador", "⚖️ Moderado", "🚀 Arrojado"], index=1)
    
    st.markdown("---")
    st.markdown("### 🎯 Filtros")
    score_min = st.slider("Score Mínimo", 0, 100, 50, 5)
    
    st.markdown("---")
    if st.button("🔄 Atualizar", use_container_width=True):
        cache_manager.clear_all_cache()
        st.success("✅ Cache limpo!")
        st.rerun()
    
    cache_info = cache_manager.get_cache_info()
    st.metric("📦 Cache", cache_info['total_items'])

# PÁGINA 1: DASHBOARD
if menu == "🏠 Dashboard":
    st.markdown('<div class="big-title">🌾 Dashboard do Agronegócio</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Monitoramento em Tempo Real</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Ativos", len(system.database.get_all_tickers()))
    with col2:
        st.metric("🟢 Oportunidades", "12", delta="+3")
    with col3:
        st.metric("📈 Score Médio", "62.5", delta="+2.3")
    with col4:
        st.metric("💰 Setor Destaque", "Frigoríficos")
    
    st.markdown("---")
    st.markdown("### 🏆 Top 5 Oportunidades")
    
    with st.spinner("🔍 Analisando..."):
        top_tickers = ['BEEF3', 'JBSS3', 'BRFS3', 'SLCE3', 'AGRO3']
        data = []
        
        for ticker in top_tickers:
            analysis = load_analysis_data(ticker)
            if analysis:
                data.append({
                    'Ticker': ticker,
                    'Empresa': analysis['info']['name'],
                    'Preço': f"R$ {analysis['price_data']['current']:.2f}",
                    'Score': f"{analysis['recommendation']['final_score']:.1f}",
                    'Recomendação': analysis['recommendation']['action']
                })
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

# PÁGINA 2: ANÁLISE INDIVIDUAL
elif menu == "📊 Análise Individual":
    st.markdown('<div class="big-title">📊 Análise Detalhada</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.selectbox("Selecione o ativo:", system.database.get_all_tickers())
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analisar", use_container_width=True, type="primary")
    
    if ticker and analyze_btn:
        with st.spinner(f"🔄 Analisando {ticker}..."):
            analysis = load_analysis_data(ticker)
            
            if analysis:
                st.markdown("---")
                st.markdown(f"## {ticker} - {analysis['info']['name']}")
                st.caption(f"📍 {analysis['info']['sector']} | {analysis['info']['subsector']}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💰 Preço", f"R$ {analysis['price_data']['current']:.2f}",
                             delta=f"{analysis['price_data']['change_1d']:+.2f}%")
                
                with col2:
                    st.metric("📈 Var 1M", f"{analysis['price_data']['change_1m']:+.2f}%")
                
                with col3:
                    st.metric("⭐ Score", f"{analysis['recommendation']['final_score']:.1f}/100")
                
                with col4:
                    st.metric("🎯 Ação", analysis['recommendation']['action'].split()[1])
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fig = create_gauge_chart(analysis['technical']['score']['score'], "📊 Score Técnico")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = create_gauge_chart(analysis['fundamental']['score']['score'], "💼 Score Fundamentalista")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    sentiment_score = (analysis['news']['sentiment']['score'] + 100) / 2
                    fig = create_gauge_chart(sentiment_score, "📰 Sentimento")
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                with st.expander("📊 ANÁLISE TÉCNICA", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📈 Tendência")
                        st.markdown(f"**Status:** {analysis['technical']['trend']['trend']}")
                        for signal in analysis['technical']['trend']['signals'][:3]:
                            st.markdown(f"- {signal}")
                    
                    with col2:
                        st.markdown("#### ⚡ Momentum")
                        st.markdown(f"**RSI:** {analysis['technical']['momentum'].get('rsi', 0):.1f}")
                        for signal in analysis['technical']['momentum']['signals'][:2]:
                            st.markdown(f"- {signal}")

# CONTINUA NA PARTE 2...
# PÁGINA 3: SCANNER
elif menu == "🔍 Scanner":
    st.markdown('<div class="big-title">🔍 Scanner de Oportunidades</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scan_score_min = st.slider("Score Mínimo", 0, 100, 60, 5)
    
    with col2:
        scan_limit = st.slider("Máximo de Ativos", 5, 30, 10)
    
    with col3:
        scan_type = st.selectbox("Tipo", ["Completa", "Técnica", "Fundamentalista"])
    
    if st.button("🚀 Iniciar Scanner", use_container_width=True, type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        tickers = system.database.get_all_tickers()[:scan_limit]
        
        for i, ticker in enumerate(tickers):
            status_text.text(f"Analisando {ticker}... ({i+1}/{len(tickers)})")
            progress_bar.progress((i + 1) / len(tickers))
            
            analysis = load_analysis_data(ticker)
            
            if analysis and analysis['recommendation']['final_score'] >= scan_score_min:
                results.append(analysis)
            
            time.sleep(0.1)
        
        status_text.empty()
        progress_bar.empty()
        
        if results:
            st.success(f"✅ {len(results)} oportunidades encontradas!")
            
            results.sort(key=lambda x: x['recommendation']['final_score'], reverse=True)
            
            data = []
            for i, r in enumerate(results, 1):
                data.append({
                    'Rank': i,
                    'Ticker': r['ticker'],
                    'Empresa': r['info']['name'],
                    'Preço': f"R$ {r['price_data']['current']:.2f}",
                    'Score': r['recommendation']['final_score'],
                    'Ação': r['recommendation']['action']
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("### 📊 Gráfico de Scores")
            fig = px.bar(df, x='Ticker', y='Score', color='Score',
                        color_continuous_scale='RdYlGn', title="Scores por Ativo")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 💾 Exportar")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button("📥 CSV", csv, 
                                 f"scan_{datetime.now().strftime('%Y%m%d')}.csv",
                                 "text/csv", use_container_width=True)
            
            with col2:
                json_data = json.dumps([r for r in results], indent=2, default=str)
                st.download_button("📥 JSON", json_data,
                                 f"scan_{datetime.now().strftime('%Y%m%d')}.json",
                                 "application/json", use_container_width=True)
        else:
            st.warning("❌ Nenhuma oportunidade encontrada")

# PÁGINA 4: COMPARADOR
elif menu == "📈 Comparador":
    st.markdown('<div class="big-title">📈 Comparador de Ativos</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        tickers_comp = st.multiselect("Selecione até 5 ativos:",
                                     system.database.get_all_tickers(),
                                     default=['BEEF3', 'JBSS3', 'BRFS3'])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        comp_btn = st.button("📊 Comparar", use_container_width=True, type="primary")
    
    if tickers_comp and comp_btn:
        if len(tickers_comp) > 5:
            st.warning("⚠️ Máximo 5 ativos")
        else:
            with st.spinner("📊 Comparando..."):
                comparisons = []
                
                for ticker in tickers_comp:
                    analysis = load_analysis_data(ticker)
                    if analysis:
                        comparisons.append(analysis)
                
                if comparisons:
                    data = []
                    for comp in comparisons:
                        data.append({
                            'Ticker': comp['ticker'],
                            'Empresa': comp['info']['name'],
                            'Preço': f"R$ {comp['price_data']['current']:.2f}",
                            'Score': comp['recommendation']['final_score'],
                            'Técnico': comp['technical']['score']['score'],
                            'Fundamental': comp['fundamental']['score']['score']
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📊 Comparação de Scores")
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(name='Técnico',
                                           x=[c['ticker'] for c in comparisons],
                                           y=[c['technical']['score']['score'] for c in comparisons]))
                        
                        fig.add_trace(go.Bar(name='Fundamentalista',
                                           x=[c['ticker'] for c in comparisons],
                                           y=[c['fundamental']['score']['score'] for c in comparisons]))
                        
                        fig.update_layout(barmode='group', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("### 💰 Variação de Preços")
                        
                        fig = go.Figure()
                        
                        for comp in comparisons:
                            fig.add_trace(go.Bar(name=comp['ticker'],
                                               x=['1D', '5D', '1M'],
                                               y=[comp['price_data']['change_1d'],
                                                  comp['price_data']['change_5d'],
                                                  comp['price_data']['change_1m']]))
                        
                        fig.update_layout(barmode='group', height=400)
                        st.plotly_chart(fig, use_container_width=True)

# PÁGINA 5: NOTÍCIAS
elif menu == "📰 Notícias":
    st.markdown('<div class="big-title">📰 Central de Notícias</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        news_ticker = st.selectbox("Ativo:", ["Todos"] + system.database.get_all_tickers())
    
    with col2:
        news_limit = st.slider("Quantidade:", 5, 20, 10)
    
    if st.button("🔄 Buscar Notícias", use_container_width=True):
        with st.spinner("📰 Buscando..."):
            if news_ticker == "Todos":
                tickers_news = system.database.get_all_tickers()[:5]
            else:
                tickers_news = [news_ticker]
            
            all_news = []
            
            for ticker in tickers_news:
                ticker_info = system.database.get_ticker_info(ticker)
                if ticker_info:
                    us_ticker = ticker_info.get('us_ticker', ticker)
                    news = system.news.get_news(ticker, us_ticker)
                    
                    for item in news[:3]:
                        title = item.get('headline', '') or item.get('title', '')
                        all_news.append({
                            'Ticker': ticker,
                            'Título': title,
                            'URL': item.get('url', item.get('link', ''))
                        })
                
                time.sleep(0.5)
            
            if all_news:
                st.success(f"✅ {len(all_news)} notícias encontradas")
                
                for news in all_news[:news_limit]:
                    with st.expander(f"📰 {news['Ticker']} - {news['Título'][:60]}..."):
                        if news['URL']:
                            st.markdown(f"[🔗 Ler notícia completa]({news['URL']})")
            else:
                st.warning("❌ Nenhuma notícia encontrada")

# PÁGINA 6: CONFIGURAÇÕES
elif menu == "⚙️ Configurações":
    st.markdown('<div class="big-title">⚙️ Configurações</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔑 APIs", "🔄 Scheduler", "💾 Cache"])
    
    with tab1:
        st.markdown("### 🔑 Configuração de APIs")
        st.info("Configure suas chaves no Streamlit Cloud em 'Settings → Secrets'")
        
        st.code("""
FINNHUB_API_KEY = "sua_chave"
NEWS_API_KEY = "sua_chave"
BRAPI_API_TOKEN = "sua_chave"
        """, language="toml")
        
        st.markdown("### 📚 Obter Chaves")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Finnhub**")
            st.markdown("[Cadastrar →](https://finnhub.io)")
        
        with col2:
            st.markdown("**News API**")
            st.markdown("[Cadastrar →](https://newsapi.org)")
        
        with col3:
            st.markdown("**Brapi**")
            st.markdown("[Cadastrar →](https://brapi.dev)")
    
    with tab2:
        st.markdown("### 🔄 Jobs Agendados")
        
        if scheduler:
            status = scheduler.get_job_status()
            
            if status:
                for job in status:
                    with st.expander(f"📋 {job['name']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Tipo", job['schedule_type'])
                            st.metric("Última Exec", job['last_run'][:19] if job['last_run'] else "Nunca")
                        
                        with col2:
                            st.metric("Status", job['last_status'])
                            st.metric("Próxima Exec", job['next_run'][:19] if job['next_run'] else "N/A")
            else:
                st.info("Nenhum job configurado")
    
    with tab3:
        st.markdown("### 💾 Cache")
        
        if cache_manager:
            cache_info = cache_manager.get_cache_info()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📦 Itens", cache_info['total_items'])
            
            with col2:
                st.metric("💾 Tamanho", f"{cache_info['total_size_mb']:.2f} MB")
            
            with col3:
                last_update = cache_manager.get_last_update()
                if last_update:
                    st.metric("🕐 Última Atualização", last_update.strftime('%H:%M:%S'))
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Limpar Expirado", use_container_width=True):
                    removed = cache_manager.clear_expired()
                    st.success(f"✅ {removed} itens removidos")
            
            with col2:
                if st.button("🗑️ Limpar Tudo", use_container_width=True):
                    cache_manager.clear_all_cache()
                    st.success("✅ Cache limpo!")

# FOOTER
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p>🌾 <strong>Agro Monitor Pro v2.0</strong></p>
    <p>Desenvolvido com 💚 para o Agronegócio Brasileiro</p>
    <p style='font-size: 12px;'>
        ⚠️ Ferramenta de análise. Não constitui recomendação de investimento.
    </p>
</div>
""", unsafe_allow_html=True)

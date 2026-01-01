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

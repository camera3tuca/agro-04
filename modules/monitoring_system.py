"""
Sistema Integrado de Monitoramento
Integra análise técnica, fundamentalista e notícias
"""

from datetime import datetime
import time
from .database import AgroDatabase
from .technical_analysis import TechnicalAnalysisEngine
from .fundamental_analysis import FundamentalAnalysisEngine
from .news_analysis import NewsAnalysisEngine

class AgroMonitoringSystem:
    """Sistema completo de monitoramento do agronegócio"""
    
    def __init__(self, finnhub_key, news_api_key, brapi_token):
        print("🌾 Inicializando Sistema de Monitoramento do Agronegócio...")
        
        self.database = AgroDatabase()
        self.technical = TechnicalAnalysisEngine()
        self.fundamental = FundamentalAnalysisEngine()
        self.news = NewsAnalysisEngine(finnhub_key, news_api_key)
        
        print(f"✅ Sistema carregado | {len(self.database.get_all_tickers())} ativos mapeados")
    
    def analyze_asset(self, ticker):
        """Análise completa de um ativo"""
        
        # Informações do ticker
        ticker_info = self.database.get_ticker_info(ticker)
        if not ticker_info:
            return None
        
        # Determina ticker US para BDRs
        us_ticker = ticker_info.get('us_ticker', ticker.replace('34', '').replace('35', ''))
        
        print(f"\n{'='*80}")
        print(f"📊 Analisando: {ticker} - {ticker_info['name']}")
        print(f"{'='*80}")
        
        # 1. ANÁLISE TÉCNICA
        print("🔍 Análise Técnica...")
        df = self.technical.get_price_data(ticker, period='6mo')
        
        if df is None or len(df) < 50:
            print("⚠️ Dados insuficientes para análise técnica")
            return None
        
        indicators = self.technical.calculate_indicators(df)
        trend = self.technical.analyze_trend(df, indicators)
        momentum = self.technical.analyze_momentum(indicators)
        macd = self.technical.analyze_macd(indicators)
        support_resistance = self.technical.calculate_support_resistance(df)
        technical_score = self.technical.generate_technical_score(trend, momentum, macd)
        
        # 2. ANÁLISE FUNDAMENTALISTA
        print("📈 Análise Fundamentalista...")
        fundamentals = self.fundamental.get_fundamental_data(ticker)
        
        if fundamentals:
            valuation = self.fundamental.analyze_valuation(fundamentals)
            profitability = self.fundamental.analyze_profitability(fundamentals)
            growth = self.fundamental.analyze_growth(fundamentals)
            health = self.fundamental.analyze_financial_health(fundamentals)
            fundamental_score = self.fundamental.generate_fundamental_score(
                valuation, profitability, growth, health
            )
        else:
            print("⚠️ Dados fundamentalistas limitados")
            valuation = profitability = growth = health = None
            fundamental_score = {'score': 50, 'classification': '⚪ N/A'}
        
        # 3. ANÁLISE DE NOTÍCIAS
        print("📰 Análise de Notícias...")
        news_list = self.news.get_news(ticker, us_ticker)
        sentiment = self.news.analyze_sentiment(news_list)
        catalysts = self.news.detect_catalysts(news_list)
        
        # 4. SCORE FINAL INTEGRADO
        # Pesos: Técnica (40%), Fundamentalista (40%), Sentimento (20%)
        final_score = (
            technical_score['score'] * 0.40 +
            fundamental_score['score'] * 0.40 +
            ((sentiment['score'] + 100) / 2) * 0.20
        )
        
        # Recomendação final
        if final_score >= 75:
            recommendation = "🟢 COMPRA FORTE"
            priority = "ALTA"
        elif final_score >= 65:
            recommendation = "🟢 COMPRA"
            priority = "MÉDIA-ALTA"
        elif final_score >= 55:
            recommendation = "🟡 ACUMULAÇÃO"
            priority = "MÉDIA"
        elif final_score >= 45:
            recommendation = "⚪ NEUTRO"
            priority = "BAIXA"
        elif final_score >= 35:
            recommendation = "🟡 REDUÇÃO"
            priority = "MÉDIA"
        else:
            recommendation = "🔴 VENDA"
            priority = "ALTA"
        
        # Retorna análise completa
        return {
            'ticker': ticker,
            'info': ticker_info,
            'price_data': {
                'current': df['Close'].iloc[-1],
                'change_1d': ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100 if len(df) > 1 else 0,
                'change_5d': ((df['Close'].iloc[-1] / df['Close'].iloc[-6]) - 1) * 100 if len(df) > 5 else 0,
                'change_1m': ((df['Close'].iloc[-1] / df['Close'].iloc[-21]) - 1) * 100 if len(df) > 20 else 0,
            },
            'technical': {
                'score': technical_score,
                'trend': trend,
                'momentum': momentum,
                'macd': macd,
                'support_resistance': support_resistance
            },
            'fundamental': {
                'score': fundamental_score,
                'valuation': valuation,
                'profitability': profitability,
                'growth': growth,
                'health': health,
                'raw_data': fundamentals
            },
            'news': {
                'sentiment': sentiment,
                'catalysts': catalysts,
                'recent_news': news_list[:3]
            },
            'recommendation': {
                'final_score': round(final_score, 1),
                'action': recommendation,
                'priority': priority
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def scan_all_assets(self, min_score=50):
        """Varre todos os ativos do agronegócio"""
        
        print("\n" + "="*80)
        print("🌾 VARREDURA COMPLETA - SETOR AGRONEGÓCIO")
        print("="*80)
        
        all_tickers = self.database.get_all_tickers()
        results = []
        
        for i, ticker in enumerate(all_tickers, 1):
            print(f"\n[{i}/{len(all_tickers)}] {ticker}...", end=' ')
            
            try:
                analysis = self.analyze_asset(ticker)
                
                if analysis and analysis['recommendation']['final_score'] >= min_score:
                    results.append(analysis)
                    print(f"✅ Score: {analysis['recommendation']['final_score']}")
                else:
                    print("⭐ Abaixo do mínimo")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
            
            time.sleep(1)  # Rate limiting
        
        # Ordena por score
        results.sort(key=lambda x: x['recommendation']['final_score'], reverse=True)
        
        print(f"\n✅ Varredura concluída: {len(results)} oportunidades identificadas")
        
        return results

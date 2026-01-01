"""
Sistema de Análise de Notícias
Análise de sentimento e detecção de catalisadores
"""

import requests
import yfinance as yf
from datetime import datetime, timedelta

class NewsAnalysisEngine:
    """Análise de notícias e catalisadores específicos do agronegócio"""
    
    def __init__(self, finnhub_key, news_api_key):
        self.finnhub_key = finnhub_key
        self.news_api_key = news_api_key
        
        # Palavras-chave específicas do agronegócio
        self.agro_keywords = {
            'positive': [
                'record harvest', 'bumper crop', 'strong demand', 'export deal',
                'price increase', 'expansion', 'acquisition', 'innovation',
                'sustainable', 'organic growth', 'market share gain',
                'safra recorde', 'demanda forte', 'exportação', 'expansão',
                'inovação', 'sustentável', 'crescimento orgânico'
            ],
            'negative': [
                'drought', 'flood', 'disease', 'pest', 'tariff', 'ban',
                'price drop', 'oversupply', 'competition', 'regulation',
                'seca', 'inundação', 'praga', 'doença', 'tarifa',
                'queda de preço', 'excesso de oferta', 'regulação'
            ],
            'neutral': [
                'weather', 'forecast', 'report', 'analysis', 'outlook',
                'clima', 'previsão', 'relatório', 'análise'
            ]
        }
    
    def get_news(self, ticker, us_ticker=None):
        """Busca notícias de múltiplas fontes"""
        all_news = []
        
        # Finnhub
        finnhub_news = self._get_finnhub_news(us_ticker if us_ticker else ticker)
        all_news.extend(finnhub_news)
        
        # Yahoo Finance
        yahoo_news = self._get_yahoo_news(ticker)
        all_news.extend(yahoo_news)
        
        return all_news[:10]  # Top 10
    
    def _get_finnhub_news(self, ticker):
        """Busca notícias do Finnhub"""
        try:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={from_date}&to={to_date}&token={self.finnhub_key}'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()[:5]
        except:
            pass
        return []
    
    def _get_yahoo_news(self, ticker):
        """Busca notícias do Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news if hasattr(stock, 'news') else []
            return news[:5]
        except:
            return []
    
    def analyze_sentiment(self, news_list):
        """Analisa sentimento das notícias"""
        if not news_list:
            return {'sentiment': 'NEUTRO', 'score': 0, 'positive': 0, 'negative': 0, 'neutral': 0}
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for news in news_list:
            title = (news.get('headline', '') or news.get('title', '')).lower()
            summary = (news.get('summary', '') or news.get('description', '') or '').lower()
            full_text = f"{title} {summary}"
            
            # Conta palavras-chave
            pos_matches = sum(1 for kw in self.agro_keywords['positive'] if kw in full_text)
            neg_matches = sum(1 for kw in self.agro_keywords['negative'] if kw in full_text)
            
            if pos_matches > neg_matches:
                positive_count += 1
            elif neg_matches > pos_matches:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(news_list)
        
        # Score de sentimento (-100 a +100)
        sentiment_score = ((positive_count - negative_count) / total) * 100
        
        # Classificação
        if sentiment_score > 30:
            sentiment = "MUITO POSITIVO"
        elif sentiment_score > 10:
            sentiment = "POSITIVO"
        elif sentiment_score > -10:
            sentiment = "NEUTRO"
        elif sentiment_score > -30:
            sentiment = "NEGATIVO"
        else:
            sentiment = "MUITO NEGATIVO"
        
        return {
            'sentiment': sentiment,
            'score': round(sentiment_score, 1),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'total': total
        }
    
    def detect_catalysts(self, news_list):
        """Detecta catalisadores importantes"""
        catalysts = []
        
        catalyst_patterns = {
            'earnings': ['earnings', 'quarterly results', 'lucro', 'resultado'],
            'dividend': ['dividend', 'dividendo', 'provento'],
            'ma': ['merger', 'acquisition', 'fusão', 'aquisição'],
            'expansion': ['expansion', 'plant', 'facility', 'expansão', 'planta', 'unidade'],
            'export': ['export', 'china', 'deal', 'exportação', 'acordo'],
            'commodity': ['wheat', 'corn', 'soy', 'cattle', 'sugar', 'trigo', 'milho', 'soja', 'boi', 'açúcar']
        }
        
        for news in news_list:
            title = (news.get('headline', '') or news.get('title', '')).lower()
            
            for catalyst_type, keywords in catalyst_patterns.items():
                if any(kw in title for kw in keywords):
                    catalysts.append({
                        'type': catalyst_type.upper(),
                        'title': news.get('headline', '') or news.get('title', ''),
                        'date': news.get('datetime', '') or news.get('providerPublishTime', ''),
                        'url': news.get('url', '') or news.get('link', '')
                    })
                    break
        
        return catalysts

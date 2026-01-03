"""
Motor de Análise Fundamentalista
Análise de valuation, rentabilidade, crescimento e saúde financeira
"""

import yfinance as yf

class FundamentalAnalysisEngine:
    """Motor de análise fundamentalista"""
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 80,
            'good': 60,
            'fair': 40,
            'poor': 20
        }
    
    def get_fundamental_data(self, ticker):
        """Obtém dados fundamentalistas"""
        try:
            # Tenta primeiro com o ticker como está
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Verifica se tem dados úteis
            if not info or len(info) < 5:
                # Tenta com .SA se não tiver
                if not ticker.endswith('.SA'):
                    ticker_sa = f"{ticker}.SA"
                    stock = yf.Ticker(ticker_sa)
                    info = stock.info
                # Tenta sem .SA
                elif ticker.endswith('.SA'):
                    ticker_no_sa = ticker.replace('.SA', '')
                    stock = yf.Ticker(ticker_no_sa)
                    info = stock.info
            
            if not info or len(info) < 5:
                print(f"⚠️ Sem dados fundamentalistas para {ticker}")
                return None
            
            # Indicadores fundamentalistas relevantes
            fundamentals = {
                # Valuation
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'price_to_book': info.get('priceToBook', None),
                'price_to_sales': info.get('priceToSalesTrailing12Months', None),
                'ev_to_ebitda': info.get('enterpriseToEbitda', None),
                
                # Rentabilidade
                'profit_margin': info.get('profitMargins', None),
                'operating_margin': info.get('operatingMargins', None),
                'roe': info.get('returnOnEquity', None),
                'roa': info.get('returnOnAssets', None),
                
                # Crescimento
                'revenue_growth': info.get('revenueGrowth', None),
                'earnings_growth': info.get('earningsGrowth', None),
                
                # Saúde Financeira
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'quick_ratio': info.get('quickRatio', None),
                
                # Dividendos
                'dividend_yield': info.get('dividendYield', None),
                'payout_ratio': info.get('payoutRatio', None),
                
                # Outros
                'market_cap': info.get('marketCap', None),
                'beta': info.get('beta', None),
                'target_price': info.get('targetMeanPrice', None),
                'recommendation': info.get('recommendationKey', None),
            }
            
            print(f"✅ Fundamentais obtidos para {ticker}")
            return fundamentals
            
        except Exception as e:
            print(f"❌ Erro ao obter fundamentals de {ticker}: {e}")
            return None
    
    def analyze_valuation(self, fundamentals):
        """Analisa se o ativo está barato ou caro"""
        if not fundamentals:
            return {'status': 'N/A', 'score': 0, 'signals': []}
        
        score = 0
        signals = []
        
        # P/L
        pe = fundamentals.get('pe_ratio')
        if pe:
            if pe < 10:
                score += 3
                signals.append(f"P/L baixo ({pe:.1f})")
            elif pe < 15:
                score += 2
                signals.append(f"P/L atrativo ({pe:.1f})")
            elif pe < 20:
                score += 1
                signals.append(f"P/L moderado ({pe:.1f})")
            elif pe > 30:
                score -= 2
                signals.append(f"P/L elevado ({pe:.1f})")
        
        # P/VP
        pb = fundamentals.get('price_to_book')
        if pb:
            if pb < 1:
                score += 2
                signals.append(f"P/VP < 1 ({pb:.2f})")
            elif pb < 2:
                score += 1
                signals.append(f"P/VP atrativo ({pb:.2f})")
        
        # EV/EBITDA
        ev_ebitda = fundamentals.get('ev_to_ebitda')
        if ev_ebitda:
            if ev_ebitda < 8:
                score += 2
                signals.append(f"EV/EBITDA atrativo ({ev_ebitda:.1f})")
            elif ev_ebitda > 15:
                score -= 1
                signals.append(f"EV/EBITDA elevado ({ev_ebitda:.1f})")
        
        # Classificação
        if score >= 5:
            status = "MUITO BARATO"
        elif score >= 3:
            status = "BARATO"
        elif score >= 1:
            status = "JUSTO"
        elif score >= -1:
            status = "NEUTRO"
        else:
            status = "CARO"
        
        return {'status': status, 'score': score, 'signals': signals}
    
    def analyze_profitability(self, fundamentals):
        """Analisa rentabilidade"""
        if not fundamentals:
            return {'quality': 'N/A', 'score': 0, 'signals': []}
        
        score = 0
        signals = []
        
        # ROE
        roe = fundamentals.get('roe')
        if roe:
            roe_pct = roe * 100
            if roe_pct > 20:
                score += 3
                signals.append(f"ROE excelente ({roe_pct:.1f}%)")
            elif roe_pct > 15:
                score += 2
                signals.append(f"ROE bom ({roe_pct:.1f}%)")
            elif roe_pct > 10:
                score += 1
                signals.append(f"ROE adequado ({roe_pct:.1f}%)")
            else:
                signals.append(f"ROE fraco ({roe_pct:.1f}%)")
        
        # Margem Operacional
        op_margin = fundamentals.get('operating_margin')
        if op_margin:
            op_pct = op_margin * 100
            if op_pct > 20:
                score += 2
                signals.append(f"Margem Op. alta ({op_pct:.1f}%)")
            elif op_pct > 10:
                score += 1
                signals.append(f"Margem Op. boa ({op_pct:.1f}%)")
        
        # Margem Líquida
        profit_margin = fundamentals.get('profit_margin')
        if profit_margin:
            profit_pct = profit_margin * 100
            if profit_pct > 15:
                score += 2
                signals.append(f"Margem Líq. alta ({profit_pct:.1f}%)")
            elif profit_pct > 8:
                score += 1
                signals.append(f"Margem Líq. boa ({profit_pct:.1f}%)")
        
        # Classificação
        if score >= 5:
            quality = "EXCELENTE"
        elif score >= 3:
            quality = "BOA"
        elif score >= 1:
            quality = "REGULAR"
        else:
            quality = "FRACA"
        
        return {'quality': quality, 'score': score, 'signals': signals}
    
    def analyze_growth(self, fundamentals):
        """Analisa crescimento"""
        if not fundamentals:
            return {'status': 'N/A', 'score': 0, 'signals': []}
        
        score = 0
        signals = []
        
        # Crescimento de Receita
        revenue_growth = fundamentals.get('revenue_growth')
        if revenue_growth:
            growth_pct = revenue_growth * 100
            if growth_pct > 20:
                score += 3
                signals.append(f"Crescimento receita forte ({growth_pct:.1f}%)")
            elif growth_pct > 10:
                score += 2
                signals.append(f"Crescimento receita bom ({growth_pct:.1f}%)")
            elif growth_pct > 5:
                score += 1
                signals.append(f"Crescimento receita moderado ({growth_pct:.1f}%)")
            elif growth_pct < 0:
                score -= 2
                signals.append(f"Receita em queda ({growth_pct:.1f}%)")
        
        # Crescimento de Lucros
        earnings_growth = fundamentals.get('earnings_growth')
        if earnings_growth:
            earn_pct = earnings_growth * 100
            if earn_pct > 20:
                score += 2
                signals.append(f"Crescimento lucro forte ({earn_pct:.1f}%)")
            elif earn_pct > 10:
                score += 1
                signals.append(f"Crescimento lucro bom ({earn_pct:.1f}%)")
        
        # Classificação
        if score >= 4:
            status = "ALTO CRESCIMENTO"
        elif score >= 2:
            status = "CRESCIMENTO"
        elif score >= 0:
            status = "ESTÁVEL"
        else:
            status = "DECLÍNIO"
        
        return {'status': status, 'score': score, 'signals': signals}
    
    def analyze_financial_health(self, fundamentals):
        """Analisa saúde financeira"""
        if not fundamentals:
            return {'health': 'N/A', 'score': 0, 'signals': []}
        
        score = 0
        signals = []
        
        # Dívida/Patrimônio
        de_ratio = fundamentals.get('debt_to_equity')
        if de_ratio:
            if de_ratio < 50:
                score += 3
                signals.append(f"Dív/PL baixo ({de_ratio:.1f})")
            elif de_ratio < 100:
                score += 2
                signals.append(f"Dív/PL moderado ({de_ratio:.1f})")
            elif de_ratio < 200:
                score += 1
                signals.append(f"Dív/PL elevado ({de_ratio:.1f})")
            else:
                score -= 1
                signals.append(f"Dív/PL muito alto ({de_ratio:.1f})")
        
        # Liquidez Corrente
        current_ratio = fundamentals.get('current_ratio')
        if current_ratio:
            if current_ratio > 2:
                score += 2
                signals.append(f"Liquidez boa ({current_ratio:.2f})")
            elif current_ratio > 1.5:
                score += 1
                signals.append(f"Liquidez adequada ({current_ratio:.2f})")
            elif current_ratio < 1:
                score -= 1
                signals.append(f"Liquidez baixa ({current_ratio:.2f})")
        
        # Classificação
        if score >= 4:
            health = "EXCELENTE"
        elif score >= 2:
            health = "BOA"
        elif score >= 0:
            health = "REGULAR"
        else:
            health = "FRACA"
        
        return {'health': health, 'score': score, 'signals': signals}
    
    def generate_fundamental_score(self, valuation, profitability, growth, health):
        """Gera score fundamentalista consolidado (0-100)"""
        
        # Pesos para cada componente
        weights = {
            'valuation': 0.25,
            'profitability': 0.30,
            'growth': 0.25,
            'health': 0.20
        }
        
        # Scores normalizados (assumindo -3 a +3 para cada)
        val_score = (valuation.get('score', 0) + 3) / 6 * 100
        prof_score = (profitability.get('score', 0) + 3) / 6 * 100
        growth_score = (growth.get('score', 0) + 3) / 6 * 100
        health_score = (health.get('score', 0) + 3) / 6 * 100
        
        # Score ponderado
        total_score = (
            val_score * weights['valuation'] +
            prof_score * weights['profitability'] +
            growth_score * weights['growth'] +
            health_score * weights['health']
        )
        
        # Classificação
        if total_score >= 75:
            classification = "🌟 EXCELENTE"
        elif total_score >= 60:
            classification = "🟢 BOM"
        elif total_score >= 40:
            classification = "🟡 REGULAR"
        else:
            classification = "🔴 FRACO"
        
        return {
            'score': round(total_score, 1),
            'classification': classification,
            'components': {
                'valuation': round(val_score, 1),
                'profitability': round(prof_score, 1),
                'growth': round(growth_score, 1),
                'health': round(health_score, 1)
            }
        }

"""
Motor de Análise Técnica
Indicadores técnicos e análise de tendência
"""

import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

class TechnicalAnalysisEngine:
    """Motor avançado de análise técnica"""
    
    def __init__(self):
        self.periods = {
            'short': 20,
            'medium': 50,
            'long': 200
        }
    
    def get_price_data(self, ticker, period='6mo'):
        """Obtém dados históricos de preço"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return None
            
            return df
        except Exception as e:
            print(f"Erro ao obter dados de {ticker}: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Calcula todos os indicadores técnicos"""
        if df is None or len(df) < 50:
            return None
        
        try:
            indicators = {}
            
            # Médias Móveis
            indicators['SMA_20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
            indicators['SMA_50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
            indicators['SMA_200'] = SMAIndicator(df['Close'], window=200).sma_indicator()
            indicators['EMA_12'] = EMAIndicator(df['Close'], window=12).ema_indicator()
            indicators['EMA_26'] = EMAIndicator(df['Close'], window=26).ema_indicator()
            
            # MACD
            macd = MACD(df['Close'])
            indicators['MACD'] = macd.macd()
            indicators['MACD_signal'] = macd.macd_signal()
            indicators['MACD_hist'] = macd.macd_diff()
            
            # RSI
            indicators['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
            
            # Bandas de Bollinger
            bollinger = BollingerBands(df['Close'], window=20, window_dev=2)
            indicators['BB_upper'] = bollinger.bollinger_hband()
            indicators['BB_middle'] = bollinger.bollinger_mavg()
            indicators['BB_lower'] = bollinger.bollinger_lband()
            
            # Estocástico
            stoch = StochasticOscillator(df['High'], df['Low'], df['Close'])
            indicators['Stoch_K'] = stoch.stoch()
            indicators['Stoch_D'] = stoch.stoch_signal()
            
            # ATR
            indicators['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
            
            # ADX
            indicators['ADX'] = ADXIndicator(df['High'], df['Low'], df['Close']).adx()
            
            # Volume
            indicators['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            
            return indicators
            
        except Exception as e:
            print(f"Erro ao calcular indicadores: {e}")
            return None
    
    def analyze_trend(self, df, indicators):
        """Analisa tendência do ativo"""
        if indicators is None:
            return {'trend': 'NEUTRO', 'strength': 0, 'signals': []}
        
        try:
            current_price = df['Close'].iloc[-1]
            sma_20 = indicators['SMA_20'].iloc[-1]
            sma_50 = indicators['SMA_50'].iloc[-1]
            sma_200 = indicators['SMA_200'].iloc[-1]
            
            signals = []
            score = 0
            
            # Análise de posição das médias
            if current_price > sma_20:
                score += 1
                signals.append("Preço > SMA20")
            if current_price > sma_50:
                score += 2
                signals.append("Preço > SMA50")
            if current_price > sma_200:
                score += 3
                signals.append("Preço > SMA200")
            
            # Golden Cross / Death Cross
            if sma_50 > sma_200:
                score += 2
                signals.append("Golden Cross (SMA50 > SMA200)")
            elif sma_50 < sma_200:
                score -= 2
                signals.append("Death Cross (SMA50 < SMA200)")
            
            # Determina tendência
            if score >= 5:
                trend = 'ALTA FORTE'
            elif score >= 3:
                trend = 'ALTA'
            elif score >= 1:
                trend = 'ALTA FRACA'
            elif score >= -1:
                trend = 'NEUTRO'
            elif score >= -3:
                trend = 'BAIXA FRACA'
            elif score >= -5:
                trend = 'BAIXA'
            else:
                trend = 'BAIXA FORTE'
            
            return {
                'trend': trend,
                'strength': abs(score),
                'signals': signals,
                'score': score
            }
            
        except Exception as e:
            return {'trend': 'NEUTRO', 'strength': 0, 'signals': [], 'score': 0}
    
    def analyze_momentum(self, indicators):
        """Analisa momentum (RSI, Estocástico)"""
        if indicators is None:
            return {'status': 'NEUTRO', 'signals': [], 'score': 0}
        
        try:
            rsi = indicators['RSI'].iloc[-1]
            stoch_k = indicators['Stoch_K'].iloc[-1]
            
            signals = []
            score = 0
            
            # Análise RSI
            if rsi < 30:
                signals.append(f"RSI Sobrevendido ({rsi:.1f})")
                score += 3
                status_rsi = "SOBREVENDIDO"
            elif rsi > 70:
                signals.append(f"RSI Sobrecomprado ({rsi:.1f})")
                score -= 3
                status_rsi = "SOBRECOMPRADO"
            elif 40 <= rsi <= 60:
                signals.append(f"RSI Neutro ({rsi:.1f})")
                status_rsi = "NEUTRO"
            elif rsi < 40:
                signals.append(f"RSI Fraco ({rsi:.1f})")
                score += 1
                status_rsi = "FRACO"
            else:
                signals.append(f"RSI Forte ({rsi:.1f})")
                score -= 1
                status_rsi = "FORTE"
            
            # Análise Estocástico
            if stoch_k < 20:
                signals.append(f"Estocástico Sobrevendido ({stoch_k:.1f})")
                score += 2
            elif stoch_k > 80:
                signals.append(f"Estocástico Sobrecomprado ({stoch_k:.1f})")
                score -= 2
            
            # Status geral
            if score >= 3:
                status = "COMPRA"
            elif score <= -3:
                status = "VENDA"
            else:
                status = "NEUTRO"
            
            return {
                'status': status,
                'signals': signals,
                'score': score,
                'rsi': rsi,
                'rsi_status': status_rsi
            }
            
        except Exception as e:
            return {'status': 'NEUTRO', 'signals': [], 'score': 0}
    
    def analyze_macd(self, indicators):
        """Analisa MACD"""
        if indicators is None:
            return {'signal': 'NEUTRO', 'strength': 0}
        
        try:
            macd = indicators['MACD'].iloc[-1]
            macd_signal = indicators['MACD_signal'].iloc[-1]
            macd_hist = indicators['MACD_hist'].iloc[-1]
            macd_hist_prev = indicators['MACD_hist'].iloc[-2]
            
            # Cruzamento
            if macd > macd_signal and macd_hist_prev < 0 and macd_hist > 0:
                return {'signal': 'COMPRA FORTE', 'strength': 3}
            elif macd < macd_signal and macd_hist_prev > 0 and macd_hist < 0:
                return {'signal': 'VENDA FORTE', 'strength': -3}
            elif macd > macd_signal:
                return {'signal': 'COMPRA', 'strength': 1}
            elif macd < macd_signal:
                return {'signal': 'VENDA', 'strength': -1}
            else:
                return {'signal': 'NEUTRO', 'strength': 0}
                
        except Exception as e:
            return {'signal': 'NEUTRO', 'strength': 0}
    
    def calculate_support_resistance(self, df, window=20):
        """Calcula suportes e resistências"""
        try:
            highs = df['High'].rolling(window=window).max()
            lows = df['Low'].rolling(window=window).min()
            
            resistance = highs.iloc[-1]
            support = lows.iloc[-1]
            current_price = df['Close'].iloc[-1]
            
            # Distância percentual
            dist_resistance = ((resistance - current_price) / current_price) * 100
            dist_support = ((current_price - support) / current_price) * 100
            
            return {
                'resistance': resistance,
                'support': support,
                'current': current_price,
                'dist_resistance_pct': dist_resistance,
                'dist_support_pct': dist_support
            }
        except:
            return None
    
    def generate_technical_score(self, trend_analysis, momentum_analysis, macd_analysis):
        """Gera score técnico consolidado (0-100)"""
        
        # Score de tendência (-6 a +6)
        trend_score = trend_analysis.get('score', 0)
        
        # Score de momentum (-3 a +3)
        momentum_score = momentum_analysis.get('score', 0)
        
        # Score MACD (-3 a +3)
        macd_score = macd_analysis.get('strength', 0)
        
        # Score total (-12 a +12)
        total_score = trend_score + momentum_score + macd_score
        
        # Normaliza para 0-100
        normalized_score = ((total_score + 12) / 24) * 100
        
        # Classificação
        if normalized_score >= 75:
            classification = "🟢 COMPRA FORTE"
        elif normalized_score >= 60:
            classification = "🟢 COMPRA"
        elif normalized_score >= 55:
            classification = "🟡 COMPRA FRACA"
        elif normalized_score >= 45:
            classification = "⚪ NEUTRO"
        elif normalized_score >= 40:
            classification = "🟡 VENDA FRACA"
        elif normalized_score >= 25:
            classification = "🔴 VENDA"
        else:
            classification = "🔴 VENDA FORTE"
        
        return {
            'score': round(normalized_score, 1),
            'classification': classification,
            'trend_contribution': trend_score,
            'momentum_contribution': momentum_score,
            'macd_contribution': macd_score
        }

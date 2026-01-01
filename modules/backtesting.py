"""
Módulo de Backtesting
Testa estratégias com dados históricos
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import yfinance as yf

class BacktestEngine:
    """Motor de backtesting"""
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Inicializa o motor de backtesting
        
        Args:
            initial_capital: Capital inicial em R$
        """
        self.initial_capital = initial_capital
        self.results = {}
    
    def get_historical_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Obtém dados históricos"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            return df
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores técnicos"""
        # Médias Móveis
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        return df
    
    def sma_cross_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Estratégia de cruzamento de médias móveis"""
        df = df.copy()
        
        # Sinais
        df['Signal'] = 0
        df.loc[df['SMA_20'] > df['SMA_50'], 'Signal'] = 1
        df.loc[df['SMA_20'] < df['SMA_50'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def rsi_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Estratégia baseada em RSI"""
        df = df.copy()
        
        df['Signal'] = 0
        df.loc[df['RSI'] < 30, 'Signal'] = 1
        df.loc[df['RSI'] > 70, 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def macd_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Estratégia baseada em MACD"""
        df = df.copy()
        
        df['Signal'] = 0
        df.loc[df['MACD'] > df['MACD_Signal'], 'Signal'] = 1
        df.loc[df['MACD'] < df['MACD_Signal'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def bollinger_breakout_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Estratégia de rompimento das Bandas de Bollinger"""
        df = df.copy()
        
        df['Signal'] = 0
        df.loc[df['Close'] < df['BB_Lower'], 'Signal'] = 1
        df.loc[df['Close'] > df['BB_Upper'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def simulate_trades(self, df: pd.DataFrame) -> Dict:
        """Simula trades e calcula performance"""
        capital = self.initial_capital
        position = 0
        shares = 0
        trades = []
        equity_curve = []
        
        for idx, row in df.iterrows():
            if position == 1:
                current_value = capital + (shares * row['Close'])
            else:
                current_value = capital
            
            equity_curve.append({
                'Date': idx,
                'Equity': current_value,
                'Price': row['Close']
            })
            
            if row['Position'] == 2:
                if position == 0:
                    shares = capital / row['Close']
                    capital = 0
                    position = 1
                    
                    trades.append({
                        'Date': idx,
                        'Type': 'BUY',
                        'Price': row['Close'],
                        'Shares': shares
                    })
            
            elif row['Position'] == -2:
                if position == 1:
                    capital = shares * row['Close']
                    
                    trades.append({
                        'Date': idx,
                        'Type': 'SELL',
                        'Price': row['Close'],
                        'Shares': shares
                    })
                    
                    position = 0
                    shares = 0
        
        if position == 1:
            final_value = shares * df['Close'].iloc[-1]
        else:
            final_value = capital
        
        equity_df = pd.DataFrame(equity_curve)
        returns = equity_df['Equity'].pct_change().dropna()
        
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        sell_trades = [t for t in trades if t['Type'] == 'SELL']
        win_rate = 0 if not sell_trades else len([t for t in sell_trades]) / len(sell_trades) * 100
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'num_trades': len(trades),
            'win_rate_pct': win_rate,
            'trades': trades,
            'equity_curve': equity_df
        }
    
    def run_backtest(self, 
                     ticker: str, 
                     strategy: str,
                     start_date: str,
                     end_date: str) -> Dict:
        """
        Executa backtest completo
        
        Args:
            ticker: Código do ativo
            strategy: Nome da estratégia ('sma_cross', 'rsi', 'macd', 'bollinger')
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
        """
        df = self.get_historical_data(ticker, start_date, end_date)
        
        if df is None or len(df) < 50:
            return {'error': 'Dados insuficientes'}
        
        df = self.calculate_indicators(df)
        
        if strategy == 'sma_cross':
            df = self.sma_cross_strategy(df)
        elif strategy == 'rsi':
            df = self.rsi_strategy(df)
        elif strategy == 'macd':
            df = self.macd_strategy(df)
        elif strategy == 'bollinger':
            df = self.bollinger_breakout_strategy(df)
        else:
            return {'error': 'Estratégia desconhecida'}
        
        results = self.simulate_trades(df)
        
        results['ticker'] = ticker
        results['strategy'] = strategy
        results['start_date'] = start_date
        results['end_date'] = end_date
        results['data'] = df
        
        buy_hold_return = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        results['buy_hold_return_pct'] = buy_hold_return
        results['outperformance_pct'] = results['total_return_pct'] - buy_hold_return
        
        return results

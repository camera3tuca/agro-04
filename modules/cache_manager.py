"""
Sistema de Cache Inteligente
Otimiza performance e reduz chamadas de API
"""

import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
import hashlib

class CacheManager:
    """Gerenciador de cache para análises e dados"""
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Inicializa o gerenciador de cache
        
        Args:
            cache_dir: Diretório para armazenar cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configurações de TTL (Time To Live)
        self.ttl_config = {
            'analysis': timedelta(hours=1),
            'price_data': timedelta(minutes=15),
            'news': timedelta(minutes=30),
            'fundamentals': timedelta(hours=24),
        }
        
        # Arquivo de índice
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Carrega índice de cache"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_index(self):
        """Salva índice de cache"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2, default=str)
        except Exception as e:
            print(f"Erro ao salvar índice: {e}")
    
    def _generate_cache_key(self, key: str, cache_type: str) -> str:
        """Gera chave única para cache"""
        combined = f"{cache_type}:{key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Retorna caminho do arquivo de cache"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def _is_cache_valid(self, cache_key: str, cache_type: str) -> bool:
        """Verifica se cache ainda é válido"""
        if cache_key not in self.index:
            return False
        
        cache_info = self.index[cache_key]
        cached_time = datetime.fromisoformat(cache_info['timestamp'])
        ttl = self.ttl_config.get(cache_type, timedelta(hours=1))
        
        return datetime.now() - cached_time < ttl
    
    def get(self, key: str, cache_type: str = 'analysis') -> Optional[Any]:
        """
        Recupera dados do cache
        
        Args:
            key: Chave de identificação (ex: ticker)
            cache_type: Tipo de cache (analysis, price_data, news, fundamentals)
        
        Returns:
            Dados em cache ou None se não existir/expirado
        """
        cache_key = self._generate_cache_key(key, cache_type)
        
        # Verifica validade
        if not self._is_cache_valid(cache_key, cache_type):
            return None
        
        # Carrega dados
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
            return None
    
    def set(self, key: str, data: Any, cache_type: str = 'analysis'):
        """
        Salva dados no cache
        
        Args:
            key: Chave de identificação
            data: Dados a serem salvos
            cache_type: Tipo de cache
        """
        cache_key = self._generate_cache_key(key, cache_type)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Salva dados
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            # Atualiza índice
            self.index[cache_key] = {
                'original_key': key,
                'cache_type': cache_type,
                'timestamp': datetime.now().isoformat(),
                'size_bytes': cache_path.stat().st_size
            }
            
            self._save_index()
            
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def delete(self, key: str, cache_type: str = 'analysis'):
        """Remove item específico do cache"""
        cache_key = self._generate_cache_key(key, cache_type)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            cache_path.unlink()
        
        if cache_key in self.index:
            del self.index[cache_key]
            self._save_index()
    
    def clear_expired(self):
        """Remove todos os itens expirados do cache"""
        expired_keys = []
        
        for cache_key, info in self.index.items():
            if not self._is_cache_valid(cache_key, info['cache_type']):
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            del self.index[key]
        
        if expired_keys:
            self._save_index()
        
        return len(expired_keys)
    
    def clear_all_cache(self):
        """Remove todo o cache"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        
        self.index = {}
        self._save_index()
    
    def get_cache_info(self) -> Dict:
        """Retorna informações sobre o cache"""
        total_size = sum(
            info.get('size_bytes', 0) 
            for info in self.index.values()
        )
        
        by_type = {}
        for info in self.index.values():
            cache_type = info['cache_type']
            by_type[cache_type] = by_type.get(cache_type, 0) + 1
        
        return {
            'total_items': len(self.index),
            'total_size_mb': total_size / (1024 * 1024),
            'by_type': by_type,
            'cache_dir': str(self.cache_dir)
        }
    
    def get_last_update(self) -> Optional[datetime]:
        """Retorna timestamp da última atualização"""
        if not self.index:
            return None
        
        timestamps = [
            datetime.fromisoformat(info['timestamp'])
            for info in self.index.values()
        ]
        
        return max(timestamps) if timestamps else None
    
    # Métodos específicos para o sistema
    
    def get_cached_analysis(self, ticker: str) -> Optional[Dict]:
        """Recupera análise completa do cache"""
        return self.get(ticker, 'analysis')
    
    def save_analysis(self, ticker: str, analysis: Dict):
        """Salva análise completa no cache"""
        self.set(ticker, analysis, 'analysis')
    
    def get_cached_price_data(self, ticker: str) -> Optional[Any]:
        """Recupera dados de preço do cache"""
        return self.get(ticker, 'price_data')
    
    def save_price_data(self, ticker: str, price_data: Any):
        """Salva dados de preço no cache"""
        self.set(ticker, price_data, 'price_data')
    
    def get_cached_news(self, ticker: str) -> Optional[list]:
        """Recupera notícias do cache"""
        return self.get(ticker, 'news')
    
    def save_news(self, ticker: str, news: list):
        """Salva notícias no cache"""
        self.set(ticker, news, 'news')
    
    def get_cached_fundamentals(self, ticker: str) -> Optional[Dict]:
        """Recupera dados fundamentalistas do cache"""
        return self.get(ticker, 'fundamentals')
    
    def save_fundamentals(self, ticker: str, fundamentals: Dict):
        """Salva dados fundamentalistas no cache"""
        self.set(ticker, fundamentals, 'fundamentals')

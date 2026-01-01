"""
Agro Monitor Pro v2.0
Sistema Profissional de Monitoramento do Agronegócio
"""

__version__ = "2.0.0"
__author__ = "Agro Monitor Team"

from .database import AgroDatabase
from .technical_analysis import TechnicalAnalysisEngine
from .fundamental_analysis import FundamentalAnalysisEngine
from .news_analysis import NewsAnalysisEngine
from .monitoring_system import AgroMonitoringSystem
from .cache_manager import CacheManager
from .scheduler import SchedulerManager

__all__ = [
    'AgroDatabase',
    'TechnicalAnalysisEngine',
    'FundamentalAnalysisEngine',
    'NewsAnalysisEngine',
    'AgroMonitoringSystem',
    'CacheManager',
    'SchedulerManager'
]

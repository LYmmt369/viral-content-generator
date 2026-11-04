"""
数据模型模块

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from .account import Account, AccountFingerprint
from .generation import (
    GenerationConfig,
    GenerationOutput,
    GenerationRequest,
    GenerationResult,
)
from .offer import Offer, OfferConfig
from .style import Style, StyleDNA, StyleMix, StyleProfile
from .trend import Trend, TrendItem, TrendMetrics

__all__ = [
    # Account
    'Account',
    'AccountFingerprint',
    # Generation
    'GenerationConfig',
    'GenerationOutput',
    'GenerationRequest',
    'GenerationResult',
    # Offer
    'Offer',
    'OfferConfig',
    # Style
    'Style',
    'StyleDNA',
    'StyleMix',
    'StyleProfile',
    # Trend
    'Trend',
    'TrendItem',
    'TrendMetrics',
]

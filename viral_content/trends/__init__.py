"""
热点情报引擎模块
v4.0

作者: Sunnyeung
版本: 4.1.3
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from .base import (
    BaseTrendSource,
    Trend,
    TrendAggregator,
    TrendCategory,
    TrendMetrics,
)
from .sources.douyin import DouyinTrendSource
from .sources.google_trends import GoogleTrendsSource
from .sources.tiktok import TikTokTrendSource
from .sources.xiaohongshu import XiaohongshuTrendSource

__all__ = [
    # 基类
    "BaseTrendSource",
    "DouyinTrendSource",
    # 热点来源
    "GoogleTrendsSource",
    "TikTokTrendSource",
    "Trend",
    "TrendAggregator",
    "TrendCategory",
    "TrendMetrics",
    "XiaohongshuTrendSource",
]

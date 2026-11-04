"""
评分系统模块
v4.0 - 爆款成交评分器

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from .base import BaseScorer, CompositeScorer, ScoreLevel, ScoreResult


class QualityScorer:
    """对外兼容的综合质量评分器。"""
    def __init__(self, scorers=None):
        self.scorers = scorers or [HookScorer(), TrustScorer(), ValueScorer(), ComplianceScorer()]
    def score_all(self, content, **context):
        return {s.name: s.score(content, context) for s in self.scorers}
    def get_improvement_suggestions(self, scores):
        return [tip for result in scores.values() for tip in result.suggestions]

ScoringResult = ScoreResult
from .compliance_scorer import ComplianceScorer
from .conversion_scorer import ConversionScorer
from .hook_scorer import HookScorer
from .interaction_scorer import InteractionScorer
from .trend_fit_scorer import AccountInfo, TrendFitScorer, TrendInfo
from .trust_scorer import TrustScorer
from .value_scorer import ValueScorer

__all__ = [
    "AccountInfo",
    # 基类
    "BaseScorer",
    "ComplianceScorer",
    "CompositeScorer",
    "ConversionScorer",
    # 专项评分器
    "HookScorer",
    "InteractionScorer",
    "QualityScorer",
    "ScoreLevel",
    "ScoreResult",
    "ScoringResult",
    # 匹配评分器
    "TrendFitScorer",
    "TrendInfo",
    "TrustScorer",
    "ValueScorer",
]

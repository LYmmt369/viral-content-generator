"""
评分器基类
v4.0 - 爆款成交评分器

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ScoreLevel(Enum):
    """评分等级"""
    EXCELLENT = "excellent"  # 优秀 (9-10分)
    GOOD = "good"  # 良好 (7-8分)
    AVERAGE = "average"  # 一般 (5-6分)
    POOR = "poor"  # 较差 (3-4分)
    FAIL = "fail"  # 失败 (0-2分)


@dataclass
class ScoreResult:
    """评分结果"""
    score: float  # 总分 (0-10)
    level: ScoreLevel  # 等级
    details: dict[str, Any]  # 详细评分
    suggestions: list[str]  # 改进建议
    passed: bool  # 是否通过阈值

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "score": self.score,
            "level": self.level.value,
            "details": self.details,
            "suggestions": self.suggestions,
            "passed": self.passed,
        }


class BaseScorer(ABC):
    """评分器基类

    所有评分器必须实现：
    - score(): 评分方法
    - get_threshold(): 获取通过阈值
    """

    def __init__(self, threshold: float = 7.0):
        """初始化评分器

        Args:
            threshold: 通过阈值（默认7.0分）
        """
        self.threshold = threshold
        self.name = self.__class__.__name__

    @abstractmethod
    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """评分内容

        Args:
            content: 待评分内容
            context: 上下文信息（可选）

        Returns:
            评分结果
        """

    def get_threshold(self) -> float:
        """获取通过阈值"""
        return self.threshold

    def set_threshold(self, threshold: float) -> None:
        """设置通过阈值

        Args:
            threshold: 新阈值 (0-10)
        """
        if not 0 <= threshold <= 10:
            raise ValueError("阈值必须在 0-10 之间")
        self.threshold = threshold

    def _calculate_level(self, score: float) -> ScoreLevel:
        """根据分数计算等级

        Args:
            score: 分数

        Returns:
            等级
        """
        if score >= 9.0:
            return ScoreLevel.EXCELLENT
        elif score >= 7.0:
            return ScoreLevel.GOOD
        elif score >= 5.0:
            return ScoreLevel.AVERAGE
        elif score >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.FAIL

    def _check_passed(self, score: float) -> bool:
        """检查是否通过阈值

        Args:
            score: 分数

        Returns:
            是否通过
        """
        return score >= self.threshold

    def _generate_suggestions(
        self,
        score: float,
        details: dict[str, Any]
    ) -> list[str]:
        """生成改进建议（可被子类覆盖）

        Args:
            score: 分数
            details: 详细评分

        Returns:
            建议列表
        """
        suggestions = []

        if score < self.threshold:
            suggestions.append(f"当前评分({score:.1f})低于阈值({self.threshold:.1f})，需要优化")

        # 子类可以添加更具体的建议
        return suggestions


class CompositeScorer(BaseScorer):
    """组合评分器

    将多个评分器组合成一个综合评分器
    """

    def __init__(
        self,
        scorers: list[BaseScorer],
        weights: dict[str, float] | None = None,
        threshold: float = 7.0
    ):
        """初始化组合评分器

        Args:
            scorers: 评分器列表
            weights: 各评分器权重（可选）
            threshold: 综合通过阈值
        """
        super().__init__(threshold)
        self.scorers = scorers

        # 默认权重：所有评分器权重相等
        if weights is None:
            weights = {scorer.name: 1.0 for scorer in scorers}

        self.weights = weights

    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """综合评分

        Args:
            content: 待评分内容
            context: 上下文信息

        Returns:
            综合评分结果
        """
        all_results = {}
        all_suggestions = []
        weighted_sum = 0.0
        weight_sum = 0.0

        for scorer in self.scorers:
            result = scorer.score(content, context)
            weight = self.weights.get(scorer.name, 1.0)

            all_results[scorer.name] = result.to_dict()
            all_suggestions.extend(result.suggestions)

            weighted_sum += result.score * weight
            weight_sum += weight

        # 计算加权平均分
        final_score = weighted_sum / weight_sum if weight_sum > 0 else 0.0

        return ScoreResult(
            score=final_score,
            level=self._calculate_level(final_score),
            details=all_results,
            suggestions=all_suggestions,
            passed=self._check_passed(final_score)
        )

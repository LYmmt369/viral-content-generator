"""
热点匹配评分器
v4.0 - 评分热点与账号的匹配度

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from dataclasses import dataclass
from typing import Any

from .base import BaseScorer, ScoreLevel, ScoreResult


@dataclass
class TrendInfo:
    """热点信息"""
    topic: str  # 话题
    description: str  # 描述
    keywords: list[str]  # 关键词
    category: str  # 分类
    metrics: dict[str, Any] | None = None  # 热度指标


@dataclass
class AccountInfo:
    """账号信息"""
    name: str  # 账号名
    identity: str  # 定位
    target_audience: list[str]  # 目标用户
    pain_points: list[str]  # 用户痛点
    topics: list[str]  # 擅长话题
    authority_assets: list[str] | None = None  # 权威资产


class TrendFitScorer(BaseScorer):
    """热点匹配评分器

    评分热点与账号的匹配度，判断是否值得为该账号创作该热点内容

    评分维度：
    1. 话题相关性 - 话题与账号定位的相关度
    2. 用户匹配度 - 热点受众与账号目标用户的重叠度
    3. 痛点匹配度 - 热点解决的用户痛点
    4. 权威匹配度 - 账号在该话题的权威性
    5. 热度价值 - 热点的传播价值
    """

    def __init__(self, threshold: float = 6.0):
        """初始化热点匹配评分器

        Args:
            threshold: 通过阈值（默认6.0，匹配度门槛）
        """
        super().__init__(threshold)

    def score(
        self,
        content: str,
        context: dict[str, Any] | None = None
    ) -> ScoreResult:
        """评分匹配度

        Args:
            content: 热点内容（通常传入JSON字符串或话题文本）
            context: 上下文，需包含 trend 和 account

        Returns:
            匹配度评分结果
        """
        if not context:
            return ScoreResult(
                score=0.0,
                level=ScoreLevel.FAIL,
                details={"error": "缺少 context 参数"},
                suggestions=["请提供 trend 和 account 信息"],
                passed=False
            )

        trend = context.get("trend")
        account = context.get("account")

        if not trend or not account:
            return ScoreResult(
                score=0.0,
                level=ScoreLevel.FAIL,
                details={"error": "context 中缺少 trend 或 account"},
                suggestions=["请提供完整的热点和账号信息"],
                passed=False
            )

        # 转换为数据对象
        if isinstance(trend, dict):
            trend = TrendInfo(**trend)
        if isinstance(account, dict):
            account = AccountInfo(**account)

        # 各维度评分
        scores = {
            "relevance": self._score_relevance(trend, account),
            "audience": self._score_audience(trend, account),
            "pain_point": self._score_pain_point(trend, account),
            "authority": self._score_authority(trend, account),
            "heat_value": self._score_heat_value(trend),
        }

        # 计算总分
        weights = {"relevance": 0.3, "audience": 0.25, "pain_point": 0.2, "authority": 0.15, "heat_value": 0.1}
        total_score = sum(scores[k] * weights[k] for k in scores)

        # 生成建议
        suggestions = self._generate_fit_suggestions(scores, trend, account)

        return ScoreResult(
            score=total_score,
            level=self._calculate_level(total_score),
            details={
                "dimension_scores": scores,
                "trend": trend.topic,
                "account": account.name
            },
            suggestions=suggestions,
            passed=self._check_passed(total_score)
        )

    def _score_relevance(self, trend: TrendInfo, account: AccountInfo) -> float:
        """评分话题相关性"""
        # 检查话题与账号定位的相关性
        identity_lower = account.identity.lower()
        topic_lower = trend.topic.lower()

        # 直接匹配
        if any(word in identity_lower for word in topic_lower.split()):
            return 10.0

        # 话题匹配
        if account.topics and any(topic in trend.topic or trend.topic in topic
               for topic in account.topics):
            return 9.0

        # 分类匹配
        if (
            account.identity
            and trend.category
            and (trend.category in account.identity or account.identity in trend.category)
        ):
            return 8.0

        # 关键词匹配
        if trend.keywords:
            match_count = sum(1 for kw in trend.keywords
                             if kw in account.identity or any(kw in topic for topic in account.topics or []))
            if match_count >= 2:
                return 7.0
            elif match_count == 1:
                return 5.0

        return 3.0

    def _score_audience(self, trend: TrendInfo, account: AccountInfo) -> float:
        """评分用户匹配度"""
        # 简化处理：假设热点的潜在用户与账号目标用户有重叠
        # 实际应用中可以从热点数据中提取用户群体信息

        if not account.target_audience:
            return 5.0  # 无信息时给中性分

        # 检查热点描述中是否包含目标用户关键词
        match_count = 0
        trend_text = (trend.topic + " " + trend.description).lower()

        for audience in account.target_audience:
            if audience.lower() in trend_text:
                match_count += 1

        if match_count >= len(account.target_audience):
            return 10.0
        elif match_count >= len(account.target_audience) * 0.5:
            return 7.5
        elif match_count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_pain_point(self, trend: TrendInfo, account: AccountInfo) -> float:
        """评分痛点匹配度"""
        if not account.pain_points:
            return 5.0

        # 检查热点是否解决用户痛点
        trend_text = (trend.topic + " " + trend.description).lower()

        match_count = 0
        for pain in account.pain_points:
            if pain.lower() in trend_text or any(
                word in trend_text for word in pain.lower().split()
            ):
                match_count += 1

        if match_count >= len(account.pain_points):
            return 10.0
        elif match_count >= len(account.pain_points) * 0.5:
            return 7.5
        elif match_count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_authority(self, trend: TrendInfo, account: AccountInfo) -> float:
        """评分权威匹配度"""
        if not account.authority_assets:
            return 5.0

        # 检查权威资产是否与话题相关
        relevant_assets = 0
        for asset in account.authority_assets:
            if any(word in asset for word in trend.topic.split()):
                relevant_assets += 1

        if relevant_assets >= 2:
            return 10.0
        elif relevant_assets >= 1:
            return 7.0
        else:
            return 5.0

    def _score_heat_value(self, trend: TrendInfo) -> float:
        """评分热度价值"""
        if not trend.metrics:
            return 5.0  # 无热度数据时给中性分

        # 根据热度指标评分
        heat_score = 0
        if "热度" in trend.metrics:
            heat = trend.metrics["热度"]
            if heat >= 80:
                heat_score += 4
            elif heat >= 60:
                heat_score += 3
            elif heat >= 40:
                heat_score += 2
            else:
                heat_score += 1

        if "讨论量" in trend.metrics:
            discussion = trend.metrics["讨论量"]
            if discussion >= 10000:
                heat_score += 3
            elif discussion >= 1000:
                heat_score += 2
            elif discussion >= 100:
                heat_score += 1

        return min(heat_score, 10.0)

    def _generate_fit_suggestions(
        self,
        scores: dict[str, float],
        trend: TrendInfo,
        account: AccountInfo
    ) -> list[str]:
        """生成匹配度改进建议"""
        suggestions = []

        if scores["relevance"] < 6.0:
            suggestions.append(f"热点「{trend.topic}」与账号定位「{account.identity}」相关性较低，谨慎创作")

        if scores["audience"] < 6.0:
            suggestions.append("热点受众与账号目标用户匹配度低，可能影响转化效果")

        if scores["pain_point"] < 6.0:
            suggestions.append("热点未能有效解决账号目标用户的痛点")

        if scores["authority"] < 6.0:
            suggestions.append("建议：在内容中突出账号在该话题的专业性和权威性")

        if scores["heat_value"] < 5.0:
            suggestions.append("当前热点热度较低，可能不具备传播价值")

        # 综合建议
        total_score = sum(scores.values()) / len(scores)
        if total_score >= 8.0:
            suggestions.append("✅ 高匹配度！强烈建议为该账号创作此热点内容")
        elif total_score >= 6.0:
            suggestions.append("⚠️ 中等匹配度，可以创作但需优化切入点")
        else:
            suggestions.append("❌ 低匹配度，不建议为该账号创作此热点内容")

        return suggestions

    def batch_score(
        self,
        trends: list[TrendInfo],
        account: AccountInfo
    ) -> list[ScoreResult]:
        """批量评分多个热点与同一账号的匹配度

        Args:
            trends: 热点列表
            account: 账号信息

        Returns:
            评分结果列表（按匹配度降序排列）
        """
        results = []

        for trend in trends:
            # 将热点转为JSON字符串作为content
            content = f"{trend.topic}: {trend.description}"
            context = {"trend": trend, "account": account}

            result = self.score(content, context)
            results.append(result)

        # 按分数降序排列
        results.sort(key=lambda x: x.score, reverse=True)

        return results

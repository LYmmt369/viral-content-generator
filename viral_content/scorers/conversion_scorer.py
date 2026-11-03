"""
转化评分器
v4.0 - 评估内容的转化能力

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from typing import Any, ClassVar

from .base import BaseScorer, ScoreResult


class ConversionScorer(BaseScorer):
    """转化评分器

    评估内容促进目标转化的能力

    评分维度：
    1. CTA 明确性 - 行动召唤清晰
    2. 紧迫感 - 时间压力
    3. 门槛适中 - 行动难度
    4. 价值主张 - 转化收益
    5. 信任铺垫 - 转化前信任
    """

    # 转化信号关键词
    CONVERSION_SIGNALS: ClassVar = {
        "cta": [
            "评论", "私信", "加微信", "关注", "购买", "下单",
            "领取", "获取", "咨询", "报名", "加入"
        ],
        "urgency": [
            "限时", "仅剩", "今天", "马上", "立即", "现在",
            "最后", "错过", "不再", "截止"
        ],
        "low_barrier": [
            "免费", "0元", "无需", "简单", "轻松",
            "只要", "只需", "快速"
        ],
        "value": [
            "价值", "优惠", "折扣", "福利", "礼物", "赠送",
            "省钱", "赚钱", "提升", "解决"
        ],
        "trust": [
            "保障", "承诺", "验证", "真实", "靠谱",
            "专业", "经验", "成功", "案例"
        ],
    }

    def __init__(self, threshold: float = 7.0, goal: str = "leads"):
        """初始化转化评分器

        Args:
            threshold: 通过阈值
            goal: 转化目标（likes/comments/leads/sales）
        """
        super().__init__(threshold)
        self.goal = goal

    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """评分转化能力

        Args:
            content: 内容全文
            context: 上下文（可选）

        Returns:
            评分结果
        """
        # 根据不同目标调整评分权重
        weights = self._get_weights_by_goal()

        # 各维度评分
        scores = {
            "cta": self._score_cta(content),
            "urgency": self._score_urgency(content),
            "barrier": self._score_barrier(content),
            "value": self._score_value(content),
            "trust": self._score_trust(content),
        }

        # 根据目标调整权重
        total_score = sum(scores[k] * weights.get(k, 0.2) for k in scores)

        # 生成建议
        suggestions = self._generate_conversion_suggestions(scores)

        return ScoreResult(
            score=total_score,
            level=self._calculate_level(total_score),
            details={"dimension_scores": scores, "goal": self.goal},
            suggestions=suggestions,
            passed=self._check_passed(total_score)
        )

    def _get_weights_by_goal(self) -> dict[str, float]:
        """根据目标获取权重"""
        if self.goal == "sales":
            return {"cta": 0.3, "urgency": 0.25, "barrier": 0.15, "value": 0.2, "trust": 0.1}
        elif self.goal == "leads":
            return {"cta": 0.3, "urgency": 0.15, "barrier": 0.2, "value": 0.25, "trust": 0.1}
        elif self.goal == "comments":
            return {"cta": 0.35, "urgency": 0.1, "barrier": 0.1, "value": 0.25, "trust": 0.2}
        else:  # likes
            return {"cta": 0.25, "urgency": 0.1, "barrier": 0.1, "value": 0.35, "trust": 0.2}

    def _score_cta(self, content: str) -> float:
        """评分CTA明确性"""
        count = sum(1 for keyword in self.CONVERSION_SIGNALS["cta"] if keyword in content)

        # 检查结尾是否有CTA
        last_part = content[-100:] if len(content) > 100 else content
        has_ending_cta = any(keyword in last_part for keyword in self.CONVERSION_SIGNALS["cta"])

        if count >= 3 or (count >= 1 and has_ending_cta):
            return 10.0
        elif count >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_urgency(self, content: str) -> float:
        """评分紧迫感"""
        count = sum(1 for keyword in self.CONVERSION_SIGNALS["urgency"] if keyword in content)

        if count >= 3:
            return 10.0
        elif count >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_barrier(self, content: str) -> float:
        """评分行动门槛"""
        low_barrier_count = sum(1 for keyword in self.CONVERSION_SIGNALS["low_barrier"] if keyword in content)

        # 检查是否有高门槛词汇（应减少）
        high_barrier_words = ["需要", "必须", "复杂", "困难", "麻烦"]
        high_barrier_count = sum(1 for word in high_barrier_words if word in content)

        if low_barrier_count >= 3 and high_barrier_count == 0:
            return 10.0
        elif low_barrier_count >= 2:
            return 7.5
        elif low_barrier_count >= 1:
            return 5.0
        else:
            if high_barrier_count > 2:
                return 3.0
            return 5.0

    def _score_value(self, content: str) -> float:
        """评分价值主张"""
        count = sum(1 for keyword in self.CONVERSION_SIGNALS["value"] if keyword in content)

        if count >= 4:
            return 10.0
        elif count >= 3:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_trust(self, content: str) -> float:
        """评分信任铺垫"""
        count = sum(1 for keyword in self.CONVERSION_SIGNALS["trust"] if keyword in content)

        if count >= 4:
            return 10.0
        elif count >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _generate_conversion_suggestions(self, scores: dict[str, float]) -> list[str]:
        """生成转化改进建议"""
        suggestions = []

        if scores["cta"] < 6.0:
            suggestions.append("在结尾添加明确的行动召唤（CTA）")

        if scores["urgency"] < 6.0 and self.goal in ["sales", "leads"]:
            suggestions.append("增加时间紧迫感（限时、限量等）")

        if scores["barrier"] < 6.0:
            suggestions.append("强调行动简单，降低门槛")

        if scores["value"] < 6.0:
            suggestions.append("明确说明转化的具体收益")

        if scores["trust"] < 6.0:
            suggestions.append("在转化前建立更多信任（案例、保障等）")

        return suggestions

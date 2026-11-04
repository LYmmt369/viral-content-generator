"""
信任度评分器
v4.0 - 评估内容建立信任的能力

作者: Sunnyeung
版本: 4.1.3
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import re
from typing import Any, ClassVar

from .base import BaseScorer, ScoreResult


class TrustScorer(BaseScorer):
    """信任度评分器

    评估内容是否能够建立读者信任

    评分维度：
    1. 权威展示 - 专业背书
    2. 数据支撑 - 事实依据
    3. 案例具体 - 真实可信
    4. 诚实透明 - 承认局限
    5. 逻辑一致 - 自洽合理
    """

    # 信任信号关键词
    TRUST_SIGNALS: ClassVar = {
        "authority": [
            "研究", "数据", "报告", "专家", "博士", "教授",
            "经验", "从业", "年", "项目", "案例", "实践"
        ],
        "data": [
            "%", "％", "倍", "万", "亿", "研究", "调查",
            "统计", "实验", "测试", "分析"
        ],
        "honesty": [
            "可能", "或许", "不一定", "因人而异", "仅供参考",
            "个人观点", "不一定适合", "需要考虑", "注意"
        ],
    }

    def __init__(self, threshold: float = 7.0):
        """初始化信任度评分器"""
        super().__init__(threshold)

    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """评分信任度

        Args:
            content: 内容全文
            context: 上下文（可选）

        Returns:
            评分结果
        """
        # 各维度评分
        scores = {
            "authority": self._score_authority(content),
            "data": self._score_data(content),
            "case": self._score_case(content),
            "honesty": self._score_honesty(content),
            "logic": self._score_logic(content),
        }

        # 计算总分
        weights = {"authority": 0.25, "data": 0.25, "case": 0.2, "honesty": 0.15, "logic": 0.15}
        total_score = sum(scores[k] * weights[k] for k in scores)

        # 生成建议
        suggestions = self._generate_trust_suggestions(scores)

        return ScoreResult(
            score=total_score,
            level=self._calculate_level(total_score),
            details={"dimension_scores": scores},
            suggestions=suggestions,
            passed=self._check_passed(total_score)
        )

    def _score_authority(self, content: str) -> float:
        """评分权威展示

        检查是否有专业背景、经验等权威信号
        """
        count = sum(1 for keyword in self.TRUST_SIGNALS["authority"] if keyword in content)

        if count >= 5:
            return 10.0
        elif count >= 3:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_data(self, content: str) -> float:
        """评分数据支撑

        检查是否有具体数据和事实依据
        """
        count = sum(1 for keyword in self.TRUST_SIGNALS["data"] if keyword in content)

        # 检查数字使用
        numbers = len(re.findall(r"\d+", content))

        if count >= 3 or numbers >= 10:
            return 10.0
        elif count >= 2 or numbers >= 5:
            return 7.5
        elif count >= 1 or numbers >= 2:
            return 5.0
        else:
            return 3.0

    def _score_case(self, content: str) -> float:
        """评分案例具体性

        检查是否有具体案例和细节
        """
        # 案例信号词
        case_signals = ["例如", "比如", "案例", "有一个", "我遇到", "曾经", "具体"]

        count = sum(1 for signal in case_signals if signal in content)

        # 检查是否有详细描述（长句）
        sentences = re.split(r"[。！？!?]", content)
        detailed_sentences = [s for s in sentences if len(s) > 30]

        if count >= 3 and len(detailed_sentences) >= 5:
            return 10.0
        elif count >= 2 and len(detailed_sentences) >= 3:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_honesty(self, content: str) -> float:
        """评分诚实透明

        检查是否有承认局限、避免绝对化表达
        """
        honesty_count = sum(1 for keyword in self.TRUST_SIGNALS["honesty"] if keyword in content)

        # 检查绝对化表达（应避免）
        absolute_words = ["一定", "肯定", "绝对", "必须", "必然"]
        absolute_count = sum(1 for word in absolute_words if word in content)

        if honesty_count >= 3 and absolute_count == 0:
            return 10.0
        elif honesty_count >= 2:
            return 8.0
        elif honesty_count >= 1:
            return 6.0
        else:
            if absolute_count > 2:
                return 3.0  # 过度绝对化
            return 5.0

    def _score_logic(self, content: str) -> float:
        """评分逻辑一致性

        检查内容是否有逻辑连接词
        """
        logic_words = [
            "因此", "所以", "因为", "由于", "但是", "然而",
            "首先", "其次", "最后", "总的来说", "综合来看",
            "一方面", "另一方面", "此外", "另外"
        ]

        count = sum(1 for word in logic_words if word in content)

        if count >= 5:
            return 10.0
        elif count >= 3:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _generate_trust_suggestions(self, scores: dict[str, float]) -> list[str]:
        """生成信任度改进建议"""
        suggestions = []

        if scores["authority"] < 6.0:
            suggestions.append("展示专业背景或从业经验，增加权威性")

        if scores["data"] < 6.0:
            suggestions.append("加入具体数据和研究结果，支撑观点")

        if scores["case"] < 6.0:
            suggestions.append("使用具体案例，增加真实感")

        if scores["honesty"] < 6.0:
            suggestions.append("避免绝对化表达，承认观点的适用范围")

        if scores["logic"] < 6.0:
            suggestions.append("使用逻辑连接词，使论证更清晰")

        return suggestions

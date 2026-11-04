"""
价值感评分器
v4.0 - 评估内容提供的价值感

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import re
from typing import Any, ClassVar

from .base import BaseScorer, ScoreResult


class ValueScorer(BaseScorer):
    """价值感评分器

    评估内容是否提供实际价值给读者

    评分维度：
    1. 实用性 - 可操作建议
    2. 独特性 - 独特见解
    3. 深度性 - 深入分析
    4. 完整性 - 系统全面
    5. 启发性 - 引发思考
    """

    # 价值信号关键词
    VALUE_SIGNALS: ClassVar = {
        "practical": [
            "方法", "技巧", "步骤", "策略", "建议", "可以",
            "如何", "怎样", "怎么做", "具体", "行动", "执行"
        ],
        "unique": [
            "独特", "不同", "区别", "差异", "很少人", "多数人不知道",
            "关键", "核心", "本质", "根本"
        ],
        "depth": [
            "深层", "本质", "原因", "为什么", "背后的", "逻辑",
            "机制", "原理", "分析", "探究"
        ],
        "complete": [
            "全面", "完整", "系统", "整体", "首先", "其次",
            "然后", "最后", "总结", "归纳"
        ],
        "insightful": [
            "思考", "启发", "感悟", "发现", "意识到",
            "原来", "没想到", "值得", "反思"
        ],
    }

    def __init__(self, threshold: float = 7.0):
        """初始化价值感评分器"""
        super().__init__(threshold)

    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """评分价值感

        Args:
            content: 内容全文
            context: 上下文（可选）

        Returns:
            评分结果
        """
        # 各维度评分
        scores = {
            "practical": self._score_practicality(content),
            "unique": self._score_uniqueness(content),
            "depth": self._score_depth(content),
            "complete": self._score_completeness(content),
            "insightful": self._score_insight(content),
        }

        # 计算总分
        weights = {"practical": 0.25, "unique": 0.2, "depth": 0.2, "complete": 0.2, "insightful": 0.15}
        total_score = sum(scores[k] * weights[k] for k in scores)

        # 生成建议
        suggestions = self._generate_value_suggestions(scores)

        return ScoreResult(
            score=total_score,
            level=self._calculate_level(total_score),
            details={"dimension_scores": scores},
            suggestions=suggestions,
            passed=self._check_passed(total_score)
        )

    def _score_practicality(self, content: str) -> float:
        """评分实用性

        检查是否有可操作的建议和方法
        """
        count = sum(1 for keyword in self.VALUE_SIGNALS["practical"] if keyword in content)

        # 检查是否有步骤性内容（ numbered list）
        numbered_points = len(re.findall(r"^\s*\d+[.、]", content, re.MULTILINE))

        if count >= 5 or numbered_points >= 3:
            return 10.0
        elif count >= 3 or numbered_points >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_uniqueness(self, content: str) -> float:
        """评分独特性

        检查是否有独特见解或差异化观点
        """
        count = sum(1 for keyword in self.VALUE_SIGNALS["unique"] if keyword in content)

        # 检查是否有对比或反常识表达
        contrast_signals = ["但是", "然而", "实际上", "相反", "与之不同"]
        contrast_count = sum(1 for signal in contrast_signals if signal in content)

        if count >= 3 or contrast_count >= 2:
            return 10.0
        elif count >= 2 or contrast_count >= 1:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_depth(self, content: str) -> float:
        """评分深度

        检查是否有深入分析和本质探究
        """
        count = sum(1 for keyword in self.VALUE_SIGNALS["depth"] if keyword in content)

        # 检查句子平均长度（深度内容通常句子更长）
        sentences = [s for s in re.split(r"[。！？!?]", content) if s.strip()]
        if sentences:
            avg_length = sum(len(s) for s in sentences) / len(sentences)

            if count >= 3 and avg_length >= 25:
                return 10.0
            elif count >= 2:
                return 7.5
            elif count >= 1:
                return 5.0
            else:
                return 3.0
        else:
            return 3.0

    def _score_completeness(self, content: str) -> float:
        """评分完整性

        检查内容是否系统全面
        """
        count = sum(1 for keyword in self.VALUE_SIGNALS["complete"] if keyword in content)

        # 检查文章结构（是否有明显的起承转合）
        has_structure = all([
            any(word in content for word in ["首先", "一开始", "开始"]),
            any(word in content for word in ["然后", "接下来", "其次"]),
            any(word in content for word in ["最后", "总之", "总结"]),
        ])

        if count >= 4 or has_structure:
            return 10.0
        elif count >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_insight(self, content: str) -> float:
        """评分启发性

        检查是否能引发读者思考
        """
        count = sum(1 for keyword in self.VALUE_SIGNALS["insightful"] if keyword in content)

        # 检查是否有金句（短小精悍的句子）
        sentences = [s for s in re.split(r"[。！？!?]", content) if s.strip()]
        short_sentences = [s for s in sentences if 10 <= len(s) <= 20]

        if count >= 3 or len(short_sentences) >= 5:
            return 10.0
        elif count >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _generate_value_suggestions(self, scores: dict[str, float]) -> list[str]:
        """生成价值感改进建议"""
        suggestions = []

        if scores["practical"] < 6.0:
            suggestions.append("增加可操作的建议和具体方法")

        if scores["unique"] < 6.0:
            suggestions.append("突出独特观点或差异化见解")

        if scores["depth"] < 6.0:
            suggestions.append("深入分析问题本质，不止于表面")

        if scores["complete"] < 6.0:
            suggestions.append("使内容更系统全面，有完整结构")

        if scores["insightful"] < 6.0:
            suggestions.append("加入能引发思考的洞察或金句")

        return suggestions

"""
互动评分器
v4.0 - 评估内容的互动潜力

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import re
from typing import Any, ClassVar

from .base import BaseScorer, ScoreResult


class InteractionScorer(BaseScorer):
    """互动评分器

    评估内容激发读者互动的能力

    评分维度：
    1. 提问引导 - 引发评论
    2. 争议空间 - 留出讨论余地
    3. 情感共鸣 - 激发情绪
    4. 行动召唤 - 明确互动指令
    5. 分享价值 - 值得转发
    """

    # 互动信号关键词
    INTERACTION_SIGNALS: ClassVar = {
        "question": [
            "你觉得", "你认为", "你怎么看", "你的观点", "你的看法",
            "呢吗", "吗", "呢", "有没有", "是不是"
        ],
        "controversy": [
            "争议", "不同", "反对", "支持", " debate ", "讨论",
            "各有", "取决于", "因人而异"
        ],
        "emotion": [
            "感动", "愤怒", "惊喜", "震惊", "担心", "焦虑",
            "开心", "难过", "心痛", "兴奋"
        ],
        "cta": [
            "评论", "留言", "分享", "转发", "点赞", "关注",
            "说出", "告诉我", "大家在"
        ],
        "shareable": [
            "转发", "分享给", "告诉", "收藏", "值得",
            "建议", "推荐", "必须看"
        ],
    }

    def __init__(self, threshold: float = 7.0):
        """初始化互动评分器"""
        super().__init__(threshold)

    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """评分互动潜力

        Args:
            content: 内容全文
            context: 上下文（可选）

        Returns:
            评分结果
        """
        # 各维度评分
        scores = {
            "question": self._score_question(content),
            "controversy": self._score_controversy(content),
            "emotion": self._score_emotion(content),
            "cta": self._score_cta(content),
            "shareable": self._score_shareable(content),
        }

        # 计算总分
        weights = {"question": 0.25, "controversy": 0.2, "emotion": 0.2, "cta": 0.2, "shareable": 0.15}
        total_score = sum(scores[k] * weights[k] for k in scores)

        # 生成建议
        suggestions = self._generate_interaction_suggestions(scores)

        return ScoreResult(
            score=total_score,
            level=self._calculate_level(total_score),
            details={"dimension_scores": scores},
            suggestions=suggestions,
            passed=self._check_passed(total_score)
        )

    def _score_question(self, content: str) -> float:
        """评分提问引导

        检查是否有引导读者提问的表达
        """
        count = sum(1 for keyword in self.INTERACTION_SIGNALS["question"] if keyword in content)

        # 检查是否有疑问句
        question_marks = content.count("？") + content.count("?")

        if count >= 3 or question_marks >= 3:
            return 10.0
        elif count >= 2 or question_marks >= 2:
            return 7.5
        elif count >= 1 or question_marks >= 1:
            return 5.0
        else:
            return 3.0

    def _score_controversy(self, content: str) -> float:
        """评分争议空间

        检查是否留出讨论和争议的空间
        """
        count = sum(1 for keyword in self.INTERACTION_SIGNALS["controversy"] if keyword in content)

        # 检查是否有不同观点的表达
        perspective_words = ["一方面", "另一方面", "有人认为", "也有人说", "观点"]
        perspective_count = sum(1 for word in perspective_words if word in content)

        if count >= 2 or perspective_count >= 2:
            return 10.0
        elif count >= 1 or perspective_count >= 1:
            return 7.0
        else:
            return 4.0

    def _score_emotion(self, content: str) -> float:
        """评分情感共鸣

        检查是否能激发读者情绪
        """
        count = sum(1 for keyword in self.INTERACTION_SIGNALS["emotion"] if keyword in content)

        # 检查情绪形容词
        emotion_adj = ["太", "非常", "特别", "极其", "超", "超级"]
        emotion_adj_count = sum(1 for word in emotion_adj if word in content)

        if count >= 3 or emotion_adj_count >= 5:
            return 10.0
        elif count >= 2 or emotion_adj_count >= 3:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_cta(self, content: str) -> float:
        """评分行动召唤

        检查是否有明确的互动指令
        """
        count = sum(1 for keyword in self.INTERACTION_SIGNALS["cta"] if keyword in content)

        # 检查结尾是否有CTA
        last_part = content[-100:] if len(content) > 100 else content
        has_ending_cta = any(keyword in last_part for keyword in ["评论", "留言", "分享", "说出"])

        if (count >= 3) or (count >= 1 and has_ending_cta):
            return 10.0
        elif count >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _score_shareable(self, content: str) -> float:
        """评分分享价值

        检查内容是否值得转发分享
        """
        count = sum(1 for keyword in self.INTERACTION_SIGNALS["shareable"] if keyword in content)

        # 检查是否有金句（容易被分享）
        sentences = re.split(r"[。！？!?]", content)
        short_sentences = [s.strip() for s in sentences if 10 <= len(s.strip()) <= 25]

        # 检查是否有总结性/建议性表达
        summary_words = ["记住", "一定要", "关键是", "最重要的是"]
        summary_count = sum(1 for word in summary_words if word in content)

        if count >= 3 or (len(short_sentences) >= 3 and summary_count >= 1):
            return 10.0
        elif count >= 2:
            return 7.5
        elif count >= 1:
            return 5.0
        else:
            return 3.0

    def _generate_interaction_suggestions(self, scores: dict[str, float]) -> list[str]:
        """生成互动改进建议"""
        suggestions = []

        if scores["question"] < 6.0:
            suggestions.append("在结尾提出问题，引导读者评论")

        if scores["controversy"] < 6.0:
            suggestions.append("留出讨论空间，允许不同观点")

        if scores["emotion"] < 6.0:
            suggestions.append("加入情感元素，激发读者情绪")

        if scores["cta"] < 6.0:
            suggestions.append("明确引导读者互动（评论/分享/点赞）")

        if scores["shareable"] < 6.0:
            suggestions.append("提炼金句或要点，增加分享价值")

        return suggestions

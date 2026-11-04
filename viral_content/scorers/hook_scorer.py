"""
钩子评分器
v4.0 - 评估开头钩子的吸引力

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import re
from typing import Any, ClassVar

from .base import BaseScorer, ScoreResult


class HookScorer(BaseScorer):
    """钩子评分器

    评估内容开头的钩子是否足够吸引人

    评分维度：
    1. 疑问句使用 - 引发好奇
    2. 数字数据 - 具体可信
    3. 冲突对立 - 制造张力
    4. 身份相关 - 建立连接
    5. 长度控制 - 简洁有力
    """

    # 钩子模式正则表达式
    HOOK_PATTERNS: ClassVar = {
        "question": r"[？?]",  # 疑问句
        "number": r"\d+[个项条人次万元%]",  # 数字+单位
        "contrast": r"(但是|然而|却|其实|反而)",  # 对比词
        "identity": r"(你|你们|打工|老板|创业|职场|家庭|孩子)",  # 身份词
    }

    def __init__(self, threshold: float = 7.0):
        """初始化钩子评分器"""
        super().__init__(threshold)
        self.ideal_hook_length = (20, 60)  # 理想钩子长度范围（字符数）

    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """评分钩子质量

        Args:
            content: 内容全文
            context: 上下文（可选）

        Returns:
            评分结果
        """
        # 提取开头（前3句或前100字）
        hook_text = self._extract_hook(content)

        # 各维度评分
        scores = {
            "question": self._score_question(hook_text),
            "number": self._score_number(hook_text),
            "contrast": self._score_contrast(hook_text),
            "identity": self._score_identity(hook_text),
            "length": self._score_length(hook_text),
        }

        # 计算总分（加权平均）
        weights = {"question": 0.25, "number": 0.2, "contrast": 0.2, "identity": 0.2, "length": 0.15}
        total_score = sum(scores[k] * weights[k] for k in scores)

        # 生成建议
        suggestions = self._generate_hook_suggestions(scores, hook_text)

        return ScoreResult(
            score=total_score,
            level=self._calculate_level(total_score),
            details={"hook_text": hook_text, "dimension_scores": scores},
            suggestions=suggestions,
            passed=self._check_passed(total_score)
        )

    def _extract_hook(self, content: str) -> str:
        """提取钩子部分

        Args:
            content: 全文

        Returns:
            钩子文本
        """
        # 按句子分割
        sentences = re.split(r"[。！？!?]", content)

        # 取前3句，或前100字
        hook_sentences = []
        char_count = 0
        for sentence in sentences:
            if sentence.strip():
                hook_sentences.append(sentence.strip())
                char_count += len(sentence)
                if len(hook_sentences) >= 3 or char_count >= 100:
                    break

        return "。".join(hook_sentences)

    def _score_question(self, hook: str) -> float:
        """评分疑问句使用

        疑问句能引发好奇，是有效的钩子技巧
        """
        count = len(re.findall(self.HOOK_PATTERNS["question"], hook))

        if count >= 2:
            return 10.0
        elif count == 1:
            return 7.0
        else:
            return 4.0

    def _score_number(self, hook: str) -> float:
        """评分数字使用

        具体数字增加可信度
        """
        count = len(re.findall(self.HOOK_PATTERNS["number"], hook))

        if count >= 2:
            return 10.0
        elif count == 1:
            return 7.0
        else:
            return 5.0

    def _score_contrast(self, hook: str) -> float:
        """评分对比词使用

        对比制造张力，吸引注意
        """
        count = len(re.findall(self.HOOK_PATTERNS["contrast"], hook))

        if count >= 1:
            return 10.0
        else:
            return 6.0

    def _score_identity(self, hook: str) -> float:
        """评分身份词使用

        身份相关词汇建立连接
        """
        matches = re.findall(self.HOOK_PATTERNS["identity"], hook)

        # 不同类型身份词加分
        unique_types = len(set(matches))

        if unique_types >= 2:
            return 10.0
        elif unique_types == 1:
            return 7.0
        else:
            return 5.0

    def _score_length(self, hook: str) -> float:
        """评分钩子长度

        钩子应该简洁有力
        """
        length = len(hook)
        min_len, max_len = self.ideal_hook_length

        if min_len <= length <= max_len:
            return 10.0
        elif length < min_len:
            # 太短
            ratio = length / min_len
            return 10.0 * ratio
        else:
            # 太长
            ratio = max_len / length
            return 10.0 * ratio

    def _generate_hook_suggestions(self, scores: dict[str, float], hook: str) -> list[str]:
        """生成钩子改进建议"""
        suggestions = []

        if scores["question"] < 6.0:
            suggestions.append("开头可以使用疑问句来引发读者好奇")

        if scores["number"] < 6.0:
            suggestions.append("加入具体数字或数据，增加可信度")

        if scores["contrast"] < 7.0:
            suggestions.append("使用对比词（但是、然而等）制造张力")

        if scores["identity"] < 6.0:
            suggestions.append("加入身份相关词汇，与目标读者建立连接")

        if scores["length"] < 7.0:
            suggestions.append("钩子长度应该控制在20-60字之间")

        return suggestions

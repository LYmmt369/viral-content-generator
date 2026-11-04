"""
合规检查评分器
v4.0 - 评估内容的合规性

作者: Sunnyeung
版本: 4.1.3
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from typing import Any, ClassVar

from .base import BaseScorer, ScoreResult


class ComplianceScorer(BaseScorer):
    """合规检查评分器

    评估内容是否符合平台规范和法律法规

    检查维度：
    1. 禁止话题 - 敏感内容
    2. 夸大宣传 - 虚假承诺
    3. 引流违规 - 过度营销
    4. 版权风险 - 侵权内容
    5. 语言规范 - 不当表达
    """

    # 禁止/敏感话题关键词（可根据需要扩展）
    BANNED_TOPICS: ClassVar = {
        "politics": ["政治", "选举", "抗议", "游行"],
        "violence": ["暴力", "恐怖", "杀人", "自杀"],
        "porn": ["色情", "淫秽", "裸聊"],
        "gambling": ["赌博", "博彩", "六合彩"],
        "drugs": ["毒品", "吸毒", "贩毒"],
        "fraud": ["诈骗", "传销", "非法集资"],
    }

    # 夸大宣传词汇
    HYPE_WORDS: ClassVar = [
        "第一", "唯一", "独家", "最", "绝对", "保证",
        "百分百", "100%", "零风险", "无风险", "必定"
    ]

    # 违规引流词
    SPAM_WORDS: ClassVar = [
        "加微信领", "私信领", "扫码领", "点击链接",
        "代购", "刷单", "兼职赚钱", "日赚"
    ]

    # 版权风险信号
    COPYRIGHT_RISKS: ClassVar = [
        "破解版", "免费下载", "盗版", "资源分享",
        "全套教程", "网盘资源"
    ]

    # 不当表达
    INAPPROPRIATE_LANGUAGE: ClassVar = [
        "傻", "蠢", "白痴", "垃圾", "废物",
        "滚", "去死", "该死"
    ]

    def __init__(self, threshold: float = 8.0):
        """初始化合规检查评分器

        Args:
            threshold: 通过阈值（默认更高，合规要求严格）
        """
        super().__init__(threshold)

    def score(self, content: str, context: dict[str, Any] | None = None) -> ScoreResult:
        """评分合规性

        Args:
            content: 内容全文
            context: 上下文（可选）

        Returns:
            评分结果
        """
        issues = []

        # 检查禁止话题
        banned_score, banned_issues = self._check_banned_topics(content)
        issues.extend(banned_issues)

        # 检查夸大宣传
        hype_score, hype_issues = self._check_hype(content)
        issues.extend(hype_issues)

        # 检查引流违规
        spam_score, spam_issues = self._check_spam(content)
        issues.extend(spam_issues)

        # 检查版权风险
        copyright_score, copyright_issues = self._check_copyright(content)
        issues.extend(copyright_issues)

        # 检查语言规范
        language_score, language_issues = self._check_language(content)
        issues.extend(language_issues)

        # 计算总分（任何严重问题都会导致不及格）
        if any("严重" in issue for issue in issues):
            total_score = 0.0
        else:
            total_score = (banned_score + hype_score + spam_score +
                          copyright_score + language_score) / 5

        return ScoreResult(
            score=total_score,
            level=self._calculate_level(total_score),
            details={"issues": issues, "issue_count": len(issues)},
            suggestions=issues,
            passed=self._check_passed(total_score)
        )

    def _check_banned_topics(self, content: str) -> tuple:
        """检查禁止话题"""
        issues = []
        score = 10.0

        for category, keywords in self.BANNED_TOPICS.items():
            for keyword in keywords:
                if keyword in content:
                    issues.append(f"严重：包含禁止话题词汇「{keyword}」（{category}）")
                    score = 0.0
                    break

        return score, issues

    def _check_hype(self, content: str) -> tuple:
        """检查夸大宣传"""
        issues = []
        found = []

        for word in self.HYPE_WORDS:
            if word in content:
                found.append(word)

        if found:
            if len(found) >= 3:
                issues.append(f"严重：大量夸大宣传词汇（{', '.join(found)}）")
                score = 0.0
            elif len(found) >= 2:
                issues.append(f"警告：多个夸大宣传词汇（{', '.join(found)}）")
                score = 5.0
            else:
                issues.append(f"注意：包含夸大宣传词汇「{found[0]}」")
                score = 7.0
        else:
            score = 10.0

        return score, issues

    def _check_spam(self, content: str) -> tuple:
        """检查引流违规"""
        issues = []
        found = []

        for word in self.SPAM_WORDS:
            if word in content:
                found.append(word)

        if found:
            issues.append(f"警告：疑似违规引流（{', '.join(found)}）")
            score = 5.0
        else:
            score = 10.0

        return score, issues

    def _check_copyright(self, content: str) -> tuple:
        """检查版权风险"""
        issues = []
        found = []

        for word in self.COPYRIGHT_RISKS:
            if word in content:
                found.append(word)

        if found:
            issues.append(f"注意：可能存在版权风险（{', '.join(found)}）")
            score = 7.0
        else:
            score = 10.0

        return score, issues

    def _check_language(self, content: str) -> tuple:
        """检查语言规范"""
        issues = []
        found = []

        for word in self.INAPPROPRIATE_LANGUAGE:
            if word in content:
                found.append(word)

        if found:
            issues.append(f"警告：包含不当语言（{', '.join(found)}）")
            score = 5.0
        else:
            score = 10.0

        return score, issues

    def get_banned_topics(self) -> dict[str, list[str]]:
        """获取禁止话题列表

        Returns:
            禁止话题字典
        """
        return self.BANNED_TOPICS.copy()

    def add_banned_keyword(self, category: str, keyword: str) -> None:
        """添加禁止关键词

        Args:
            category: 分类
            keyword: 关键词
        """
        if category not in self.BANNED_TOPICS:
            self.BANNED_TOPICS[category] = []
        self.BANNED_TOPICS[category].append(keyword)

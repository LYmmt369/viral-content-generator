"""
成交漏斗写作器
v4.0 - 根据成交目标生成内容结构

作者: Sunnyeung
版本: 4.1.4
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar


class ConversionGoal(Enum):
    """成交目标类型"""
    LIKES = "likes"        # 高赞内容
    COMMENTS = "comments"  # 高互动内容
    LEADS = "leads"        # 高线索内容
    SALES = "sales"        # 高成交内容


@dataclass
class ContentStructure:
    """内容结构配置"""
    opening_ratio: float = 0.15     # 开头占比
    body_ratio: float = 0.70         # 主体占比
    closing_ratio: float = 0.15      # 结尾占比

    opening_focus: str = ""          # 开头重点
    body_focus: str = ""             # 主体重点
    closing_focus: str = ""           # 结尾重点

    cta_style: str = ""              # CTA风格
    cta_density: str = "medium"      # CTA密度


class ConversionFunnel:
    """成交漏斗写作器

    功能：
    1. 根据成交目标确定内容结构
    2. 生成针对性的CTA策略
    3. 提供质量评分标准
    4. 优化内容呈现方式
    """

    # 目标对应的配置
    GOAL_CONFIGS: ClassVar[dict[ConversionGoal, ContentStructure]] = {
        ConversionGoal.LIKES: ContentStructure(
            opening_ratio=0.15,
            body_ratio=0.70,
            closing_ratio=0.15,
            opening_focus="观点冲击、反常识、颠覆认知",
            body_focus="情绪共鸣、金句密度高、情感节点多",
            closing_focus="总结观点、强化金句、引导点赞",
            cta_style="认同的点个赞、这段话对你有启发吗",
            cta_density="low",
        ),
        ConversionGoal.COMMENTS: ContentStructure(
            opening_ratio=0.20,
            body_ratio=0.60,
            closing_ratio=0.20,
            opening_focus="提出有争议的观点、明确站队空间、引导讨论",
            body_focus="多角度分析、留出反驳空间、设置互动钩子",
            closing_focus="总结不绝对、明确引导评论、开放式问题",
            cta_style="你怎么看这个问题、评论区留下你的观点",
            cta_density="high",
        ),
        ConversionGoal.LEADS: ContentStructure(
            opening_ratio=0.25,
            body_ratio=0.50,
            closing_ratio=0.25,
            opening_focus="击中目标用户痛点、展示深度理解、建立信任",
            body_focus="展示方法论、提供部分价值、制造知识缺口",
            closing_focus="免费工具诱饵、评论关键词、私信路径",
            cta_style="评论「咨询」获取详细方案、私信「资料」领取",
            cta_density="high",
        ),
        ConversionGoal.SALES: ContentStructure(
            opening_ratio=0.20,
            body_ratio=0.50,
            closing_ratio=0.30,
            opening_focus="展示问题严重性、量化损失、制造紧迫感",
            body_focus="独特方法论、案例背书、风险承诺",
            closing_focus="明确行动步骤、设置门槛、稀缺性+紧迫感",
            cta_style="限时优惠仅剩X个名额、点击下方链接立即购买",
            cta_density="very_high",
        ),
    }

    def __init__(self, goal: ConversionGoal = ConversionGoal.LEADS):
        """初始化成交漏斗

        Args:
            goal: 成交目标
        """
        self.goal = goal
        self.config = self.GOAL_CONFIGS.get(goal, self.GOAL_CONFIGS[ConversionGoal.LEADS])

    def get_content_structure(self) -> ContentStructure:
        """获取内容结构配置

        Returns:
            ContentStructure实例
        """
        return self.config

    def get_cta_suggestions(self) -> list[str]:
        """获取CTA建议列表

        Returns:
            CTA建议列表
        """
        base_ctas = {
            ConversionGoal.LIKES: [
                "认同的点个赞",
                "这段话对你有启发吗",
                "转发给需要的人",
                "让更多人看到",
            ],
            ConversionGoal.COMMENTS: [
                "你怎么看这个问题",
                "评论区留下你的观点",
                "同意还是不同意，说说理由",
                "有什么不同意见吗",
            ],
            ConversionGoal.LEADS: [
                "评论「咨询」获取详细方案",
                "私信「资料」领取XXX",
                "点击下方链接免费诊断",
                "添加微信深度沟通",
            ],
            ConversionGoal.SALES: [
                "限时优惠，仅剩X个名额",
                "现在购买立省XXX元",
                "点击下方链接立即购买",
                "今天下单享受专属优惠",
            ],
        }

        return base_ctas.get(self.goal, [])

    def get_quality_standards(self) -> dict[str, Any]:
        """获取质量标准

        Returns:
            质量标准字典
        """
        standards = {
            ConversionGoal.LIKES: {
                "观点犀利度": "≥8/10",
                "情绪共鸣度": "≥8/10",
                "金句密度": "每200字1个",
                "分享冲动": "≥8/10",
            },
            ConversionGoal.COMMENTS: {
                "争议性": "≥7/10",
                "讨论空间": "≥8/10",
                "互动钩子": "≥3个",
                "观点平衡": "不绝对化",
            },
            ConversionGoal.LEADS: {
                "痛点精准度": "≥9/10",
                "信任建立度": "≥8/10",
                "转化自然度": "≥8/10",
                "CTA明确度": "≥9/10",
            },
            ConversionGoal.SALES: {
                "需求匹配度": "≥9/10",
                "信任充分度": "≥8/10",
                "CTA明确度": "≥9/10",
                "紧迫感": "≥7/10",
            },
        }

        return standards.get(self.goal, {})

    def generate_content_outline(self, word_count: int = 1000) -> dict[str, int]:
        """生成内容大纲字数分配

        Args:
            word_count: 总字数

        Returns:
            各部分字数分配
        """
        return {
            "开头": int(word_count * self.config.opening_ratio),
            "主体": int(word_count * self.config.body_ratio),
            "结尾": int(word_count * self.config.closing_ratio),
        }

    def get_section_guidance(self, section: str) -> str:
        """获取各部分的写作指导

        Args:
            section: 部分名称（opening/body/closing）

        Returns:
            写作指导文字
        """
        guidance = {
            "opening": self.config.opening_focus,
            "body": self.config.body_focus,
            "closing": self.config.closing_focus,
        }

        return guidance.get(section, "")

    def optimize_for_goal(self, content: str) -> str:
        """根据目标优化内容

        Args:
            content: 原始内容

        Returns:
            优化后的内容
        """
        # 这里可以添加实际的优化逻辑
        # 例如：调整CTA位置、增加互动钩子等

        lines = content.split("\n")
        optimized = lines.copy()

        return "\n".join(optimized)

    @classmethod
    def from_string(cls, goal_str: str) -> "ConversionFunnel":
        """从字符串创建实例

        Args:
            goal_str: 目标字符串

        Returns:
            ConversionFunnel实例
        """
        try:
            goal = ConversionGoal(goal_str)
        except ValueError:
            goal = ConversionGoal.LEADS

        return cls(goal)


def create_conversion_funnel(goal: str = "leads") -> ConversionFunnel:
    """便捷函数：创建成交漏斗

    Args:
        goal: 成交目标字符串

    Returns:
        ConversionFunnel实例
    """
    return ConversionFunnel.from_string(goal)

# 兼容旧版流水线名称
ConversionFunnelWriter = ConversionFunnel


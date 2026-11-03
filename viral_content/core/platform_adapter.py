"""
多平台适配器
v4.0 - 一个热点输出全平台版本

作者: Sunnyeung
版本: 4.0.0
许可: MIT License
GitHub: https://github.com/Sunnyeung369/viral-content-generator
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar


class ContentPlatform(Enum):
    """内容平台枚举"""
    WECHAT = "wechat"  # 公众号
    VIDEO = "video"  # 视频号
    XIAOHONGSHU = "xiaohongshu"  # 小红书
    ZHIHU = "zhihu"  # 知乎
    DOUYIN = "douyin"  # 抖音
    BILIBILI = "bilibili"  # B站
    WEIBO = "weibo"  # 微博


@dataclass
class PlatformSpec:
    """平台规格"""
    name: str  # 平台名称
    content_type: str  # 内容类型（图文/短视频/长视频/短文）
    length_range: tuple[int, int]  # 长度范围（字数或秒）
    structure_hint: str  # 结构提示
    cta_style: str  # CTA风格
    tone_hint: str  # 语气提示
    visual_hint: str  # 视觉提示

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "content_type": self.content_type,
            "length_range": self.length_range,
            "structure_hint": self.structure_hint,
            "cta_style": self.cta_style,
            "tone_hint": self.tone_hint,
            "visual_hint": self.visual_hint,
        }


@dataclass
class PlatformPackage:
    """平台内容包"""
    platform: ContentPlatform
    content: str  # 生成的内容
    metadata: dict[str, Any] = field(default_factory=dict)  # 元数据
    score: float | None = None  # 评分（可选）


class PlatformAdapter:
    """多平台适配器

    功能：
    1. 为单个热点生成多平台内容
    2. 批量生成多平台内容包
    3. 平台规格管理
    """

    # 平台规格配置
    PLATFORM_SPECS: ClassVar[dict[ContentPlatform, PlatformSpec]] = {
        ContentPlatform.WECHAT: PlatformSpec(
            name="公众号",
            content_type="图文长文",
            length_range=(1500, 3000),
            structure_hint="完整清晰，分段明确，有标题和小标题",
            cta_style="文末设置明确的行动指引，可放置二维码/链接",
            tone_hint="专业但不失亲和，深度有启发",
            visual_hint="排版舒适，善用空行和配图"
        ),
        ContentPlatform.VIDEO: PlatformSpec(
            name="视频号",
            content_type="短视频",
            length_range=(30, 60),
            structure_hint="3秒抓人 → 主体干货 → 结尾CTA",
            cta_style="口播引导（点击下方链接），评论区置顶",
            tone_hint="口语化、有节奏、带情绪",
            visual_hint="真人出镜，场景丰富"
        ),
        ContentPlatform.XIAOHONGSHU: PlatformSpec(
            name="小红书",
            content_type="图文/短视频",
            length_range=(500, 1000),
            structure_hint="标题吸引 → 场景描述 → 真实体验 → 推荐理由",
            cta_style="自然种草，评论引导，私信/收藏",
            tone_hint="姐妹感、温暖、真诚",
            visual_hint="精致图片/真实生活"
        ),
        ContentPlatform.ZHIHU: PlatformSpec(
            name="知乎",
            content_type="长文回答",
            length_range=(1000, 3000),
            structure_hint="问题分析 → 多维解答 → 案例支撑 → 总结建议",
            cta_style="专业形象建立，引导私信咨询",
            tone_hint="专业但不晦涩，数据支撑",
            visual_hint="清晰层次，善用小标题"
        ),
        ContentPlatform.DOUYIN: PlatformSpec(
            name="抖音",
            content_type="短视频",
            length_range=(15, 60),
            structure_hint="3秒抓人 → 快节奏内容 → 反转/高潮 → CTA",
            cta_style="强调紧迫感，引导点击购物车，评论区互动",
            tone_hint="节奏快、情绪饱满、有记忆点",
            visual_hint="动态、冲击、创意"
        ),
        ContentPlatform.BILIBILI: PlatformSpec(
            name="B站",
            content_type="中长视频",
            length_range=(300, 900),  # 5-15分钟
            structure_hint="引入 → 展开 → 高潮 → 总结",
            cta_style="视频中自然植入，引导三连，评论区置顶链接",
            tone_hint="有趣但不失专业，有梗",
            visual_hint="动画、图表、弹幕互动"
        ),
        ContentPlatform.WEIBO: PlatformSpec(
            name="微博",
            content_type="短文",
            length_range=(140, 500),
            structure_hint="金句开头 → 简短论证 → 观点总结",
            cta_style="引导转发/评论，观点站队",
            tone_hint="犀利、有态度、易转发",
            visual_hint="参与热点话题，配图重要"
        ),
    }

    def __init__(self):
        """初始化多平台适配器"""
        self.supported_platforms = list(self.PLATFORM_SPECS.keys())

    def get_platform_spec(self, platform: ContentPlatform) -> PlatformSpec:
        """获取平台规格

        Args:
            platform: 平台枚举

        Returns:
            平台规格
        """
        return self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS[ContentPlatform.WECHAT])

    def generate_package(
        self,
        topic: str,
        platforms: list[ContentPlatform] | None = None,
        generator_func: Callable[..., str] | None = None,
        **kwargs
    ) -> list[PlatformPackage]:
        """生成多平台内容包

        Args:
            topic: 热点话题
            platforms: 目标平台列表（None表示全部平台）
            generator_func: 生成函数（实际调用AI生成）
            **kwargs: 其他参数（风格、账号等）

        Returns:
            平台内容包列表
        """
        if platforms is None:
            platforms = self.supported_platforms

        packages = []

        for platform in platforms:
            spec = self.get_platform_spec(platform)

            # 构建平台专属提示
            platform_prompt = self._build_platform_prompt(topic, spec, **kwargs)

            # 如果提供了生成函数，调用生成
            if generator_func:
                content = generator_func(platform_prompt, platform, **kwargs)
            else:
                # 否则返回提示供后续生成
                content = platform_prompt

            package = PlatformPackage(
                platform=platform,
                content=content,
                metadata={
                    "spec": spec.to_dict(),
                    "topic": topic,
                }
            )

            packages.append(package)

        return packages

    def _build_platform_prompt(
        self,
        topic: str,
        spec: PlatformSpec,
        style: str | None = None,
        account: dict[str, Any] | None = None,
        goal: str | None = None,
        **kwargs
    ) -> str:
        """构建平台专属提示词

        Args:
            topic: 话题
            spec: 平台规格
            style: 风格配置
            account: 账号配置
            goal: 成交目标
            **kwargs: 其他参数

        Returns:
            平台专属提示词
        """
        parts = []

        # 话题
        parts.append(f"# 话题：{topic}\n")

        # 平台信息
        parts.append(f"## 目标平台：{spec.name}")
        parts.append(f"- 内容类型：{spec.content_type}")
        parts.append(f"- 建议长度：{spec.length_range[0]}-{spec.length_range[1]}")
        parts.append(f"- 结构提示：{spec.structure_hint}")
        parts.append(f"- CTA风格：{spec.cta_style}")
        parts.append(f"- 语气提示：{spec.tone_hint}")
        parts.append(f"- 视觉提示：{spec.visual_hint}")

        # 风格配置
        if style:
            parts.append("\n## 风格配置")
            parts.append(f"- 风格：{style}")

        # 账号配置
        if account:
            parts.append("\n## 账号定位")
            parts.append(f"- 账号：{account.get('name', '')}")
            parts.append(f"- 定位：{account.get('identity', '')}")

        # 成交目标
        if goal:
            parts.append("\n## 成交目标")
            parts.append(f"- 目标：{goal}")

        # 生成指令
        parts.append("\n## 生成要求")
        parts.append(f"请根据以上配置，为{spec.name}平台创作一篇关于「{topic}」的{spec.content_type}内容。")
        parts.append(f"内容长度控制在{spec.length_range[0]}-{spec.length_range[1]}之间，")
        parts.append(f"遵循{spec.structure_hint}的结构，")
        parts.append(f"结尾使用{spec.cta_style}的CTA风格。")

        return "\n".join(parts)

    def convert_to_platform(
        self,
        content: str,
        from_platform: ContentPlatform,
        to_platform: ContentPlatform
    ) -> str:
        """将内容从一个平台转换到另一个平台

        Args:
            content: 原始内容
            from_platform: 原平台
            to_platform: 目标平台

        Returns:
            转换后的内容提示
        """
        from_spec = self.get_platform_spec(from_platform)
        to_spec = self.get_platform_spec(to_platform)

        conversion_prompt = f"""# 内容转换任务

## 原平台：{from_spec.name}
- 内容类型：{from_spec.content_type}
- 原始长度范围：{from_spec.length_range[0]}-{from_spec.length_range[1]}

## 目标平台：{to_spec.name}
- 内容类型：{to_spec.content_type}
- 目标长度范围：{to_spec.length_range[0]}-{to_spec.length_range[1]}
- 结构提示：{to_spec.structure_hint}
- CTA风格：{to_spec.cta_style}
- 语气提示：{to_spec.tone_hint}

## 原始内容
{content}

## 转换要求
请将上述内容从{from_spec.name}转换适配到{to_spec.name}平台：
1. 调整内容长度到{to_spec.length_range[0]}-{to_spec.length_range[1]}范围
2. 按照{to_spec.structure_hint}重新组织结构
3. 使用{to_spec.tone_hint}的语气
4. 结尾使用{to_spec.cta_style}的CTA风格
5. 保留核心观点和价值，改变呈现形式
"""

        return conversion_prompt

    def batch_convert(
        self,
        content: str,
        from_platform: ContentPlatform,
        to_platforms: list[ContentPlatform] | None = None
    ) -> list[PlatformPackage]:
        """批量转换内容到多个平台

        Args:
            content: 原始内容
            from_platform: 原平台
            to_platforms: 目标平台列表

        Returns:
            转换后的内容包列表
        """
        if to_platforms is None:
            to_platforms = [p for p in self.supported_platforms if p != from_platform]

        packages = []

        for platform in to_platforms:
            converted_prompt = self.convert_to_platform(content, from_platform, platform)

            package = PlatformPackage(
                platform=platform,
                content=converted_prompt,
                metadata={
                    "from_platform": from_platform.value,
                    "conversion": True,
                }
            )

            packages.append(package)

        return packages

    def get_recommended_platforms(
        self,
        topic: str,
        goal: str = "leads"
    ) -> list[ContentPlatform]:
        """根据话题和目标推荐平台

        Args:
            topic: 话题
            goal: 成交目标

        Returns:
            推荐平台列表（按优先级排序）
        """
        # 根据目标推荐平台
        if goal == "sales":
            # 成交优先：视频号、抖音、小红书
            return [
                ContentPlatform.VIDEO,
                ContentPlatform.DOUYIN,
                ContentPlatform.XIAOHONGSHU,
            ]
        elif goal == "leads":
            # 线索优先：公众号、知乎、视频号
            return [
                ContentPlatform.WECHAT,
                ContentPlatform.ZHIHU,
                ContentPlatform.VIDEO,
            ]
        elif goal == "comments":
            # 互动优先：微博、抖音、小红书
            return [
                ContentPlatform.WEIBO,
                ContentPlatform.DOUYIN,
                ContentPlatform.XIAOHONGSHU,
            ]
        else:  # likes
            # 点赞优先：小红书、抖音、视频号
            return [
                ContentPlatform.XIAOHONGSHU,
                ContentPlatform.DOUYIN,
                ContentPlatform.VIDEO,
            ]

    def create_content_matrix(
        self,
        topic: str,
        primary_platform: ContentPlatform,
        generator_func: Callable[..., str] | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """创建内容矩阵

        以主平台为核心，自动适配到其他平台

        Args:
            topic: 话题
            primary_platform: 主平台
            generator_func: 生成函数
            **kwargs: 其他参数

        Returns:
            内容矩阵字典
        """
        matrix = {
            "topic": topic,
            "primary_platform": primary_platform.value,
            "packages": {},
        }

        # 生成主平台内容
        if generator_func:
            primary_package = self.generate_package(
                topic=topic,
                platforms=[primary_platform],
                generator_func=generator_func,
                **kwargs
            )[0]
            matrix["packages"][primary_platform.value] = primary_package

            # 以主平台内容为基础，转换到其他平台
            secondary_platforms = [p for p in self.supported_platforms if p != primary_platform]
            converted_packages = self.batch_convert(
                content=primary_package.content,
                from_platform=primary_platform,
                to_platforms=secondary_platforms
            )

            for pkg in converted_packages:
                # 如果提供了生成函数，实际生成转换后的内容
                if generator_func:
                    actual_content = generator_func(pkg.content, pkg.platform, **kwargs)
                    pkg.content = actual_content

                matrix["packages"][pkg.platform.value] = pkg

        return matrix


# 全局单例
_adapter_instance: PlatformAdapter | None = None


def get_platform_adapter() -> PlatformAdapter:
    """获取平台适配器单例

    Returns:
        PlatformAdapter实例
    """
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = PlatformAdapter()
    return _adapter_instance

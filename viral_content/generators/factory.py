"""
生成器工厂

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""


from viral_content.exceptions.custom import ValidationError
from viral_content.generators.base import ContentGenerator
from viral_content.generators.claude import ClaudeGenerator
from viral_content.generators.gemini import GeminiGenerator
from viral_content.generators.openai import OpenAIGenerator
from viral_content.models.generation import GenerationConfig

# 生成器映射表
GENERATOR_MAP: dict[str, type[ContentGenerator]] = {
    'openai': OpenAIGenerator,
    'claude': ClaudeGenerator,
    'gemini': GeminiGenerator,
}


def create_generator(
    platform: str = 'claude',
    api_key: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
    config: GenerationConfig | None = None,
    **kwargs
) -> ContentGenerator:
    """
    创建生成器实例（简化版）

    Args:
        platform: AI平台（openai/claude/gemini）
        api_key: API密钥
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大token数
        config: 完整配置对象（可选）
        **kwargs: 其他参数

    Returns:
        ContentGenerator: 生成器实例

    Raises:
        ValidationError: 当平台不支持时
    """
    if config is None:
        # 从参数创建配置
        config = GenerationConfig(
            topic="",  # 将在使用时设置
            platform=platform,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    generator_class = GENERATOR_MAP.get(config.platform)
    if generator_class is None:
        raise ValidationError(
            f"不支持的平台: {config.platform}，"
            f"支持的平台: {list(GENERATOR_MAP.keys())}"
        )
    return generator_class(config)


# 保留原始函数以向后兼容
def create_generator_from_config(config: GenerationConfig) -> ContentGenerator:
    """
    从配置对象创建生成器实例

    Args:
        config: 生成配置

    Returns:
        ContentGenerator: 生成器实例

    Raises:
        ValidationError: 当平台不支持时
    """
    return create_generator(config=config)


def register_generator(platform: str, generator_class: type[ContentGenerator]) -> None:
    """
    注册新的生成器

    Args:
        platform: 平台名称
        generator_class: 生成器类
    """
    GENERATOR_MAP[platform] = generator_class


class GeneratorFactory:
    """兼容旧版流水线的生成器工厂外观。"""
    create = staticmethod(create_generator)
    create_from_config = staticmethod(create_generator_from_config)

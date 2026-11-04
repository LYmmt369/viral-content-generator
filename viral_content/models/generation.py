"""
生成配置和结果数据模型

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..trends.base import Trend
    from .account import Account
    from .offer import Offer
    from .style import Style


@dataclass
class GenerationConfig:
    """生成配置（v4.0 扩展版）"""
    # 基础参数（v3.1 兼容）
    topic: str
    style: str = '老司机风格'
    word_count: int = 6000
    platform: str = 'openai'  # AI 平台
    api_key: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 16384
    stream: bool = False
    output_path: str | None = None


    # v4.0 新增参数
    account_path: str | None = None  # 账号配置文件路径
    offer_path: str | None = None  # 产品配置文件路径
    goal: str = 'likes'  # 成交目标: likes, comments, leads, sales, consult
    content_platforms: list[str] = field(default_factory=list)  # 内容输出平台
    style_mix: str | None = None  # 风格混合 (如: "global:tech_explainer,china:business_savage")
    variants: int = 1  # 生成变体数量

    # 热点输入（手动或自动）
    trend_input: str | None = None  # 热点输入（JSON/YAML 字符串）
    trend_file: str | None = None  # 热点文件路径

    # 评分选项
    enable_scoring: bool = False  # 是否启用自动评分
    show_revision_advice: bool = True  # 是否显示修改建议

    # 输出选项
    save_all_variants: bool = False  # 是否保存所有变体
    output_format: str = 'markdown'  # 输出格式: markdown, json, html

    # Direct drafting uses explicit prompts and a single attempt, without the legacy Skill.
    system_prompt: str | None = None
    user_prompt: str | None = None
    max_attempts: int = 3
    timeout: float = 60.0


@dataclass
class GenerationResult:
    """生成结果（v4.0 扩展版）"""
    content: str
    platform: str  # AI 平台
    model: str
    tokens_used: int = 0
    duration_seconds: float = 0.0
    truncated: bool = False

    # v4.0 新增字段
    variant_index: int = 0  # 变体索引
    content_platform: str | None = None  # 内容输出平台
    goal: str | None = None  # 成交目标

    # 评分结果
    scores: dict[str, float] | None = None
    revision_advice: list[str] | None = None

    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)

    # 保存路径
    saved_path: str | None = None


@dataclass
class GenerationRequest:
    """生成请求（用于 Pipeline）"""
    config: GenerationConfig
    account: 'Account | None' = None
    offer: 'Offer | None' = None
    styles: list['Style'] | None = None
    trends: list['Trend'] | None = None

    # 编译后的提示词
    compiled_prompt: str | None = None


@dataclass
class GenerationOutput:
    """生成输出（多平台/多变体）"""
    request: GenerationRequest
    results: list[GenerationResult]

    # 汇总信息
    total_tokens_used: int = 0
    total_duration: float = 0.0
    average_score: float = 0.0

    # 输出目录
    output_dir: Path | None = None

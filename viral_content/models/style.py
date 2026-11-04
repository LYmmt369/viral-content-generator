"""
风格基因数据模型

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StyleDNA:
    """风格基因卡"""
    # 基本信息
    id: str = ""
    label: str = ""
    category: str = ""
    region: str = "global"
    reference_level: str = "publicly observable style traits only"

    # 风格 DNA 核心
    style_dna: dict[str, Any] = field(default_factory=dict)

    # 钩子模式
    hook_patterns: list[str] = field(default_factory=list)

    # 逻辑模式
    logic_patterns: list[str] = field(default_factory=list)

    # 情绪曲线
    emotion_curve: dict[str, str] = field(default_factory=dict)

    # 避免事项
    avoid: list[str] = field(default_factory=list)

    # 转化适配
    conversion_fit: dict[str, Any] = field(default_factory=dict)

    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StyleMix:
    """风格混合配置"""
    styles: list[StyleDNA] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)
    combination_rules: dict[str, Any] = field(default_factory=dict)


# 简化别名（兼容旧版与流水线类型名）
Style = StyleDNA
StyleProfile = StyleDNA

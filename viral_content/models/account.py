"""
账号指纹数据模型

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AccountFingerprint:
    """账号指纹配置"""
    # 基本信息
    name: str = ""
    identity: str = ""  # 专业定位（一句话）

    # 目标用户
    target_audience: list[str] = field(default_factory=list)

    # 用户痛点
    pain_points: list[str] = field(default_factory=list)

    # 权威资产
    authority_assets: list[str] = field(default_factory=list)

    # 商业目标
    business_goal: dict[str, Any] = field(default_factory=dict)

    # 产品阶梯
    offer_ladder: dict[str, str] = field(default_factory=dict)

    # 语气限制
    tone_constraints: list[str] = field(default_factory=list)

    # 内容限制
    content_constraints: list[str] = field(default_factory=list)

    # 平台偏好
    platform_preferences: dict[str, list[str]] = field(default_factory=dict)

    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)


# 简化别名
Account = AccountFingerprint

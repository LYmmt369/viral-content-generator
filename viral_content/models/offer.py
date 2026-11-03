"""
产品服务数据模型

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OfferConfig:
    """产品服务配置"""
    # 基本信息
    name: str = ""
    type: str = "consulting"  # consulting, course, product, service
    category: str = ""

    # 价格阶梯
    pricing: dict[str, str] = field(default_factory=dict)

    # 核心卖点
    unique_value_proposition: list[str] = field(default_factory=list)

    # 成交门槛
    commitment_required: dict[str, str] = field(default_factory=dict)

    # 目标客户匹配
    ideal_customer_profile: list[str] = field(default_factory=list)

    # 转化路径
    conversion_path: dict[str, Any] = field(default_factory=dict)

    # 信任背书
    social_proof: dict[str, list] = field(default_factory=dict)

    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)


# 简化别名
Offer = OfferConfig

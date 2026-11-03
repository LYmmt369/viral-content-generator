"""
Viral Content Generator v4.0
热点风格成交引擎

作者: Sunnyeung
版本: 4.1.0
许可: MIT License
GitHub: https://github.com/Sunnyeung369/viral-content-generator
"""

__version__ = "4.1.0"
__author__ = "Sunnyeung"

# 核心模块
# 配置
from .config import Settings, get_settings
from .core import (
    AccountFingerprint,
    ConversionFunnel,
    ConversionGoal,
    PipelineBuilder,
    PlatformAdapter,
    PromptCompiler,
    StyleMixer,
    ViralContentPipeline,
)
from .core.platform_adapter import ContentPlatform as Platform

# 数据模型
from .models import (
    Account,
    GenerationConfig,
    GenerationResult,
    Offer,
    StyleProfile,
    Trend,
)

# 工具
from .utils import FileHandler, Validator, YamlFileLoader

__all__ = [
    "Account",
    "AccountFingerprint",
    "ConversionFunnel",
    "ConversionGoal",
    # 工具
    "FileHandler",
    # 数据模型
    "GenerationConfig",
    "GenerationResult",
    "Offer",
    "PipelineBuilder",
    "Platform",
    "PlatformAdapter",
    # 核心模块
    "PromptCompiler",
    "Settings",
    "StyleMixer",
    "StyleProfile",
    "Trend",
    "Validator",
    # 核心流程
    "ViralContentPipeline",
    "YamlFileLoader",
    "__author__",
    # 版本
    "__version__",
    # 配置
    "get_settings",
]

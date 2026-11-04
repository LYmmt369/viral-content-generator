"""
核心引擎模块
v4.0

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from .account_fingerprint import AccountFingerprint, load_account
from .conversion_funnel import (
    ContentStructure,
    ConversionFunnel,
    ConversionGoal,
    create_conversion_funnel,
)
from .pipeline import PipelineBuilder, ViralContentPipeline
from .platform_adapter import (
    ContentPlatform,
    PlatformAdapter,
    PlatformPackage,
    PlatformSpec,
    get_platform_adapter,
)
from .prompt_compiler import PromptCompiler, get_compiler
from .style_mixer import StyleMixer, get_style_mixer

__all__ = [
    # Account Fingerprint
    "AccountFingerprint",
    "ContentPlatform",
    "ContentStructure",
    # Conversion Funnel
    "ConversionFunnel",
    "ConversionGoal",
    "PipelineBuilder",
    # Platform Adapter
    "PlatformAdapter",
    "PlatformPackage",
    "PlatformSpec",
    # Prompt Compiler
    "PromptCompiler",
    # Style Mixer
    "StyleMixer",
    # Pipeline
    "ViralContentPipeline",
    "create_conversion_funnel",
    "get_compiler",
    "get_platform_adapter",
    "get_style_mixer",
    "load_account",
]

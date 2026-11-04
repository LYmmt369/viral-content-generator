"""
设置加载模块
v4.0 - 从YAML文件和环境变量加载配置

作者: Sunnyeung
版本: 4.1.3
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import logging
import os
from pathlib import Path
from typing import Any, ClassVar

import yaml

from ..exceptions.custom import ConfigurationError

logger = logging.getLogger(__name__)


class Settings:
    """全局设置管理器

    加载顺序（后加载覆盖先加载）：
    1. 默认配置
    2. 配置文件 (config.yaml)
    3. 环境变量
    4. 运行时传入
    """

    # 默认配置
    DEFAULTS: ClassVar[dict[str, Any]] = {
        # AI生成器配置
        "generator": {
            "provider": "openai",  # openai, claude, gemini
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 30,
        },

        # 路径配置
        "paths": {
            "data_dir": "data",
            "styles_dir": "data/styles",
            "accounts_dir": "data/accounts",
            "offers_dir": "data/offers",
            "trends_dir": "data/trends",
            "prompts_dir": "prompts",
            "output_dir": "outputs",
        },

        # 热点配置
        "trends": {
            "sources": ["google_trends", "tiktok", "douyin", "xiaohongshu"],
            "refresh_interval": 3600,  # 1小时
            "max_cache_age": 7200,  # 2小时
        },

        # 评分配置
        "scoring": {
            "enabled": True,
            "weights": {
                "hook": 0.2,
                "trust": 0.2,
                "value": 0.2,
                "interaction": 0.15,
                "conversion": 0.15,
                "trend_fit": 0.1,
            },
            "thresholds": {
                "minimum": 6.0,
                "good": 7.5,
                "excellent": 8.5,
            },
        },

        # 风格配置
        "styles": {
            "max_mix": 3,
            "default_fallback": "tech_explainer_global",
        },

        # 平台配置
        "platforms": {
            "default": "wechat",
            "emoji_support": {
                "wechat": True,
                "xiaohongshu": True,
                "douyin": True,
                "tiktok": True,
                "linkedin": False,
                "twitter": True,
            },
        },

        # 合规配置
        "compliance": {
            "enabled": True,
            "banned_topics_file": "data/trends/banned_topics.yaml",
            "min_age_check": False,
        },

        # 日志配置
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }

    def __init__(self, config_file: str | None = None):
        """初始化设置

        Args:
            config_file: 配置文件路径
        """
        self._config: dict[str, Any] = {}
        self._config_file: str | None = config_file

        # 加载配置
        self._load_defaults()
        if config_file:
            self._load_from_file(config_file)
        self._load_from_env()

        logger.info(f"Settings loaded (config_file={config_file})")

    def _load_defaults(self):
        """加载默认配置"""
        self._config = self._deep_copy(self.DEFAULTS)

    def _load_from_file(self, config_file: str):
        """从文件加载配置"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_file}")
                return

            with open(config_path, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f) or {}

            self._deep_merge(self._config, file_config)
            logger.info(f"Loaded config from {config_file}")

        except Exception as e:  # noqa: BLE001 - normalize boundary errors for stable CLI/API behavior
            raise ConfigurationError(f"Failed to load config file: {e}")

    def _load_from_env(self):
        """从环境变量加载配置"""
        env_mappings = {
            "VIRAL_PROVIDER": ["generator", "provider"],
            "VIRAL_MODEL": ["generator", "model"],
            "VIRAL_API_KEY": ["generator", "api_key"],
            "VIRAL_TEMPERATURE": ["generator", "temperature"],
            "VIRAL_MAX_TOKENS": ["generator", "max_tokens"],
            "VIRAL_DATA_DIR": ["paths", "data_dir"],
            "VIRAL_OUTPUT_DIR": ["paths", "output_dir"],
            "VIRAL_LOG_LEVEL": ["logging", "level"],
        }

        for env_key, config_path in env_mappings.items():
            value = os.getenv(env_key)
            if value is not None:
                self._set_nested_value(self._config, config_path, self._parse_env_value(value))

    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试转换为数字
        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        # 尝试转换为布尔
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False

        # 返回字符串
        return value

    def get(self, *keys: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            *keys: 配置路径（如 "generator", "provider"）
            default: 默认值

        Returns:
            配置值
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, *keys: str, value: Any):
        """设置配置值

        Args:
            *keys: 配置路径
            value: 新值
        """
        self._set_nested_value(self._config, keys, value)

    def get_all(self) -> dict[str, Any]:
        """获取全部配置"""
        return self._deep_copy(self._config)

    def get_generator_config(self) -> dict[str, Any]:
        """获取生成器配置"""
        return self.get("generator", default={})

    def get_paths(self) -> dict[str, str]:
        """获取路径配置"""
        return self.get("paths", default={})

    def get_scoring_weights(self) -> dict[str, float]:
        """获取评分权重"""
        return self.get("scoring", "weights", default={})

    def is_compliance_enabled(self) -> bool:
        """是否启用合规检查"""
        return self.get("compliance", "enabled", default=True)

    def get_banned_topics_file(self) -> str | None:
        """获取禁止话题文件路径"""
        return self.get("compliance", "banned_topics_file")

    def get_platform_config(self, platform: str) -> dict[str, Any]:
        """获取平台特定配置"""
        emoji_support = self.get("platforms", "emoji_support", default={})
        return {
            "emoji_support": emoji_support.get(platform, True),
        }

    @staticmethod
    def _deep_copy(obj: Any) -> Any:
        """深拷贝"""
        import copy
        return copy.deepcopy(obj)

    @staticmethod
    def _deep_merge(base: dict[str, Any], update: dict[str, Any]):
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Settings._deep_merge(base[key], value)
            else:
                base[key] = value

    @staticmethod
    def _set_nested_value(config: dict[str, Any], path: list[str], value: Any):
        """设置嵌套值"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value


# 全局设置实例
_global_settings: Settings | None = None


def get_settings(config_file: str | None = None) -> Settings:
    """获取全局设置实例

    Args:
        config_file: 配置文件路径（仅首次调用有效）

    Returns:
        设置实例
    """
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings(config_file)
    return _global_settings


def reload_settings(config_file: str | None = None) -> Settings:
    """重新加载设置

    Args:
        config_file: 配置文件路径

    Returns:
        新的设置实例
    """
    global _global_settings
    _global_settings = Settings(config_file)
    return _global_settings

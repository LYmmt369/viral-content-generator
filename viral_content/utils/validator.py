"""
参数验证模块
v4.0 - 验证输入参数和配置

作者: Sunnyeung
版本: 4.1.3
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import logging
import re
from pathlib import Path
from typing import Any, ClassVar

from ..core.conversion_funnel import ConversionGoal
from ..core.platform_adapter import ContentPlatform as Platform
from ..exceptions.custom import ValidationError

logger = logging.getLogger(__name__)


class Validator:
    """参数验证器"""

    # 邮箱正则
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # URL正则
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    # 平台名称
    VALID_PLATFORMS: ClassVar[set[str]] = {p.value for p in Platform}

    # 成交目标
    VALID_GOALS: ClassVar[set[str]] = {g.value for g in ConversionGoal}

    @staticmethod
    def validate_required(value: Any, field_name: str = "value"):
        """验证必需参数"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} is required")

    @staticmethod
    def validate_email(email: str, field_name: str = "email"):
        """验证邮箱格式"""
        if not Validator.EMAIL_PATTERN.match(email):
            raise ValidationError(f"Invalid {field_name} format: {email}")

    @staticmethod
    def validate_url(url: str, field_name: str = "url"):
        """验证URL格式"""
        if not Validator.URL_PATTERN.match(url):
            raise ValidationError(f"Invalid {field_name} format: {url}")

    @staticmethod
    def validate_platform(platform: str | Platform):
        """验证平台名称"""
        platform_value = platform.value if isinstance(platform, Platform) else platform
        if platform_value not in Validator.VALID_PLATFORMS:
            raise ValidationError(
                f"Invalid platform: {platform}. "
                f"Valid options: {', '.join(Validator.VALID_PLATFORMS)}"
            )

    @staticmethod
    def validate_goal(goal: str | ConversionGoal):
        """验证成交目标"""
        goal_value = goal.value if isinstance(goal, ConversionGoal) else goal
        if goal_value not in Validator.VALID_GOALS:
            raise ValidationError(
                f"Invalid conversion goal: {goal}. "
                f"Valid options: {', '.join(Validator.VALID_GOALS)}"
            )

    @staticmethod
    def validate_file_path(
        path: str,
        must_exist: bool = True,
        expected_extension: str | None = None,
        field_name: str = "file"
    ):
        """验证文件路径"""
        file_path = Path(path)

        if must_exist and not file_path.exists():
            raise ValidationError(f"{field_name} does not exist: {path}")

        if expected_extension and file_path.suffix.lower() != expected_extension.lower():
            raise ValidationError(
                f"{field_name} must have {expected_extension} extension: {path}"
            )

    @staticmethod
    def validate_style_mix(styles: list[str], max_styles: int = 3):
        """验证风格组合"""
        if not styles:
            raise ValidationError("At least one style must be specified")

        if len(styles) > max_styles:
            raise ValidationError(
                f"Maximum {max_styles} styles allowed, got {len(styles)}"
            )

        # 检查重复
        if len(styles) != len(set(styles)):
            raise ValidationError("Duplicate styles in mix")

    @staticmethod
    def validate_topic(topic: str, min_length: int = 5):
        """验证话题"""
        if not topic or len(topic.strip()) < min_length:
            raise ValidationError(
                f"Topic must be at least {min_length} characters"
            )

    @staticmethod
    def validate_price(price: float | str, field_name: str = "price"):
        """验证价格"""
        try:
            price_value = float(price) if isinstance(price, str) else price
            if price_value < 0:
                raise ValidationError(f"{field_name} must be non-negative")
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid {field_name}: {price}")

    @staticmethod
    def validate_config_dict(config: dict[str, Any], required_keys: list[str]):
        """验证配置字典"""
        missing_keys = [k for k in required_keys if k not in config]
        if missing_keys:
            raise ValidationError(
                f"Missing required keys in config: {', '.join(missing_keys)}"
            )


class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate_account_config(config: dict[str, Any]):
        """验证账号配置"""
        required_fields = ["name", "identity"]
        Validator.validate_config_dict(config, required_fields)

        # 验证目标用户
        if "target_audience" in config and not isinstance(config["target_audience"], list):
            raise ValidationError("target_audience must be a list")

        # 验证成交目标
        if "business_goal" in config:
            goal = config["business_goal"]
            if isinstance(goal, dict) and "primary" not in goal:
                raise ValidationError("business_goal must have 'primary' field")

    @staticmethod
    def validate_offer_config(config: dict[str, Any]):
        """验证产品配置"""
        required_fields = ["name", "type"]
        Validator.validate_config_dict(config, required_fields)

        # 验证价格阶梯
        if "pricing" in config:
            pricing = config["pricing"]
            if isinstance(pricing, dict):
                for key, value in pricing.items():
                    Validator.validate_price(value, f"pricing.{key}")

        # 验证产品类型
        valid_types = {"consulting", "course", "product", "service"}
        offer_type = config.get("type")
        if offer_type not in valid_types:
            raise ValidationError(
                f"Invalid offer type: {offer_type}. "
                f"Valid types: {', '.join(valid_types)}"
            )

    @staticmethod
    def validate_style_config(config: dict[str, Any]):
        """验证风格配置"""
        required_fields = ["id", "label", "style_dna"]
        Validator.validate_config_dict(config, required_fields)

        # 验证style_dna
        if "style_dna" in config:
            style_dna = config["style_dna"]
            if not isinstance(style_dna, dict):
                raise ValidationError("style_dna must be a dictionary")


class GenerationConfigValidator:
    """生成配置验证器"""

    @staticmethod
    def validate(config: Any):
        """验证生成配置"""
        if config is None:
            raise ValidationError("Generation config cannot be None")

        # 验证provider
        if hasattr(config, 'provider'):
            valid_providers = {"openai", "claude", "gemini"}
            if config.provider not in valid_providers:
                raise ValidationError(
                    f"Invalid provider: {config.provider}. "
                    f"Valid options: {', '.join(valid_providers)}"
                )

        # 验证temperature
        if hasattr(config, 'temperature'):
            temp = config.temperature
            if temp is not None and (temp < 0 or temp > 2):
                raise ValidationError(f"Temperature must be between 0 and 2, got {temp}")

        # 验证max_tokens
        if hasattr(config, 'max_tokens'):
            tokens = config.max_tokens
            if tokens is not None and tokens <= 0:
                raise ValidationError(f"max_tokens must be positive, got {tokens}")


class TrendValidator:
    """热点数据验证器"""

    @staticmethod
    def validate_trend_dict(trend: dict[str, Any]):
        """验证热点字典"""
        required_fields = ["topic", "source"]
        Validator.validate_config_dict(trend, required_fields)

        # 验证话题
        Validator.validate_topic(trend.get("topic", ""))

    @staticmethod
    def validate_trend_list(trends: list[dict[str, Any]]):
        """验证热点列表"""
        if not trends:
            raise ValidationError("Trend list cannot be empty")

        for i, trend in enumerate(trends):
            try:
                TrendValidator.validate_trend_dict(trend)
            except ValidationError as e:
                raise ValidationError(f"Trend at index {i} is invalid: {e}")


class InputSanitizer:
    """输入清洗器"""

    # 危险字符（防止注入攻击）
    DANGEROUS_CHARS: ClassVar[list[str]] = ['<', '>', '&', '\x00', '\n', '\r']

    @staticmethod
    def sanitize_string(value: str, max_length: int | None = None) -> str:
        """清洗字符串"""
        if not isinstance(value, str):
            return str(value)

        # 移除危险字符
        result = ''.join(c for c in value if c not in InputSanitizer.DANGEROUS_CHARS)

        # 限制长度
        if max_length and len(result) > max_length:
            result = result[:max_length]

        return result.strip()

    @staticmethod
    def sanitize_topic(topic: str) -> str:
        """清洗话题"""
        return InputSanitizer.sanitize_string(topic, max_length=500)

    @staticmethod
    def sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        """清洗元数据"""
        result = {}
        for key, value in metadata.items():
            # 清洗key
            clean_key = InputSanitizer.sanitize_string(str(key), max_length=50)

            # 清洗value
            if isinstance(value, str):
                clean_value = InputSanitizer.sanitize_string(value, max_length=1000)
            elif isinstance(value, (int, float, bool)):
                clean_value = value
            elif isinstance(value, list):
                clean_value = [
                    InputSanitizer.sanitize_string(str(v), max_length=500)
                    for v in value
                ][:100]  # 限制列表长度
            elif isinstance(value, dict):
                clean_value = InputSanitizer.sanitize_metadata(value)
            else:
                clean_value = str(value)

            result[clean_key] = clean_value

        return result

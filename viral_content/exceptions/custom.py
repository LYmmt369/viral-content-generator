"""
自定义异常类

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""


class ViralContentError(Exception):
    """基础异常类"""


class SkillLoadError(ViralContentError):
    """Skill文件加载错误"""


class APIError(ViralContentError):
    """API调用错误"""


class ValidationError(ViralContentError):
    """参数验证错误"""


class ConfigError(ViralContentError):
    """配置错误"""


class AccountLoadError(ViralContentError):
    """账号配置加载错误"""


class OfferLoadError(ViralContentError):
    """产品配置加载错误"""


class StyleLoadError(ViralContentError):
    """风格配置加载错误"""


# 兼容旧版命名
ConfigurationError = ConfigError
GenerationError = APIError

FileOperationError = ViralContentError


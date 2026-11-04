"""
账号指纹引擎
v4.0 - 账号定位和目标用户管理

作者: Sunnyeung
版本: 4.1.4
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from pathlib import Path
from typing import Any

import yaml


class AccountFingerprint:
    """账号指纹配置管理器

    功能：
    1. 加载账号配置
    2. 验证配置完整性
    3. 提取账号定位信息
    4. 生成账号相关的提示词片段
    """

    def __init__(self, account_path: Path | None = None):
        """初始化账号指纹

        Args:
            account_path: 账号配置文件路径
        """
        self.account_path = Path(account_path) if account_path else None
        self._config: dict[str, Any] = {}
        self._accounts_dir: Path | None = None

        if account_path:
            self.load(account_path)

    @property
    def accounts_dir(self) -> Path:
        """获取账号配置目录"""
        if self._accounts_dir is None:
            from viral_content.config.constants import ACCOUNTS_DIR
            self._accounts_dir = ACCOUNTS_DIR
        return self._accounts_dir

    def load(self, account_path: Path | None = None) -> dict[str, Any]:
        """加载账号配置

        Args:
            account_path: 账号配置文件路径

        Returns:
            账号配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置格式错误
        """
        if account_path:
            self.account_path = Path(account_path)

        if self.account_path is None:
            raise ValueError("未指定账号配置文件路径")

        if not self.account_path.exists():
            # 尝试在accounts_dir中查找
            default_path = self.accounts_dir / self.account_path.name
            if default_path.exists():
                self.account_path = default_path
            else:
                raise FileNotFoundError(f"账号配置文件不存在: {self.account_path}")

        with open(self.account_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"YAML解析错误: {e}")

        if not data or "account" not in data:
            raise ValueError("账号配置缺少'account'字段")

        self._config = data["account"]
        return self._config

    def validate(self) -> list[str]:
        """验证配置完整性

        Returns:
            错误列表，空列表表示验证通过
        """
        errors = []

        required_fields = ["name", "identity"]
        for field in required_fields:
            if field not in self._config or not self._config[field]:
                errors.append(f"缺少必需字段: {field}")

        return errors

    @property
    def name(self) -> str:
        """账号名称"""
        return self._config.get("name", "")

    @property
    def identity(self) -> str:
        """账号定位"""
        return self._config.get("identity", "")

    @property
    def target_audience(self) -> list[str]:
        """目标用户"""
        return self._config.get("target_audience", [])

    @property
    def pain_points(self) -> list[str]:
        """用户痛点"""
        return self._config.get("pain_points", [])

    @property
    def authority_assets(self) -> list[str]:
        """权威资产"""
        return self._config.get("authority_assets", [])

    @property
    def business_goal(self) -> dict[str, Any]:
        """商业目标"""
        return self._config.get("business_goal", {})

    @property
    def offer_ladder(self) -> dict[str, str]:
        """产品阶梯"""
        return self._config.get("offer_ladder", {})

    @property
    def tone_constraints(self) -> list[str]:
        """语气限制"""
        return self._config.get("tone_constraints", [])

    @property
    def content_constraints(self) -> list[str]:
        """内容限制"""
        return self._config.get("content_constraints", [])

    @property
    def platform_preferences(self) -> dict[str, list[str]]:
        """平台偏好"""
        return self._config.get("platform_preferences", {})

    def get_prompt_context(self) -> str:
        """获取账号相关的提示词上下文

        Returns:
            格式化的账号信息字符串
        """
        parts = []

        if self.name:
            parts.append(f"**账号名称**: {self.name}")

        if self.identity:
            parts.append(f"**账号定位**: {self.identity}")

        if self.target_audience:
            parts.append("**目标用户**:\n" + "\n".join(f"  - {u}" for u in self.target_audience[:3]))

        if self.pain_points:
            parts.append("**用户痛点**:\n" + "\n".join(f"  - {p}" for p in self.pain_points[:3]))

        if self.authority_assets:
            parts.append("**权威资产**:\n" + "\n".join(f"  - {a}" for a in self.authority_assets[:3]))

        if self.tone_constraints:
            parts.append("**语气要求**:\n" + "\n".join(f"  - {t}" for t in self.tone_constraints[:3]))

        return "\n\n".join(parts)

    def get_conversion_hints(self) -> dict[str, Any]:
        """获取成交相关的提示信息

        Returns:
            成交提示字典
        """
        conversion_prefs = self._config.get("conversion_preferences", {})

        return {
            "preferred_goal": conversion_prefs.get("preferred_goal", "leads"),
            "cta_style": conversion_prefs.get("cta_style", "价值先行 + 私信咨询"),
            "follow_up": conversion_prefs.get("follow_up", "自动发送资料包"),
        }

    @classmethod
    def load_default(cls) -> "AccountFingerprint":
        """加载默认账号配置

        Returns:
            AccountFingerprint实例
        """
        current_dir = Path(__file__).parent.parent.parent
        default_path = current_dir / "data" / "accounts" / "default_account.yaml"
        return cls(default_path)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典

        Returns:
            账号配置字典
        """
        return self._config.copy()


def load_account(account_path: Path | None = None) -> AccountFingerprint:
    """便捷函数：加载账号配置

    Args:
        account_path: 账号配置文件路径

    Returns:
        AccountFingerprint实例
    """
    return AccountFingerprint(account_path)

"""
提示词编译器
v4.0 - 动态编译提示词

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import json
from pathlib import Path
from string import Template
from typing import Any


class PromptCompiler:
    """提示词编译器

    功能：
    1. 加载markdown模板
    2. 编译变量
    3. 组合多个模板
    4. 输出完整提示词
    """

    def __init__(self, prompts_dir: Path | None = None):
        """初始化编译器

        Args:
            prompts_dir: 提示词模板目录，默认为项目prompts目录
        """
        if prompts_dir is None:
            # 默认使用项目根目录下的prompts目录
            from viral_content.config.constants import PROMPTS_DIR

            prompts_dir = PROMPTS_DIR

        self.prompts_dir = Path(prompts_dir)
        self._templates: dict[str, str] = {}
        self._cache: dict[str, str] = {}

    def load_template(self, template_name: str) -> str:
        """加载模板文件

        Args:
            template_name: 模板文件名（不含.md后缀）

        Returns:
            模板内容

        Raises:
            FileNotFoundError: 模板文件不存在
        """
        if template_name in self._templates:
            return self._templates[template_name]

        template_path = self.prompts_dir / f"{template_name}.md"

        if not template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        self._templates[template_name] = content
        return content

    def compile(self, template_name: str, variables: dict[str, Any] | None = None, **kwargs) -> str:
        """编译单个模板

        Args:
            template_name: 模板名称
            variables: 变量字典
            **kwargs: 额外的变量

        Returns:
            编译后的内容
        """
        template_content = self.load_template(template_name)

        # 合并变量
        all_vars = {}
        if variables:
            all_vars.update(variables)
        all_vars.update(kwargs)

        # 使用Template进行变量替换
        template = Template(template_content)
        try:
            compiled = template.substitute(all_vars)
        except KeyError:
            # 如果有变量缺失，使用safe_substitute
            template = Template(template_content)
            compiled = template.safe_substitute(all_vars)

        return compiled

    def compose(
        self,
        templates: list[str],
        variables: dict[str, Any] | None = None,
        separator: str = "\n\n---\n\n",
        **kwargs,
    ) -> str:
        """组合多个模板

        Args:
            templates: 模板名称列表
            variables: 共享变量字典
            separator: 模板间的分隔符
            **kwargs: 额外的变量

        Returns:
            组合后的完整内容
        """
        parts = []
        for template_name in templates:
            content = self.compile(template_name, variables, **kwargs)
            parts.append(content)

        return separator.join(parts)

    def build_system_prompt(
        self,
        topic: str,
        style_config: dict[str, Any] | None = None,
        account_config: dict[str, Any] | None = None,
        offer_config: dict[str, Any] | None = None,
        goal: str = "likes",
        platform: str = "wechat",
        **kwargs,
    ) -> str:
        """构建完整的系统提示词

        Args:
            topic: 热点话题
            style_config: 风格配置
            account_config: 账号配置
            offer_config: 产品配置
            goal: 成交目标
            platform: 目标平台
            **kwargs: 额外参数

        Returns:
            完整的系统提示词
        """
        # 在开头添加任务信息
        task_info = f"""# 任务信息

## 话题
{topic}

## 成交目标
{goal}

## 目标平台
{platform}

---

"""

        # 基础系统提示词
        base_prompt = task_info + self.compile("base_system")

        # 根据成交目标添加模板
        if goal in ["likes", "comments", "leads", "sales"]:
            goal_prompt = self.compile("conversion_goal")
            base_prompt += "\n\n## 成交目标策略\n\n"
            base_prompt += goal_prompt

        # 根据平台添加适配策略
        platform_mapping = {
            "wechat": "公众号",
            "video": "视频号",
            "xiaohongshu": "小红书",
            "zhihu": "知乎",
            "douyin": "抖音",
            "bilibili": "B站",
            "weibo": "微博",
        }

        platform_name = platform_mapping.get(platform, platform)
        platform_prompt = self.compile("platform_adapter")
        base_prompt += f"\n\n## 平台适配: {platform_name}\n\n"
        base_prompt += platform_prompt

        # 添加风格配置
        if style_config:
            style_desc = self._format_style_config(style_config)
            base_prompt += f"\n\n## 风格配置\n\n{style_desc}"

        # 添加账号配置
        if account_config:
            account_desc = self._format_account_config(account_config)
            base_prompt += f"\n\n## 账号定位\n\n{account_desc}"

        # 添加产品配置
        if offer_config:
            offer_desc = self._format_offer_config(offer_config)
            base_prompt += f"\n\n## 产品服务\n\n{offer_desc}"

        return base_prompt

    @staticmethod
    def _format_config(config: dict[str, Any]) -> str:
        """Preserve every supplied field, including lists and nested constraints."""
        return json.dumps(config, ensure_ascii=False, indent=2, allow_nan=False)

    def _format_style_config(self, style_config: dict[str, Any]) -> str:
        return self._format_config(style_config)

    def _format_account_config(self, account_config: dict[str, Any]) -> str:
        return self._format_config(account_config)

    def _format_offer_config(self, offer_config: dict[str, Any]) -> str:
        return self._format_config(offer_config)

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()

    def clear_templates(self):
        """清除已加载的模板"""
        self._templates.clear()
        self.clear_cache()


# 全局单例实例
_compiler_instance: PromptCompiler | None = None


def get_compiler(prompts_dir: Path | None = None) -> PromptCompiler:
    """获取编译器单例

    Args:
        prompts_dir: 提示词模板目录

    Returns:
        PromptCompiler实例
    """
    global _compiler_instance
    if _compiler_instance is None:
        _compiler_instance = PromptCompiler(prompts_dir)
    return _compiler_instance

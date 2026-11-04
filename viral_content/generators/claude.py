"""
Claude 生成器

作者: Sunnyeung
版本: 4.1.3
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import logging

from viral_content.exceptions.custom import APIError
from viral_content.generators.base import ContentGenerator
from viral_content.models.generation import GenerationResult

logger = logging.getLogger(__name__)


class ClaudeGenerator(ContentGenerator):
    """Claude生成器"""

    PLATFORM_NAME = "Claude"
    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def _setup_client(self) -> None:
        try:
            import anthropic
            options = {"api_key": self.config.api_key, "timeout": self.config.timeout}
            if self.config.max_attempts == 1:
                options["max_retries"] = 0
            self._client = anthropic.Anthropic(**options)
        except ImportError:
            raise APIError("未安装anthropic库，请运行: pip install anthropic")

    def _generate_internal(self, prompt: str) -> GenerationResult:
        try:
            if self.config.stream:
                return self._generate_stream(prompt)

            message = self._client.messages.create(
                model=self.model,
                max_tokens=self.config.max_tokens,
                system=self.skill_content,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens

            return GenerationResult(
                content=content,
                platform="claude",
                model=self.model,
                tokens_used=tokens_used,
                truncated=message.stop_reason == "max_tokens",
            )

        except Exception as e:  # noqa: BLE001 - SDK exception types vary by provider
            raise APIError(f"Claude API调用失败: {e}")

    def _generate_stream(self, prompt: str) -> GenerationResult:
        """流式生成"""
        print("\n[流式生成中...]\n")

        with self._client.messages.stream(
            model=self.model,
            max_tokens=self.config.max_tokens,
            system=self.skill_content,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            content = ""
            for text in stream.text_stream:
                content += text
                print(text, end='', flush=True)

        print()  # 换行

        message = stream.get_final_message()
        tokens_used = message.usage.input_tokens + message.usage.output_tokens

        return GenerationResult(
            content=content,
            platform="claude",
            model=self.model,
            tokens_used=tokens_used,
            truncated=message.stop_reason == "max_tokens",
        )

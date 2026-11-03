"""
OpenAI GPT 生成器

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import logging

from viral_content.exceptions.custom import APIError
from viral_content.generators.base import ContentGenerator
from viral_content.models.generation import GenerationResult

logger = logging.getLogger(__name__)


class OpenAIGenerator(ContentGenerator):
    """OpenAI GPT生成器"""

    PLATFORM_NAME = "OpenAI"
    DEFAULT_MODEL = "gpt-4o"

    def _generation_options(self) -> dict:
        if self.config.system_prompt is not None:
            return {"max_completion_tokens": self.config.max_tokens}
        return {"temperature": self.config.temperature, "max_tokens": self.config.max_tokens}

    def _setup_client(self) -> None:
        try:
            from openai import OpenAI
            options = {"api_key": self.config.api_key, "timeout": self.config.timeout}
            if self.config.max_attempts == 1:
                options["max_retries"] = 0
            self._client = OpenAI(**options)
        except ImportError:
            raise APIError("未安装openai库，请运行: pip install openai")

    def _generate_internal(self, prompt: str) -> GenerationResult:
        try:
            if self.config.stream:
                return self._generate_stream(prompt)

            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.skill_content},
                    {"role": "user", "content": prompt}
                ],
                **self._generation_options()
            )

            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            return GenerationResult(
                content=content,
                platform="openai",
                model=self.model,
                tokens_used=tokens_used,
                truncated=response.choices[0].finish_reason != "stop"
            )

        except Exception as e:  # noqa: BLE001 - SDK exception types vary by provider
            raise APIError(f"OpenAI API调用失败: {e}")

    def _generate_stream(self, prompt: str) -> GenerationResult:
        """流式生成"""
        print("\n[流式生成中...]\n")

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.skill_content},
                {"role": "user", "content": prompt}
            ],
            **self._generation_options(),
            stream=True
        )

        content = ""
        tokens_used = 0

        for chunk in response:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                content += text
                print(text, end='', flush=True)

            if chunk.usage:
                tokens_used = chunk.usage.total_tokens

        print()  # 换行

        return GenerationResult(
            content=content,
            platform="openai",
            model=self.model,
            tokens_used=tokens_used
        )

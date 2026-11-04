"""
Gemini 生成器

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import logging
import math

from viral_content.exceptions.custom import APIError
from viral_content.generators.base import ContentGenerator
from viral_content.models.generation import GenerationResult

logger = logging.getLogger(__name__)


class GeminiGenerator(ContentGenerator):
    """Gemini生成器"""

    PLATFORM_NAME = "Gemini"
    DEFAULT_MODEL = "gemini-3.8-flash"

    def _setup_client(self) -> None:
        try:
            from google import genai
            from google.genai import types

            self._types = types
            self._client = genai.Client(
                api_key=self.config.api_key,
                http_options=types.HttpOptions(
                    timeout=max(1, math.ceil(self.config.timeout * 1000)),
                    # ContentGenerator owns retries; disable the SDK retry layer.
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
        except ImportError:
            raise APIError("未安装google-genai库，请运行: pip install google-genai")

    def _generate_internal(self, prompt: str) -> GenerationResult:
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._types.GenerateContentConfig(
                    system_instruction=self.skill_content,
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                ),
            )
            content = response.text or ""

            usage = getattr(response, "usage_metadata", None)
            tokens_used = getattr(usage, "total_token_count", 0) or 0

            return GenerationResult(
                content=content,
                platform="gemini",
                model=self.model,
                tokens_used=tokens_used,
                truncated=any(
                    candidate.finish_reason == self._types.FinishReason.MAX_TOKENS
                    for candidate in (response.candidates or [])
                ),
            )

        except Exception as e:  # noqa: BLE001 - SDK exception types vary by provider
            raise APIError(f"Gemini API调用失败: {e}")

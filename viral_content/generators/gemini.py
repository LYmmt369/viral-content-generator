"""
Gemini 生成器

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


class GeminiGenerator(ContentGenerator):
    """Gemini生成器"""

    PLATFORM_NAME = "Gemini"
    DEFAULT_MODEL = "gemini-2.0-flash-exp"

    def _setup_client(self) -> None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.api_key)
            self._genai = genai
            self._model_client = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=self.skill_content
            )
        except ImportError:
            raise APIError("未安装google-generativeai库，请运行: pip install google-generativeai")

    def _generate_internal(self, prompt: str) -> GenerationResult:
        try:
            options = {"timeout": self.config.timeout}
            if self.config.max_attempts == 1:
                options["retry"] = None
            response = self._model_client.generate_content(
                prompt,
                generation_config={"max_output_tokens": self.config.max_tokens},
                request_options=options,
            )
            content = response.text

            # Gemini 不返回token使用情况，估算
            tokens_used = len(content) // 2  # 粗略估算

            return GenerationResult(
                content=content,
                platform="gemini",
                model=self.model,
                tokens_used=tokens_used,
                truncated=any(candidate.finish_reason == 2 for candidate in response.candidates),
            )

        except Exception as e:  # noqa: BLE001 - SDK exception types vary by provider
            raise APIError(f"Gemini API调用失败: {e}")

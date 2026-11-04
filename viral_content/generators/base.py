"""
内容生成器抽象基类

作者: Sunnyeung
版本: 4.1.5
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import logging
import time
from abc import ABC, abstractmethod

from viral_content.config.constants import RETRY_DELAY
from viral_content.exceptions.custom import APIError
from viral_content.models.generation import GenerationConfig, GenerationResult
from viral_content.utils.skill_loader import load_skill

logger = logging.getLogger(__name__)


class ContentGenerator(ABC):
    """内容生成器抽象基类"""

    # 平台默认模型
    DEFAULT_MODEL: str = ""
    # 平台名称
    PLATFORM_NAME: str = ""

    def __init__(self, config: GenerationConfig):
        self.config = config
        self.skill_content = config.system_prompt if config.system_prompt is not None else load_skill()
        self._client = None
        self._setup_client()

    @abstractmethod
    def _setup_client(self) -> None:
        """设置API客户端"""

    @abstractmethod
    def _generate_internal(self, prompt: str) -> GenerationResult:
        """内部生成方法"""

    @property
    def model(self) -> str:
        """获取使用的模型名称"""
        return self.config.model or self.DEFAULT_MODEL

    def build_prompt(self) -> str:
        """构建提示词（基础版本，v4.0 将由 PromptCompiler 替代）"""
        if self.config.user_prompt is not None:
            return self.config.user_prompt
        return (f"请根据已提供的材料，以{self.config.style}写作关于「{self.config.topic}」的文章，"
                f"目标长度约{self.config.word_count}字。保留事实边界，缺少依据时标明待核实；"
                "直接输出稿件，不编造经历、数据和来源。")


    def generate(self) -> GenerationResult:
        """
        生成内容（带重试机制）

        Returns:
            GenerationResult: 生成结果

        Raises:
            APIError: 当API调用失败时
        """
        last_error = None
        prompt = self.build_prompt()

        attempts = self.config.max_attempts
        if type(attempts) is not int or attempts < 1:
            raise APIError("max_attempts must be a positive integer")
        for attempt in range(attempts):
            try:
                logger.info(f"调用 {self.PLATFORM_NAME} API (尝试 {attempt + 1}/{attempts})...")

                start_time = time.time()
                result = self._generate_internal(prompt)
                result.duration_seconds = time.time() - start_time

                logger.info(
                    f"{self.PLATFORM_NAME} API调用成功，"
                    f"生成内容长度: {len(result.content)}字，"
                    f"耗时: {result.duration_seconds:.2f}秒"
                )

                return result

            except Exception as e:  # noqa: BLE001 - SDK exception types vary by provider
                last_error = e
                if attempts == 1:
                    raise APIError(f"{self.PLATFORM_NAME} request failed") from e
                if attempt < attempts - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)  # 指数退避
                    logger.warning(f"API调用失败，{wait_time}秒后重试: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API调用失败，已达最大重试次数: {e}")

        raise APIError(f"{self.PLATFORM_NAME} API调用失败: {last_error}")

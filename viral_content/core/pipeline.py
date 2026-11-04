"""Shared configured generation service for Python and command-line callers."""

import math
from dataclasses import asdict, is_dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from .conversion_funnel import ConversionGoal
from .platform_adapter import ContentPlatform as Platform
from .prompt_compiler import PromptCompiler
from .quality_gate import QualityGate
from .style_mixer import StyleMixer
from ..exceptions.custom import GenerationError, ValidationError
from ..generators.factory import create_generator
from ..models import Account, Offer, GenerationConfig, GenerationResult, Trend


class ViralContentPipeline:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = dict(config or {})
        self.prompt_compiler = PromptCompiler()
        self.style_mixer = StyleMixer()

    @staticmethod
    def _load_config(value, kind):
        if value is None:
            return None
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, dict):
            return dict(value)
        with Path(value).open(encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        if not isinstance(payload, dict) or not isinstance(payload.get(kind), dict):
            raise ValidationError(f"配置必须包含 {kind} 对象")
        return payload[kind]

    def run(
        self,
        topic,
        account=None,
        offer=None,
        style_mix=None,
        goal="likes",
        platform="wechat",
        trend_data=None,
        config=None,
        *,
        generator_factory=None,
    ):
        platform = Platform(platform).value
        goal = ConversionGoal(goal).value
        if not isinstance(topic, str) or not topic.strip():
            raise ValidationError("主题不能为空")
        account_data = self._load_config(account, "account")
        offer_data = self._load_config(offer, "offer")
        styles = None
        if style_mix:
            ids = (
                [s.strip() for s in style_mix.split(",")]
                if isinstance(style_mix, str)
                else style_mix
            )
            if (
                not isinstance(ids, list)
                or not ids
                or any(not isinstance(style_id, str) or not style_id for style_id in ids)
            ):
                raise ValidationError("style_mix 必须包含至少一个非空风格 ID")
            for style_id in ids:
                if not self.style_mixer.get_style(style_id):
                    raise ValidationError(f"未知风格: {style_id}")
            styles = (
                self.style_mixer.get_style(ids[0])
                if len(ids) == 1
                else self.style_mixer.mix_styles(ids)
            )
        prompt = self.prompt_compiler.build_system_prompt(
            topic,
            account_config=account_data,
            offer_config=offer_data,
            style_config=styles,
            goal=goal,
            platform=platform,
        )
        if trend_data is not None:
            import json

            def encode(value):
                if is_dataclass(value):
                    return asdict(value)
                if hasattr(value, "to_dict"):
                    return value.to_dict()
                return str(value)

            prompt += "\n\n用户提供的背景材料（不代表已核实）：\n" + json.dumps(
                trend_data, ensure_ascii=False, default=encode
            )
        base = config or GenerationConfig(**{**self.config, "topic": topic})
        if not isinstance(base, GenerationConfig):
            raise ValidationError("config 必须是 GenerationConfig")
        if base.stream:
            raise ValidationError("检查通过前不输出流式草稿，请关闭 stream")
        if base.enable_scoring:
            raise ValidationError(
                "自动评分未实现；请关闭 enable_scoring，避免把长度启发式当成质量分"
            )
        task = replace(
            base,
            topic=topic,
            system_prompt=prompt,
            user_prompt=f"请为{platform}撰写关于「{topic}」的完整内容。",
            content_platforms=[platform],
            goal=goal,
        )
        if type(task.variants) is not int or not 1 <= task.variants <= 8:
            raise ValidationError("variants 必须在 1 到 8 之间")
        if type(task.max_tokens) is not int or task.max_tokens < 1:
            raise ValidationError("max_tokens 必须是正整数")
        if type(task.max_attempts) is not int or task.max_attempts < 1:
            raise ValidationError("max_attempts 必须是正整数")
        if (
            type(task.timeout) not in (int, float)
            or not math.isfinite(task.timeout)
            or task.timeout <= 0
        ):
            raise ValidationError("timeout 必须是有限正数")
        if (
            type(task.temperature) not in (int, float)
            or not math.isfinite(task.temperature)
            or not 0 <= task.temperature <= 2
        ):
            raise ValidationError("temperature 必须是 0 到 2 之间的有限数")
        factory = generator_factory or create_generator
        generator = factory(config=task)
        accepted = []
        for index in range(task.variants):
            generator.config.user_prompt = (
                f"请为{platform}撰写关于「{topic}」的完整内容。" + f"\n候选编号：{index + 1}"
            )
            result = generator.generate()
            if not isinstance(result, GenerationResult):
                raise GenerationError("生成器必须返回 GenerationResult")
            if not isinstance(result.content, str) or not result.content.strip():
                raise GenerationError("模型未返回可检查的文本")
            if not isinstance(result.metadata, dict):
                raise GenerationError("生成结果 metadata 必须是字典")
            if result.truncated:
                continue
            gate = QualityGate().check(result.content, require_cta=goal in {"leads", "sales"})
            if gate.passed:
                result.variant_index = index
                result.content_platform = platform
                result.goal = goal
                result.metadata.update({"checked": True, "candidate_count": task.variants})
                accepted.append(result)
        if not accepted:
            raise GenerationError("所有候选均未通过检查，未生成可交付内容")
        # Length is only a stable presentation heuristic, never an outcome score.
        return max(accepted, key=lambda item: min(len(item.content.strip()), 800))

    def run_batch(
        self,
        trends,
        account=None,
        offer=None,
        style_mix=None,
        goal="likes",
        platforms=None,
        config=None,
        *,
        generator_factory=None,
    ):
        if not isinstance(trends, list) or not trends:
            raise ValidationError("trends 必须是非空列表")
        targets = [Platform(p).value for p in (platforms or ["wechat"])]
        if len(set(targets)) != len(targets):
            raise ValidationError("平台不能重复")
        normalized = []
        for index, trend in enumerate(trends):
            if isinstance(trend, dict):
                topic = trend.get("topic") or trend.get("description")
            else:
                topic = getattr(trend, "topic", None)
            if not isinstance(topic, str) or not topic.strip():
                raise ValidationError(f"trends[{index}] 缺少非空 topic 或 description")
            normalized.append((trend, topic.strip()))

        results = []
        for trend, topic in normalized:
            for platform in targets:
                results.append(
                    self.run(
                        topic,
                        account,
                        offer,
                        style_mix,
                        goal,
                        platform,
                        trend,
                        config,
                        generator_factory=generator_factory,
                    )
                )
        return results


class PipelineBuilder:
    """流程构建器（Builder模式）"""

    def __init__(self):
        """初始化构建器"""
        self._config: dict[str, Any] = {}
        self._account: str | Account | None = None
        self._offer: str | Offer | None = None
        self._styles: str | list[str] | None = None
        self._goal: ConversionGoal | None = None
        self._platform: Platform | None = None
        self._generation_config: GenerationConfig | None = None

    def with_config(self, config: dict[str, Any]) -> "PipelineBuilder":
        """设置全局配置"""
        self._config.update(config)
        return self

    def with_account(self, account: str | Account) -> "PipelineBuilder":
        """设置账号"""
        self._account = account
        return self

    def with_offer(self, offer: str | Offer) -> "PipelineBuilder":
        """设置产品"""
        self._offer = offer
        return self

    def with_styles(self, styles: str | list[str]) -> "PipelineBuilder":
        """设置风格"""
        self._styles = styles
        return self

    def with_goal(self, goal: str | ConversionGoal) -> "PipelineBuilder":
        """设置成交目标"""
        self._goal = goal if isinstance(goal, ConversionGoal) else ConversionGoal(goal)
        return self

    def with_platform(self, platform: str | Platform) -> "PipelineBuilder":
        """设置平台"""
        self._platform = platform if isinstance(platform, Platform) else Platform(platform)
        return self

    def with_generation_config(self, config: GenerationConfig) -> "PipelineBuilder":
        """设置生成配置"""
        self._generation_config = config
        return self

    def build(self) -> ViralContentPipeline:
        """构建流程"""
        pipeline = ViralContentPipeline(self._config)

        # 验证必需参数
        if not all([self._account, self._offer, self._styles, self._goal, self._platform]):
            raise ValidationError("Missing required parameters for pipeline")

        return pipeline

    def generate(
        self, topic: str, trend_data: str | Trend | list[Trend] | None = None
    ) -> GenerationResult:
        """快速生成（一步构建并执行）"""
        pipeline = self.build()
        return pipeline.run(
            topic=topic,
            account=self._account or "",  # type: ignore
            offer=self._offer or "",  # type: ignore
            style_mix=self._styles or [],  # type: ignore
            goal=self._goal or ConversionGoal.LEADS,  # type: ignore
            platform=self._platform or Platform.WECHAT,  # type: ignore
            trend_data=trend_data,
            config=self._generation_config,
        )

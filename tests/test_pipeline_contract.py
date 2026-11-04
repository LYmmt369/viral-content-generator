from pathlib import Path
from types import SimpleNamespace

import pytest

from viral_content import ViralContentPipeline
from viral_content.models import GenerationConfig, GenerationResult

ROOT = Path(__file__).resolve().parents[1]


def factory_log(log, bad_platform=None):
    def factory(config):
        log.append(config)

        def generate():
            content = (
                f"平台 {config.content_platforms[0]}：具体案例说明边界，提供可执行建议。" * 30
                + "欢迎评论提出问题。"
            )
            if config.content_platforms[0] == bad_platform:
                content = "保证爆款，绝对有效。" * 30
            return GenerationResult(content, "openai", "fixture")

        return SimpleNamespace(config=config, generate=generate)

    return factory


def test_documented_pipeline_loads_files_and_returns_checked_content():
    calls = []
    result = ViralContentPipeline().run(
        topic="案例",
        account=ROOT / "data/accounts/default_account.yaml",
        offer=ROOT / "data/offers/default_offer.yaml",
        style_mix="tech_explainer_global",
        goal="leads",
        platform="xiaohongshu",
        generator_factory=factory_log(calls),
    )
    assert result.content_platform == "xiaohongshu"
    assert result.metadata["checked"]
    assert len(calls) == 1
    assert "pain_points" in calls[0].system_prompt


def test_two_platforms_make_two_distinct_generation_requests():
    calls = []
    result = ViralContentPipeline().run_batch(
        [{"topic": "同一案例"}],
        platforms=["wechat", "xiaohongshu"],
        generator_factory=factory_log(calls),
    )
    assert len(calls) == len(result) == 2
    assert result[0].content != result[1].content
    assert calls[0].system_prompt != calls[1].system_prompt


def test_batch_failure_is_explicit_not_partial_success():
    with pytest.raises(Exception, match="未通过检查"):
        ViralContentPipeline().run_batch(
            [{"topic": "案例"}],
            platforms=["wechat", "xiaohongshu"],
            generator_factory=factory_log([], "xiaohongshu"),
        )


def test_batch_validates_every_item_before_starting_model_calls():
    calls = []
    with pytest.raises(Exception, match=r"trends\[1\]"):
        ViralContentPipeline().run_batch(
            [{"topic": "有效"}, {"description": "  "}],
            generator_factory=factory_log(calls),
        )
    assert calls == []


def test_batch_accepts_documented_description_fallback():
    calls = []
    result = ViralContentPipeline().run_batch(
        [{"description": "描述主题"}], generator_factory=factory_log(calls)
    )
    assert len(result) == len(calls) == 1
    assert calls[0].topic == "描述主题"


@pytest.mark.parametrize(
    "overrides",
    [
        {"max_tokens": 0},
        {"max_attempts": 0},
        {"timeout": float("inf")},
        {"temperature": float("nan")},
        {"temperature": 2.1},
        {"timeout": True},
        {"enable_scoring": True},
    ],
)
def test_invalid_or_unimplemented_generation_options_fail_before_client_setup(overrides):
    calls = []
    config = GenerationConfig(topic="案例", **overrides)
    with pytest.raises(Exception):
        ViralContentPipeline().run("案例", config=config, generator_factory=factory_log(calls))
    assert calls == []


def test_invalid_generator_result_has_a_stable_boundary_error():
    factory = lambda config: SimpleNamespace(config=config, generate=lambda: None)
    with pytest.raises(Exception, match="GenerationResult"):
        ViralContentPipeline().run("案例", generator_factory=factory)


def test_call_does_not_mutate_shared_generation_config():
    config = GenerationConfig(topic="original", content_platforms=["douyin"])
    ViralContentPipeline().run("案例", config=config, generator_factory=factory_log([]))
    assert config.topic == "original"
    assert config.content_platforms == ["douyin"]
    assert config.system_prompt is None


def test_platform_conversion_executes_callback_and_never_returns_prompt_as_content():
    from viral_content.core.platform_adapter import PlatformAdapter, ContentPlatform

    adapter = PlatformAdapter()
    calls = []

    def generate(prompt, platform):
        calls.append((prompt, platform))
        return "这是一篇有具体案例和可执行建议的成稿。" * 30

    result = adapter.batch_convert(
        "原始材料",
        ContentPlatform.WECHAT,
        [ContentPlatform.XIAOHONGSHU, ContentPlatform.DOUYIN],
        generate,
    )
    assert len(calls) == len(result) == 2
    assert all("原始材料" in prompt for prompt, _ in calls)
    assert all(not item.content.startswith("# 内容转换任务") for item in result)
    with pytest.raises(ValueError, match="generator_func"):
        adapter.batch_convert("材料", ContentPlatform.WECHAT)
    with pytest.raises(ValueError, match="generator_func"):
        adapter.generate_package("主题")

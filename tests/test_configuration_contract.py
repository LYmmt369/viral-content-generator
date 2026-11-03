"""Every supplied configuration constraint must reach the model task."""

import json

from viral_content.core.prompt_compiler import PromptCompiler


def test_all_nested_fields_and_list_entries_reach_compiled_task():
    account = {
        "name": "ACCOUNT_NAME",
        "pain_points": ["PAIN"],
        "authority_assets": ["EVIDENCE"],
        "tone_constraints": ["TONE_LIMIT"],
        "content_constraints": ["CONTENT_LIMIT"],
        "target_audience": [f"AUDIENCE_{i}" for i in range(6)],
        "platform_preferences": {"wechat": ["PLATFORM_PREF"]},
    }
    style = {
        "style_dna": {"tone": "TONE", "rhythm": "RHYTHM"},
        "logic_patterns": ["LOGIC"],
        "avoid": ["AVOID"],
        "hook_patterns": [f"HOOK_{i}" for i in range(6)],
    }
    offer = {"constraints": ["OFFER_LIMIT"], "pricing": {"amount": 99}}
    compiler = PromptCompiler()
    prompt = compiler.build_system_prompt(
        "TOPIC", account_config=account, style_config=style, offer_config=offer
    )
    for config in (account, style, offer):
        assert json.dumps(config, ensure_ascii=False, indent=2) in prompt


def test_default_templates_use_packaged_resources():
    from viral_content.config.constants import PROMPTS_DIR

    assert PromptCompiler().prompts_dir == PROMPTS_DIR
    assert PromptCompiler().load_template("base_system")

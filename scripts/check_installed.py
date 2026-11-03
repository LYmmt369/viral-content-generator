"""Run outside the checkout: python -I check_installed.py INSTALL_TARGET."""

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

target = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(target))
import viral_content
import viral_content_cli
import viral_content_revision
from viral_content.models import GenerationResult
from viral_content.config.constants import ACCOUNTS_DIR, OFFERS_DIR
from viral_content.core.experiment import FeedbackRecord, summarize_feedback

assert all(
    Path(m.__file__).resolve().is_relative_to(target)
    for m in (viral_content, viral_content_cli, viral_content_revision)
)
assert viral_content.__version__ == "4.1.1"
calls = []


def factory(config):
    calls.append(config)
    return SimpleNamespace(
        config=config,
        generate=lambda: GenerationResult(
            (config.content_platforms[0] + "：具体案例，清晰边界，执行步骤。") * 30,
            "openai",
            "fixed-test-reply",
        ),
    )


with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / "draft.md"
    with patch("viral_content_cli.create_generator", side_effect=factory):
        viral_content_cli.ViralContentCLI().generate(
            "案例",
            goal="likes",
            account=ACCOUNTS_DIR / "default_account.yaml",
            offer=OFFERS_DIR / "default_offer.yaml",
            style="tech_explainer_global",
            content_platforms=["wechat", "xiaohongshu"],
            output_path=output,
        )
    assert len(calls) == 2
    assert "content_constraints" in calls[0].system_prompt
    assert output.with_name("draft.wechat.md").is_file()
    assert output.with_name("draft.xiaohongshu.md").is_file()
    original = "保持原句。修改这里。"
    proposal = {
        "base_sha256": viral_content_revision.fingerprint(original),
        "protected": ["保持原句。"],
        "edits": [{"before": "修改这里。", "after": "新句。"}],
    }
    revised = viral_content_revision.apply_revision(original, proposal)
    assert viral_content_revision.revert_revision(revised.content, revised.receipt) == original
summary = summarize_feedback([FeedbackRecord(0, "wechat", "2026-11-04", leads=2)])
assert summary.metrics[0]["lead_rate"] is None
assert summary.winner_index is None
print("Installed 4.1.1: packaged configs, two platforms, exact undo and missing denominator passed")

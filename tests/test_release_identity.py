"""Keep active entrypoints and shipped metadata consistent."""

from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_skill_source_and_packaged_copy_match_current_release():
    import viral_content

    canonical = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert canonical == (ROOT / "viral_content/resources/skill.md").read_text(encoding="utf-8")
    meta = yaml.safe_load(canonical.split("---", 2)[1])
    assert meta["name"] == "LYmmt369-viral-article-generator"
    assert meta["metadata"]["version"] == viral_content.__version__ == "4.1.3"
    assert f'version = "{viral_content.__version__}"' in (ROOT / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert f"version: {viral_content.__version__}" in (ROOT / "CITATION.cff").read_text(
        encoding="utf-8"
    )


def test_repository_has_no_rejected_identity_or_unprefixed_skill_name():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    rejected = (
        "小跃" + "AI",
        "StepFun" + " AI Team",
        "github.com/Sunnyeung369/" + "viral-content-generator",
        "github.com:Sunnyeung369/" + "viral-content-generator",
    )
    failures = []
    for name in names:
        if not name or not (ROOT / name).is_file():
            continue
        try:
            text = (ROOT / name).read_text(encoding="utf-8")
        except UnicodeError:
            continue
        if any(token in text for token in rejected):
            failures.append(name)
        if re.search(r"(?<![\w-])viral-article-" + "generator", text):
            failures.append(name)
    assert not failures

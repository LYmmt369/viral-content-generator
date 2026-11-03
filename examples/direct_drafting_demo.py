"""Offline, fixed-response demonstration of write -> edit -> revert. No cloud calls."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from viral_content_revision import fingerprint, main as revise_cli

DRAFT = """# 把每一次改稿的范围说清楚

这是虚构演示稿，以下数字不代表真实业务效果。

同一份材料准备了3版草稿，内部阅读者共5人。

如果我们每次都把整篇文章从头到尾重新写一遍，就会让已经确认过的表达也跟着发生变化。

已确认的结尾：每次只改需要修改的地方。
"""
LONG_SENTENCE = "如果我们每次都把整篇文章从头到尾重新写一遍，就会让已经确认过的表达也跟着发生变化。"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory already exists; choose a new directory")
    args.output.mkdir(parents=True)
    materials = args.output / "materials.md"
    materials.write_bytes((Path(__file__).with_name("materials.md")).read_bytes())
    draft, revised, restored = [
        args.output / name for name in ["draft.md", "revised.md", "restored.md"]
    ]
    calls = []

    def writer(system, user):
        payload = json.loads(user)
        assert payload["materials"] == materials.read_bytes().decode("utf-8")
        calls.append("write")
        return DRAFT

    def editor(system, user):
        payload = json.loads(user)
        assert payload["manuscript"] == DRAFT
        calls.append("edit")
        return json.dumps(
            {
                "edits": [
                    {
                        "before": LONG_SENTENCE,
                        "after": "整篇重写，容易改动已确认的表达。",
                        "reason": "按要求只缩短长句",
                    }
                ]
            },
            ensure_ascii=False,
        )

    commands = [
        (
            [
                "write",
                str(materials),
                "根据虚构材料写一段介绍",
                "--model",
                "fixed-fixture",
                "--output",
                str(draft),
            ],
            writer,
        ),
        (
            [
                "edit",
                str(draft),
                "只缩短那句长句",
                "--model",
                "fixed-fixture",
                "--protect",
                "内部阅读者共5人",
                "--protect",
                "已确认的结尾：每次只改需要修改的地方。",
                "--output",
                str(revised),
            ],
            editor,
        ),
        (["revert", str(revised), str(revised) + ".receipt.json", "--output", str(restored)], None),
    ]
    for command, generate in commands:
        if revise_cli(command, generate=generate) != 0:
            raise RuntimeError("offline demonstration failed")
    assert calls == ["write", "edit"]
    assert restored.read_bytes() == draft.read_bytes()
    assert revised.read_bytes().decode("utf-8") == DRAFT.replace(
        LONG_SENTENCE, "整篇重写，容易改动已确认的表达。"
    )
    checks = {
        "model_replies": "fixed fixtures; no cloud inference",
        "generation_calls": calls,
        "exact_revert": True,
        "draft_sha256": fingerprint(DRAFT),
    }
    (args.output / "checks.json").write_bytes(
        (json.dumps(checks, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps(checks))


if __name__ == "__main__":
    main()

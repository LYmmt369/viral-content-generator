"""A fictional before/after example. No API keys, network calls or user questions."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from viral_content_revision import RevisionError, apply_revision, fingerprint, revert_revision

ORIGINAL = """# 少改一点，文章更接近作者

这是虚构演示材料，以下数字不代表真实业务效果。

演练记录：同一份材料准备了3版草稿，内部阅读者共5人。

文章好不好，最重要的是有没有真正把想表达的意思完完整整地表达清楚。

先把事实说清楚，再决定怎么表达。

有时候我们为了把内容做得更加丰富和充实，会反复增加很多其实可以不用出现的表达。

已确认的结尾：把每次修改变成下一次可检查的依据。
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory already exists; choose a new directory")
    request = {
        "base_sha256": fingerprint(ORIGINAL),
        "protected": [
            "演练记录：同一份材料准备了3版草稿，内部阅读者共5人。",
            "已确认的结尾：把每次修改变成下一次可检查的依据。",
        ],
        "edits": [
            {
                "before": "文章好不好，最重要的是有没有真正把想表达的意思完完整整地表达清楚。",
                "after": "好文章先把意思说清楚。",
                "reason": "压缩重复表达",
            },
            {
                "before": "有时候我们为了把内容做得更加丰富和充实，会反复增加很多其实可以不用出现的表达。",
                "after": "反复加话，未必增加内容。",
                "reason": "保留判断，缩短句子",
            },
        ],
    }
    result = apply_revision(ORIGINAL, request)
    restored = revert_revision(result.content, result.receipt)
    rejected = {**request, "edits": [{"before": "内部阅读者共5人", "after": "内部阅读者共50人"}]}
    try:
        apply_revision(ORIGINAL, rejected)
    except RevisionError as error:
        rejection = str(error)
    else:
        raise RuntimeError("protected text was changed")
    if restored.encode("utf-8") != ORIGINAL.encode("utf-8"):
        raise RuntimeError("revert did not restore the exact original bytes")
    args.output.mkdir(parents=True)
    files = {
        "original.md": ORIGINAL,
        "proposal.json": json.dumps(request, ensure_ascii=False, indent=2) + "\n",
        "revised.md": result.content,
        "receipt.json": json.dumps(result.receipt, ensure_ascii=False, indent=2) + "\n",
        "changes.diff": result.diff,
        "restored.md": restored,
        "checks.json": json.dumps(
            {
                "fictional_example": True,
                "edits_applied": 2,
                "original_sha256": fingerprint(ORIGINAL),
                "restored_sha256": fingerprint(restored),
                "protected_edit_rejected": rejection,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    }
    for name, content in files.items():
        (args.output / name).write_bytes(content.encode("utf-8"))
    print(
        json.dumps(
            {
                "output": str(args.output),
                "edits_applied": 2,
                "exact_revert": True,
                "protected_edit_rejected": True,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

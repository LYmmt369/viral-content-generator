"""Exact manuscript edits and a flat drafting CLI. Offline commands use only stdlib."""

import argparse
import difflib
import hashlib
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from collections.abc import Callable


class RevisionError(ValueError):
    """An edit cannot be applied without changing its declared boundaries."""


@dataclass
class RevisionResult:
    content: str
    receipt: dict[str, Any]
    diff: str


def fingerprint(text: str) -> str:
    """Identify the exact UTF-8 manuscript, including its line endings and BOM."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _check_hash(text: str, expected: Any, label: str) -> None:
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise RevisionError(f"{label} must be a lowercase SHA-256 fingerprint")
    if fingerprint(text) != expected:
        raise RevisionError(f"{label} mismatch: the manuscript version has changed")


def _edit_list(value: Any, *, receipt: bool = False) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RevisionError("edits must be a non-empty list")
    for edit in value:
        allowed = (
            {"before", "after", "reason", "start"} if receipt else {"before", "after", "reason"}
        )
        if not isinstance(edit, dict) or set(edit) - allowed:
            raise RevisionError("each edit must contain only before, after and optional reason")
        if not isinstance(edit.get("before"), str) or not edit["before"]:
            raise RevisionError("before must be a non-empty exact quotation")
        if not isinstance(edit.get("after"), str):
            raise RevisionError("after must be text; an empty string means deletion")
        if edit["before"] == edit["after"]:
            raise RevisionError("before and after are identical")
        if "reason" in edit and not isinstance(edit["reason"], str):
            raise RevisionError("reason must be text")
        if receipt and (type(edit.get("start")) is not int or edit["start"] < 0):
            raise RevisionError("receipt edit start must be a non-negative integer")
    return value


def _protected_ranges(text: str, value: Any) -> list[tuple[int, int]]:
    if not isinstance(value, list) or any(not isinstance(s, str) or not s for s in value):
        raise RevisionError("protected must be a list of non-empty exact quotations")
    ranges = []
    for quotation in value:
        start = text.find(quotation)
        if start < 0:
            raise RevisionError("a protected quotation is absent from the manuscript")
        while start >= 0:
            ranges.append((start, start + len(quotation)))
            start = text.find(quotation, start + 1)
    return ranges


def apply_revision(text: str, proposal: dict[str, Any]) -> RevisionResult:
    """Apply unique, non-overlapping quotations against one exact base version.

    Protected quotations cannot overlap a replacement, even if its new text repeats
    them. Quotes are literal data. This checks edit boundaries, not factual truth.
    """
    if not isinstance(proposal, dict) or set(proposal) - {"base_sha256", "edits", "protected"}:
        raise RevisionError("proposal must contain base_sha256, edits and optional protected")
    _check_hash(text, proposal.get("base_sha256"), "base_sha256")
    edits = _edit_list(proposal.get("edits"))
    protected = proposal.get("protected", [])
    locks = _protected_ranges(text, protected)
    located = []
    for edit in edits:
        before = edit["before"]
        start = text.find(before)
        if start < 0:
            raise RevisionError("an edit quotation is absent from the manuscript")
        if text.find(before, start + 1) >= 0:
            raise RevisionError("ambiguous quotation: include more surrounding text")
        end = start + len(before)
        if any(start < stop and end > begin for begin, stop in locks):
            raise RevisionError("an edit overlaps a protected quotation")
        located.append({**edit, "start": start})
    located.sort(key=lambda edit: edit["start"])
    for left, right in zip(located, located[1:]):
        if left["start"] + len(left["before"]) > right["start"]:
            raise RevisionError("edit quotations overlap; split or combine the edits")

    revised = text
    for edit in reversed(located):
        start = edit["start"]
        revised = revised[:start] + edit["after"] + revised[start + len(edit["before"]) :]
    receipt = {
        "schema_version": 1,
        "base_sha256": fingerprint(text),
        "result_sha256": fingerprint(revised),
        "edits": located,
        "protected": protected,
    }
    diff = (
        "\n".join(
            difflib.unified_diff(
                text.splitlines(),
                revised.splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )
        + "\n"
    )
    return RevisionResult(revised, receipt, diff)


def revert_revision(text: str, receipt: dict[str, Any]) -> str:
    """Restore the original manuscript only when both version hashes agree."""
    allowed = {"schema_version", "base_sha256", "result_sha256", "edits", "protected"}
    if (
        not isinstance(receipt, dict)
        or set(receipt) - allowed
        or type(receipt.get("schema_version")) is not int
        or receipt["schema_version"] != 1
    ):
        raise RevisionError("unsupported revision receipt")
    _check_hash(text, receipt.get("result_sha256"), "result_sha256")
    edits = _edit_list(receipt.get("edits"), receipt=True)
    ranges = []
    offset = 0
    previous_end = 0
    for edit in edits:
        if edit["start"] < previous_end:
            raise RevisionError("receipt edits are out of order or overlap")
        start = edit["start"] + offset
        end = start + len(edit["after"])
        if start < 0 or end > len(text) or text[start:end] != edit["after"]:
            raise RevisionError("receipt does not match the revised manuscript")
        ranges.append((start, end, edit["before"]))
        offset += len(edit["after"]) - len(edit["before"])
        previous_end = edit["start"] + len(edit["before"])
    restored = text
    for start, end, before in reversed(ranges):
        restored = restored[:start] + before + restored[end:]
    _check_hash(restored, receipt.get("base_sha256"), "base_sha256")
    return restored


def _read_text(path: Path) -> str:
    # Path.read_text normalizes line endings; keep the original UTF-8 bytes instead.
    return path.read_bytes().decode("utf-8")


def _check_output_paths(paths: list[Path], inputs: list[Path]) -> None:
    targets = [path.resolve() for path in paths]
    if len(set(targets)) != len(targets) or set(targets) & {p.resolve() for p in inputs}:
        raise RevisionError("outputs must be separate from each other and the inputs")
    if any(path.exists() for path in targets):
        raise RevisionError("an output already exists; choose a new output path")


def _write_new_files(files: dict[Path, str], inputs: list[Path]) -> None:
    _check_output_paths(list(files), inputs)
    created = []
    try:
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                created.append(path)
                handle.write(content.encode("utf-8"))
    except (OSError, UnicodeError, TypeError):
        for path in reversed(created):
            path.unlink()
        raise


def main(
    argv: list[str] | None = None, *, generate: Callable[[str, str], str] | None = None
) -> int:
    parser = argparse.ArgumentParser(
        description="Draft from materials or make exact edits. No Skill routing or interactive questions."
    )
    parser.add_argument("--version", action="version", version="%(prog)s 4.1.3")
    commands = parser.add_subparsers(dest="command", required=True)
    identify = commands.add_parser("fingerprint", help="print the exact manuscript version")
    identify.add_argument("manuscript", type=Path)
    for name in ["write", "edit"]:
        command = commands.add_parser(
            name, help="draft from materials" if name == "write" else "edit using one instruction"
        )
        command.add_argument(
            "manuscript",
            type=Path,
            help="UTF-8 materials" if name == "write" else "UTF-8 manuscript",
        )
        command.add_argument("instruction", help="what to write or change")
        command.add_argument("--output", type=Path, required=True)
        command.add_argument(
            "--provider",
            choices=["openai", "claude", "gemini"],
            default=os.getenv("VIRAL_PROVIDER", "openai"),
        )
        command.add_argument(
            "--model", default=os.getenv("VIRAL_MODEL"), help="model identifier, or VIRAL_MODEL"
        )
        command.add_argument("--max-tokens", type=int, default=8192)
        command.add_argument("--timeout", type=float, default=60.0)
        if name == "edit":
            command.add_argument(
                "--protect",
                action="append",
                default=[],
                help="exact quotation to preserve; repeatable",
            )
    for name, help_text in [
        ("apply", "apply an edit proposal"),
        ("revert", "revert using a receipt"),
    ]:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("manuscript", type=Path)
        command.add_argument("record", type=Path)
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        text = _read_text(args.manuscript)
        if args.command == "fingerprint":
            print(fingerprint(text))
            return 0
        if args.command in {"write", "edit"}:
            if not args.model or not args.model.strip():
                raise RevisionError("supply --model or set VIRAL_MODEL")
            if args.provider not in {"openai", "claude", "gemini"}:
                raise RevisionError("provider must be openai, claude or gemini")
            if args.max_tokens < 1 or not math.isfinite(args.timeout) or args.timeout <= 0:
                raise RevisionError("max-tokens and timeout must be positive")
            from viral_content_drafting import draft_from_materials, revise_from_instruction

            options = {
                "provider": args.provider,
                "model": args.model,
                "max_tokens": args.max_tokens,
                "timeout": args.timeout,
            }
            if args.command == "write":
                source_path = args.output.with_name(args.output.name + ".sources.json")
                _check_output_paths([args.output, source_path], [args.manuscript])
                content = draft_from_materials(text, args.instruction, generate=generate, **options)
                sources = {
                    "source": args.manuscript.name,
                    "source_sha256": fingerprint(text),
                    "result_sha256": fingerprint(content),
                    "instruction": args.instruction,
                    "provider": args.provider,
                    "model": args.model,
                }
                files = {
                    args.output: content,
                    source_path: json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
                }
                summary = {"output": str(args.output), "sources": str(source_path)}
            else:
                receipt_path = args.output.with_name(args.output.name + ".receipt.json")
                diff_path = args.output.with_name(args.output.name + ".diff")
                _check_output_paths([args.output, receipt_path, diff_path], [args.manuscript])
                result = revise_from_instruction(
                    text, args.instruction, protected=args.protect, generate=generate, **options
                )
                files = {
                    args.output: result.content,
                    receipt_path: json.dumps(result.receipt, ensure_ascii=False, indent=2) + "\n",
                    diff_path: result.diff,
                }
                summary = {
                    "output": str(args.output),
                    "receipt": str(receipt_path),
                    "diff": str(diff_path),
                    "edits": len(result.receipt["edits"]),
                }
            if _read_text(args.manuscript) != text:
                raise RevisionError("source changed during the model request; no output was saved")
            _write_new_files(files, [args.manuscript])
            print(json.dumps(summary))
            return 0
        record = json.loads(args.record.read_bytes().decode("utf-8-sig"))
        if args.command == "apply":
            result = apply_revision(text, record)
            receipt_path = args.output.with_name(args.output.name + ".receipt.json")
            diff_path = args.output.with_name(args.output.name + ".diff")
            files = {
                args.output: result.content,
                receipt_path: json.dumps(result.receipt, ensure_ascii=False, indent=2) + "\n",
                diff_path: result.diff,
            }
            _write_new_files(files, [args.manuscript, args.record])
            summary = {
                "output": str(args.output),
                "receipt": str(receipt_path),
                "diff": str(diff_path),
                "edits": len(result.receipt["edits"]),
            }
        else:
            restored = revert_revision(text, record)
            _write_new_files({args.output: restored}, [args.manuscript, args.record])
            summary = {"output": str(args.output), "sha256": fingerprint(restored)}
        print(json.dumps(summary))
        return 0
    except (RevisionError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

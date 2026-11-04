# Viral Content Generator v4.1.3

**Draft from your own materials, then make exact, reversible edits.**

One source file and one instruction produce a manuscript. One manuscript and one editing instruction produce bounded replacements, a readable diff and an undo receipt.

[中文](README.md) · [Detailed usage](docs/precise-revisions.md) · [Changes](CHANGELOG.md)

## Local demonstration

Python 3.10–3.12, no API key or dependencies required:

```bash
python examples/direct_drafting_demo.py --output output/direct-demo
```

The demonstration uses labeled, fixed model replies. It validates the workflow rather than real model writing quality.

## Use a model

```bash
pip install .
viral-revise write notes.md "Write a concise project introduction using these materials" --provider openai --model YOUR_MODEL --output draft.md
viral-revise edit draft.md "Shorten only the long sentences" --provider openai --model YOUR_MODEL --output revised.md
viral-revise revert revised.md revised.md.receipt.json --output restored.md
```

Choose an available model identifier. OpenAI uses Chat Completions. Configure OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY / GEMINI_API_KEY for the selected provider; VIRAL_API_KEY is an optional project-specific override. VIRAL_PROVIDER and VIRAL_MODEL can supply command defaults.

Use repeatable --protect arguments for exact quotations that must remain unchanged. The caller, not the model, owns the source version and protection list.

## What the program checks

Only uniquely located, non-overlapping replacements can be applied. Everything outside those ranges stays byte-for-byte unchanged in UTF-8. Protected quotations cannot overlap a replacement. Invalid proposals, stale source versions, truncated responses and existing output paths are rejected. Undo verifies both version hashes.

The edit, receipt and diff are saved together after validation. Source drafting records the source and result hashes. A provider workflow makes one generation attempt without skill routing, interviews or background orchestration.

The program enforces edit boundaries. The model still determines what to change; writing quality and factual correctness require review. No factual or publishing-performance guarantee is implied.

## Offline edits

```bash
viral-revise fingerprint draft.md
viral-revise apply draft.md edits.json --output revised.md
```

These commands and revert use only the standard library. From a source checkout, use python viral_content_revision.py instead of viral-revise.

Styles and account templates remain available. Multiple platforms generate independent results through the shared pipeline; all requested results must pass checks before any output file is saved.

## Validation

```bash
python -m pytest -q
python scripts/check_docs.py
python scripts/check_secrets.py
python -m build --wheel
```

[Validation scope](docs/v4.1-validation.md) · [Roadmap](docs/v4.1-roadmap.md) · [Contributing](CONTRIBUTING.md) · [Citation](CITATION.cff)

MIT License.

## Configured multi-platform generation

`viral-content --topic "Case study" --platform wechat xiaohongshu --ai-platform openai --model YOUR_MODEL --output drafts/` produces separate checked manuscripts. The CLI shares the Python pipeline. All requested platforms must pass before files are written. Existing files are never overwritten. Streaming is not supported by the checked workflow. See [API](docs/API文档.md), [Skill](SKILL.md), and [feedback semantics](docs/feedback.md).

The legacy Douyin, Xiaohongshu, TikTok and Google Trends `fetch()` methods return labeled sample data, not live platform observations.

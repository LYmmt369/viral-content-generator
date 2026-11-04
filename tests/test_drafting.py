"""Source-to-draft and instruction-to-edit contracts, with controlled model replies."""

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from viral_content_drafting import _generate_text, draft_from_materials, revise_from_instruction
from viral_content_revision import RevisionError, fingerprint, main, revert_revision


class DirectDraftingContracts(unittest.TestCase):
    def test_source_and_instruction_are_passed_once_without_interview_or_routing(self):
        model = Mock(return_value="# 成稿\n材料中记录了3次内部演练。")
        materials = "项目笔记：内部演练3次。"
        draft = draft_from_materials(materials, "写成一段项目介绍", generate=model)
        self.assertEqual(draft, "# 成稿\n材料中记录了3次内部演练。")
        model.assert_called_once()
        system, payload = model.call_args.args
        self.assertIn("不要主动提问", system)
        self.assertEqual(
            json.loads(payload), {"instruction": "写成一段项目介绍", "materials": materials}
        )

    def test_blank_source_or_instruction_never_calls_the_model(self):
        model = Mock()
        for materials, instruction in [("", "写稿"), ("材料", " ")]:
            with self.subTest(materials=materials), self.assertRaises(RevisionError):
                draft_from_materials(materials, instruction, generate=model)
        model.assert_not_called()

    def test_finite_edit_preserves_unselected_text_and_round_trips(self):
        text = "\ufeff标题\r\n需要压缩的唯一一句话。\r\n演练5人。结尾不动。"
        model = Mock(
            return_value=json.dumps(
                {"edits": [{"before": "需要压缩的唯一一句话。", "after": "短句。"}]},
                ensure_ascii=False,
            )
        )
        result = revise_from_instruction(
            text, "只压缩那句长句", protected=["演练5人。", "结尾不动。"], generate=model
        )
        self.assertEqual(result.content, "\ufeff标题\r\n短句。\r\n演练5人。结尾不动。")
        self.assertEqual(revert_revision(result.content, result.receipt), text)
        self.assertEqual(json.loads(model.call_args.args[1])["manuscript"], text)
        model.assert_called_once()

    def test_protection_is_owned_by_the_caller_and_cannot_be_weakened_by_the_model(self):
        text = "正文。数据5人。"
        for response in [
            {"edits": [{"before": "数据5人。", "after": "数据50人。"}]},
            {"edits": [{"before": "正文。", "after": "新正文。"}], "protected": []},
            {
                "edits": [{"before": "正文。", "after": "新正文。"}],
                "base_sha256": fingerprint(text),
            },
        ]:
            with self.subTest(response=response), self.assertRaises(RevisionError):
                revise_from_instruction(
                    text,
                    "改正文",
                    protected=["数据5人。"],
                    generate=lambda *_, response=response: json.dumps(response),
                )

    def test_accepts_a_single_json_fence_but_rejects_prose_or_incomplete_json(self):
        text = "唯一原句。"
        good = '{"edits": [{"before": "唯一原句。", "after": "新句。"}]}'
        result = revise_from_instruction(
            text, "改短", generate=lambda *_: "```json\n" + good + "\n```"
        )
        self.assertEqual(result.content, "新句。")
        for bad in [
            "先问几个问题。" + good,
            good[:-3],
            "[]",
            "null",
            '{"edits": [], "edits": []}',
            '{"edits": []}',
        ]:
            with self.subTest(bad=bad), self.assertRaises(RevisionError):
                revise_from_instruction(text, "改短", generate=lambda *_, reply=bad: reply)

    def test_bad_protection_is_rejected_before_a_request(self):
        model = Mock()
        for protected in ["原句", ["缺失的原句"]]:
            with self.subTest(protected=protected), self.assertRaises(RevisionError):
                revise_from_instruction("原句", "改短", protected=protected, generate=model)
        model.assert_not_called()

    def test_no_text_or_truncated_output_is_never_treated_as_a_complete_draft(self):
        for response in [None, "", "   "]:
            with self.subTest(response=response), self.assertRaises(RevisionError):
                draft_from_materials("材料", "写稿", generate=lambda *_, reply=response: reply)
        with patch("viral_content.generators.factory.create_generator") as factory:
            factory.return_value.generate.return_value = Mock(truncated=True)
            with self.assertRaisesRegex(RevisionError, "truncated"):
                _generate_text("system", "user", provider="openai", model="fixture")

    def test_provider_failure_does_not_expose_request_details_or_retry_the_workflow(self):
        with patch("viral_content.generators.factory.create_generator") as factory:
            factory.return_value.generate.side_effect = RuntimeError("sensitive request details")
            with self.assertRaises(RevisionError) as raised:
                _generate_text("system", "user", provider="openai", model="fixture")
            self.assertNotIn("sensitive request details", str(raised.exception))
            factory.return_value.generate.assert_called_once()
            options = factory.call_args.kwargs
            self.assertEqual(options["max_attempts"], 1)
            self.assertEqual(options["system_prompt"], "system")
            self.assertEqual(options["user_prompt"], "user")


class NaturalLanguageCLIContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "源稿😀.md"
        self.text = "\ufeff标题\r\n长句只改这里。\r\n演练5人。结尾保持。"
        self.source.write_bytes(self.text.encode("utf-8"))
        self.output = self.root / "新稿😀.md"

    def invoke(self, command, instruction, model, *extra):
        args = [
            command,
            str(self.source),
            instruction,
            "--model",
            "fixture",
            "--output",
            str(self.output),
            *extra,
        ]
        with redirect_stdout(StringIO()) as stdout, redirect_stderr(StringIO()) as stderr:
            code = main(args, generate=model)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_write_creates_a_complete_draft_and_source_version_record(self):
        model = Mock(return_value="# 新稿\n直接成稿。")
        code, stdout, _ = self.invoke("write", "根据材料写介绍", model)
        self.assertEqual(code, 0)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "# 新稿\n直接成稿。")
        record = json.loads(Path(json.loads(stdout)["sources"]).read_text(encoding="utf-8"))
        self.assertEqual(record["source_sha256"], fingerprint(self.text))
        self.assertEqual(self.source.read_bytes(), self.text.encode("utf-8"))

    def test_edit_executes_one_instruction_and_produces_a_reversible_receipt(self):
        model = Mock(
            return_value=json.dumps({"edits": [{"before": "长句只改这里。", "after": "短句。"}]})
        )
        code, stdout, _ = self.invoke(
            "edit", "缩短长句", model, "--protect", "演练5人。", "--protect", "结尾保持。"
        )
        self.assertEqual(code, 0)
        revised = self.output.read_bytes().decode("utf-8")
        receipt = json.loads(Path(json.loads(stdout)["receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(revised, self.text.replace("长句只改这里。", "短句。"))
        self.assertEqual(revert_revision(revised, receipt), self.text)
        model.assert_called_once()

    def test_existing_outputs_are_rejected_before_spending_a_model_call(self):
        for suffix in ["", ".receipt.json", ".diff"]:
            target = Path(str(self.output) + suffix)
            target.write_bytes(b"existing")
            model = Mock()
            code, _, _ = self.invoke("edit", "改短", model)
            self.assertEqual(code, 2)
            model.assert_not_called()
            self.assertEqual(target.read_bytes(), b"existing")
            target.unlink()

    def test_invalid_model_reply_or_concurrent_source_edit_saves_no_partial_result(self):
        code, _, _ = self.invoke("edit", "改短", Mock(return_value="not JSON"))
        self.assertEqual(code, 2)
        self.assertFalse(self.output.exists())

        def concurrent_change(*_):
            self.source.write_bytes(b"newer manuscript")
            return '{"edits": [{"before": "长句只改这里。", "after": "短句。"}]}'

        code, _, stderr = self.invoke("edit", "改短", concurrent_change)
        self.assertEqual(code, 2)
        self.assertIn("source changed", json.loads(stderr)["error"])
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source.read_bytes(), b"newer manuscript")

    def test_blank_instruction_or_invalid_limits_never_call_the_model(self):
        for instruction, extra in [
            (" ", []),
            ("改短", ["--max-tokens", "0"]),
            ("改短", ["--timeout", "nan"]),
        ]:
            model = Mock()
            code, _, _ = self.invoke("edit", instruction, model, *extra)
            self.assertEqual(code, 2)
            model.assert_not_called()


if __name__ == "__main__":
    unittest.main()

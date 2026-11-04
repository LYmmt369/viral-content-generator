"""The legacy CLI must pass compiled tasks through the same generator contract."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from viral_content.models import GenerationResult
from viral_content_cli import ViralContentCLI, parse_arguments


class GenerationBridgeContracts(unittest.TestCase):
    def test_compiled_task_reaches_the_generator_without_unsupported_keywords(self):
        generator = Mock(config=SimpleNamespace(user_prompt=None))
        generator.generate.return_value = GenerationResult(
            "A concrete explanation of a real situation and a useful next step. " * 8,
            "openai",
            "fixture",
        )
        with patch("viral_content_cli.create_generator", return_value=generator) as factory:
            content = ViralContentCLI().generate("主题", goal="likes", content_platforms=["wechat"])
        generator.generate.assert_called_once_with()
        self.assertIn("主题", generator.config.user_prompt)
        self.assertIn("主题", factory.call_args.kwargs["config"].system_prompt)
        self.assertEqual(content, generator.generate.return_value.content)

    def test_failed_candidates_never_become_a_saved_manuscript(self):
        generator = Mock(config=SimpleNamespace(user_prompt=None))
        generator.generate.return_value = GenerationResult(
            "保证爆款，绝对有效。" * 30, "openai", "fixture"
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "draft.md"
            with (
                patch("viral_content_cli.create_generator", return_value=generator),
                self.assertRaises(Exception),
            ):
                ViralContentCLI().generate("主题", goal="likes", variants=2, output_path=output)
            self.assertFalse(output.exists())

    def test_multiple_platforms_generate_and_save_separate_manuscripts(self):
        calls = []

        def factory(config):
            calls.append(config)
            target = config.content_platforms[0]
            return SimpleNamespace(
                config=config,
                generate=lambda: GenerationResult(
                    (target + "：具体案例、明确边界和执行步骤。") * 30, "openai", "fixture"
                ),
            )

        with (
            tempfile.TemporaryDirectory() as directory,
            patch("viral_content_cli.create_generator", side_effect=factory),
        ):
            output = Path(directory) / "draft.md"
            content = ViralContentCLI().generate(
                "主题", goal="likes", content_platforms=["wechat", "douyin"], output_path=output
            )
            self.assertEqual(len(calls), 2)
            self.assertIn("wechat", content)
            self.assertIn("douyin", content)
            self.assertTrue(output.with_name("draft.wechat.md").exists())
            self.assertTrue(output.with_name("draft.douyin.md").exists())
            self.assertFalse(output.exists())

    def test_second_platform_failure_writes_no_partial_package(self):
        def factory(config):
            content = (
                "保证爆款" * 30
                if config.content_platforms == ["douyin"]
                else "具体案例和执行步骤。" * 50
            )
            return SimpleNamespace(
                config=config, generate=lambda: GenerationResult(content, "openai", "fixture")
            )

        with (
            tempfile.TemporaryDirectory() as directory,
            patch("viral_content_cli.create_generator", side_effect=factory),
        ):
            with self.assertRaises(Exception):
                ViralContentCLI().generate(
                    "主题",
                    goal="likes",
                    content_platforms=["wechat", "douyin"],
                    output_path=Path(directory) / "draft.md",
                )
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_batch_file_output_keeps_each_topic(self):
        def factory(config):
            return SimpleNamespace(
                config=config,
                generate=lambda: GenerationResult(
                    (config.topic + "：具体案例和执行步骤。") * 30, "openai", "fixture"
                ),
            )

        with (
            tempfile.TemporaryDirectory() as directory,
            patch("viral_content_cli.create_generator", side_effect=factory),
        ):
            target = Path(directory) / "draft.md"
            results = ViralContentCLI().batch_generate(
                [{"topic": "主题一"}, {"topic": "主题二"}],
                goal="likes",
                content_platforms=["wechat"],
                output_path=target,
            )
            self.assertTrue(all(item["success"] for item in results))
            self.assertIn("主题一", target.with_name("draft.1.md").read_text(encoding="utf-8"))
            self.assertIn("主题二", target.with_name("draft.2.md").read_text(encoding="utf-8"))

    def test_documented_topic_option_and_positional_topic_agree(self):
        for argv in [["cli", "主题"], ["cli", "--topic", "主题"]]:
            with self.subTest(argv=argv), patch("sys.argv", argv):
                self.assertEqual(parse_arguments().topic, "主题")


if __name__ == "__main__":
    unittest.main()

"""The legacy CLI must pass compiled tasks through the same generator contract."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from viral_content_cli import ViralContentCLI, parse_arguments


class GenerationBridgeContracts(unittest.TestCase):
    def test_compiled_task_reaches_the_generator_without_unsupported_keywords(self):
        generator = Mock(config=SimpleNamespace(user_prompt=None))
        generator.generate.return_value = SimpleNamespace(
            content="A concrete explanation of a real situation and a useful next step. " * 8
        )
        with patch("viral_content_cli.create_generator", return_value=generator) as factory:
            content = ViralContentCLI().generate("主题", goal="likes", content_platforms=["wechat"])
        generator.generate.assert_called_once_with()
        self.assertIn("主题", generator.config.user_prompt)
        self.assertIn("system_prompt", factory.call_args.kwargs)
        self.assertEqual(content, generator.generate.return_value.content)

    def test_failed_candidates_never_become_a_saved_manuscript(self):
        generator = Mock(config=SimpleNamespace(user_prompt=None))
        generator.generate.return_value = SimpleNamespace(content="保证爆款，绝对有效。" * 30)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "draft.md"
            with (
                patch("viral_content_cli.create_generator", return_value=generator),
                self.assertRaises(ValueError),
            ):
                ViralContentCLI().generate("主题", goal="likes", variants=2, output_path=output)
            self.assertFalse(output.exists())

    def test_multiple_platforms_are_not_silently_discarded(self):
        with patch("viral_content_cli.create_generator") as factory, self.assertRaises(ValueError):
            ViralContentCLI().generate("主题", content_platforms=["wechat", "douyin"])
        factory.assert_not_called()

    def test_documented_topic_option_and_positional_topic_agree(self):
        for argv in [["cli", "主题"], ["cli", "--topic", "主题"]]:
            with self.subTest(argv=argv), patch("sys.argv", argv):
                self.assertEqual(parse_arguments().topic, "主题")


if __name__ == "__main__":
    unittest.main()

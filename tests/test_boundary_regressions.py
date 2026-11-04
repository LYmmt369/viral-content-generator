from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

from viral_content_cli import ViralContentCLI
from viral_content_revision import _write_new_files, fingerprint, main as revision_main


def test_encoding_failure_rolls_back_all_new_outputs(tmp_path):
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    with pytest.raises(UnicodeError):
        _write_new_files({first: "valid", second: "\ud800"}, [])
    assert not first.exists()
    assert not second.exists()


def test_malformed_batch_item_is_reported_without_aborting_valid_items():
    with patch.object(ViralContentCLI, "generate", return_value="checked") as generate:
        results = ViralContentCLI().batch_generate([None, {"topic": "有效主题"}])
    assert [entry["success"] for entry in results] == [False, True]
    assert "热点条目" in results[0]["error"]
    generate.assert_called_once_with(topic="有效主题")


def test_importing_cli_does_not_create_a_log_file(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-c", "import viral_content_cli"],
        cwd=tmp_path,
        env={"PYTHONPATH": str(root)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "viral_content_generator.log").exists()


def test_revision_cli_rejects_duplicate_json_fields(tmp_path, capsys):
    manuscript = tmp_path / "base.md"
    record = tmp_path / "proposal.json"
    output = tmp_path / "result.md"
    manuscript.write_text("原文", encoding="utf-8")
    digest = fingerprint("原文")
    record.write_text(
        '{"base_sha256":"' + digest + '","edits":[],"edits":[{"before":"原文","after":"新文"}]}',
        encoding="utf-8",
    )
    assert revision_main(["apply", str(manuscript), str(record), "--output", str(output)]) == 2
    assert "duplicate field" in capsys.readouterr().err
    assert not output.exists()

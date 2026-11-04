from pathlib import Path
from unittest.mock import patch

import pytest

from viral_content_cli import ViralContentCLI
from viral_content_revision import _write_new_files


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

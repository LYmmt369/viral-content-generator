import json
from pathlib import Path
from unittest.mock import patch

import pytest

from viral_content_cli import HotTopicInput, ViralContentCLI, main, parse_arguments
from viral_content.core.pipeline import ViralContentPipeline
from viral_content.exceptions.custom import ValidationError


@pytest.mark.parametrize("payload", [[], {"trends": []}, {"trends": {}}, None])
def test_empty_or_invalid_topic_file_is_rejected(tmp_path, payload):
    source = tmp_path / "topics.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="热点数据格式错误"):
        HotTopicInput.from_file(source)


def test_empty_batch_never_reports_success(tmp_path):
    source = tmp_path / "topics.json"
    source.write_text("[]", encoding="utf-8")
    with patch("sys.argv", ["viral-content", "--trends-file", str(source)]):
        assert main() == 1
    with pytest.raises(ValueError, match="不能为空"):
        ViralContentCLI().batch_generate([])
    with pytest.raises(ValidationError, match="非空列表"):
        ViralContentPipeline().run_batch([])


def test_topic_and_topic_file_cannot_silently_override_each_other(tmp_path):
    source = tmp_path / "topics.json"
    source.write_text('[{"topic":"文件主题"}]', encoding="utf-8")
    with patch("sys.argv", ["viral-content", "--topic", "命令主题", "--trends-file", str(source)]):
        with pytest.raises(SystemExit) as error:
            parse_arguments()
    assert error.value.code == 2

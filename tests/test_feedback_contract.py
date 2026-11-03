import json
from dataclasses import replace

import pytest

from viral_content.core.experiment import FeedbackRecord, summarize_feedback, export_feedback_report


def record(**kwargs):
    return FeedbackRecord(0, "wechat", "2026-11-04", **kwargs)


def test_missing_denominator_and_numerator_are_unknown():
    result = summarize_feedback([record(leads=2), record(impressions=100)])
    assert result.metrics[0]["lead_rate"] is None
    assert result.metrics[1]["lead_rate"] is None
    assert result.winner_index is None


def test_zero_is_not_replaced_with_other_denominator():
    result = summarize_feedback([record(impressions=0, views=100, leads=2)])
    assert result.metrics[0]["lead_rate"] is None
    explicit = summarize_feedback([record(impressions=0, views=100, leads=2, denominator="views")])
    assert explicit.metrics[0]["lead_rate"] == 2


def test_same_candidate_different_publications_never_overwrite():
    result = summarize_feedback(
        [record(publication_id=str(i), impressions=100, leads=i) for i in (1, 2, 3)]
    )
    assert [v["lead_rate"] for v in result.metrics.values()] == [1, 2, 3]
    assert result.sample_size == 3
    assert not result.reliable
    assert result.winner_index is None


def test_latest_cumulative_snapshot_selected_without_adding(tmp_path):
    early = record(
        publication_id="post", observed_at="2026-11-04T01:00:00Z", impressions=100, leads=2
    )
    late = replace(early, observed_at="2026-11-04T02:00:00Z", impressions=200, leads=3)
    result = summarize_feedback([late, early, late])
    assert result.sample_size == 1
    assert result.metrics[0]["lead_rate"] == 1.5
    path = tmp_path / "feedback.json"
    export_feedback_report([early, late], str(path))
    assert len(json.loads(path.read_text(encoding="utf-8"))["records"]) == 2


def test_contexts_and_windows_are_not_combined():
    base = record(publication_id="post", impressions=100, leads=2, window_hours=24)
    result = summarize_feedback(
        [
            base,
            replace(base, platform="douyin"),
            replace(base, window_hours=48),
            replace(base, account_id="another"),
        ]
    )
    assert result.platform == "mixed"
    assert len(result.metrics) == 4
    assert result.winner_index is None


def test_conflicting_snapshots_and_missing_snapshot_times_rejected():
    base = record(publication_id="post", impressions=100)
    with pytest.raises(ValueError, match="observed_at"):
        summarize_feedback([base, replace(base, impressions=200)])
    timed = replace(base, observed_at="2026-11-04T01:00:00Z")
    with pytest.raises(ValueError, match="冲突"):
        summarize_feedback([timed, replace(timed, impressions=200)])


@pytest.mark.parametrize("invalid", [-1, True, 1.5, "10"])
def test_invalid_counts_rejected(invalid):
    with pytest.raises(ValueError):
        summarize_feedback([record(impressions=invalid)])

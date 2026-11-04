from datetime import timezone

import pytest

from viral_content.trends.base import Trend, TrendAggregator
import viral_content.trends.sources.google_trends as google_trends_module
from viral_content.trends.sources.douyin import DouyinTrendSource
from viral_content.trends.sources.xiaohongshu import XiaohongshuTrendSource
from viral_content.trends.sources.tiktok import TikTokTrendSource
from viral_content.trends.sources.google_trends import GoogleTrendsSource


@pytest.mark.parametrize(
    "source_class",
    [DouyinTrendSource, XiaohongshuTrendSource, TikTokTrendSource, GoogleTrendsSource],
)
def test_sample_trends_cannot_look_like_live_platform_observations(source_class):
    sample = source_class().fetch(limit=1)[0]
    assert sample.id.startswith("sample_")
    assert sample.source.startswith("sample:")
    assert sample.created_at is None
    assert sample.metrics.timestamp is None
    exported = sample.to_dict()
    assert exported["created_at"] is None
    restored = Trend.from_dict(exported)
    assert restored.source == sample.source
    assert restored.created_at is None
    assert restored.metrics.timestamp is None


@pytest.mark.parametrize(
    ("source_class", "category"),
    [
        (DouyinTrendSource, "tech"),
        (XiaohongshuTrendSource, "lifestyle"),
        (TikTokTrendSource, "business"),
        (GoogleTrendsSource, "social"),
    ],
)
def test_advertised_category_filter_is_applied(source_class, category):
    trends = source_class().fetch(limit=2, category=category)
    assert trends
    assert all(trend.category.value == category for trend in trends)


@pytest.mark.parametrize("limit", [0, -1, 1.5, True])
def test_invalid_trend_limits_are_rejected(limit):
    with pytest.raises(ValueError, match="limit"):
        GoogleTrendsSource().fetch(limit=limit)


def test_real_google_trends_uses_first_column_without_inventing_a_score(monkeypatch):
    class FakeSeries:
        def __init__(self, values):
            self.values = values

        def dropna(self):
            return FakeSeries([value for value in self.values if value is not None])

        def astype(self, kind):
            assert kind is str
            return FakeSeries([str(value) for value in self.values])

        def __iter__(self):
            return iter(self.values)

    class FakeILoc:
        def __getitem__(self, key):
            assert key == (slice(None), 0)
            return FakeSeries(["AI Agent", "高考 志愿", None])

    class FakeFrame:
        empty = False
        shape = (3, 1)
        iloc = FakeILoc()

    class FakeTrendReq:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def trending_searches(self, pn):
            assert pn == "CN"
            return FakeFrame()

    monkeypatch.setattr(google_trends_module, "TrendReq", FakeTrendReq)
    trends = GoogleTrendsSource().fetch_real_trends(limit=1, category="social")
    assert len(trends) == 1
    assert trends[0].topic == "高考 志愿"
    assert trends[0].metrics.heat == 0
    assert trends[0].url.endswith("q=%E9%AB%98%E8%80%83+%E5%BF%97%E6%84%BF")


def test_real_google_trends_does_not_fall_back_to_sample_when_dependency_is_missing(monkeypatch):
    monkeypatch.setattr(google_trends_module, "TrendReq", None)
    with pytest.raises(RuntimeError, match="无法获取真实"):
        GoogleTrendsSource().fetch_real_trends()


def test_z_timestamps_round_trip_on_all_supported_python_versions():
    restored = Trend.from_dict(
        {
            "id": "live-1",
            "topic": "topic",
            "metrics": {"时间戳": "2026-11-04T01:02:03Z"},
            "created_at": "2026-11-04T01:02:03Z",
        }
    )
    assert restored.created_at.tzinfo == timezone.utc
    assert restored.metrics.timestamp.tzinfo == timezone.utc


def test_aggregator_rejects_invalid_final_limit():
    with pytest.raises(ValueError, match="limit"):
        TrendAggregator().merge_and_rank({}, limit=0)


def test_aggregator_preserves_sample_provenance():
    sample = DouyinTrendSource().fetch(limit=1)[0]
    merged = TrendAggregator().merge_and_rank({"抖音": [sample]})
    assert merged[0].source == "sample:抖音"


def test_aggregator_does_not_confuse_source_failure_with_no_results():
    class BrokenSource(DouyinTrendSource):
        def fetch(self, limit=20, category=None):
            raise OSError("private upstream details")

    aggregator = TrendAggregator([BrokenSource()])
    with pytest.raises(RuntimeError, match="获取抖音热点失败"):
        aggregator.fetch_all()
    assert aggregator.fetch_all(strict=False) == {"抖音": []}

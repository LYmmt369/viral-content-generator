import pytest

from viral_content.trends.base import Trend
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

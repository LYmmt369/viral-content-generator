"""
Google Trends 热点来源
v4.0 - 从 Google Trends 获取热点

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

from ..base import BaseTrendSource, Trend, TrendCategory, TrendMetrics

try:
    from pytrends.request import TrendReq
except ImportError:  # Optional dependency; simulated trends remain available.
    TrendReq = None


class GoogleTrendsSource(BaseTrendSource):
    """Google Trends 热点来源

    注意：这是一个简化实现，实际使用时可能需要：
    1. 使用 pytrends 库（需安装）
    2. 或使用 Google Trends API
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """初始化 Google Trends 来源

        Args:
            config: 配置参数（geo: 国家代码, language: 语言）
        """
        super().__init__("Google Trends", config)
        self.geo = config.get("geo", "CN") if config else "CN"
        self.language = config.get("language", "zh-CN") if config else "zh-CN"

    def fetch(self, limit: int = 20, category: str | None = None) -> list[Trend]:
        """获取 Google Trends 热点

        Args:
            limit: 返回数量
            category: 分类过滤

        Returns:
            热点列表
        """
        # 简化实现：返回模拟数据
        # 实际应用中应该调用 pytrends 或 Google Trends API
        requested_category = self.validate_request(limit, category)
        trends = []

        # 模拟热点数据
        sample_trends = self._get_sample_trends()

        for i, item in enumerate(sample_trends):
            trend = Trend(
                id=f"sample_google_trends_{i}",
                topic=item["topic"],
                description=item.get("description", ""),
                source="sample:Google Trends",
                url=item.get("url", ""),
                category=self._infer_category(item["topic"]),
                keywords=item.get("keywords", []),
                metrics=TrendMetrics(
                    heat=item.get("heat", 50),
                    discussion_count=item.get("discussion", 0),
                    growth_rate=item.get("growth", 0.0),
                    timestamp=None,
                ),
                created_at=None,
            )
            if self.category_matches(trend, requested_category):
                trends.append(trend)
            if len(trends) >= limit:
                break

        return trends

    def _get_sample_trends(self) -> list[dict[str, Any]]:
        """获取示例热点数据（模拟）"""
        # 模拟当前热点
        return [
            {
                "topic": "AI Agent Runtime 崩溃问题",
                "description": "2026年6月初，多家AI Agent平台出现Runtime崩溃",
                "url": "https://trends.google.com/trends",
                "keywords": ["AI", "Agent", "Runtime", "崩溃"],
                "heat": 86,
                "discussion": 50000,
                "growth": 15.5,
            },
            {
                "topic": "马斯克 2026 访谈解读",
                "description": "马斯克最新访谈引发热议",
                "url": "https://trends.google.com/trends",
                "keywords": ["马斯克", "访谈", "特斯拉", "SpaceX"],
                "heat": 92,
                "discussion": 120000,
                "growth": 8.2,
            },
            {
                "topic": "2026年高考志愿填报指南",
                "description": "高考结束，志愿填报成热点",
                "url": "https://trends.google.com/trends",
                "keywords": ["高考", "志愿", "填报", "大学"],
                "heat": 78,
                "discussion": 30000,
                "growth": 25.0,
            },
            {
                "topic": "新能源汽车价格战升级",
                "description": "多家新能源车企降价促销",
                "url": "https://trends.google.com/trends",
                "keywords": ["新能源", "汽车", "价格", "降价"],
                "heat": 75,
                "discussion": 25000,
                "growth": 5.5,
            },
            {
                "topic": "远程办公软件评测 2026",
                "description": "最新远程办公工具对比",
                "url": "https://trends.google.com/trends",
                "keywords": ["远程", "办公", "软件", "工具"],
                "heat": 65,
                "discussion": 15000,
                "growth": 3.2,
            },
        ]

    def _infer_category(self, topic: str) -> TrendCategory:
        """根据话题推断分类"""
        tech_keywords = ["AI", "软件", "科技", "互联网", "数据", "算法", "智能"]
        business_keywords = ["马斯克", "特斯拉", "股价", "创业", "公司", "商业"]
        auto_keywords = ["汽车", "新能源", "购车", "驾驶"]
        education_keywords = ["高考", "志愿", "大学", "教育", "考试"]

        topic_lower = topic.lower()

        if any(kw.lower() in topic_lower for kw in tech_keywords):
            return TrendCategory.TECH
        elif any(kw.lower() in topic_lower for kw in business_keywords):
            return TrendCategory.BUSINESS
        elif any(kw.lower() in topic_lower for kw in auto_keywords):
            return TrendCategory.BUSINESS  # 汽车归为商业
        elif any(kw.lower() in topic_lower for kw in education_keywords):
            return TrendCategory.SOCIAL
        else:
            return TrendCategory.UNKNOWN

    def fetch_real_trends(self, limit: int = 20, category: str | None = None) -> list[Trend]:
        """获取真实 Google Trends 热点（需要 pytrends）

        此方法需要安装 pytrends: pip install pytrends

        Args:
            limit: 返回数量
            category: 分类过滤

        Returns:
            热点列表
        """
        requested_category = self.validate_request(limit, category)
        if TrendReq is None:
            raise RuntimeError("pytrends 未安装，无法获取真实 Google Trends 数据")

        try:

            pytrends = TrendReq(hl=self.language, tz=480)

            # 获取实时搜索趋势
            trending_searches = pytrends.trending_searches(pn=self.geo)

            if trending_searches is None or getattr(trending_searches, "empty", True):
                return []
            if getattr(trending_searches, "shape", (0, 0))[1] < 1:
                raise RuntimeError("Google Trends 返回的数据缺少话题列")

            topics = trending_searches.iloc[:, 0].dropna().astype(str)
            trends = []
            now = datetime.now(timezone.utc)
            for row_index, topic in enumerate(topics):
                topic = topic.strip()
                if not topic:
                    continue
                trend = Trend(
                    id=f"gt_real_{now.strftime('%Y%m%d')}_{row_index}",
                    topic=topic,
                    description="Google Trends 搜索趋势",
                    source="Google Trends (Real)",
                    url=f"https://trends.google.com/trends/explore?q={quote_plus(topic)}",
                    category=self._infer_category(topic),
                    keywords=[],
                    metrics=TrendMetrics(
                        # trending_searches only returns ranked terms, not a heat score.
                        heat=0,
                        discussion_count=0,  # Google Trends 不提供讨论量
                        growth_rate=0.0,
                        timestamp=now,
                    ),
                    created_at=now,
                )
                if self.category_matches(trend, requested_category):
                    trends.append(trend)
                if len(trends) >= limit:
                    break

            return trends

        except RuntimeError:
            raise
        except Exception as error:  # noqa: BLE001 - normalize SDK/network errors
            raise RuntimeError("获取真实 Google Trends 数据失败") from error

    def is_available(self) -> bool:
        """检查 Google Trends 是否可用"""
        # The source is always available because fetch() provides sample data.
        return True

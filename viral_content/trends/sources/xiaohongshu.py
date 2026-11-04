"""
小红书热点来源
v4.0 - 从小红书获取热点话题

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from typing import Any

from ..base import BaseTrendSource, Trend, TrendCategory, TrendMetrics


class XiaohongshuTrendSource(BaseTrendSource):
    """小红书热点来源

    注意：实际使用需要小红书 API 或爬虫
    这里提供简化实现和模拟数据
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """初始化小红书来源

        Args:
            config: 配置参数
        """
        super().__init__("小红书", config)

    def fetch(self, limit: int = 20, category: str | None = None) -> list[Trend]:
        """获取小红书热点话题

        Args:
            limit: 返回数量
            category: 分类过滤

        Returns:
            热点列表
        """
        requested_category = self.validate_request(limit, category)
        trends = []

        # 模拟小红书热点话题
        sample_trends = self._get_sample_trends()

        for i, item in enumerate(sample_trends):
            trend = Trend(
                id=f"sample_xiaohongshu_{i}",
                topic=item["topic"],
                description=item.get("description", ""),
                source="sample:小红书",
                url=item.get("url", ""),
                category=self._infer_category(item["topic"], item.get("tags", [])),
                keywords=item.get("tags", []),
                metrics=TrendMetrics(
                    heat=item.get("likes", 0) // 1000,  # 将点赞数转换为热度
                    discussion_count=item.get("comments", 0) + item.get("collects", 0),
                    growth_rate=item.get("growth", 0.0),
                    timestamp=None,
                ),
                content_snippet=item.get("snippet"),
                created_at=None,
            )
            if self.category_matches(trend, requested_category):
                trends.append(trend)
            if len(trends) >= limit:
                break

        return trends

    def _get_sample_trends(self) -> list[dict[str, Any]]:
        """获取示例小红书热点数据（模拟）"""
        return [
            {
                "topic": "2026年流行穿搭趋势",
                "description": "最新穿搭趋势分享",
                "url": "https://xiaohongshu.com/topic/穿搭趋势",
                "tags": ["穿搭", "时尚", "2026流行", "OOTD"],
                "likes": 100000,
                "comments": 5000,
                "collects": 20000,
                "growth": 15.0,
                "snippet": "姐妹们，2026年最火的穿搭风格来了...",
            },
            {
                "topic": "平价好物分享",
                "description": "平价好物种草",
                "url": "https://xiaohongshu.com/topic/平价好物",
                "tags": ["好物", "平价", "种草", "推荐"],
                "likes": 80000,
                "comments": 4000,
                "collects": 15000,
                "growth": 12.0,
                "snippet": "挖到宝了！这些平价好物真的绝绝子...",
            },
            {
                "topic": "减脂食谱一周不重样",
                "description": "健康减脂食谱",
                "url": "https://xiaohongshu.com/topic/减脂食谱",
                "tags": ["减脂", "食谱", "健康", "饮食"],
                "likes": 120000,
                "comments": 6000,
                "collects": 30000,
                "growth": 20.0,
                "snippet": "一周减脂食谱，好吃不胖掉秤快...",
            },
            {
                "topic": "独居生活好物推荐",
                "description": "独居生活必备好物",
                "url": "https://xiaohongshu.com/topic/独居好物",
                "tags": ["独居", "好物", "生活", "居家"],
                "likes": 90000,
                "comments": 4500,
                "collects": 18000,
                "growth": 10.0,
                "snippet": "独居女孩提升幸福感的10件好物...",
            },
            {
                "topic": "职场通勤穿搭",
                "description": "职场通勤穿搭指南",
                "url": "https://xiaohongshu.com/topic/通勤穿搭",
                "tags": ["职场", "通勤", "穿搭", "OL"],
                "likes": 70000,
                "comments": 3500,
                "collects": 12000,
                "growth": 8.0,
                "snippet": "职场通勤穿搭，得体又时尚...",
            },
        ]

    def _infer_category(self, topic: str, tags: list[str]) -> TrendCategory:
        """根据话题和标签推断分类"""
        fashion_keywords = ["穿搭", "时尚", "服装", "OOTD", "搭配"]
        beauty_keywords = ["美妆", "护肤", "彩妆", "美容", "妆容"]
        lifestyle_keywords = ["好物", "家居", "生活", "居家", "独居"]
        food_keywords = ["食谱", "美食", "减脂", "饮食", "做饭"]
        work_keywords = ["职场", "工作", "通勤", "办公", "OL"]

        all_text = topic.lower() + " " + " ".join(tags).lower()

        if (
            any(kw.lower() in all_text for kw in fashion_keywords)
            or any(kw.lower() in all_text for kw in beauty_keywords)
            or any(kw.lower() in all_text for kw in lifestyle_keywords)
            or any(kw.lower() in all_text for kw in food_keywords)
        ):
            return TrendCategory.LIFESTYLE
        elif any(kw.lower() in all_text for kw in work_keywords):
            return TrendCategory.BUSINESS
        else:
            return TrendCategory.UNKNOWN

    def is_available(self) -> bool:
        """检查小红书是否可用"""
        return True

"""
TikTok 热点来源
v4.0 - 从 TikTok 获取热点话题

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from datetime import datetime, timezone
from typing import Any

from ..base import BaseTrendSource, Trend, TrendCategory, TrendMetrics


class TikTokTrendSource(BaseTrendSource):
    """TikTok 热点来源

    注意：实际使用需要 TikTok API 或第三方服务
    这里提供简化实现和模拟数据
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """初始化 TikTok 来源

        Args:
            config: 配置参数（region: 地区, language: 语言）
        """
        super().__init__("TikTok", config)
        self.region = config.get("region", "US") if config else "US"
        self.language = config.get("language", "en") if config else "en"

    def fetch(
        self,
        limit: int = 20,
        category: str | None = None
    ) -> list[Trend]:
        """获取 TikTok 热点话题

        Args:
            limit: 返回数量
            category: 分类过滤

        Returns:
            热点列表
        """
        # 简化实现：返回模拟数据
        trends = []

        # 模拟 TikTok 热点话题
        sample_trends = self._get_sample_trends()

        for i, item in enumerate(sample_trends[:limit]):
            trend = Trend(
                id=f"tiktok_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{i}",
                topic=item["topic"],
                description=item.get("description", ""),
                source="TikTok",
                url=item.get("url", ""),
                category=self._infer_category(item["topic"], item.get("hashtags", [])),
                keywords=item.get("hashtags", []),
                metrics=TrendMetrics(
                    heat=item.get("views", 0) // 10000,  # 将播放量转换为热度
                    discussion_count=item.get("engagement", 0),
                    growth_rate=item.get("growth", 0.0),
                    timestamp=datetime.now(timezone.utc)
                ),
                content_snippet=item.get("snippet"),
                created_at=datetime.now(timezone.utc)
            )
            trends.append(trend)

        return trends

    def _get_sample_trends(self) -> list[dict[str, Any]]:
        """获取示例 TikTok 热点数据（模拟）"""
        return [
            {
                "topic": "#AI工具使用技巧",
                "description": "AI 工具相关视频爆火",
                "url": "https://tiktok.com/tag/AI工具",
                "hashtags": ["AI工具", "生产力", "ChatGPT", "技巧"],
                "views": 5000000,
                "engagement": 500000,
                "growth": 20.5,
                "snippet": "用AI工具提升10倍工作效率的秘密..."
            },
            {
                "topic": "#2026年趋势预测",
                "description": "各行业2026年趋势预测",
                "url": "https://tiktok.com/tag/2026趋势",
                "hashtags": ["趋势", "预测", "2026", "未来"],
                "views": 3500000,
                "engagement": 300000,
                "growth": 15.0,
                "snippet": "这些行业将在2026年迎来爆发..."
            },
            {
                "topic": "#居家健身挑战",
                "description": "居家健身挑战赛",
                "url": "https://tiktok.com/tag/居家健身",
                "hashtags": ["健身", "居家", "挑战", "运动"],
                "views": 8000000,
                "engagement": 800000,
                "growth": 8.0,
                "snippet": "7天居家健身挑战，第1天..."
            },
            {
                "topic": "#创业故事分享",
                "description": "创业者分享真实经历",
                "url": "https://tiktok.com/tag/创业故事",
                "hashtags": ["创业", "故事", "经验", "商业"],
                "views": 2000000,
                "engagement": 200000,
                "growth": 12.0,
                "snippet": "从0到100万，我的创业故事..."
            },
            {
                "topic": "#美食制作教程",
                "description": "简单美食制作教程",
                "url": "https://tiktok.com/tag/美食教程",
                "hashtags": ["美食", "教程", "烹饪", "食谱"],
                "views": 10000000,
                "engagement": 1000000,
                "growth": 5.5,
                "snippet": "5分钟搞定豪华晚餐..."
            },
        ]

    def _infer_category(self, topic: str, hashtags: list[str]) -> TrendCategory:
        """根据话题和标签推断分类"""
        tech_keywords = ["AI", "工具", "软件", "科技", "数字"]
        business_keywords = ["创业", "商业", "赚钱", "副业"]
        lifestyle_keywords = ["健身", "美食", "居家", "生活"]
        entertainment_keywords = ["搞笑", "娱乐", "明星", "电影"]

        topic_lower = topic.lower()
        all_keywords = topic_lower + " " + " ".join(hashtags).lower()

        if any(kw in all_keywords for kw in tech_keywords):
            return TrendCategory.TECH
        elif any(kw in all_keywords for kw in business_keywords):
            return TrendCategory.BUSINESS
        elif any(kw in all_keywords for kw in lifestyle_keywords):
            return TrendCategory.LIFESTYLE
        elif any(kw in all_keywords for kw in entertainment_keywords):
            return TrendCategory.ENTERTAINMENT
        else:
            return TrendCategory.UNKNOWN

    def is_available(self) -> bool:
        """检查 TikTok 是否可用"""
        # 简化实现：总是返回 True（使用模拟数据）
        # 实际应用中应该检查 API 连接
        return True

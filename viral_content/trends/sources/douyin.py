"""
抖音热点来源
v4.0 - 从抖音获取热点话题

作者: Sunnyeung
版本: 4.1.4
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from datetime import datetime, timezone
from typing import Any

from ..base import BaseTrendSource, Trend, TrendCategory, TrendMetrics


class DouyinTrendSource(BaseTrendSource):
    """抖音热点来源

    注意：实际使用需要抖音 API 或第三方服务
    这里提供简化实现和模拟数据
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """初始化抖音来源

        Args:
            config: 配置参数
        """
        super().__init__("抖音", config)

    def fetch(self, limit: int = 20, category: str | None = None) -> list[Trend]:
        """获取抖音热点话题

        Args:
            limit: 返回数量
            category: 分类过滤

        Returns:
            热点列表
        """
        trends = []

        # 模拟抖音热点话题
        sample_trends = self._get_sample_trends()

        for i, item in enumerate(sample_trends[:limit]):
            trend = Trend(
                id=f"sample_douyin_{i}",
                topic=item["topic"],
                description=item.get("description", ""),
                source="sample:抖音",
                url=item.get("url", ""),
                category=self._infer_category(item["topic"], item.get("hashtags", [])),
                keywords=item.get("hashtags", []),
                metrics=TrendMetrics(
                    heat=item.get("heat", 50),
                    discussion_count=item.get("comments", 0) + item.get("shares", 0),
                    growth_rate=item.get("growth", 0.0),
                    timestamp=None,
                ),
                content_snippet=item.get("snippet"),
                created_at=None,
            )
            trends.append(trend)

        return trends

    def _get_sample_trends(self) -> list[dict[str, Any]]:
        """获取示例抖音热点数据（模拟）"""
        return [
            {
                "topic": "#2026高考志愿填报",
                "description": "高考志愿填报相关内容爆火",
                "url": "https://douyin.com/challenge/高考志愿",
                "hashtags": ["高考志愿", "填报", "大学", "专业"],
                "heat": 92,
                "comments": 50000,
                "shares": 30000,
                "growth": 25.0,
                "snippet": "志愿填报避坑指南，这几点一定要知道...",
            },
            {
                "topic": "#AI副业赚钱",
                "description": "AI副业赚钱方法",
                "url": "https://douyin.com/challenge/AI副业",
                "hashtags": ["AI副业", "赚钱", "副业", "AI工具"],
                "heat": 88,
                "comments": 30000,
                "shares": 20000,
                "growth": 18.5,
                "snippet": "用AI工具每天多赚500元的方法...",
            },
            {
                "topic": "#职场生存指南",
                "description": "职场生存技巧分享",
                "url": "https://douyin.com/challenge/职场指南",
                "hashtags": ["职场", "生存", "技巧", "工作"],
                "heat": 75,
                "comments": 15000,
                "shares": 10000,
                "growth": 10.0,
                "snippet": "职场人必看的5条生存法则...",
            },
            {
                "topic": "#短视频爆款公式",
                "description": "短视频爆款创作方法",
                "url": "https://douyin.com/challenge/爆款公式",
                "hashtags": ["短视频", "爆款", "创作", "公式"],
                "heat": 82,
                "comments": 25000,
                "shares": 18000,
                "growth": 12.5,
                "snippet": "3个简单公式，让你的视频轻松10万+...",
            },
            {
                "topic": "#宝妈创业故事",
                "description": "宝妈创业真实经历",
                "url": "https://douyin.com/challenge/宝妈创业",
                "hashtags": ["宝妈", "创业", "故事", "女性"],
                "heat": 78,
                "comments": 20000,
                "shares": 15000,
                "growth": 8.0,
                "snippet": "从全职宝妈到月入5万，我的创业路...",
            },
        ]

    def _infer_category(self, topic: str, hashtags: list[str]) -> TrendCategory:
        """根据话题和标签推断分类"""
        tech_keywords = ["AI", "科技", "数字化", "智能"]
        business_keywords = ["创业", "副业", "赚钱", "商业", "职场"]
        education_keywords = ["高考", "志愿", "大学", "学习", "教育"]
        lifestyle_keywords = ["宝妈", "生活", "育儿", "家庭"]

        all_text = topic.lower() + " " + " ".join(hashtags).lower()

        if any(kw in all_text for kw in tech_keywords):
            return TrendCategory.TECH
        elif any(kw in all_text for kw in business_keywords):
            return TrendCategory.BUSINESS
        elif any(kw in all_text for kw in education_keywords):
            return TrendCategory.SOCIAL
        elif any(kw in all_text for kw in lifestyle_keywords):
            return TrendCategory.LIFESTYLE
        else:
            return TrendCategory.UNKNOWN

    def is_available(self) -> bool:
        """检查抖音是否可用"""
        return True

"""
热点引擎基类
v4.0 - 热点情报引擎

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TrendCategory(Enum):
    """热点分类"""

    TECH = "tech"  # 科技
    BUSINESS = "business"  # 商业
    ENTERTAINMENT = "entertainment"  # 娱乐
    SPORTS = "sports"  # 体育
    POLITICAL = "political"  # 政治
    SOCIAL = "social"  # 社会
    LIFESTYLE = "lifestyle"  # 生活
    UNKNOWN = "unknown"  # 未知


@dataclass
class TrendMetrics:
    """热点指标"""

    heat: int = 0  # 热度 (0-100)
    discussion_count: int = 0  # 讨论量
    growth_rate: float = 0.0  # 增长率
    timestamp: datetime | None = None  # 时间戳

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "热度": self.heat,
            "讨论量": self.discussion_count,
            "增长率": self.growth_rate,
            "时间戳": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class Trend:
    """热点数据"""

    id: str  # 唯一标识
    topic: str  # 话题标题
    description: str = ""  # 描述
    source: str = ""  # 来源平台
    url: str = ""  # 原始链接
    category: TrendCategory = TrendCategory.UNKNOWN  # 分类
    keywords: list[str] = field(default_factory=list)  # 关键词
    metrics: TrendMetrics | None = None  # 热度指标
    content_snippet: str | None = None  # 内容片段
    related_topics: list[str] = field(default_factory=list)  # 相关话题
    created_at: datetime | None = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # 抓取时间

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "source": self.source,
            "url": self.url,
            "category": (
                self.category.value if isinstance(self.category, TrendCategory) else self.category
            ),
            "keywords": self.keywords,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "content_snippet": self.content_snippet,
            "related_topics": self.related_topics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Trend":
        """从字典创建

        Args:
            data: 字典数据

        Returns:
            Trend实例
        """

        def parse_datetime(value: str) -> datetime:
            # Python 3.10 does not consistently accept the ISO-8601 Z suffix.
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        # 处理category
        category = data.get("category", "unknown")
        if isinstance(category, str):
            try:
                category = TrendCategory(category)
            except ValueError:
                category = TrendCategory.UNKNOWN

        # 处理metrics
        metrics_data = data.get("metrics")
        metrics = None
        if metrics_data:
            metrics = TrendMetrics(
                heat=metrics_data.get("热度", 0),
                discussion_count=metrics_data.get("讨论量", 0),
                growth_rate=metrics_data.get("增长率", 0.0),
                timestamp=(
                    parse_datetime(metrics_data["时间戳"]) if metrics_data.get("时间戳") else None
                ),
            )

        return cls(
            id=data.get("id", ""),
            topic=data.get("topic", ""),
            description=data.get("description", ""),
            source=data.get("source", ""),
            url=data.get("url", ""),
            category=category,
            keywords=data.get("keywords", []),
            metrics=metrics,
            content_snippet=data.get("content_snippet"),
            related_topics=data.get("related_topics", []),
            **(
                {"created_at": (parse_datetime(data["created_at"]) if data["created_at"] else None)}
                if "created_at" in data
                else {}
            ),
        )


class BaseTrendSource(ABC):
    """热点来源基类

    所有热点来源必须实现：
    - fetch(): 获取热点列表
    - normalize(): 标准化热点数据
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        """初始化热点来源

        Args:
            name: 来源名称
            config: 配置参数（API密钥等）
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def fetch(self, limit: int = 20, category: str | None = None) -> list[Trend]:
        """获取热点列表

        Args:
            limit: 返回数量限制
            category: 分类过滤（可选）

        Returns:
            热点列表
        """

    def normalize(self, raw_data: Any) -> Trend:
        """标准化原始数据为Trend对象

        Args:
            raw_data: 原始数据

        Returns:
            标准化的Trend对象
        """
        # 子类可以覆盖此方法实现特定转换

    def get_source_name(self) -> str:
        """获取来源名称"""
        return self.name

    def is_available(self) -> bool:
        """检查来源是否可用"""
        return True

    @staticmethod
    def validate_request(limit: int, category: str | TrendCategory | None) -> TrendCategory | None:
        """Validate the shared fetch contract and normalize a category filter."""
        if type(limit) is not int or limit < 1:
            raise ValueError("limit 必须是正整数")
        if category is None:
            return None
        if isinstance(category, TrendCategory):
            return category
        if not isinstance(category, str):
            raise ValueError("category 必须是有效分类字符串")
        try:
            return TrendCategory(category)
        except ValueError as error:
            raise ValueError(f"未知分类: {category}") from error

    @staticmethod
    def category_matches(trend: Trend, category: TrendCategory | None) -> bool:
        return category is None or trend.category == category


class TrendAggregator:
    """热点聚合器

    从多个来源聚合热点数据
    """

    def __init__(self, sources: list[BaseTrendSource] | None = None):
        """初始化聚合器

        Args:
            sources: 热点来源列表
        """
        self.sources = sources or []

    def fetch_all(
        self,
        limit_per_source: int = 10,
        category: str | None = None,
        *,
        strict: bool = True,
    ) -> dict[str, list[Trend]]:
        """从所有来源获取热点

        Args:
            limit_per_source: 每个来源的限制
            category: 分类过滤

        Returns:
            按来源分组的热点字典
        """
        BaseTrendSource.validate_request(limit_per_source, category)
        results = {}

        for source in self.sources:
            try:
                if source.is_available():
                    trends = source.fetch(limit=limit_per_source, category=category)
                    results[source.get_source_name()] = trends
                else:
                    results[source.get_source_name()] = []
            except Exception as error:  # noqa: BLE001 - source plugins have varied errors
                if strict:
                    raise RuntimeError(f"获取{source.get_source_name()}热点失败") from error
                results[source.get_source_name()] = []

        return results

    def merge_and_rank(self, all_trends: dict[str, list[Trend]], limit: int = 50) -> list[Trend]:
        """合并并排序所有热点

        Args:
            all_trends: 按来源分组的热点
            limit: 返回数量限制

        Returns:
            合并排序后的热点列表
        """
        if type(limit) is not int or limit < 1:
            raise ValueError("limit 必须是正整数")
        if not isinstance(all_trends, dict):
            raise ValueError("all_trends 必须是按来源分组的字典")

        # 收集所有热点
        merged = []

        for source_name, trends in all_trends.items():
            for trend in trends:
                # Never erase explicit provenance such as sample: or a live API label.
                if not trend.source:
                    trend.source = source_name
                merged.append(trend)

        # 按热度排序
        merged.sort(key=lambda t: t.metrics.heat if t.metrics else 0, reverse=True)

        # 去重（按话题相似度）
        unique = []
        seen_topics = set()

        for trend in merged:
            # 简单去重：完全相同的标题
            if trend.topic not in seen_topics:
                unique.append(trend)
                seen_topics.add(trend.topic)

            if len(unique) >= limit:
                break

        return unique

    def fetch_merged(
        self,
        limit_per_source: int = 10,
        final_limit: int = 50,
        category: str | None = None,
        *,
        strict: bool = True,
    ) -> list[Trend]:
        """获取并合并热点（便捷方法）

        Args:
            limit_per_source: 每个来源的限制
            final_limit: 最终返回数量
            category: 分类过滤

        Returns:
            合并排序后的热点列表
        """
        all_trends = self.fetch_all(limit_per_source, category, strict=strict)
        return self.merge_and_rank(all_trends, final_limit)

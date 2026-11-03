"""Candidate experiments and outcome feedback models."""

import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Candidate:
    content: str
    quality_score: float
    passed_gate: bool
    index: int = 0
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class FeedbackRecord:
    candidate_index: int
    platform: str
    published_at: str
    impressions: int | None = None
    views: int | None = None
    comments: int | None = None
    leads: int | None = None
    conversions: int | None = None
    source: str = "manual"
    publication_id: str | None = None
    observed_at: str | None = None
    window_hours: int | None = None
    account_id: str | None = None
    traffic_type: str = "unknown"
    denominator: str = "impressions"

    def to_dict(self) -> dict[str, object]:
        return {k: v for k, v in self.__dict__.items()}


class CandidateRanker:
    """Explainable ranking with goal-specific weights."""

    DEFAULT_WEIGHTS: ClassVar[dict[str, tuple[float, float]]] = {
        "likes": (0.55, 0.45),
        "comments": (0.50, 0.50),
        "leads": (0.40, 0.60),
        "sales": (0.35, 0.65),
    }
    PLATFORM_BIAS: ClassVar[dict[str, float]] = {
        "douyin": 0.15,
        "xiaohongshu": 0.10,
        "bilibili": 0.05,
        "wechat": 0.0,
        "zhihu": -0.05,
    }

    def __init__(self, goal: str = "leads", platform: str = "wechat", weights: tuple | None = None):
        self.goal = goal
        bias = self.PLATFORM_BIAS.get(platform, 0.0)
        base_quality, _ = weights or self.DEFAULT_WEIGHTS.get(goal, (0.5, 0.5))
        self.quality_weight = min(0.8, max(0.2, base_quality + bias))
        self.gate_weight = 1.0 - self.quality_weight

    def describe(self) -> dict[str, object]:
        return {
            "goal": self.goal,
            "quality_weight": self.quality_weight,
            "gate_weight": self.gate_weight,
        }

    def rank(self, candidates: list[Candidate]) -> list[Candidate]:
        return sorted(
            candidates,
            key=lambda c: self.quality_weight * c.quality_score
            + self.gate_weight * (10.0 if c.passed_gate else 0.0),
            reverse=True,
        )


@dataclass
class ExperimentSummary:
    platform: str
    sample_size: int
    winner_index: int | None
    metrics: dict[int, dict[str, object]]
    reliable: bool
    note: str


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    # Legacy date-only records use midnight UTC; explicit timestamps must include a zone.
    if parsed.tzinfo is None:
        if len(value) != 10:
            raise ValueError("反馈时间必须带时区，或使用 YYYY-MM-DD")
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def summarize_feedback(records: list[FeedbackRecord], min_samples: int = 3) -> ExperimentSummary:
    """Report independent observations; never infer significance or causation.

    Counts are cumulative snapshots, not increments. Explicit publication IDs
    select the latest snapshot within the same observation window and context.
    Legacy records without IDs remain separate observations, with unknown identity.
    The export retains all input records, including superseded snapshots.
    """
    if min_samples < 1:
        raise ValueError("min_samples 必须大于零")
    if not records:
        return ExperimentSummary("unknown", 0, None, {}, False, "暂无发布反馈")
    selected = {}
    seen = set()
    for index, record in enumerate(records):
        for name in ("impressions", "views", "comments", "leads", "conversions"):
            value = getattr(record, name)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"{name} 必须为非负整数或 null")
        if record.denominator not in {"impressions", "views"}:
            raise ValueError("denominator 必须为 impressions 或 views")
        if record.window_hours is not None and (
            type(record.window_hours) is not int or record.window_hours <= 0
        ):
            raise ValueError("window_hours 必须为正整数或 null")
        published = _timestamp(record.published_at)
        observed = _timestamp(record.observed_at) if record.observed_at else published
        if observed < published:
            raise ValueError("观察时间不能早于发布时间")
        fingerprint = json.dumps(record.to_dict(), sort_keys=True)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        key = (
            record.platform,
            record.account_id,
            record.publication_id,
            record.window_hours,
            record.traffic_type,
            record.denominator,
        )
        if not record.publication_id:
            key = (*key, index)
        if key in selected:
            previous, previous_time = selected[key]
            if (previous.candidate_index, previous.published_at) != (
                record.candidate_index,
                record.published_at,
            ):
                raise ValueError("同一作品的候选身份或发布时间冲突")
            if not previous.observed_at or not record.observed_at:
                raise ValueError("同一作品的多个快照必须提供 observed_at")
            if observed == previous_time:
                raise ValueError("同一作品同一观察时间存在冲突快照")
            if observed < previous_time:
                continue
        selected[key] = (record, observed)
    metrics = {}
    for index, (record, _) in enumerate(selected.values()):
        denominator = getattr(record, record.denominator)
        item = record.to_dict()
        item["denominator_value"] = denominator
        for metric, numerator_name in (
            ("engagement_rate", "comments"),
            ("lead_rate", "leads"),
            ("conversion_rate", "conversions"),
        ):
            numerator = getattr(record, numerator_name)
            item[metric] = (
                100 * numerator / denominator
                if denominator is not None and denominator > 0 and numerator is not None
                else None
            )
        metrics[index] = item
    platforms = {r.platform for r, _ in selected.values()}
    platform = next(iter(platforms)) if len(platforms) == 1 else "mixed"
    note = (
        "描述性记录，不选择胜者、不证明因果或统计可靠性；"
        "比率使用记录明确指定的分母，缺失值为 null；"
        "不同作品、平台、账号及观察窗口分别列出，不合并。"
    )
    if len(selected) < min_samples:
        note += f" 样本量少于 {min_samples} 条。"
    return ExperimentSummary(platform, len(selected), None, metrics, False, note)


def export_feedback_report(
    records: list[FeedbackRecord], path: str, min_samples: int = 3
) -> ExperimentSummary:
    """Write a portable JSON report and return its summary."""
    summary = summarize_feedback(records, min_samples=min_samples)
    payload = {
        "summary": {
            "platform": summary.platform,
            "sample_size": summary.sample_size,
            "winner_index": summary.winner_index,
            "metrics": summary.metrics,
            "reliable": summary.reliable,
            "note": summary.note,
        },
        "records": [r.to_dict() for r in records],
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return summary

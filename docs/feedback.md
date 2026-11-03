# 发布反馈的口径

反馈只汇总实际提交的数据，不预测流量，不自动判断因果或统计显著性。

每条 `FeedbackRecord` 对应一份累计观察数据。建议同时提供：

- `publication_id`：平台作品 ID；同一候选发布为不同作品时使用不同 ID。
- `account_id`、`platform`、`traffic_type`：账号、平台及流量类型。
- `published_at`：发布时间。
- `observed_at`：采集累计数据的时间，使用带时区的 ISO 时间。
- `window_hours`：本次比较约定的观察窗口；不同窗口分别展示。
- `denominator`：明确选择 `impressions`（默认）或 `views`。

`engagement_rate` 当前指评论数/指定分母；`lead_rate` 为线索数/指定分母；`conversion_rate` 为成交数/指定分母。返回值单位为百分比。这些分子可能是次数，不能自动解释为独立用户占比或线索到成交转化率。

缺分子、缺分母或分母为零时，比率为 `null`。不会把缺失计数补成零，也不会把零曝光换成阅读量。调用方若需要按阅读计算，必须明确指定 `denominator="views"`。

不同作品、平台、账号、流量类型和观察窗口不混合计算。同一作品相同上下文有多个累计快照时，采用最新 `observed_at` 的整条快照，不累加。快照时间缺失、相同时间数据冲突或作品身份冲突会报错。完全相同的记录去重。未提供作品 ID 的旧记录保留为独立观察，不能据此推断独立作品数量。

`summary.metrics` 的键是本次报告的观察序号，不再用候选序号作为唯一键；每项包含原来的 `candidate_index`、作品信息、计数、分母及比率。`sample_size` 是去重和快照选择后的观察数。

`winner_index` 始终为 `null`，`reliable` 始终为 `false`。这两个旧字段仅为兼容保留；三条自然发布记录不能证明胜者或可靠性。`min_samples` 仅控制少量观察的文字提示，不是统计门槛。

`export_feedback_report` 的 `records` 保存全部输入，包括被较新快照取代的记录，方便核验；`summary` 保存上述描述性结果。

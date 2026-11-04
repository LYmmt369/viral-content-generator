# 可复现案例：同一选题的目标切换

## 输入

```text
AI 工具让团队少开一半无效会议
```

## 旧做法

只要求模型“写一篇爆款文章”，没有账号定位、平台和行动目标。结果通常观点泛化，难以比较，也无法知道下一轮该改什么。

## 新做法

```bash
python examples/local_demo.py
python viral_content_cli.py \
  --topic "AI 工具让团队少开一半无效会议" \
  --goal leads \
  --platform xiaohongshu \
  --style-mix "tech_explainer_global,business_savage_china" \
  --variants 3
```

先用本地 Demo 验证规则，再接入模型生成多个候选。发布后把真实曝光、互动和线索填入 `FEEDBACK.md`，下一轮只调整一个变量。

## 如何比较

| 项目 | 旧做法 | 新做法 |
|---|---|---|
| 输入 | 只有主题 | 主题 + 目标 + 平台 + 风格 |
| 输出 | 单个草稿 | 多候选、质量门和明确的长度参考选择 |
| 复盘 | 凭感觉修改 | 记录真实反馈后做下一轮实验 |

这里展示的是工作流差异，不是曝光或成交保证。

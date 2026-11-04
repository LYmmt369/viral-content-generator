# LYmmt369 Viral Content Generator 4.1.3 API

安装：在仓库根目录运行 `pip install .`。模型调用需要对应环境变量密钥。下列 YOUR_MODEL 替换为账号可用模型。

## Python 生成

```python
from viral_content import ViralContentPipeline
from viral_content.models import GenerationConfig

pipeline = ViralContentPipeline()
config = GenerationConfig(topic="项目案例", platform="openai", model="YOUR_MODEL")
result = pipeline.run(
    topic="项目案例", account="data/accounts/default_account.yaml",
    offer="data/offers/default_offer.yaml", style_mix="tech_explainer_global",
    goal="leads", platform="xiaohongshu", config=config,
)
print(result.content)
```

account 和 offer 可为 YAML 路径、配置字典或对应数据模型；省略则不注入。style_mix 可为逗号分隔的风格 ID 或列表。配置所有字段进入提示词，这不保证模型服从所有限制。未知风格、平台、无效配置和全部候选失败会抛出异常。

`GenerationConfig` 的 platform 是模型提供方，run 的 platform 是内容平台。variants 范围 1–8。截断或检查失败的候选不交付。选择依据只是长度参考，不预测内容价值或发布效果。

## 多平台

```python
results = pipeline.run_batch(
    trends=[{"topic": "项目案例"}], platforms=["wechat", "xiaohongshu"],
    account="data/accounts/default_account.yaml", goal="likes", config=config,
)
for result in results:
    print(result.content_platform, result.content)
```

返回逐主题、逐平台的独立结果；失败抛出异常，不静默跳过。Python API 返回对象，不自动写文件。

```bash
viral-content --topic "项目案例" --platform wechat xiaohongshu --ai-platform openai --model YOUR_MODEL --output drafts/
```

CLI 与 Python API 使用同一生成与检查流程。目录输出各平台独立文件；文件名 draft.md 对多平台扩展为 draft.wechat.md 等。全部检查通过才写出；写入失败回滚本次新建文件。禁止覆盖已有输出。--stream 当前明确拒绝，避免检查前输出草稿。批量主题命令逐主题记录成功或失败，有失败时退出码为 1。指定文件 draft.md 时按主题顺序写入 draft.1.md、draft.2.md；多平台再添加平台后缀。

## 平台转换

`PlatformAdapter.convert_to_platform(content, from_platform, to_platform)` 只构建转换提示词，返回值不是成稿。

`batch_convert(content, from_platform, to_platforms, generator_func)` 必须提供实际生成回调；回调签名为 `(prompt, platform) -> str`。返回 `PlatformPackage` 列表，content 是生成后检查通过的文字。`generate_package` 同样要求回调，签名 `(prompt, platform, **kwargs) -> str`。没有回调或内容未通过检查时明确报错。

## 成稿、改稿和撤回

见[精准改稿](precise-revisions.md)。这些命令与 [SKILL.md](../SKILL.md) 使用相同的版本指纹、替换范围及回执机制。

## 发布反馈

见[反馈口径](feedback.md)：原始记录完整保留；缺数据为 null；不同作品及观察窗口分别展示；累计快照不相加；不自动宣称胜者或统计可靠性。

## 趋势源

抖音、小红书、TikTok 及 Google Trends 的 `fetch()` 当前返回内置示例，`source` 以 `sample:` 开头，`created_at` 和指标时间为 null。示例不能作为实时热点或真实表现数据。Google Trends 的可选 `fetch_real_trends()` 单独依赖 pytrends；依赖缺失时会明确提示并返回已标记的示例。

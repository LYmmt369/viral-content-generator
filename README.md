# Viral Content Generator v4.1.5

**用自己的材料成稿，再按作者意图精准改好。**

提供材料和一句要求，直接生成稿件；提供稿件和一句改法，模型提出有限修改，程序检查后生成新稿、差异和撤回记录。

[English](README.en.md) · [使用说明](docs/precise-revisions.md) · [更新记录](CHANGELOG.md)

## 先看一个无需 Key 的示例

Python 3.10–3.12：

```bash
python examples/direct_drafting_demo.py --output output/direct-demo
```

示例使用明确标注的固定模型回复，演示材料成稿、局部修改和准确撤回。它不调用云服务，不代表真实模型的写作表现。编辑边界的独立示例见 [precise_revision_demo.py](examples/precise_revision_demo.py)。

## 安装与模型配置

```bash
pip install .
```

设置所选服务的环境变量：OpenAI 使用 OPENAI_API_KEY，Claude 使用 ANTHROPIC_API_KEY，Gemini 使用 GOOGLE_API_KEY 或 GEMINI_API_KEY。也可使用项目专用的 VIRAL_API_KEY。密钥不写进命令参数、稿件或回执。

以下命令中的 YOUR_MODEL 要替换为账号可用的模型标识。OpenAI 适配使用 Chat Completions 接口。也可通过 VIRAL_PROVIDER 和 VIRAL_MODEL 设置提供方与模型。

## 从材料成稿

```bash
viral-revise write examples/materials.md "写成一篇简洁的项目介绍，保留材料中的事实范围" --provider openai --model YOUR_MODEL --output draft.md
```

输出完整稿件和 draft.md.sources.json。来源记录保存材料文件名、材料与成稿的版本指纹、写作要求和模型标识。

这个入口只使用明确提交的材料；不自动搜索，不建立知识库，不主动访谈。材料缺口要求模型标明【待核实】，不会把草稿标为已核验事实。

## 一句话改稿

```bash
viral-revise edit draft.md "只压缩冗长句，保留原有立场" --provider openai --model YOUR_MODEL --output revised.md
```

需要保护特定原句时，加 --protect "原稿中必须保留的原句"，可重复使用。保护文字必须逐字取自原稿。

模型只返回有限替换。程序会核对原稿版本、唯一原句、重叠范围和保护范围；通过后才保存新稿、revised.md.diff 和 revised.md.receipt.json。

- 替换范围之外的文字逐字保持，包括 BOM、换行、空格。
- 模型不能取消调用方设置的保护，也不能选择其他原稿版本。
- 修改目标不明确、版本变化或模型回复无效时，返回错误并保留原稿。
- 每条请求只有一次模型生成尝试，不自动路由 Skill、追问或扩大工作流。

**程序保证修改边界，模型负责理解改法。** 是否选对修改位置、是否写得更好，仍应看差异；未保护的事实不等于经过事实核查。

## 撤回与已有修改提议

```bash
viral-revise revert revised.md revised.md.receipt.json --output restored.md
viral-revise fingerprint draft.md
viral-revise apply draft.md edits.json --output revised.md
```

撤回同时核验修改后与恢复后的版本指纹。原稿和已有输出不会被覆盖。fingerprint、apply、revert 和本地演示只使用 Python 标准库；源代码中可用 python viral_content_revision.py 代替 viral-revise。

## 当前范围

项目聚焦材料成稿与单篇稿件的精准迭代。没有自动 Skill 路由、主动访谈、通用商业诊断、多 Agent 编排或后台任务。新入口通过显式提示直接调用现有模型适配器，不加载旧 Skill 方法库。

v4 的风格卡、账号、产品与单平台生成接口继续保留。CLI 与 Python API 共用生成流程，支持一次请求多个内容平台，全部通过检查后分别保存；质量检查失败的候选不再保存。旧的长度参考值不能预测内容质量、流量或成交。

## 验证与维护

```bash
python -m pytest -q
python scripts/check_docs.py
python scripts/check_secrets.py
python -m build --wheel
```

[验收范围与方法](docs/v4.1-validation.md) · [当前路线](docs/v4.1-roadmap.md) · [旧规则演示](examples/local_demo.py) · [v4 文档](docs/v4.0_升级说明.md) · [引用信息](CITATION.cff) · [贡献指南](CONTRIBUTING.md)

MIT License。项目不承诺爆款、成交或自动事实核查。

## 配置与多平台

```bash
viral-content --topic "项目案例" --account data/accounts/default_account.yaml --style tech_explainer_global --platform wechat xiaohongshu --ai-platform openai --model YOUR_MODEL --output drafts/
```

目录输出使用各平台独立文件名；若指定 draft.md，多平台输出为 draft.wechat.md、draft.xiaohongshu.md。已有文件不会覆盖。非流式生成通过检查后交付，--stream 暂不支持。

[Skill 入口](SKILL.md) · [当前 API](docs/API文档.md) · [反馈口径](docs/feedback.md)

批量主题若指定文件路径 draft.md，将按主题顺序写入 draft.1.md、draft.2.md；每个主题的多平台文件再加平台后缀。

旧趋势源中的抖音、小红书、TikTok 和 Google Trends `fetch()` 当前返回**内置示例**；返回值明确标为 `sample:`，不作为实时平台数据。

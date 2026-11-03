# 精准改稿：一个轻量的执行内核

本项目接下来的核心是：围绕一篇稿件，做好生成与精准修改。先把“只改指定位置、保留已认可内容、改动可撤回”做成可运行的行为。

v4.1.0 已接通材料成稿和自然语言改稿。程序核验修改边界与版本；它不判断事实真伪，不预测流量。

## 怎样使用

无需安装依赖、配置 Key 或回答问题，直接运行：

```bash
python examples/precise_revision_demo.py --output output/revision-demo
```

演示数据是虚构的。输出包含原稿、两处修改后的稿件、逐项改动记录、阅读用 diff、恢复稿和检查结果。尝试把受保护的“5人”改成“50人”时会被拒绝；恢复稿与原稿的 UTF-8 字节完全一致。

完整的离线流程示例使用固定模型回复，不调用云服务：

```bash
python examples/direct_drafting_demo.py --output output/direct-demo
```

## 直接使用自然语言

安装项目并设置所选服务的 API Key 环境变量。OpenAI 使用 OPENAI_API_KEY，Claude 使用 ANTHROPIC_API_KEY，Gemini 使用 GOOGLE_API_KEY 或 GEMINI_API_KEY。VIRAL_API_KEY 可作为项目专用覆盖值。提供方和模型也可通过 VIRAL_PROVIDER、VIRAL_MODEL 设置。

```bash
viral-revise write notes.md "根据材料写一篇项目介绍" --provider openai --model YOUR_MODEL --output draft.md
viral-revise edit draft.md "只压缩冗长句" --provider openai --model YOUR_MODEL --output revised.md
```

YOUR_MODEL 替换为账号可用的模型标识；OpenAI 适配使用 Chat Completions。--max-tokens 设置输出预算，--timeout 设置请求超时秒数。保护原句使用可重复的 --protect 参数。

write 输出稿件和来源版本记录；edit 输出新稿、diff 和撤回回执。两条路径每次只执行一次模型生成尝试，显式提示不加载旧 Skill 方法库。已有输出或缺失保护原句会在请求前拒绝；模型返回后再次核对源文件版本。

稿件和明确提交的材料会发送给所选模型服务。程序不自动搜集目录、读取其他资料或把密钥写入产物。现有 Gemini 适配仍使用仓库已有的旧 SDK；本次没有做 SDK 迁移。

在已有安装中，也可以使用新增的命令入口：

```bash
viral-revise fingerprint draft.md
viral-revise apply draft.md edits.json --output revised.md
viral-revise revert revised.md revised.md.receipt.json --output restored.md
```

未安装项目时，把 viral-revise 替换成 python viral_content_revision.py。

## 核心行为

- 每份修改绑定原稿 SHA-256。原稿变化后，旧修改不会被套到新版本。
- 每处修改使用原文的唯一片段定位，所有位置都在同一版原稿上计算。
- 未指定的字符保持原样，包括 BOM、换行和空格。作者明确保护的原句不能进入替换范围。
- 重复片段、重叠修改、过期版本和缺失原句会返回错误，不猜位置、不发起询问。
- 整批检查通过后才保存新稿、修改回执和 diff。原稿与现有输出均不会被覆盖。
- 撤回时同时核验修改后与恢复后的版本指纹。新稿被再次修改后，旧回执不能强行回退。

## 内部数据

修改提议只有原稿指纹、替换片段和可选保护原句：

```json
{
  "base_sha256": "原稿的64位SHA-256",
  "edits": [
    {"before": "原文唯一片段", "after": "替换内容", "reason": "可选修改原因"}
  ],
  "protected": ["作者要求保留的原句"]
}
```

JSON 是模型或编辑器与执行内核之间的数据约定。自然语言 edit 入口让模型只返回 edits，再由程序绑定当前原稿指纹和调用方的保护清单。作者无需填表或选择 Skill，模型不能取消保护或指定另一版原稿。

删除使用空的 after。插入可用“保留原片段并追加文字”的替换表示。重复片段需要更完整的上下文。保护原句出现多次时全部保护。整段替换即使保留保护文字，也会被拒绝，应缩小替换范围。

diff 用于阅读；回执用于准确撤回。回执保留修改前后的原句，和稿件一起留在本地。

## 范围

精确执行修改，不等于证明修改正确。模型仍可能建议错误事实或不好的表达；未明确保护的数字也可能被修改。版本哈希用于校验一致性，不是作者身份或数字签名。

这一版没有自动 Skill 路由、主动访谈、通用商业诊断、知识库搭建、长期偏好推断、多 Agent 或后台流程。测试使用固定回复和本地模拟服务，没有真实付费模型质量或发布效果验证。

后续只围绕真实改稿案例评估：修改目标是否完成、非目标内容是否保留、作者需要手工修复多少。是否扩展其他能力，由这些结果决定。

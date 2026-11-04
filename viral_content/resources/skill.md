---
name: LYmmt369-viral-article-generator
description: 用用户提供的材料直接成稿，按明确改法局部修改已有稿件，输出差异并支持准确撤回。适用于文章、平台文案及稿件修订。
metadata:
  version: "4.1.2"
  author: LYmmt369
---

# LYmmt369-viral-article-generator

直接完成用户要求的稿件或修改。沿用已有材料、受众、立场和限制；不启动商业诊断、Skill 路由或预设访谈。材料不足的事实标为【待核实】，不编造经历、数字或出处。

## 成稿

优先使用当前宿主的模型能力根据材料直接写作。需要命令行生成时，使用已安装的 `viral-revise write materials.md "写作要求" --provider openai --model YOUR_MODEL --output draft.md`。模型标识须为用户账号可用值，密钥从环境变量读取。

## 精准改稿

按用户意图提出有限的原句替换。先读取原稿，并用 `viral-revise fingerprint draft.md` 取得版本指纹。每个 before 必须在同一版本原稿中唯一出现，替换范围不得重叠；明确要求保持的原句写入 protected。

把修改提议保存为 UTF-8 JSON：

```json
{"base_sha256":"原稿指纹","protected":["必须保留的原句"],"edits":[{"before":"待改原句","after":"修改后原句","reason":"修改理由"}]}
```

使用 `viral-revise apply draft.md edits.json --output revised.md` 执行，交付新稿、diff 和 receipt。原稿不覆盖，已有输出不覆盖。命令因歧义、版本或保护范围报错时，依据错误重新检查提议，不用整篇重写绕过检查。

撤回使用 `viral-revise revert revised.md revised.md.receipt.json --output restored.md`。只有版本核验通过才能声称准确恢复。

也可使用 `viral-revise edit draft.md "改稿要求" --provider openai --model YOUR_MODEL --output revised.md` 让指定模型提出修改。程序保证替换范围外的字节不变；模型理解、事实准确性和写作质量仍需检查，不能把执行成功等同于内容已核实。

## 配置与平台

显式要求账号、产品或风格配置时，用 `viral-content --topic "主题" --account account.yaml --offer offer.yaml --style tech_explainer_global --platform wechat xiaohongshu --ai-platform openai --model YOUR_MODEL --output drafts/`。两个平台分别生成、检查和保存；本次请求全部通过后才写出文件。失败须如实说明，不把提示词交成成稿。

环境缺少本项目 CLI 时，可以直接交付稿件与修改建议，但不要声称已执行程序核验或精确撤回。反馈计算只描述提交的数据，缺分母为未知，不能据少量自然发布记录宣布可靠性或因果。

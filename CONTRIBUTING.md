# 贡献指南

感谢你考虑为爆款内容生成器做出贡献！🎉

本文档将指导你如何参与这个项目。

---

## 📋 目录

1. [行为准则](#行为准则)
2. [如何贡献](#如何贡献)
3. [开发流程](#开发流程)
4. [代码规范](#代码规范)
5. [提交规范](#提交规范)
6. [问题反馈](#问题反馈)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

### 我们的标准

**积极行为包括：**
- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

**不可接受的行为包括：**
- 使用性化的语言或图像
- 侮辱性/贬损性评论，人身攻击或政治攻击
- 公开或私下骚扰
- 未经明确许可发布他人的私人信息
- 其他在专业环境中可能被认为不适当的行为

---

## 如何贡献

### 贡献类型

你可以通过以下方式贡献：

#### 1. 📝 改进文档
- 修复错别字
- 改进说明
- 添加使用示例
- 翻译文档

#### 2. 🐛 报告Bug
- 发现并报告问题
- 提供复现步骤
- 建议修复方案

#### 3. ✨ 提出新功能
- 建议新的功能
- 讨论实现方案
- 提供使用场景

#### 4. 💻 贡献代码
- 修复Bug
- 实现新功能
- 优化性能
- 重构代码

#### 5. 🎨 贡献内容
- 分享你的创作案例
- 提供新的风格模板
- 分享实战经验

---

## 开发流程

### 步骤1：Fork项目

1. 访问项目页面
2. 点击右上角的"Fork"按钮
3. 将项目Fork到你的账号下

### 步骤2：克隆到本地

```bash
git clone https://github.com/LYmmt369/viral-content-generator.git
cd viral-content-generator
```

### 步骤3：创建分支

```bash
# 创建新分支
git checkout -b feature/your-feature-name

# 或修复bug
git checkout -b fix/your-bug-fix
```

**分支命名规范：**
- `feature/功能名称` - 新功能
- `fix/bug名称` - Bug修复
- `docs/文档名称` - 文档更新
- `refactor/重构名称` - 代码重构
- `test/测试名称` - 测试相关

### 步骤4：进行修改

1. 进行你的修改
2. 确保代码符合规范
3. 添加必要的测试
4. 更新相关文档

### 步骤5：提交更改

```bash
# 添加修改的文件
git add .

# 提交（遵循提交规范）
git commit -m "feat: 添加新功能"

# 推送到你的Fork
git push origin feature/your-feature-name
```

### 步骤6：创建Pull Request

1. 访问你的Fork页面
2. 点击"New Pull Request"
3. 填写PR描述（使用模板）
4. 等待审核

---

## 代码规范

### Python代码规范

遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)规范：

```python
# 好的示例
def generate_article(topic, style, word_count):
    """
    生成文章
    
    Args:
        topic: 主题
        style: 风格
        word_count: 字数
        
    Returns:
        str: 生成的文章
    """
    # 实现代码
    pass

# 不好的示例
def gen(t,s,w):
    # 没有文档字符串
    pass
```

### Markdown文档规范

```markdown
# 一级标题

## 二级标题

### 三级标题

**重点内容用粗体**

*强调内容用斜体*

- 列表项1
- 列表项2

1. 有序列表1
2. 有序列表2

`代码用反引号`

```代码块用三个反引号```
```

### 文件命名规范

- 使用小写字母
- 单词之间用下划线或连字符
- 有意义的名称

**好的示例：**
- `user_guide.md`
- `quick-start.md`
- `skill_v3.0.md`

**不好的示例：**
- `file1.md`
- `temp.md`
- `新文件.md`

---

## 提交规范

### Commit Message格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 示例

```bash
# 新功能
git commit -m "feat(短视频): 添加抖音脚本模板"

# Bug修复
git commit -m "fix(质量检查): 修复评分计算错误"

# 文档更新
git commit -m "docs(README): 更新安装说明"

# 代码格式
git commit -m "style(skill): 统一代码缩进"

# 重构
git commit -m "refactor(创作流程): 优化大纲生成逻辑"

# 测试
git commit -m "test(CLI): 添加命令行工具测试"

# 其他
git commit -m "chore(deps): 更新依赖版本"
```

---

## 问题反馈

### 报告Bug

使用[Issue模板](https://github.com/LYmmt369/viral-content-generator/issues/new?template=bug_report.md)报告Bug。

**请包含：**
1. 问题描述
2. 复现步骤
3. 预期行为
4. 实际行为
5. 环境信息
6. 截图（如果适用）

### 功能请求

使用[Issue模板](https://github.com/LYmmt369/viral-content-generator/issues/new?template=feature_request.md)提出功能请求。

**请包含：**
1. 功能描述
2. 使用场景
3. 期望效果
4. 替代方案
5. 其他信息

---

## Pull Request流程

### PR检查清单

提交PR前，请确保：

- [ ] 代码符合规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] Commit message符合规范
- [ ] 通过了所有测试
- [ ] 解决了所有冲突

### PR描述模板

```markdown
## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 变更描述
简要描述你的变更...

## 相关Issue
Closes #issue_number

## 测试
描述你如何测试这些变更...

## 截图（如果适用）
添加截图...

## 检查清单
- [ ] 代码符合规范
- [ ] 添加了测试
- [ ] 更新了文档
- [ ] Commit message符合规范
```

### 审核流程

1. **自动检查**：CI/CD自动运行测试
2. **代码审核**：维护者审核代码
3. **讨论修改**：如有需要，进行讨论和修改
4. **合并**：审核通过后合并到主分支

---

## 开发环境设置

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装开发依赖（如果有）
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_skill.py

# 查看覆盖率
pytest --cov=.
```

### 代码检查

```bash
# 代码格式检查
flake8 .

# 代码格式化
black .

# 类型检查
mypy .
```

---

## 文档贡献

### 文档结构

```
docs/
├── README.md           # 项目说明
├── 使用手册.md          # 使用教程
├── 风格配置模板.md      # 风格定制
├── 快速参考卡.md        # 速查卡片
└── 跨平台使用指南.md    # 跨平台教程
```

### 文档规范

1. **清晰简洁**：用简单的语言解释复杂的概念
2. **结构化**：使用标题、列表、表格组织内容
3. **示例丰富**：提供足够的示例代码
4. **保持更新**：代码变更时同步更新文档

---

## 社区

### 交流渠道

- **GitHub Discussions**：讨论功能、分享经验
- **GitHub Issues**：报告问题、提出建议
- **Pull Requests**：贡献代码、改进文档

### 获取帮助

如果你需要帮助：

1. 查看[文档](./README.md)
2. 搜索[已有Issues](https://github.com/LYmmt369/viral-content-generator/issues)
3. 在[Discussions](https://github.com/LYmmt369/viral-content-generator/discussions)提问
4. 创建新的Issue

---

## 致谢

感谢所有贡献者！

你的贡献让这个项目变得更好。🙏

---

## 许可证

通过贡献代码，你同意你的贡献将在[MIT License](./LICENSE)下发布。

---

**再次感谢你的贡献！** 🎉

如有任何问题，欢迎随时联系维护者。

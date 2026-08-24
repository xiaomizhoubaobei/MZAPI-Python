# 贡献指南

感谢您对 MZAPI Python SDK 项目的关注！我们欢迎任何形式的贡献，包括但不限于：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📖 改进文档
- 🛠️ 提交代码
- 🎨 改进 UI/UX
- 🌍 帮助翻译
- 💬 参与讨论

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交流程](#提交流程)
- [Pull Request 指南](#pull-request-指南)
- [报告问题](#报告问题)
- [获取帮助](#获取帮助)

## 行为准则

参与本项目即表示您同意遵守我们的[行为准则](CODE_OF_CONDUCT.md)。请确保您的互动友好、包容和尊重。

## 如何贡献

### 1. 寻找要处理的问题

- 查看 [Issues](https://github.com/xiaomizhoubaobei/MZAPI-Python/issues) 页面
- 寻找标记为 `good-first-issue` 或 `help-wanted` 的问题
- 在开始工作之前，请先评论表示您正在处理该问题
- 如果您想贡献新功能，请先创建一个 Issue 讨论

### 2. Fork 仓库

1. 点击项目页面右上角的 "Fork" 按钮
2. 克隆您的 Fork 到本地：

```bash
git clone https://github.com/您的用户名/MZAPI-Python.git
cd MZAPI-Python
```

### 3. 创建分支

为您的贡献创建一个新分支：

```bash
git checkout -b feature/您的功能名称
# 或
git checkout -b fix/您修复的问题
```

## 开发环境设置

### 环境要求

- Python 3.10 或更高版本（支持 3.10, 3.11, 3.12, 3.13, 3.14）
- pip
- Git

### 安装依赖

1. 创建虚拟环境（推荐）：

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 或使用 conda
conda create -n mzapi python=3.10
conda activate mzapi
```

2. 安装项目依赖：

```bash
pip install -r requirements.txt
```

3. 安装开发依赖：

```bash
pip install -r requirements-dev.txt
```

4. 以开发模式安装项目：

```bash
pip install -e .
```

### 设置 Pre-commit Hooks

Pre-commit 钩子会在您提交代码前自动运行检查：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行所有检查
pre-commit run --all-files
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_example.py

# 运行测试并生成覆盖率报告
pytest --cov=mzapi --cov-report=html

# 运行测试并显示详细输出
pytest -v
```

## 代码规范

### Python 代码规范

我们遵循以下代码规范：

- **PEP 8** - Python 代码风格指南
- **Black** - 代码格式化工具（行宽 88）
- **isort** - Import 语句排序
- **flake8** - 代码质量检查
- **mypy** - 静态类型检查（推荐）

### 代码格式化

使用 Black 自动格式化代码：

```bash
black .
```

使用 isort 排序 import 语句：

```bash
isort .
```

### 代码检查

运行 flake8 检查代码质量：

```bash
flake8 mzapi/
```

### 类型检查（可选）

如果您使用类型注解，可以运行 mypy 检查：

```bash
mypy mzapi/
```

### 文档字符串

我们使用 Google 风格的文档字符串：

```python
def example_function(param1, param2):
    """函数的简要描述。

    更详细的描述可以跨越多行。

    Args:
        param1: 参数1的描述
        param2: 参数2的描述

    Returns:
        返回值的描述

    Raises:
        ValueError: 当参数无效时
    """
    pass
```

### Commit 消息规范

使用清晰、有意义的 commit 消息：

```
<类型>(<范围>): <简短描述>

<详细描述>

<页脚>
```

**类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新功能也不是修复）
- `test`: 添加测试
- `chore`: 构建过程或辅助工具的变动

**示例：**

```
feat(ocr): 添加表格识别功能

实现了表格识别功能，支持检测和提取表格内容。

Closes #123
```

## 提交流程

### 1. 提交更改

```bash
git add .
git commit -m "feat: 添加新功能"
```

### 2. 推送到您的 Fork

```bash
git push origin feature/您的功能名称
```

### 3. 创建 Pull Request

1. 访问您 Fork 的 GitHub 页面
2. 点击 "New Pull Request" 按钮
3. 选择您的分支
4. 填写 PR 模板

## Pull Request 指南

### PR 标题

使用与 commit 消息相同的格式：

```
feat: 添加新功能
```

### PR 描述

请提供：

- **更改的目的**：为什么要做这个更改？
- **更改的内容**：您做了什么？
- **测试说明**：如何测试这些更改？
- **相关 Issue**：关联的 Issue 编号（如 `Closes #123`）
- **截图/录屏**（如果适用）：UI 更改的视觉证明
- **破坏性更改**：是否有破坏性更改？如何迁移？

### PR 检查清单

在提交 PR 之前，请确保：

- [ ] 代码符合项目规范（已通过 Black、isort、flake8 检查）
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 添加了清晰的 commit 消息
- [ ] PR 描述清晰完整
- [ ] 没有合并冲突

### PR 审查流程

1. **自动检查**：CI 会自动运行测试和代码检查
2. **人工审查**：维护者会审查您的代码
3. **反馈**：如果需要修改，请根据反馈进行调整
4. **合并**：通过审查后，PR 将被合并到主分支

## 报告问题

### Bug 报告

报告 Bug 时，请提供：

1. **清晰的标题**：简明扼要地描述问题
2. **问题描述**：详细说明发生了什么
3. **重现步骤**：如何重现这个问题
4. **预期行为**：您期望发生什么
5. **实际行为**：实际发生了什么
6. **环境信息**：
   - 操作系统
   - Python 版本
   - MZAPI SDK 版本
7. **复现代码**：能够重现问题的最小代码示例
8. **日志/错误信息**：相关的错误消息或日志
9. **附加信息**：任何其他相关信息

### Bug 报告模板

```markdown
**Bug 描述**
简要描述 Bug 的内容

**重现步骤**
1. 步骤1
2. 步骤2
3. 步骤3

**预期行为**
描述您期望发生什么

**实际行为**
描述实际发生了什么

**环境信息**
- 操作系统: [例如 Ubuntu 20.04]
- Python 版本: [例如 3.10.0]
- MZAPI SDK 版本: [例如 0.0.1]

**复现代码**
```python
# 在这里粘贴代码
```

**错误信息**
```
# 在这里粘贴错误信息
```

**附加信息**
其他相关信息

### 功能请求

提出新功能时，请说明：

1. **问题描述**：您想解决什么问题？
2. **提议的解决方案**：您希望如何解决？
3. **替代方案**：您考虑过的其他解决方案
4. **附加信息**：示例、截图、或其他相关信息

### 功能请求模板

```markdown
**问题描述**
清晰地描述您想要解决的问题

**提议的解决方案**
详细描述您希望实现的功能

**替代方案**
描述您考虑过的其他解决方案或功能

**附加信息**
示例、截图或其他相关信息
```

## 获取帮助

### 文档

- [README.md](README.md) - 项目概述和快速开始
- [CHANGELOG.md](CHANGELOG.md) - 版本更新日志
- [代码文档](https://docs.mizhoubaobei.top) - 详细 API 文档

### 沟通渠道

- **GitHub Issues**：报告 Bug 或提出功能请求
- **GitHub Discussions**：一般性讨论和问题
- **邮箱**：qixiaoxin@stu.sqxy.edu.cn

### 社区资源

- [项目主页](https://github.com/xiaomizhoubaobei/MZAPI-Python)
- [PyPI 页面](https://pypi.org/project/MZAPI-Python)
- [文档网站](https://docs.mizhoubaobei.top)

## 许可证

通过贡献代码，您同意您的贡献将在 [MPL-2.0](LICENSE) 许可证下发布。

## 认可贡献者

我们感谢所有贡献者的贡献！贡献者名单将在项目的 README 和其他相关文档中列出。

## 再次感谢

感谢您花时间阅读本贡献指南，并感谢您对 MZAPI Python SDK 项目的贡献！

---

**最后更新**: 2026-01-28
**版本**: 1.0

# CNB NPC 全局指令

## ⚠️ 最重要的规则 — 必须发布评论

**你运行在 CLI 非交互模式下（claude -p），你的文本输出不会被任何人看到！**

唯一能让用户看到你回复的方式是：用 **Bash 工具**直接执行 **curl** 命令将评论发布到 Issue 或 PR。

- **无论任务完成与否，最终步骤都必须是发布评论**
- 如果你只输出文本而不执行 curl，用户将收不到任何回复
- 直接执行 curl 命令即可，**不要在命令前加 "bash" 前缀**
- 合理分配 turns：**预留至少 2 个 turns 用于发布评论**
- **【关键】调用 CNB API 时，认证 Token 必须且只能使用环境变量 $CNB_TOKEN（如 -H "Authorization: Bearer $CNB_TOKEN"），禁止在命令中直接粘贴 token 明文**
- **【关键】调用 CNB API 时，仓库路径必须且只能使用环境变量 $CNB_REPO_SLUG，严禁自行拼接或猜测仓库名称。正确写法：`${CNB_REPO_SLUG}`**
- **【关键】在 Bash 中只能执行有效的 shell 命令（如 curl、cat、cnb 等），不要直接输入文件名（如 CLAUDE.md）作为命令**

## 信任目录

以下目录已被标记为可信任，可以直接读写操作：
- `/workspace`
- `/repo`

## CNB 平台操作自动识别

当用户的请求涉及以下 CNB 平台相关关键词时，应自动使用 `cnb` 命令（cnb-api 技能提供）或 CNB OpenAPI 来查询和执行相关操作：

**匹配关键词**：cnb、cnb.cool、仓库、代码仓库、repo、repository、issue、问题、pull request、合并请求、PR、MR、merge request、分支、branch、标签、tag、release、发布、构建、build、CI、CD、pipeline、组织、organization、成员、member、权限、permission、工作空间、workspace、镜像、registry、安全、security、收藏、star、关注、follow、贡献者、contributor、标签管理、label、知识库、knowledgebase、任务、mission、徽章、badge、计费、charge、活动、activity、事件、event、AI对话、ai chat、auto pr

## 可用技能(Skills)

本项目的技能位于 `.claude/skills/` 目录中（Claude Code 原生 Skills 路径）。在相应场景下**必须主动加载并使用**：

| 技能 | 路径 | 用途 |
|------|------|------|
| **cnb-api** | `.claude/skills/cnb-api/SKILL.md` | CNB 平台 OpenAPI 交互，通过 `cnb` CLI 操作仓库、Issue、PR、流水线等资源 |
| **cnb-knowledge-base** | `.claude/skills/cnb-knowledge-base/SKILL.md` | 查询 CNB 平台官方文档（docs.cnb.cool），回答平台使用问题 |
| **cnb-pipeline** | `.claude/skills/cnb-pipeline/SKILL.md` | 编写/修改 `.cnb.yml` 流水线配置文件，覆盖触发规则、构建环境、阶段任务等 |
| **code-commit** | `.claude/skills/code-commit/SKILL.md` | 编写代码并提交推送。修改代码后 **必须** 加载此技能完成 git add/commit/push，必要时创建 PR |
| **code-review** | `.claude/skills/code-review/SKILL.md` | PR 代码评审。获取 diff、检查安全漏洞/Bug/代码质量，通过 API 发送行级评审评论 |
| **diagnose-ci-pipeline** | `.claude/skills/diagnose-ci-pipeline/SKILL.md` | CI 流水线失败诊断。通过 PR 编号/构建 sn/链接获取失败日志，分析根因并给出修复建议 |
| **npc-delegate** | `.claude/skills/npc-delegate/SKILL.md` | 指挥 NPC 干活。确保 NPC 开启工作模式后才能执行代码变更任务 |
| **pr-diff** | `.claude/skills/pr-diff/SKILL.md` | 获取 PR 的 diff 变更信息，用于评审和总结等场景 |
| **pr-summary** | `.claude/skills/pr-summary/SKILL.md` | 对 PR 变更生成结构化总结，分析改动内容和影响 |
| **tapd-resource-fetcher** | `.claude/skills/tapd-resource-fetcher/SKILL.md` | 获取 Tapd 资源（需求/缺陷/任务/迭代），根据 Tapd 链接调用接口获取完整数据 |
| **text-path-converter** | `.claude/skills/text-path-converter/SKILL.md` | 读取 Issue/PR 内容时，将描述中的相对路径转为绝对路径，避免路径歧义 |
| **upload-attachment** | `.claude/skills/upload-attachment/SKILL.md` | 上传附件（图片/文档/压缩包等）到 Issue 或 PR，返回 Markdown 附件链接 |

## 可用命令(Commands)

本项目的自定义命令位于 `.claude/commands/` 目录中（Claude Code 原生 Commands 路径）。每个命令对应同名技能：

| 命令 | 路径 | 说明 |
|------|------|------|
| **cnb-api** | `.claude/commands/cnb-api.md` | 调用 CNB 平台 API |
| **cnb-knowledge-base** | `.claude/commands/cnb-knowledge-base.md` | 查询 CNB 平台文档 |
| **cnb-pipeline** | `.claude/commands/cnb-pipeline.md` | 编写/修改流水线配置 |
| **code-commit** | `.claude/commands/code-commit.md` | 编写代码并提交推送 |
| **code-review** | `.claude/commands/code-review.md` | 对 PR 进行代码评审 |
| **diagnose-ci-pipeline** | `.claude/commands/diagnose-ci-pipeline.md` | 诊断 CI 流水线失败 |
| **npc-delegate** | `.claude/commands/npc-delegate.md` | 指挥 NPC 执行开发任务 |
| **pr-diff** | `.claude/commands/pr-diff.md` | 获取 PR 的代码变更 diff |
| **pr-summary** | `.claude/commands/pr-summary.md` | 对 PR 变更生成结构化总结 |
| **tapd-resource-fetcher** | `.claude/commands/tapd-resource-fetcher.md` | 获取 Tapd 资源数据 |
| **text-path-converter** | `.claude/commands/text-path-converter.md` | 转换文本中的相对路径 |
| **upload-attachment** | `.claude/commands/upload-attachment.md` | 上传附件到 Issue/PR |

## 核心能力

1. **代码理解与分析**：阅读、理解仓库代码，回答代码相关问题
2. **Issue 处理**：分析 Issue 内容，提供解决方案，回复评论
3. **PR 审查**：使用 `code-review` 技能执行代码评审
4. **PR 总结**：使用 `pr-summary` 技能生成 PR 变更总结
5. **代码编写与提交**：使用 `code-commit` 技能编写代码、提交推送并创建 PR
6. **CNB API 操作**：**优先使用 `cnb` 命令**（cnb-api 技能提供），执行 `cnb --help` 获取可用模块和工具列表
7. **流水线配置**：使用 `cnb-pipeline` 技能编写/修改 `.cnb.yml` 配置
8. **CI 诊断**：使用 `diagnose-ci-pipeline` 技能诊断流水线失败原因
9. **附件上传**：使用 `upload-attachment` 技能上传文件到 Issue/PR

## CNB API 调用方式

### 方式一（优先）：`cnb` 命令工具

cnb-api 技能提供了 `cnb` CLI 工具，封装了 CNB 全部 OpenAPI：

```bash
# 查看所有可用模块
cnb --help

# 查看特定模块的工具列表
cnb --module <模块名> --help

# 查看工具详细参数
cnb --module <模块名> --tool <工具名> --help

# 执行工具
cnb --module <模块名> --tool <工具名> --path '{}' --query '{}' --data '{}'
```

**使用原则**：
- 必须先执行 `cnb --help` 获取最新使用方式，禁止推测
- 工具返回标准 JSON：`status`（HTTP 状态码）、`data`（实体内容）、`header`（含分页信息）

### 方式二（备选）：手动 curl 调用

当 `cnb` 命令无法满足需求时，可直接使用 curl 调用 CNB OpenAPI。参考文档：
- 主文档：`instructions/cnb-openapi.md`
- API 详细参考：`instructions/references/` （200+ 个 API 接口文档）

## 环境变量

以下环境变量在 CNB NPC 运行时自动注入：

| 变量 | 说明 |
|---|---|
| `CNB_TOKEN` | CNB 平台 API 认证 Token |
| `CNB_API_ENDPOINT` | CNB API 基础地址（默认 https://api.cnb.cool） |
| `CNB_REPO_SLUG` | 当前仓库 slug（格式：{owner}/{repo}） |
| `CNB_PULL_REQUEST_IID` | PR 的内部编号（IID） |
| `CNB_PULL_REQUEST_SHA` | PR 的 head commit SHA |
| `CNB_PULL_REQUEST_TARGET_SHA` | PR 的 target commit SHA |
| `CNB_NPC_ENABLE_WORKMODE` | 是否启用工作模式（true/false） |

## 编程语言编码规范

> **说明（给 AI 看）** 以下规范为"**强约束**"。编写、评审、重构代码时，必须严格遵循对应语言的规范。若项目中存在对应工具的配置文件（如 `.eslintrc`、`pyproject.toml`、`Cargo.toml`、`rustfmt.toml` 等），则**以配置文件为准**，本文档规范作为兜底。

本项目可能涉及多种编程语言，以下列出每种语言**必须遵守**的编码规范。编写或审查代码时，必须遵循对应语言的规范要求。

### Python

必须遵守 **PEP 8**（https://peps.python.org/pep-0008/），并遵循以下现代 Python 最佳实践：

#### 基础规范

- **最低版本**：Python ≥ 3.10（支持 `match/case`、`X | Y` 类型联合等新语法）
- **缩进**：4 个空格，禁止 Tab
- **行长**：≤ 79 字符（项目允许时可放宽至 120）
- **空行**：顶层函数 / 类之间空 2 行，类内方法之间空 1 行
- **字符串**：统一使用单引号 `'`，包含引号时使用双引号 `"`
- **行尾**：禁止行尾空格，文件末尾保留一个空行

#### 命名规范

- 函数 / 变量：`snake_case`
- 类：`PascalCase`
- 常量（模块级）：`UPPER_SNAKE_CASE`
- 私有成员：单前缀 `_`（受保护）或双前缀 `__`（名称修饰，谨慎使用）
- 魔术方法：双下划线包围，如 `__init__`、`__repr__`
- 布尔变量 / 方法：使用 `is_`、`has_`、`can_` 前缀，如 `is_valid`、`has_permission`

#### 导入规范

```python
# 每行一个 import，顺序：标准库 → 第三方库 → 本地模块
# 各组之间用空行分隔

import json
import os
from pathlib import Path

import requests
from fastapi import APIRouter

from myproject.models import User
from myproject.utils import helper
```

- **禁止**：`from module import *`（通配符导入）
- **禁止**：循环导入；如不可避免，使用延迟导入（函数内 import）
- 排序工具：`isort` / `ruff check --select I`

#### 类型注解（PEP 484 / 604 / 585）

**所有函数签名必须添加类型注解**（参数 + 返回值）：

```python
# ✅ 正确
def calculate_total(items: list[dict[str, float]], tax_rate: float = 0.08) -> float:
    ...

# ✅ 使用 PEP 604 联合类型（推荐，替代 Union）
def find_user(user_id: int | None) -> User | None:
    ...

# ❌ 错误：缺少类型注解
def calculate_total(items, tax_rate=0.08):
    ...
```

- 使用内置泛型 `list[T]`、`dict[K, V]`（PEP 585），**禁止** `List[T]`、`Dict[K, V]`
- 使用 `X | Y`（PEP 604），**禁止** `Union[X, Y]`、`Optional[X]`（改为 `X | None`）
- 复杂类型提取为 `TypeAlias`：`type UserID = int`
- `Callable`、`Sequence` 等从 `collections.abc` 导入，**禁止** 从 `typing` 导入
- 数据类优先使用 `@dataclass` 或 `pydantic.BaseModel`，避免裸 `dict` 传递复杂结构

#### 文档规范（PEP 257）

**公共模块、类、函数必须编写 docstring**，使用 Google 风格或 NumPy 风格。

**说明注释必须使用中文**（docstring、行内注释、块注释均适用）：

```python
def fetch_user(user_id: int, timeout: float = 30.0) -> dict[str, str]:
    """从远程 API 获取用户信息。

    Args:
        user_id: 用户的唯一标识符。
        timeout: 请求超时时间，单位为秒。

    Returns:
        包含用户资料数据的字典。

    Raises:
        ConnectionError: 当 API 不可达时抛出。
        ValueError: 当 user_id 为负数时抛出。
    """
    ...
```

#### 错误处理

```python
# ✅ 精确捕获异常类型，避免 bare except
try:
    result = api_call()
except ConnectionError as e:
    logger.error("Connection failed: %s", e)
    raise

# ✅ 使用自定义异常表达业务逻辑
class InsufficientBalanceError(Exception):
    """当账户余额低于所需金额时抛出。"""

# ❌ 禁止：捕获 Exception 或 BaseException 后静默忽略
try:
    risky_operation()
except Exception:
    pass  # 这是绝对禁止的！
```

- 捕获尽可能精确的异常类型，**禁止** `except Exception: pass`
- 使用 `logging.exception()` 记录异常堆栈，**禁止** `print()` 输出错误
- 资源清理优先使用 `with` 语句（上下文管理器），其次使用 `try/finally`

#### 测试规范

```bash
# 目录结构
tests/
    conftest.py          # 共享 fixture
    test_<module>.py     # 对应 src 下的模块
```

- **框架**：`pytest`（禁止使用 `unittest` 的 TestCase 继承风格）
- **文件命名**：`test_<module>.py`，函数命名 `test_<功能描述>`
- **Fixture**：使用 `@pytest.fixture`，通过 `conftest.py` 共享
- **断言**：直接使用 `assert`，不使用 `self.assertEqual` 等
- **覆盖率**：核心模块要求覆盖率 ≥ 80%（`pytest-cov`）
- **Mock**：使用 `unittest.mock` 或 `pytest-mock`，mock 外部依赖（网络、数据库、文件系统）
- **参数化**：使用 `@pytest.mark.parametrize` 替代重复测试

#### 依赖与项目管理

```toml
# pyproject.toml（唯一项目配置入口，禁止 setup.py / setup.cfg）
[project]
name = "my-project"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "mypy>=1.0", "ruff>=0.4"]
```

- **项目配置**：统一使用 `pyproject.toml`，**禁止** `setup.py`、`setup.cfg`、`requirements.txt` 管理依赖
- **包管理工具**：优先使用 `uv`，其次 `poetry`，**禁止** 直接使用 `pip install`
- **虚拟环境**：每个项目必须使用独立虚拟环境（`uv venv` / `python -m venv`），**禁止** 全局安装
- **锁定文件**：使用 `uv.lock` 或 `poetry.lock` 锁定依赖版本，提交到版本控制
- **依赖更新**：定期检查依赖安全性（`uv audit` / `pip-audit`）

#### 代码质量工具链

```toml
# pyproject.toml 中的工具配置

[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --cov=src"
```

| 工具 | 用途 | 优先级 |
|---|---|---|
| `ruff format` | 代码格式化（替代 black） | **必须** |
| `ruff check` | Lint 检查（替代 flake8 + isort + 多个插件） | **必须** |
| `mypy --strict` | 静态类型检查 | **必须** |
| `pytest` | 单元 / 集成测试 | **必须** |
| `pre-commit` | Git 提交前自动检查（集成上述工具） | 强烈推荐 |
| `bandit` | 安全漏洞扫描 | 推荐 |
| `pip-audit` / `uv audit` | 依赖安全审计 | 推荐 |

#### 安全规范

- **输入验证**：所有外部输入必须校验（使用 Pydantic 模型验证请求数据）
- **SQL 注入**：使用 ORM（SQLAlchemy）或参数化查询，**禁止** 字符串拼接 SQL
- **密钥管理**：使用环境变量或 `.env` 文件，**禁止** 硬编码密钥到源码
- **依赖安全**：定期运行 `pip-audit` / `uv audit` 扫描已知漏洞
- **反序列化**：**禁止** `pickle.loads()` 处理不受信任的数据（远程代码执行风险）
- **文件操作**：使用 `pathlib.Path`，校验路径防止目录穿越攻击
- **临时文件**：使用 `tempfile` 模块创建，脚本退出时清理

#### 并发与性能

- **asyncio**：I/O 密集型任务优先使用 `async/await`（配合 `httpx`、`aiofiles` 等异步库）
- **GIL 注意**：CPU 密集型任务使用 `multiprocessing` 或 `concurrent.futures.ProcessPoolExecutor`
- **类型提示中的并发**：`asyncio.Task[T]`、`asyncio.Future[T]` 需正确标注
- **性能分析**：使用 `cProfile`、`line_profiler`、`py-spy` 定位瓶颈，**禁止** 凭直觉优化

#### 文件与目录结构

```
my_project/
    src/
        __init__.py
        main.py
        models/
        services/
        utils/
    tests/
        __init__.py
        conftest.py
        test_main.py
    pyproject.toml          # 唯一配置入口
    uv.lock / poetry.lock   # 依赖锁文件
    README.md
```

- 禁止在模块顶层放置业务逻辑（放在函数或类方法中）
- `__init__.py` 仅用于控制导出（`__all__`），**禁止** 包含业务代码

### TypeScript / JavaScript

必须遵守 **TypeScript Strict Mode**，以项目 ESLint / Prettier 配置为准，兜底规则如下。

#### 基础规范

- **最低版本**：TypeScript ≥ 5.0，Node.js ≥ 18（LTS）
- **缩进**：2 个空格
- **行长**：≤ 100 字符（Prettier `printWidth`）
- **分号**：统一加分号（`semi: true`），或统一不加（与项目保持一致，推荐加分号）
- **字符串**：统一使用单引号 `'`，包含引号时使用反引号 `` ` ``
- **空行**：顶层函数 / 类之间空 1 行，逻辑块之间空 1 行
- **行尾**：禁止行尾空格，文件末尾保留一个空行
- **Trailing Comma**：多行结构使用尾逗号（`trailingComma: "all"`）

#### 命名规范

- 变量 / 函数：`camelCase`
- 类 / 接口 / 类型 / 枚举 / React 组件：`PascalCase`
- 常量（模块级）：`UPPER_SNAKE_CASE`
- 布尔变量 / 方法：使用 `is`、`has`、`can`、`should` 前缀，如 `isValid`、`hasPermission`、`shouldReload`
- 私有成员：使用 `#` 前缀（原生私有字段）或 `_` 前缀（约定）
- 事件回调：使用 `handle` 前缀，如 `handleSubmit`、`handleClick`
- 事件监听器：使用 `on` 前缀，如 `onChange`、`onClick`
- getter / setter：使用 `get` / `set` 前缀，如 `getFullName()`

```typescript
// ✅ 正确
const MAX_RETRY_COUNT = 3;
const isActive = true;
class UserService {
  #db: Database;
  getFullName(): string { /* ... */ }
}
const handleSubmit = () => { /* ... */ };

// ❌ 错误
const max_retry_count = 3;
class user_service { /* ... */ }
```

#### 导入规范

```typescript
// 顺序：内置模块 → 第三方库 → 本地模块 → 相对导入
// 各组之间用空行分隔

import path from 'node:path';
import { randomUUID } from 'node:crypto';

import express from 'express';
import { z } from 'zod';

import { UserService } from '@/services/user.service';
import { logger } from '@/utils/logger';
```

- **必须**使用 ES Module（`import / export`），**禁止** `require` / `module.exports`
- **禁止**：循环导入；如不可避免，使用动态 `import()` 延迟加载
- **禁止**：通配符导入 `import * as xxx from '...'`（除非是测试 mock 场景）
- **禁止**：过度使用 barrel export（`index.ts` re-export all），导致打包体积膨胀
- 路径别名：使用 `@/` 前缀映射项目根目录（配置 `tsconfig.json` 的 `paths`）
- 导入排序工具：`@typescript-eslint/consistent-type-imports` + `simple-import-sort`

#### 类型注解规范

**TypeScript 项目必须开启 `strict: true`**，所有函数签名必须添加类型注解：

```typescript
// ✅ 正确：明确的类型注解
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

function calculateTotal(
  items: Array<{ price: number; quantity: number }>,
  taxRate: number = 0.08
): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0) * (1 + taxRate);
}

// ✅ 使用类型别名简化复杂类型
type UserID = string;
type AsyncResult<T> = Promise<{ data: T; error: null } | { data: null; error: Error }>;

// ❌ 错误：缺少类型注解
function calculateTotal(items, taxRate = 0.08) { /* ... */ }
```

- **禁止**使用 `any`，优先使用具体类型或 `unknown`（配合类型断言 / 类型守卫使用）
- **禁止**使用 `enum`，优先使用 `as const` 对象（`const` assertion）
- **禁止**使用 `namespace`，优先使用 ES Module 组织代码
- 优先使用 `interface` 定义对象结构（支持声明合并和 extends）
- 使用 `type` 定义联合类型、交叉类型、工具类型等
- 泛型约束使用 `extends`：`function first<T extends unknown[]>(arr: T): T[0]`
- 函数返回值类型：当函数体超过 5 行时必须显式标注返回类型
- 断言使用 `satisfies`（TS 4.9+）替代 `as`，保持类型推断：

```typescript
// ✅ 使用 satisfies 保留类型推断
const config = {
  port: 3000,
  host: 'localhost',
} satisfies ServerConfig;

// ❌ 使用 as 丢失了部分推断能力
const config = { port: 3000, host: 'localhost' } as ServerConfig;
```

#### 文档规范（JSDoc / TSDoc）

**公共模块、类、公开方法必须编写 JSDoc 注释**。

**说明注释必须使用中文**（JSDoc、行内注释、块注释均适用）：

```typescript
/**
 * 从远程 API 获取用户信息。
 *
 * @param userId - 用户的唯一标识符
 * @param options - 请求配置项
 * @returns 包含用户资料的对象
 * @throws {ConnectionError} 当 API 不可达时抛出
 * @throws {NotFoundError} 当用户不存在时抛出
 *
 * @example
 * const user = await fetchUser('u-123');
 */
async function fetchUser(
  userId: string,
  options?: RequestInit
): Promise<User> {
  // 实现细节...
}
```

- 参数类型注解和 JSDoc `@param` 不重复：已有 TypeScript 类型时，JSDoc 可省略类型
- `@example` 示例代码可被 `tsd` / `tsc` 编译器检查
- 类型定义中的文档注释：对每个字段添加说明

#### 错误处理

```typescript
// ✅ 自定义错误类，保留原始错误链
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly cause?: Error
  ) {
    super(message, { cause });
    this.name = 'AppError';
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id '${id}' not found`, 'NOT_FOUND');
  }
}

// ✅ async 函数统一 try-catch
async function getUser(userId: string): Promise<User> {
  try {
    const user = await db.users.findUnique({ where: { id: userId } });
    if (!user) throw new NotFoundError('User', userId);
    return user;
  } catch (error) {
    if (error instanceof AppError) throw error;
    logger.error('Failed to fetch user', { userId, error });
    throw new AppError('Failed to fetch user', 'INTERNAL_ERROR', error as Error);
  }
}

// ❌ 禁止：静默吞掉错误
async function getUser(userId: string): Promise<User | undefined> {
  try {
    return await db.users.findUnique({ where: { id: userId } });
  } catch {
    // 禁止空 catch 块！
  }
}
```

- 捕获尽可能精确的异常类型，**禁止** `catch {}` 或 `catch (e) { /* 空 */ }`
- 使用 `logger.error()` 记录异常，**禁止** `console.error()` 输出生产错误日志
- Promise 链中的错误：使用 `.catch()` 或 `async/await + try-catch`，**禁止**未处理的 Promise rejection
- 异步函数返回值：统一使用 `Promise<T>`，**禁止** `Promise<any>`
- 资源清理：优先使用 `try/finally`，或 `using` 声明（TS 5.2+ Explicit Resource Management）

#### 测试规范

```bash
# 目录结构
src/
    services/
        user.service.ts
tests/
    services/
        user.service.test.ts    # 与被测文件对应
    fixtures/                   # 测试数据
    helpers/                    # 测试工具函数
```

- **框架**：`vitest`（推荐）或 `jest`，**禁止** 使用过时的 `mocha` + 手动断言
- **文件命名**：`<module>.test.ts` 或 `<module>.spec.ts`，与源文件同目录或在 `tests/` 下
- **函数命名**：`describe('模块名', () => { it('应该xxx', () => { ... }) })`
- **断言**：使用 `expect()`，不使用 `assert`
- **覆盖率**：核心模块要求覆盖率 ≥ 80%
- **Mock**：使用 `vi.fn()` / `vi.mock()`（vitest）或 `jest.fn()` / `jest.mock()`，mock 外部依赖（网络、数据库、文件系统）
- **测试隔离**：每个测试用例独立，使用 `beforeEach` / `afterEach` 清理状态
- **参数化**：使用 `it.each` / `test.each` 替代重复测试

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { UserService } from './user.service';

describe('UserService', () => {
  let service: UserService;
  const mockDb = { users: { findUnique: vi.fn() } };

  beforeEach(() => {
    vi.clearAllMocks();
    service = new UserService(mockDb as any);
  });

  it.each([
    { input: 'u-001', expected: 'Alice' },
    { input: 'u-002', expected: 'Bob' },
  ])('应该根据 ID $input 返回用户名 $expected', async ({ input, expected }) => {
    mockDb.users.findUnique.mockResolvedValue({ name: expected });
    const user = await service.getById(input);
    expect(user?.name).toBe(expected);
  });
});
```

#### 依赖与项目管理

```json
// package.json（项目配置入口）
{
  "name": "my-project",
  "type": "module",
  "engines": { "node": ">=18" },
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "lint": "eslint src/",
    "format": "prettier --write src/",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

- **包管理工具**：优先使用 `pnpm`，其次 `npm` / `yarn`，**禁止** 手动下载依赖
- **锁文件**：必须提交 `pnpm-lock.yaml`（或 `package-lock.json` / `yarn.lock`），**禁止** 删除锁文件
- **Node 版本管理**：使用 `.node-version` 或 `.nvmrc` 锁定 Node 版本
- **Monorepo**：使用 `pnpm workspace`（`pnpm-workspace.yaml`）或 `turborepo`
- **依赖安全**：定期运行 `pnpm audit` / `npm audit` 扫描已知漏洞
- **devDependencies**：开发工具（TypeScript、ESLint、Prettier、测试框架）统一放在 `devDependencies`
- **禁止**：在生产代码中引入 `devDependencies` 中的包

#### 代码质量工具链

```jsonc
// tsconfig.json（TypeScript 编译配置）
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "dist",
    "rootDir": "src",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

```jsonc
// eslint.config.js（Flat Config 格式，ESLint 9+）
// 推荐使用 @typescript-eslint/eslint-plugin + eslint-plugin-import
```

```jsonc
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```

| 工具 | 用途 | 优先级 |
|---|---|---|
| `tsc --noEmit` | 静态类型检查（开启 `strict: true`） | **必须** |
| `eslint` | Lint 检查（使用 Flat Config 格式） | **必须** |
| `prettier` | 代码格式化 | **必须** |
| `vitest` / `jest` | 单元 / 集成测试 | **必须** |
| `pre-commit` | Git 提交前自动检查（集成上述工具） | 强烈推荐 |
| `knip` | 未使用代码 / 依赖检测 | 推荐 |
| `depcheck` | 依赖检查 | 推荐 |
| `ts-prune` / `ts-unused-exports` | 未使用导出检测 | 推荐 |

#### 安全规范

- **输入校验**：所有外部输入必须使用 `zod` / `io-ts` / `yup` 等库进行运行时验证
- **SQL 注入**：使用 ORM（Prisma / TypeORM / Drizzle）或参数化查询，**禁止** 字符串拼接 SQL
- **密钥管理**：使用环境变量（`process.env`）或 `.env` 文件（配合 `dotenv`），**禁止** 硬编码密钥到源码
- **依赖安全**：定期运行 `pnpm audit` / `npm audit` 扫描已知漏洞
- **原型污染**：**禁止** 直接合并用户输入到对象（`Object.assign` / 展开运算符），使用安全合并函数
- **正则注入**：**禁止** 将用户输入直接拼入 `RegExp`，使用 `RegExp` 构造函数并转义
- **eval**：**禁止** 使用 `eval()` / `new Function()` / `setTimeout(string)`
- **文件操作**：使用 `path.resolve()` + 白名单校验路径，防止目录穿越攻击
- **临时文件**：使用 `tmp` / `temp` 库创建，脚本退出时清理

#### 并发与异步

- **async/await**：优先使用 `async/await`，**禁止** `.then().catch()` 链式调用（除简单链式场景）
- **并行执行**：多个独立异步操作使用 `Promise.all()` / `Promise.allSettled()`
- **超时控制**：网络请求必须设置超时（`AbortSignal.timeout()`）
- **重试机制**：对外部 API 调用实现指数退避重试（`exponential backoff`）
- **内存泄漏**：事件监听器使用后必须 `removeEventListener`，定时器必须 `clearTimeout` / `clearInterval`
- **流处理**：大数据量使用 `ReadableStream` / `AsyncIterator`，避免一次性加载到内存

```typescript
// ✅ 并行请求 + 超时控制
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 5000);

try {
  const [users, posts] = await Promise.all([
    fetch('/api/users', { signal: controller.signal }),
    fetch('/api/posts', { signal: controller.signal }),
  ]);
} finally {
  clearTimeout(timeout);
}

// ✅ 错误安全的并行请求
const results = await Promise.allSettled([
  fetchUserData(id),
  fetchUserPosts(id),
]);
const failures = results.filter((r) => r.status === 'rejected');
```

#### 文件与目录结构

```
my-project/
    src/
        index.ts              # 入口文件
        config/               # 配置模块
            index.ts
            env.ts
        services/             # 业务逻辑层
            user.service.ts
            auth.service.ts
        models/               # 数据模型 / 类型定义
            user.model.ts
        utils/                # 工具函数
            logger.ts
            errors.ts
        types/                # 全局类型声明
            index.d.ts
    tests/                    # 测试文件
        services/
            user.service.test.ts
        fixtures/
    tsconfig.json
    eslint.config.js
    .prettierrc
    package.json
    pnpm-lock.yaml
```

- **模块化**：每个文件导出单一职责的模块，文件不超过 300 行
- **入口文件**：`index.ts` 仅负责组装和导出，**禁止** 包含业务逻辑
- **类型文件**：全局类型声明放在 `types/`，业务类型与实现文件同目录
- **配置文件**：环境变量解析放在 `config/env.ts`，使用 `zod` 校验环境变量类型
- **工具函数**：纯函数放在 `utils/`，无副作用

### Go

必须遵守 **Effective Go**（https://go.dev/doc/effective_go）与 **Go Code Review Comments**（https://github.com/golang/go/wiki/CodeReviewComments）：

#### 基础规范

- **最低版本**：Go ≥ 1.22（支持 range over func、增强的 routing 等新特性）
- **格式化**：**必须**使用 `gofmt` / `goimports` 格式化所有代码，禁止手动调整格式
- **缩进**：Tab（由 gofmt 自动处理）
- **行长**：不强制限制，但建议 ≤ 120 字符；长参数列表换行时对齐到开括号后
- **字符串**：优先使用双引号 `"` 字面量，需要转义时使用反引号 `` ` `` 原始字符串
- **空行**：函数之间空 1 行，逻辑块之间空 1 行，文件末尾保留空行
- **Semicolon**：Go 的分号由词法分析器自动插入，**禁止**手动添加分号

#### 命名规范

- 导出标识符（包、类型、函数、方法、常量、变量）：`PascalCase`
- 未导出标识符：`camelCase`
- 接口：单方法接口使用方法名 + `er` 后缀（如 `Reader`、`Writer`、`Stringer`）；多方法接口使用描述性名词（如 `ReadWriter`、`io.Closer`）
- 常量：未导出使用 `camelCase`，导出使用 `PascalCase`；枚举值使用 `iota` 或 `UPPER_SNAKE_CASE`（仅全局常量）
- 缩写词保持大写：`HTTPServer`、`URLParser`、`IDGenerator`、`JSONEncoder`
- 布尔变量 / 方法：使用 `is`、`has`、`can`、`should` 前缀，如 `isValid`、`hasPermission`
- 接收者名称：使用类型名的 1-2 个字母缩写，**保持一致**（如 `User` 类型使用 `u`）；不要使用 `this` 或 `self`
- 包名：使用简短的、全小写的、单词形式，不要使用下划线或驼峰（如 `json`、`http`，而非 `json_utils`、`JsonParser`）

#### 导入规范

```go
import (
    // 标准库
    "context"
    "fmt"
    "net/http"

    // 第三方库
    "github.com/gin-gonic/gin"
    "go.uber.org/zap"

    // 本项目包（使用相对路径或完整模块路径）
    "myproject/internal/model"
    "myproject/pkg/logger"
)
```

- 分组顺序：标准库 → 第三方库 → 本项目包，各组之间用空行分隔
- **禁止**：循环导入；如不可避免，提取公共接口到独立包
- **禁止**：点导入（`import . "pkg"`），除非是测试中的 matcher
- **禁止**：匿名导入（`import _ "pkg"`），除非是 side-effect 注册（如 `database/sql` 驱动、`net/http/pprof`）
- 使用 `goimports` 自动管理导入分组和排序

#### 类型声明规范

```go
// ✅ 推荐：结构体字段使用行尾注释说明含义
type User struct {
    ID        int64     `json:"id" db:"id"`         // 用户唯一标识
    Name      string    `json:"name" db:"name"`     // 用户名称
    Email     string    `json:"email" db:"email"`   // 电子邮箱
    CreatedAt time.Time `json:"created_at" db:"created_at"` // 创建时间
}

// ✅ 使用类型别名简化复杂类型
type HandlerFunc func(http.ResponseWriter, *http.Request)

// ✅ 使用 iota 定义枚举
type Status int

const (
    StatusActive   Status = iota // 活跃状态
    StatusInactive               // 未激活
    StatusBanned                 // 已封禁
)

// ❌ 禁止：空接口泛用
func Process(data interface{}) { // 应使用 any 或具体类型
    // ...
}
```

- 优先使用 `struct` 定义数据结构（支持 JSON/DB tag），**禁止**使用 `map[string]interface{}` 传递结构化数据
- `interface{}` 已被 `any` 替代（Go 1.18+），**禁止**使用 `interface{}`
- 类型断言必须使用 `value, ok := x.(Type)` 的 comma-ok 模式，**禁止**无检查断言
- 使用 `type` 为函数签名、常量组等创建有意义的别名，增强可读性

#### 文档规范（godoc）

**导出的包、类型、函数、方法必须编写 godoc 注释**。注释必须以被注释对象的名称开头：

```go
// Package logger 提供结构化日志记录功能。
//
// 本包基于 zap 实现，支持 JSON 格式输出和多级别日志。
package logger

// User 表示系统中的一个注册用户。
//
// User 包含用户的基本信息和认证状态。
// 创建用户时必须提供有效的 Name 和 Email。
type User struct {
    // ...
}

// FetchUser 根据用户 ID 从远程 API 获取用户信息。
//
// 参数 userId 为用户的唯一标识符，必须为正数。
// timeout 控制请求超时时间，单位为秒。
//
// 返回值为包含用户资料的结构体指针。
// 当用户不存在时返回 nil，不抛出错误。
//
// 如果网络请求失败，会返回包含上下文信息的 error。
func FetchUser(ctx context.Context, userID int64, timeout float64) (*User, error) {
    // ...
}
```

**说明注释必须使用中文**（godoc、行内注释、块注释均适用）：

- 包注释：描述包的用途和主要功能
- 导出类型：说明类型的用途、字段含义
- 导出函数：说明功能、参数、返回值、错误条件
- 复杂逻辑：在函数内部用行内注释解释意图，而非解释"做了什么"

#### 错误处理

```go
// ✅ 必须显式检查每个错误
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doSomething failed: %w", err) // 使用 %w 包装错误
}

// ✅ 使用 errors.Is / errors.As 比较和提取错误
if errors.Is(err, sql.ErrNoRows) {
    return nil, nil // 无数据，非错误
}

var pathError *os.PathError
if errors.As(err, &pathError) {
    log.Printf("文件操作失败: path=%s", pathError.Path)
}

// ✅ 定义哨兵错误（Sentinel Error）
var (
    ErrNotFound     = errors.New("资源不存在")
    ErrUnauthorized = errors.New("未授权访问")
    ErrRateLimited  = errors.New("请求频率超限")
)

// ✅ 使用自定义错误类型携带上下文
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("验证失败: 字段 %s - %s", e.Field, e.Message)
}
```

- **禁止**：使用 `_` 忽略错误（`result, _ := doSomething()`）
- **禁止**：仅 `return err`，必须使用 `fmt.Errorf("上下文: %w", err)` 包装，提供调用链路
- **禁止**：`panic()` 处理可预见的业务错误（`panic` 仅用于真正不可恢复的编程错误）
- 错误信息使用小写字母开头，不以标点结尾
- 在 API/HTTP 边界层将内部错误转换为用户友好的错误信息，**禁止**将内部错误详情暴露给调用方

#### 测试规范

```bash
# 目录结构
myproject/
    internal/
        service/
            user.go
            user_test.go       # 与被测文件同目录
    pkg/
        logger/
            logger.go
            logger_test.go
    tests/                     # 集成测试（可选）
        integration_test.go
    testdata/                  # 测试数据文件
```

- **文件命名**：`xxx_test.go`，与被测文件同目录（白盒测试）或在 `tests/` 目录（黑盒测试）
- **函数命名**：`Test功能描述`（如 `TestFetchUser_NotFound`）
- **表驱动测试**（Go 推荐模式）：

```go
func TestFetchUser(t *testing.T) {
    tests := []struct {
        name    string
        userID  int64
        want    *User
        wantErr error
    }{
        {
            name:   "有效用户",
            userID: 1,
            want:   &User{ID: 1, Name: "Alice"},
        },
        {
            name:    "用户不存在",
            userID:  999,
            wantErr: ErrNotFound,
        },
        {
            name:    "无效ID",
            userID:  -1,
            wantErr: &ValidationError{Field: "userID", Message: "must be positive"},
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := FetchUser(context.Background(), tt.userID, 30)
            if tt.wantErr != nil {
                if !errors.Is(err, tt.wantErr) && !errors.As(err, &tt.wantErr) {
                    t.Errorf("FetchUser() error = %v, wantErr %v", err, tt.wantErr)
                }
                return
            }
            if err != nil {
                t.Errorf("FetchUser() unexpected error = %v", err)
                return
            }
            if got.ID != tt.want.ID || got.Name != tt.want.Name {
                t.Errorf("FetchUser() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

- **基准测试**：函数以 `Benchmark` 开头，使用 `testing.B`，放在 `_test.go` 文件中
- **模糊测试**：使用 `func FuzzXxx(f *testing.F)` 进行模糊测试（Go 1.18+）
- **测试覆盖率**：核心包要求覆盖率 ≥ 80%（`go test -cover`）
- **Mock**：使用 `go.uber.org/mock` 或 `github.com/stretchr/testify/mock`，mock 外部依赖（网络、数据库、文件系统）
- **测试隔离**：每个测试用例独立，使用 `t.Cleanup` / `t.TempDir` 清理资源
- **并行测试**：无状态的测试使用 `t.Parallel()` 提高执行速度

#### 并发与性能

```go
// ✅ 使用 context 控制超时和取消
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

result, err := doWork(ctx)

// ✅ 使用 errgroup 管理多个并发任务的错误
g, ctx := errgroup.WithContext(ctx)

g.Go(func() error {
    return fetchUserData(ctx, userID)
})

g.Go(func() error {
    return fetchUserOrders(ctx, userID)
})

if err := g.Wait(); err != nil {
    return fmt.Errorf("并发任务失败: %w", err)
}

// ✅ 使用 select 实现非阻塞 channel 操作
select {
case msg := <-ch:
    handleMessage(msg)
case <-ctx.Done():
    return ctx.Err()
case <-time.After(time.Second):
    return errors.New("操作超时")
}
```

- **goroutine 泄漏**：每个启动的 goroutine 必须有明确的退出路径（通过 context 取值、channel 关闭或 `sync.WaitGroup`）
- **channel 所有权**：明确 channel 的写入方和读取方；通常由写入方负责 close
- **sync 包**：优先使用 `sync.Mutex` / `sync.RWMutex` 保护共享状态；使用 `sync.Once` 实现单次初始化；使用 `sync.Pool` 减少内存分配
- **性能分析**：使用 `pprof`（`net/http/pprof` 或 `runtime/pprof`）定位 CPU/内存/goroutine 瓶颈
- **内存分配**：使用 `go tool alloc` 和 `-gcflags="-m"` 检查逃逸分析，减少堆分配
- **禁止**：在热路径中使用 `fmt.Sprintf` 拼接字符串（使用 `strings.Builder` 或 `bytes.Buffer`）
- **禁止**：无限制地启动 goroutine（使用 worker pool 或 semaphore 限制并发数）

#### 依赖与项目管理

```go
// go.mod — 唯一的依赖声明入口
module myproject

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    go.uber.org/zap v1.27.0
)
```

- **依赖管理**：使用 `go mod` 管理依赖（`go mod tidy`、`go mod vendor`），**禁止**手动编辑 `go.mod` / `go.sum`
- **版本锁定**：`go.sum` 必须提交到版本控制，确保团队依赖一致
- **依赖更新**：使用 `go get -u` 更新依赖，更新后执行 `go mod tidy` 清理
- **安全审计**：使用 `govulncheck` 扫描已知漏洞
- **工作区**：多模块项目使用 `go.work`（Go 1.18+ workspace）管理本地依赖
- **新依赖评估**：新增第三方依赖前评估其维护状态、许可证兼容性、社区活跃度

#### 代码质量工具链

```yaml
# .golangci.yml — golangci-lint 配置
run:
  timeout: 5m
  go: "1.22"

linters:
  enable:
    - errcheck      # 检查未处理的错误
    - gosimple      # 简化代码建议
    - govet         # go vet 检查
    - ineffassign   # 检查无效赋值
    - staticcheck   # 综合静态分析
    - unused        # 检查未使用代码
    - gocritic      # 代码审查建议
    - revive        # 可配置的 linter（替代 golint）
    - goimports     # 导入分组检查
    - misspell      # 拼写检查
    - bodyclose     # HTTP response body 关闭检查
    - noctx         # 检查没有 context 的 HTTP 请求
    - exportloopref # 循环变量引用检查

linters-settings:
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
```

| 工具 | 用途 | 优先级 |
|---|---|---|
| `gofmt` / `goimports` | 代码格式化（**必须**在提交前执行） | **必须** |
| `go vet` | 标准静态检查（可疑代码构造） | **必须** |
| `staticcheck` | 高级静态分析（包含 go vet 的超集） | **必须** |
| `golangci-lint` | 综合 Lint 工具（集成多个 linter） | **必须** |
| `govulncheck` | 依赖安全漏洞扫描 | **必须** |
| `go test -race` | 竞态条件检测 | **必须** |
| `go test -cover` | 测试覆盖率报告 | **必须** |
| `pre-commit` | Git 提交前自动检查（集成上述工具） | 强烈推荐 |

#### 安全规范

- **输入验证**：所有外部输入（HTTP 请求参数、环境变量、文件内容）必须进行校验
- **SQL 注入**：使用 `database/sql` 的参数化查询（`?` 占位符），**禁止**字符串拼接 SQL
  ```go
  // ✅ 正确
  row := db.QueryRowContext(ctx, "SELECT * FROM users WHERE id = ?", userID)

  // ❌ 禁止
  query := fmt.Sprintf("SELECT * FROM users WHERE id = %d", userID)
  ```
- **密钥管理**：使用环境变量（`os.Getenv`）或密钥管理服务，**禁止**硬编码密钥到源码
- **依赖安全**：定期运行 `govulncheck` / `go mod verify` 扫描已知漏洞
- **文件操作**：使用 `filepath.Clean` + `filepath.Abs` 校验和规范化路径，防止目录穿越攻击
- **临时文件**：使用 `os.CreateTemp` / `os.MkdirTemp` 创建，脚本退出时清理
- **HTTP 安全**：设置合理的超时（`http.Client.Timeout`），限制请求体大小，验证 TLS 证书
- **反序列化**：使用 `json.Decoder` 而非 `json.Unmarshal` 处理 HTTP 请求体，防止内存耗尽
- **竞态安全**：使用 `go test -race` 检测竞态条件，生产代码中正确使用锁或原子操作

#### 文件与目录结构

```
myproject/
    cmd/                        # 可执行入口
        server/
            main.go             # 主程序入口
        worker/
            main.go             # 后台任务入口
    internal/                   # 私有包（不可被外部导入）
        handler/                # HTTP 处理器
            user.go
            user_test.go
        service/                # 业务逻辑层
            user.go
            user_test.go
        repository/             # 数据访问层
            user.go
            user_test.go
        model/                  # 数据模型
            user.go
            errors.go
    pkg/                        # 可被外部导入的公共包
        logger/
            logger.go
            logger_test.go
    api/                        # API 定义（protobuf/OpenAPI）
    configs/                    # 配置文件
        config.yaml
    scripts/                    # 脚本
    migrations/                 # 数据库迁移文件
    testdata/                   # 测试数据
    tests/                      # 集成/E2E 测试
    go.mod
    go.sum
    Makefile                    # 常用命令入口
    .golangci.yml               # Lint 配置
    README.md
```

- **`cmd/`**：每个可执行文件一个子目录，`main.go` 仅负责组装和启动，**禁止**包含业务逻辑
- **`internal/`**：私有包，Go 编译器强制禁止外部导入，核心业务逻辑放在此处
- **`pkg/`**：可被外部项目导入的公共库代码
- **分层架构**：`handler`（输入处理）→ `service`（业务逻辑）→ `repository`（数据访问），各层通过接口解耦
- **每个文件不超过 500 行**，超过时按职责拆分为多个文件
- **`Makefile`**：统一管理常用命令（`make build`、`make test`、`make lint`、`make docker`）

### C++

必须遵守 **C++ Core Guidelines**（https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines）与 **Google C++ Style Guide**（https://google.github.io/styleguide/cppguide.html）：

#### 基础规范

- **最低版本**：C++ ≥ 17（推荐 C++20，支持 Concepts、Ranges、Coroutines 等新特性）
- **格式化**：必须使用 `clang-format` 格式化所有代码，配置文件为 `.clang-format`
- **缩进**：2 个空格（Google 风格），禁止 Tab
- **行长**：≤ 100 字符
- **空行**：顶层函数 / 类之间空 1 行，类内方法之间空 1 行，逻辑块之间空 1 行
- **大括号**：函数体左大括号换行，控制语句不换行（K&R for control, Allman for function）
- **行尾**：禁止行尾空格，文件末尾保留一个空行
- **头文件保护**：使用 `#pragma once` 或传统 include guard（`#ifndef` / `#define` / `#endif`）
- **命名空间**：禁止使用 `using namespace` 在头文件中；源文件中可使用 `using` 声明

#### 命名规范

- 文件名：`snake_case`（如 `user_service.cpp`、`user_service.h`）
- 类 / 结构体 / 枚举 / 类型别名 / 模板参数：`PascalCase`
- 函数 / 方法：`PascalCase`（Google 风格）或 `camelCase`（与项目保持一致）
- 变量 / 参数：`snake_case`
- 成员变量：`snake_case_`（尾部下划线），或使用 `m_` 前缀（与项目保持一致）
- 常量（`constexpr` / `const`）：`kPascalCase`（Google 风格）或 `UPPER_SNAKE_CASE`
- 枚举值：`UPPER_SNAKE_CASE` 或 `kPascalCase`（与项目保持一致）
- 宏：`UPPER_SNAKE_CASE`
- 模板类型参数：单个大写字母 `T`，多个用递增字母 `T1`、`T2`；语义化命名如 `ValueType`、`CallbackType`
- 布尔变量 / 方法：使用 `is`、`has`、`can`、`should` 前缀，如 `is_valid`、`has_permission`
- 缩写词保持大小写规则：`HTTPClient`、`URLParser`、`IDGenerator`

```cpp
// ✅ 正确
class UserService {
 public:
  // 公有方法
  bool IsActive() const { return is_active_; }
  std::string GetFullName() const;
 private:
  static constexpr int kMaxRetryCount = 3;
  int user_id_;
  bool is_active_;
};

// ❌ 错误
class user_service {
  const int maxRetryCount = 3;  // 应为 kMaxRetryCount 或 UPPER_SNAKE_CASE
  int userId;                   // 应为 user_id_
  bool active;                  // 缺少 is 前缀和尾部下划线
};
```

#### 头文件与包含规范

```cpp
// 顺序：对应头文件 → C 标准库 → C++ 标准库 → 第三方库 → 本项目头文件
// 各组之间用空行分隔

#include "user_service.h"           // 对应头文件（.cpp 首行）

#include <stdio.h>                  // C 标准库
#include <string.h>

#include <algorithm>                // C++ 标准库
#include <memory>
#include <string>
#include <vector>

#include "absl/strings/str_format.h"  // 第三方库
#include "gtest/gtest.h"

#include "project/utils/logger.h"      // 本项目头文件
```

- **必须**使用对应头文件作为 `.cpp` 文件的首行包含
- **禁止**：在头文件中使用 `using namespace`；源文件中可有限使用
- **禁止**：循环包含；使用前向声明（forward declaration）打破循环依赖
- **推荐**：使用前向声明替代不必要的 `#include`，减少编译依赖
- 包含路径：使用相对路径（`"project/utils/logger.h"`）或配置好的 include path

#### 类型规范

```cpp
// ✅ 使用智能指针管理动态内存
auto user = std::make_unique<User>(args);
auto shared = std::make_shared<User>(args);

// ✅ 使用 enum class 替代传统枚举
enum class PaymentMethod : uint8_t {
  kCreditCard = 0,
  kAlipay     = 1,
  kWechatPay  = 2,
};

// ✅ 使用 auto 进行类型推导（当类型显而易见时）
auto it = map.find(key);
auto count = static_cast<int>(vec.size());

// ✅ 使用 using 替代 typedef
using UserID = std::string;
using UserMap = std::unordered_map<UserID, User>;
using Callback = std::function<void(int, const std::string&)>;

// ✅ 使用 constexpr 替代宏定义常量
constexpr double kPi = 3.14159265358979;
constexpr int kBufferSize = 1024;

// ❌ 禁止：使用宏定义常量
#define PI 3.14159
#define BUFFER_SIZE 1024

// ❌ 禁止：裸指针管理动态内存
User* user = new User();  // 应使用 std::unique_ptr
```

- **优先**：使用值语义（栈对象），避免不必要的堆分配
- **必须**：使用 `std::unique_ptr` / `std::shared_ptr` 管理动态分配的对象，**禁止** 裸 `new` / `delete`
- **优先**：使用 `enum class`（强类型枚举）替代传统 `enum`
- **禁止**：使用 `NULL` 或 `0` 表示空指针，**必须**使用 `nullptr`
- **禁止**：使用 C 风格类型转换（如 `(int)x`），**必须**使用 `static_cast` / `dynamic_cast` / `const_cast` / `reinterpret_cast`
- **推荐**：使用 `std::optional`（C++17）表示可选值，而非空指针或哨兵值
- **推荐**：使用 `std::variant` / `std::any`（C++17）替代 `union` 和 `void*`
- **推荐**：使用 `std::string_view`（C++17）替代 `const std::string&` 作为只读字符串参数
- **推荐**：使用 `std::span`（C++20）替代裸指针 + 长度的数组参数

#### 文档规范（Doxygen / 注释）

**公共头文件、类、公共方法必须编写文档注释**。说明注释必须使用中文：

```cpp
/**
 * @brief 用户服务类，提供用户相关的业务逻辑操作。
 *
 * 本类负责处理用户注册、查询、更新等核心业务流程。
 * 所有方法均为线程安全的。
 *
 * @note 创建用户时必须提供有效的 name 和 email。
 */
class UserService {
 public:
  /**
   * @brief 根据用户 ID 查询用户信息。
   *
   * 当用户不存在时返回 nullptr，不抛出异常。
   *
   * @param user_id 用户的唯一标识符，必须为正数
   * @param timeout 查询超时时间，单位为秒
   * @return 包含用户信息的 unique_ptr；用户不存在时返回 nullptr
   *
   * @throws std::invalid_argument 当 user_id 为负数时抛出
   * @throws ConnectionError 当数据库连接失败时抛出
   */
  std::unique_ptr<User> FindUserById(int user_id, double timeout);

 private:
  // 数据库连接池
  ConnectionPool pool_;
};
```

- 使用 `@brief`、`@param`、`@return`、`@throws`、`@note`、`@see` 等 Doxygen 标签
- **说明注释必须使用中文**
- 复杂逻辑在函数内部使用行内注释解释意图（而非解释"做了什么"）
- TODO 注释格式：`// TODO(负责人): 描述待办事项`，禁止遗留无主 TODO
- 类的公有成员函数和公有成员变量需要注释，私有成员可选

#### 错误处理

```cpp
// ✅ 使用异常处理可恢复的错误
class AppError : public std::runtime_error {
 public:
  explicit AppError(const std::string& msg,
                    const std::string& code = "",
                    std::exception_ptr cause = nullptr)
      : std::runtime_error(msg), code_(code), cause_(cause) {}

  const std::string& code() const { return code_; }
  std::exception_ptr cause() const { return cause_; }

 private:
  std::string code_;
  std::exception_ptr cause_;
};

// ✅ 使用错误码处理性能敏感的错误路径
enum class ErrorCode : int {
  kOk = 0,
  kNotFound = -1,
  kInvalidArgument = -2,
  kInternal = -3,
};

// ✅ 使用 std::expected（C++23）或 tl::expected 库
// ✅ 使用 std::optional 表示"无结果"
std::unique_ptr<User> FindUserById(int user_id) {
  if (user_id < 0) {
    throw std::invalid_argument("user_id must be positive");
  }
  try {
    auto user = db_->Query(user_id);
    return user;
  } catch (const DatabaseError& e) {
    LOG(ERROR) << "Database query failed: " << e.what();
    throw AppError("Failed to query user", "DB_ERROR", std::current_exception());
  }
}

// ❌ 禁止：空 catch 块
try {
  risky_operation();
} catch (...) {
  // 禁止空 catch 块！
}
```

- **可恢复错误**：使用异常（`try` / `catch`），适用于业务逻辑错误
- **性能敏感路径**：使用错误码（`enum class`）+ 输出参数，避免异常开销
- **捕获**：使用具体异常类型，**禁止** `catch (...)` 静默忽略
- **资源清理**：优先使用 RAII（Resource Acquisition Is Initialization），其次使用 `try` / `finally`（配合 `gsl::finally`）
- **日志**：使用 `LOG(ERROR)` 或项目日志库记录异常，**禁止** `printf` / `std::cerr` 输出生产日志
- **异常链**：使用 `std::current_exception()` + `std::rethrow_exception()` 保留原始异常

#### 测试规范

```bash
# 目录结构
project/
    src/
        user_service.cpp
        user_service.h
    tests/
        user_service_test.cpp    # 与被测文件对应
        test_main.cpp            # 测试入口
    third_party/
        googletest/              # Google Test 框架
```

- **框架**：Google Test（`gtest`）+ Google Mock（`gmock`），**禁止** 使用过时的 `CPPUnit`
- **文件命名**：`<module>_test.cpp`，与源文件同目录或在 `tests/` 下
- **函数命名**：`TEST(ClassName, ShouldDoSomethingWhenCondition)` 或 `TEST_F`（Fixture）
- **断言**：使用 `EXPECT_*`（非致命）和 `ASSERT_*`（致命），推荐 `EXPECT_*`
- **覆盖率**：核心模块要求覆盖率 ≥ 80%（使用 `gcov` / `lcov`）
- **Mock**：使用 `gmock` mock 外部依赖（网络、数据库、文件系统）

```cpp
#include "user_service.h"
#include "gmock/gmock.h"
#include "gtest/gtest.h"

using ::testing::_;
using ::testing::Return;

class MockUserRepository : public UserRepository {
 public:
  MOCK_METHOD(std::unique_ptr<User>, FindById, (int user_id), (const, override));
  MOCK_METHOD(bool, Save, (const User& user), (const, override));
};

class UserServiceTest : public ::testing::Test {
 protected:
  void SetUp() override {
    mock_repo_ = std::make_unique<MockUserRepository>();
    service_ = std::make_unique<UserService>(std::move(mock_repo_));
  }

  std::unique_ptr<MockUserRepository> mock_repo_;
  std::unique_ptr<UserService> service_;
};

TEST_F(UserServiceTest, ShouldReturnUserWhenFound) {
  // Arrange
  auto user = std::make_unique<User>(1, "Alice");
  EXPECT_CALL(*mock_repo_, FindById(1)).WillOnce(Return(std::move(user)));

  // Act
  auto result = service_->FindUserById(1, 30.0);

  // Assert
  ASSERT_NE(result, nullptr);
  EXPECT_EQ(result->name(), "Alice");
}

TEST_F(UserServiceTest, ShouldReturnNullptrWhenUserNotFound) {
  EXPECT_CALL(*mock_repo_, FindById(999)).WillOnce(Return(nullptr));
  auto result = service_->FindUserById(999, 30.0);
  EXPECT_EQ(result, nullptr);
}
```

#### 依赖与项目管理

```cmake
# CMakeLists.txt — 推荐的构建系统入口
cmake_minimum_required(VERSION 3.20)
project(MyProject VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 第三方依赖（推荐使用 FetchContent 或 vcpkg/conan）
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

# 项目源文件
add_library(my_project
  src/user_service.cpp
  src/utils/logger.cpp
)

target_include_directories(my_project PUBLIC src/)

# 测试
enable_testing()
add_executable(my_project_tests
  tests/user_service_test.cpp
)
target_link_libraries(my_project_tests
  my_project
  GTest::gtest_main
  GTest::gmock
)
include(GoogleTest)
gtest_discover_tests(my_project_tests)
```

- **构建系统**：推荐 CMake（≥ 3.20），**禁止** 手动维护 Makefile（大型项目除外）
- **包管理**：推荐 `vcpkg`（微软官方）或 `conan`（JFrog），**禁止** 手动下载第三方库
- **依赖锁定**：使用 `vcpkg.json` + `vcpkg-lock.json` 或 `conanfile.txt` + `conanfile.lock` 锁定版本
- **依赖安全**：定期扫描第三方库的已知漏洞
- **C++ 标准**：通过 `CMAKE_CXX_STANDARD` 或编译选项指定，**禁止**在代码中依赖编译器特定扩展

#### 代码质量工具链

```yaml
# .clang-format — 代码格式化配置
BasedOnStyle: Google
IndentWidth: 2
ColumnLimit: 100
AllowShortFunctionsOnASingleLine: Empty
AllowShortIfStatementsOnASingleLine: Never
BreakBeforeBraces: Attach
PointerAlignment: Left
```

```yaml
# .clang-tidy — 静态分析配置
Checks: >
  -*,
  clang-analyzer-*,
  cppcoreguidelines-*,
  bugprone-*,
  modernize-*,
  performance-*,
  readability-*,
  -modernize-use-trailing-return-type
```

| 工具 | 用途 | 优先级 |
|---|---|---|
| `clang-format` | 代码格式化（**必须**在提交前执行） | **必须** |
| `clang-tidy` | 静态分析（C++ Core Guidelines 检查） | **必须** |
| `cppcheck` | 补充静态分析（检测未定义行为等） | **必须** |
| `Google Test` | 单元 / 集成测试框架 | **必须** |
| `gcov` / `lcov` | 测试覆盖率报告 | **必须** |
| `cmake-lint` | CMake 配置文件检查 | 推荐 |
| `include-what-you-use` | 头文件包含优化 | 推荐 |

#### 安全规范

- **输入验证**：所有外部输入（HTTP 请求、文件内容、命令行参数）必须进行校验
- **内存安全**：使用智能指针和容器，**禁止** 裸 `new` / `delete`；使用 `std::array` 替代 C 数组
- **缓冲区溢出防护**：使用 `std::string`、`std::vector` 等安全容器；使用 `snprintf` 替代 `sprintf`
- **密钥管理**：使用环境变量或密钥管理服务，**禁止** 硬编码密钥到源码
- **反序列化**：使用安全的序列化库（如 `protobuf`、`nlohmann/json`），**禁止** 直接解析不受信任的二进制数据
- **格式化字符串**：使用 `std::format`（C++20）或 `fmt::fmt`，**禁止** `printf` / `sprintf` 处理不受信任的输入
- **整数溢出**：使用 `checked_cast`（GSL）或编译器内置检查（`-ftrapv`）
- **编译器加固**：启用 `-fstack-protector-strong`、`-D_FORTIFY_SOURCE=2`、`-fPIE` / `-pie`

#### 并发与性能

```cpp
// ✅ 使用 std::thread 和线程池管理并发
auto pool = std::make_shared<ThreadPool>(num_threads);
auto future = pool->enqueue([](int x) { return x * x; }, 42);

// ✅ 使用 std::atomic 保护简单的共享状态
std::atomic<int> counter{0};
counter.fetch_add(1, std::memory_order_relaxed);

// ✅ 使用 std::mutex 和 std::lock_guard 保护临界区
std::mutex mtx;
{
  std::lock_guard<std::mutex> lock(mtx);
  shared_state_ = new_value;
}

// ✅ 使用 std::shared_mutex 实现读写锁（C++17）
std::shared_mutex rw_mutex;
{
  std::shared_lock<std::shared_mutex> read_lock(rw_mutex);  // 读锁
  auto value = shared_map_[key];
}
{
  std::unique_lock<std::shared_mutex> write_lock(rw_mutex);  // 写锁
  shared_map_[key] = new_value;
}

// ✅ 使用 std::condition_variable 实现等待 / 通知
std::condition_variable cv;
std::mutex cv_mtx;
std::unique_lock<std::mutex> lock(cv_mtx);
cv.wait(lock, [&] { return data_ready; });

// ❌ 禁止：使用裸 std::thread 而不管理生命周期
std::thread t([] { do_work(); });  // 应使用线程池或 join/detach 管理
```

- **内存模型**：正确使用 `std::memory_order`，默认使用 `memory_order_seq_cst`
- **线程安全**：使用 `std::atomic` 保护简单标志，使用 `std::mutex` 保护复杂共享状态
- **数据竞争**：使用 ThreadSanitizer（`-fsanitize=thread`）检测数据竞争
- **性能分析**：使用 `perf`、`gprof` 或 `Google Benchmark` 定位性能瓶颈
- **RAII 资源管理**：使用 `std::lock_guard` / `std::unique_lock` 管理锁，**禁止** 手动 `lock()` / `unlock()`
- **移动语义**：优先使用 `std::move` 传递大型对象的所有权，避免不必要的拷贝
- **禁止**：在热路径中使用 `std::shared_ptr` 的原子引用计数（开销大）
- **禁止**：使用 `std::endl`（强制刷新缓冲区），**优先**使用 `'\n'`

#### 文件与目录结构

```
my_project/
    src/                        # 源文件
        user_service.cpp
        user_service.h
        utils/
            logger.cpp
            logger.h
    include/                    # 公共头文件（可选，与 src/ 分离）
        my_project/
            user_service.h
    tests/                      # 测试文件
        user_service_test.cpp
        fixtures/               # 测试数据
    third_party/                # 第三方依赖（或使用 vcpkg/conan）
        googletest/
    cmake/                      # CMake 模块
        FindXXX.cmake
    CMakeLists.txt              # 构建配置入口
    .clang-format               # 代码格式化配置
    .clang-tidy                 # 静态分析配置
    vcpkg.json                  # 依赖声明（vcpkg）
    README.md
```

- **头文件与源文件分离**：`.h`（声明）与 `.cpp`（实现）分离，**禁止** 在头文件中包含函数实现（模板和 inline 函数除外）
- **每个文件不超过 500 行**，超过时按职责拆分为多个文件
- **命名空间**：按项目 / 模块组织，如 `my_project::service`、`my_project::utils`
- **前向声明**：在头文件中优先使用前向声明替代 `#include`，减少编译依赖
- **CMake 组织**：每个子目录一个 `CMakeLists.txt`，使用 `add_subdirectory()` 组织

### Rust

必须遵守 **Rust API Guidelines** 与 `rustfmt` 标准：

- **格式化**：必须使用 `rustfmt` 格式化所有代码
- **命名**：函数 / 变量 `snake_case`，类型 `PascalCase`，常量 `SCREAMING_SNAKE_CASE`
- **文档**：公共 API 必须有 `///` 文档注释并包含示例
- **错误处理**：使用 `Result<T, E>` 传播错误，`unwrap()` 仅在测试和原型中使用
- **Lint**：使用 `clippy`，禁止随意 `#[allow(clippy::...)]` 覆盖核心警告
- **生命周期**：显式标注生命周期，避免不必要的 `'static`
- **unsafe**：禁止无说明的 `unsafe` 代码块，必须注释安全理由
- **依赖**：新增依赖需评估安全性、维护状态与许可证兼容性

### Java

以 **Google Java Style Guide** 为主（https://google.github.io/styleguide/javaguide.html）：

#### 基础规范

- **最低版本**：Java ≥ 17（推荐 21 LTS，支持虚拟线程、Record 模式匹配等新特性）
- **缩进**：2 个空格（Google 风格），禁止 Tab
- **行长**：≤ 100 字符（Google 风格默认 100）
- **空行**：顶层类之间空 1 行，类内方法之间空 1 行，逻辑块之间空 1 行
- **大括号**：K&R 风格（左大括号不换行），`else`、`catch`、`finally` 与右大括号同行
- **行尾**：禁止行尾空格，文件末尾保留一个空行

```java
// ✅ 正确：K&R 风格大括号
if (condition) {
    doSomething();
} else {
    doOtherThing();
}

// ❌ 错误：Allman 风格
if (condition)
{
    doSomething();
}
```

#### 命名规范

- 包名：全小写，使用反转域名（`com.example.project`），禁止下划线
- 类 / 接口 / 注解 / 枚举：`PascalCase`，如 `UserService`、`HttpRequestHandler`
- 方法 / 变量：`lowerCamelCase`，如 `getUserName()`、`isActive`
- 常量（`static final`）：`UPPER_SNAKE_CASE`，如 `MAX_RETRY_COUNT`
- 枚举值：`UPPER_SNAKE_CASE`（Google 风格），如 `Status.ACTIVE`
- 泛型类型参数：单个大写字母，如 `T`、`E`、`K`、`V`；多个用递增字母 `T1`、`T2`
- 布尔变量 / 方法：使用 `is`、`has`、`can`、`should` 前缀，如 `isValid`、`hasPermission`
- 测试方法：使用 `should` 前缀描述预期行为，如 `shouldReturnUserWhenFound()`

```java
// ✅ 正确
public class UserService {
    private static final int MAX_RETRY_COUNT = 3;
    private final UserRepository userRepository;

    public boolean isActive() { /* ... */ }
    public Optional<User> findUserById(String userId) { /* ... */ }
}

// ❌ 错误
public class user_service {
    private static final int maxRetryCount = 3;  // 应为 UPPER_SNAKE_CASE
    public boolean active() { /* ... */ }         // 缺少 is 前缀
}
```

#### 导入规范

```java
// 顺序：静态导入 → 标准库 → 第三方库 → 本项目包
// 各组之间用空行分隔，每行一个 import

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import com.google.common.collect.ImmutableList;
import org.springframework.stereotype.Service;

import com.example.project.model.User;
import com.example.project.repository.UserRepository;
```

- **禁止**：通配符导入 `import xxx.*`（静态断言中的 `Assertions.*` 除外）
- **禁止**：循环依赖；如不可避免，使用接口抽象或依赖注入解耦
- 排序工具：`google-java-format` 自动处理 import 顺序
- **静态导入优先**：测试断言、常量、工具方法使用静态导入提高可读性

#### 类型规范

```java
// ✅ 使用 Record 定义不可变数据类（Java 16+）
public record UserDTO(String id, String name, String email) {
    // Record 自动生成构造器、getter、equals、hashCode、toString
}

// ✅ 使用 sealed class 限制继承（Java 17+）
public sealed interface Shape
    permits Circle, Rectangle, Triangle {
}

// ✅ 使用 enum 实现策略模式
public enum PaymentMethod {
    CREDIT_CARD("信用卡"),
    ALIPAY("支付宝"),
    WECHAT_PAY("微信支付");

    private final String displayName;

    PaymentMethod(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }
}

// ✅ 使用 Optional 表达可选值
public Optional<User> findUserById(String id) {
    return userRepository.findById(id);
}

// ❌ 禁止：返回 null 表示未找到
public User findUserById(String id) {
    return userRepository.findById(id).orElse(null);  // 不推荐
}
```

- 优先使用 `Record` 定义不可变 DTO / Value Object，**禁止** 手写样板代码
- 优先使用 `sealed class/interface` 限制类层次
- 集合优先使用不可变工厂方法：`List.of()`、`Map.of()`、`Set.of()`
- 使用 `Optional` 表达可选返回值，**禁止** 方法返回 `null` 表示"未找到"
- 泛型上限使用 `extends`：`<T extends Comparable<T>>`
- **禁止** 原始类型（`List` 而非 `List<String>`）

#### 文档规范（Javadoc）

**公共类、公共方法、公共接口必须编写 Javadoc 注释**。说明注释必须使用中文：

```java
/**
 * 用户服务类，提供用户相关的业务逻辑操作。
 *
 * <p>本类负责处理用户注册、查询、更新等核心业务流程。
 * 所有方法均为线程安全的。
 *
 * @author team
 * @since 1.0
 */
@Service
public class UserService {

    /**
     * 根据用户 ID 查询用户信息。
     *
     * <p>当用户不存在时返回 Optional.empty()，不抛出异常。
     *
     * @param userId 用户的唯一标识符，不能为空
     * @param timeout 查询超时时间，单位为秒，必须为正数
     * @return 包含用户信息的 Optional；用户不存在时返回 empty
     * @throws IllegalArgumentException 当 userId 为空或 timeout 为负数时抛出
     * @throws ConnectionException 当数据库连接失败时抛出
     */
    public Optional<User> findUserById(String userId, long timeout) {
        // 实现细节...
    }
}
```

- 使用 `{@link}` 引用其他类或方法，使用 `{@code}` 标记代码片段
- `@param`、`@return`、`@throws` 必须完整且使用中文描述
- 复杂逻辑在方法内部使用行内注释解释意图（而非解释"做了什么"）
- TODO 注释格式：`// TODO(负责人): 描述待办事项`，禁止遗留无主 TODO

#### 错误处理

```java
// ✅ 使用自定义异常表达业务逻辑
public class InsufficientBalanceException extends RuntimeException {
    private final String accountId;
    private final BigDecimal currentBalance;
    private final BigDecimal requiredAmount;

    public InsufficientBalanceException(
            String accountId,
            BigDecimal currentBalance,
            BigDecimal requiredAmount) {
        super(String.format("账户 %s 余额不足: 当前 %.2f, 需要 %.2f",
                accountId, currentBalance, requiredAmount));
        this.accountId = accountId;
        this.currentBalance = currentBalance;
        this.requiredAmount = requiredAmount;
    }
    // getter 方法...
}

// ✅ 检查型异常用于可恢复场景，非检查型异常用于编程错误
public void transferMoney(String from, String to, BigDecimal amount)
        throws InsufficientBalanceException {
    // ...
}

// ✅ 使用 try-with-resources 管理资源
try (var connection = dataSource.getConnection();
     var statement = connection.prepareStatement(sql)) {
    // 自动关闭资源，无需 finally 块
}

// ❌ 禁止：捕获 Exception 后静默忽略
try {
    riskyOperation();
} catch (Exception e) {
    // 禁止空 catch 块！
}
```

- 检查型异常（`checked exception`）：用于可恢复的业务场景（如 `IOException`）
- 非检查型异常（`unchecked exception`）：用于编程错误（如 `NullPointerException`）
- 使用自定义异常类携带上下文信息，**禁止** 直接抛出通用 `Exception`
- 资源清理优先使用 `try-with-resources`（`AutoCloseable`），**禁止** 手动 `finally` 关闭
- 日志记录使用 `logger.error("操作描述", exception)`，**禁止** `e.printStackTrace()`
- 异常链：使用 `throw new AppException("上下文", cause)` 保留原始异常

#### 测试规范

```bash
# 目录结构（Maven 标准布局）
src/
    main/
        java/
        resources/
    test/
        java/
        resources/
```

- **框架**：JUnit 5（`jupiter`），**禁止** 使用过时的 JUnit 4 `@RunWith`
- **文件命名**：`<ClassName>Test.java`，与被测类同包名
- **方法命名**：`should<预期行为>When<条件>()` 或 `test<方法名>_<场景>()`
- **断言**：使用 `Assertions.*` 静态导入，推荐结合 AssertJ 流式断言
- **覆盖率**：核心模块要求覆盖率 ≥ 80%（`JaCoCo`）
- **Mock**：使用 Mockito（`@Mock`、`@InjectMocks`），mock 外部依赖
- **参数化测试**：使用 `@ParameterizedTest` + `@ValueSource` / `@CsvSource`

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void shouldReturnUserWhenFound() {
        // Given
        String userId = "u-001";
        User expectedUser = new User(userId, "Alice");
        when(userRepository.findById(userId)).thenReturn(Optional.of(expectedUser));

        // When
        Optional<User> result = userService.findUserById(userId, 30);

        // Then
        assertTrue(result.isPresent());
        assertEquals("Alice", result.get().name());
        verify(userRepository, times(1)).findById(userId);
    }

    @Test
    void shouldReturnEmptyWhenUserNotFound() {
        when(userRepository.findById("nonexistent")).thenReturn(Optional.empty());

        Optional<User> result = userService.findUserById("nonexistent", 30);

        assertTrue(result.isEmpty());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "  ", "null"})
    void shouldThrowWhenUserIdIsBlank(String userId) {
        assertThrows(IllegalArgumentException.class,
            () -> userService.findUserById(userId, 30));
    }
}
```

#### 依赖与项目管理

```xml
<!-- pom.xml（Maven 项目配置入口） -->
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.release>17</maven.compiler.release>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>
```

或

```kotlin
// build.gradle.kts（Gradle Kotlin DSL，推荐）
plugins {
    java
    id("org.springframework.boot") version "3.2.0"
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}
```

- **构建工具**：推荐 Maven 或 Gradle（Kotlin DSL），**禁止** 手动管理 JAR
- **依赖管理**：使用 BOM（Bill of Materials）统一版本，如 Spring Boot Starter Parent
- **版本锁定**：Maven 使用 `mvn versions:lockdown`，Gradle 使用 `gradle.lockfile`
- **依赖安全**：定期运行 `mvn dependency-check:check` / `gradle dependencyCheckAnalyze`
- **模块化**：大型项目使用 `multi-module` 结构，按职责拆分子模块

#### 代码质量工具链

```xml
<!-- Spotless 格式化插件（Maven） -->
<plugin>
    <groupId>com.diffplug.spotless</groupId>
    <artifactId>spotless-maven-plugin</artifactId>
    <configuration>
        <java>
            <googleJavaFormat>
                <version>1.19.2</version>
            </googleJavaFormat>
            <removeUnusedImports/>
            <trimTrailingWhitespace/>
            <endWithNewline/>
        </java>
    </configuration>
</plugin>
```

| 工具 | 用途 | 优先级 |
|---|---|---|
| `google-java-format` | 代码格式化（通过 Spotless 集成） | **必须** |
| `Checkstyle` | 代码风格检查（Google 风格规则集） | **必须** |
| `SpotBugs` + `Find Security Bugs` | 静态分析 + 安全漏洞检测 | **必须** |
| `PMD` | 代码质量检查（潜在 Bug、死代码） | **必须** |
| `JaCoCo` | 测试覆盖率报告 | **必须** |
| `ErrorProne` | 编译时 Bug 检测 | **必须** |
| `SonarQube` | 综合代码质量平台 | 强烈推荐 |
| `Dependabot` / `Renovate` | 依赖自动更新 | 强烈推荐 |
| `pre-commit` | Git 提交前自动检查（集成上述工具） | 强烈推荐 |

#### 安全规范

- **输入验证**：所有外部输入必须校验（使用 Jakarta Validation / Hibernate Validator）
  ```java
  public record CreateUserRequest(
      @NotBlank @Size(min = 2, max = 50) String name,
      @Email String email,
      @NotNull @Min(0) Integer age
  ) {}
  ```
- **SQL 注入**：使用 JPA / MyBatis 参数化查询，**禁止** 字符串拼接 SQL
  ```java
  // ✅ 正确：参数化查询
  @Query("SELECT u FROM User u WHERE u.email = :email")
  Optional<User> findByEmail(@Param("email") String email);

  // ❌ 禁止：字符串拼接 SQL
  String sql = "SELECT * FROM users WHERE email = '" + email + "'";
  ```
- **密钥管理**：使用环境变量或 Vault / Spring Cloud Config，**禁止** 硬编码密钥
- **依赖安全**：定期运行 OWASP Dependency Check 扫描已知漏洞
- **反序列化**：**禁止** 使用 Java 原生反序列化（`ObjectInputStream`）处理不受信任的数据
- **文件操作**：使用 `Path.of()` + `Files` API，校验路径防止目录穿越
- **SSRF 防护**：对外部 URL 请求进行白名单校验
- **日志安全**：**禁止** 在日志中输出密码、Token 等敏感信息

#### 并发与性能

```java
// ✅ 使用虚拟线程（Java 21+）
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            // 每个任务运行在独立的虚拟线程上
            Thread.sleep(Duration.ofSeconds(1));
            return i;
        });
    });
}

// ✅ 使用 CompletableFuture 组合异步操作
CompletableFuture<User> userFuture = CompletableFuture
    .supplyAsync(() -> userService.findById(userId))
    .thenApply(user -> enrichUser(user))
    .exceptionally(ex -> handleDefault(ex));

// ✅ 使用线程安全集合
ConcurrentHashMap<String, User> cache = new ConcurrentHashMap<>();
copyOnWriteArrayList.add(item);  // 读多写少场景

// ❌ 禁止：手动创建 Thread 而不管理生命周期
new Thread(() -> doWork()).start();  // 应使用 ExecutorService
```

- I/O 密集型任务：优先使用虚拟线程（Java 21+）或 `CompletableFuture`
- CPU 密集型任务：使用 `ForkJoinPool` 或固定大小线程池
- 线程安全：优先使用 `java.util.concurrent` 包下的并发集合，**禁止** 手动 `synchronized`
- 不可变对象：优先使用 `Record`、`List.of()` 等不可变结构避免并发问题
- 性能分析：使用 JFR（Java Flight Recorder）、async-profiler 定位瓶颈
- **禁止**：在热路径中使用 `String` 拼接，使用 `StringBuilder` 或 SLF4J 参数化日志
- **禁止**：无限制创建线程池，必须配置合理的队列大小和拒绝策略

#### 文件与目录结构

```
my-project/
    src/
        main/
            java/
                com/example/project/
                    Application.java            # 启动类
                    config/                     # 配置类
                        WebConfig.java
                    controller/                 # HTTP 控制器层
                        UserController.java
                    service/                    # 业务逻辑层
                        UserService.java
                        impl/
                            UserServiceImpl.java
                    repository/                 # 数据访问层
                        UserRepository.java
                    model/                      # 数据模型 / 实体
                        User.java
                        dto/
                            UserDTO.java
                    exception/                  # 自定义异常
                        InsufficientBalanceException.java
                    util/                       # 工具类
                        DateUtils.java
            resources/
                application.yml
                application-dev.yml
                application-prod.yml
        test/
            java/
                com/example/project/
                    service/
                        UserServiceTest.java
                    controller/
                        UserControllerTest.java
            resources/
                test-data/
    pom.xml                    # Maven 配置入口
    build.gradle.kts           # 或 Gradle 配置入口
    README.md
```

- **分层架构**：`controller`（输入处理）→ `service`（业务逻辑）→ `repository`（数据访问），各层通过接口解耦
- **入口类**：`Application.java` 仅负责启动，**禁止** 包含业务逻辑
- **配置分离**：按环境拆分配置文件（`application-{profile}.yml`）
- **DTO 分离**：Entity 与 DTO 严格分离，禁止直接暴露数据库实体给前端
- **每个文件不超过 300 行**，超过时按职责拆分为多个文件
- **异常统一处理**：使用 `@RestControllerAdvice` + `@ExceptionHandler` 全局异常处理

### PHP

必须遵守 **PSR-12**（https://www.php-fig.org/psr/psr-12/）编码风格指南，并遵循以下现代 PHP 最佳实践：

#### 基础规范

- **最低版本**：PHP ≥ 8.1（支持枚举 `enum`、交集类型、纤维 `Fiber`、只读属性等新特性）
- **严格模式**：每个 PHP 文件首行必须声明 `declare(strict_types=1);`
- **缩进**：4 个空格，禁止 Tab
- **行长**：≤ 120 字符
- **空行**：顶层函数 / 类之间空 2 行，类内方法之间空 1 行
- **字符串**：单引号 `'` 为主，需要变量插值时使用双引号 `"` 或 Heredoc 语法
- **行尾**：禁止行尾空格，文件末尾保留一个空行
- **短标签**：禁止使用 `<?`，必须使用 `<?php` 开始 PHP 代码

#### 命名规范

- 类 / Trait / Interface / Enum：`PascalCase`
- 函数 / 方法：`camelCase`
- 变量：`$camelCase`（带 `$` 符号）
- 常量（`const` / `define`）：`UPPER_SNAKE_CASE`
- 私有属性：使用 `$camelCase`，禁止单下划线前缀（PHP 8+ 原生支持私有方法和属性）
- 布尔变量 / 方法：使用 `$is`、`$has`、`$can`、`$should` 前缀
- 接口：描述性名词或 `Interface` 后缀（如 `LoggerInterface`、`RepositoryInterface`）
- 抽象类：`Abstract` 前缀（如 `AbstractController`）
- 特质（Trait）：`Trait` 后缀（如 `CacheableTrait`）
- 测试方法：`test` 前缀描述预期行为（如 `testReturnsUserWhenFound()`）

```php
// ✅ 正确
class UserService
{
    private const MAX_RETRY_COUNT = 3;

    private bool $isActive = false;

    public function getFullName(): string { /* ... */ }
    public function handleSubmit(): void { /* ... */ }
}

// ❌ 错误
class user_service
{
    const maxRetryCount = 3; // 应为 UPPER_SNAKE_CASE
    public function active(): bool { /* ... */ } // 缺少 is 前缀
}
```

#### 导入规范

```php
<?php

declare(strict_types=1);

namespace App\Service;

// 标准库（PHP 内置类，通常无需 use）
use Exception;
use InvalidArgumentException;

// 第三方库
use GuzzleHttp\Client;
use Psr\Log\LoggerInterface;
use Symfony\Component\HttpFoundation\Request;

// 本项目包（按命名空间层级分组）
use App\Model\User;
use App\Repository\UserRepository;
use App\Utils\StringHelper;
```

- 每行一个 `use` 语句，按分组用空行分隔：标准库 → 第三方库 → 本项目包
- **禁止**：使用 `include` / `require` / `include_once` / `require_once` 加载类文件（使用 Composer 自动加载）
- **禁止**：循环依赖；如不可避免，使用接口抽象或依赖注入解耦
- 常量导入：`use const App\Constants\MAX_SIZE;`
- 函数导入：`use function App\Utils\helper;`

#### 类型规范

```php
<?php

declare(strict_types=1);

// ✅ 使用枚举（PHP 8.1+）替代常量数组
enum PaymentMethod: string
{
    case CreditCard = 'credit_card';
    case Alipay = 'alipay';
    case WechatPay = 'wechat_pay';

    // 枚举可以包含方法
    public function getDisplayName(): string
    {
        return match ($this) {
            self::CreditCard => '信用卡',
            self::Alipay => '支付宝',
            self::WechatPay => '微信支付',
        };
    }
}

// ✅ 使用联合类型（PHP 8.0+）
function findUser(int|string $identifier): ?User
{
    // ...
}

// ✅ 使用交集类型（PHP 8.1+）
function process(LoggerInterface&CacheableInterface $service): void
{
    // ...
}

// ✅ 使用只读属性（PHP 8.1+）
final readonly class UserDTO
{
    public function __construct(
        public string $id,
        public string $name,
        public string $email,
    ) {}
}

// ✅ 使用属性提升构造函数参数（PHP 8.0+）
class UserService
{
    public function __construct(
        private readonly UserRepository $userRepository,
        private readonly LoggerInterface $logger,
    ) {}
}

// ❌ 禁止：省略类型注解
function calculateTotal($items, $taxRate = 0.08) { /* ... */ }
```

- 所有函数参数和返回值必须添加类型注解
- 使用 `?Type` 或 `Type|null` 表示可空类型
- **禁止**使用 `mixed` 类型（除非确实无法确定类型）
- 优先使用 `readonly` 属性和构造函数属性提升（Constructor Promotion）
- 使用 `match` 表达式替代复杂 `switch` 语句
- 使用枚举（`enum`）替代常量数组定义有限值集合

#### 文档规范（PHPDoc）

**公共类、公共方法、公共接口必须编写 PHPDoc 注释**。说明注释必须使用中文：

```php
/**
 * 用户服务类，提供用户相关的业务逻辑操作。
 *
 * 本类负责处理用户注册、查询、更新等核心业务流程。
 * 所有方法均为线程安全的（在 Web 请求上下文中）。
 */
class UserService
{
    /**
     * 根据用户 ID 查询用户信息。
     *
     * 当用户不存在时返回 null，不抛出异常。
     *
     * @param int|string $userId 用户的唯一标识符，必须为正数
     * @param float      $timeout 查询超时时间，单位为秒，必须为正数
     *
     * @return User|null 包含用户信息的对象；用户不存在时返回 null
     *
     * @throws InvalidArgumentException 当 userId 为空或 timeout 为负数时抛出
     * @throws ConnectionException      当数据库连接失败时抛出
     */
    public function findUser(int|string $userId, float $timeout = 30.0): ?User
    {
        // 实现细节...
    }
}
```

- `@param`、`@return`、`@throws` 必须完整且使用中文描述
- 复杂逻辑在方法内部使用行内注释解释意图（而非解释"做了什么"）
- TODO 注释格式：`// TODO(负责人): 描述待办事项`，禁止遗留无主 TODO
- 使用 `@see` 引用关联的测试方法或文档

#### 错误处理

```php
<?php

declare(strict_types=1);

// ✅ 使用自定义异常表达业务逻辑
class InsufficientBalanceException extends RuntimeException
{
    public function __construct(
        private readonly string $accountId,
        private readonly float  $currentBalance,
        private readonly float  $requiredAmount,
    ) {
        parent::__construct(sprintf(
            '账户 %s 余额不足: 当前 %.2f, 需要 %.2f',
            $accountId,
            $currentBalance,
            $requiredAmount,
        ));
    }

    // getter 方法...
}

// ✅ 必须显式捕获具体异常类型
try {
    $result = $this->apiCall();
} catch (ConnectionException $e) {
    $this->logger->error('连接失败', ['error' => $e->getMessage()]);
    throw new AppException('服务暂时不可用', 0, $e);
} catch (TimeoutException $e) {
    $this->logger->warning('请求超时', ['error' => $e->getMessage()]);
    throw new AppException('请求超时', 0, $e);
}

// ✅ 使用 finally 清理资源
$connection = null;
try {
    $connection = $this->getConnection();
    $connection->beginTransaction();
    // 业务逻辑...
    $connection->commit();
} catch (Exception $e) {
    if ($connection !== null) {
        $connection->rollBack();
    }
    throw $e;
} finally {
    if ($connection !== null) {
        $connection->close();
    }
}

// ❌ 禁止：空 catch 块
try {
    $this->riskyOperation();
} catch (Exception $e) {
    // 禁止空 catch 块！
}
```

- 捕获尽可能精确的异常类型，**禁止** `catch (\Exception $e) {}` 空块
- 使用 `$this->logger->error()` 记录异常，**禁止** `echo` / `print` 输出生产错误日志
- 异常链：使用 `new AppException('上下文', 0, $cause)` 保留原始异常
- 在 API 边界层将内部异常转换为用户友好的错误信息，**禁止**将内部异常详情暴露给调用方

#### 测试规范

```bash
# 目录结构
src/
    Service/
        UserService.php
tests/
    Unit/
        Service/
            UserServiceTest.php    # 与被测文件对应
    Fixtures/                      # 测试数据
    Helpers/                       # 测试工具函数
```

- **框架**：PHPUnit（推荐 10+）
- **文件命名**：`<ClassName>Test.php`，与被测类对应
- **方法命名**：`test<预期行为>When<条件>()` 或使用 `@dataProvider` 注解
- **断言**：使用 `$this->assert*()` 系列方法
- **覆盖率**：核心模块要求覆盖率 ≥ 80%（PHPUnit 内置覆盖率工具）
- **Mock**：使用 PHPUnit Mock 或 Mockery，mock 外部依赖（网络、数据库、文件系统）
- **测试隔离**：每个测试用例独立，使用 `setUp()` / `tearDown()` 清理状态

```php
<?php

declare(strict_types=1);

namespace Tests\Unit\Service;

use App\Model\User;
use App\Repository\UserRepository;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use PHPUnit\Framework\MockObject\MockObject;

class UserServiceTest extends TestCase
{
    private UserService $userService;
    private MockObject&UserRepository $userRepository;

    protected function setUp(): void
    {
        $this->userRepository = $this->createMock(UserRepository::class);
        $this->userService = new UserService($this->userRepository);
    }

    #[Test]
    public function testShouldReturnUserWhenFound(): void
    {
        // Given
        $userId = 'u-001';
        $expectedUser = new User($userId, 'Alice');
        $this->userRepository->method('findById')
            ->with($userId)
            ->willReturn($expectedUser);

        // When
        $result = $this->userService->findUser($userId, 30.0);

        // Then
        $this->assertNotNull($result);
        $this->assertSame('Alice', $result->name);
    }

    #[Test]
    public function testShouldReturnEmptyWhenUserNotFound(): void
    {
        $this->userRepository->method('findById')
            ->with('nonexistent')
            ->willReturn(null);

        $result = $this->userService->findUser('nonexistent', 30.0);

        $this->assertNull($result);
    }

    #[DataProvider('invalidUserIdProvider')]
    #[Test]
    public function testShouldThrowWhenUserIdIsInvalid(string|int $userId): void
    {
        $this->expectException(InvalidArgumentException::class);
        $this->userService->findUser($userId, 30.0);
    }

    public static function invalidUserIdProvider(): array
    {
        return [
            'empty string' => [''],
            'negative number' => [-1],
        ];
    }
}
```

#### 依赖与项目管理

```json
// composer.json — 唯一的依赖声明入口
{
    "name": "my-org/my-project",
    "description": "项目描述",
    "type": "project",
    "license": "MIT",
    "require": {
        "php": ">=8.1",
        "guzzlehttp/guzzle": "^7.8",
        "symfony/console": "^6.4"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.4",
        "phpstan/phpstan": "^1.12",
        "friendsofphp/php-cs-fixer": "^3.64"
    },
    "autoload": {
        "psr-4": {
            "App": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests": "tests/"
        }
    }
}
```

- **包管理工具**：必须使用 **Composer**，**禁止**手动下载依赖
- **锁文件**：必须提交 `composer.lock`，**禁止**删除锁文件
- **自动加载**：使用 PSR-4 自动加载标准，**禁止**使用 `spl_autoload_register` 手动注册
- **依赖更新**：定期运行 `composer update` 更新依赖
- **安全审计**：使用 `composer audit` 扫描已知漏洞
- **`require-dev`**：开发工具（PHPUnit、PHP-CS-Fixer、PHPStan）统一放在 `require-dev`
- **禁止**：在生产代码中引入 `require-dev` 中的包

#### 代码质量工具链

| 工具 | 用途 | 优先级 |
|---|---|---|
| `PHP-CS-Fixer` | 代码格式化（遵循 PSR-12） | **必须** |
| `PHPStan` / `Psalm` | 静态类型分析（Level 8+） | **必须** |
| `PHPUnit` | 单元 / 集成测试 | **必须** |
| `Rector` | 自动化代码重构和升级 | 推荐 |
| `PHP CodeSniffer` | 代码风格检查（备选） | 推荐 |
| `Deptrac` | 依赖层架构检查 | 推荐 |
| `Infection` | 变异测试（验证测试有效性） | 推荐 |

#### 安全规范

- **输入验证**：所有外部输入必须使用 `filter_var()` / `filter_input()` 或 Symfony Validator 进行校验
- **SQL 注入**：使用 PDO 参数化查询或 ORM（Doctrine / Eloquent），**禁止**字符串拼接 SQL
  ```php
  // ✅ 正确：使用预处理语句
  $stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
  $stmt->execute(['id' => $userId]);

  // ❌ 禁止：字符串拼接 SQL
  $sql = "SELECT * FROM users WHERE id = $userId";
  ```
- **XSS 防护**：输出到 HTML 时必须使用 `htmlspecialchars()` 或模板引擎自动转义
- **CSRF 防护**：表单提交必须包含 CSRF Token
- **密钥管理**：使用环境变量（`getenv()` / `$_ENV`）或 `.env` 文件（配合 `vlucas/phpdotenv`），**禁止**硬编码密钥到源码
- **依赖安全**：定期运行 `composer audit` 扫描已知漏洞
- **反序列化**：**禁止**使用 `unserialize()` 处理不受信任的数据（远程代码执行风险）
- **文件操作**：使用 `realpath()` 校验路径，防止目录穿越攻击
- **临时文件**：使用 `tempnam()` 创建临时文件，脚本退出时清理
- **密码哈希**：必须使用 `password_hash()` 和 `password_verify()`，**禁止** MD5 / SHA1

#### 并发与性能

- **异步任务**：使用队列（Redis / RabbitMQ）处理耗时操作，避免阻塞 Web 请求
- **协程**：PHP 8.1+ 可使用 `Fiber` 实现轻量级协程
- **缓存**：使用 Redis / Memcached 缓存热点数据，减少数据库查询
- **连接池**：数据库和 Redis 使用连接池，避免频繁创建/销毁连接
- **性能分析**：使用 Xdebug / Blackfire 定位性能瓶颈
- **内存管理**：大文件处理使用流式读取，避免一次性加载到内存
- **禁止**：在热路径中使用 `sprintf` 拼接大量字符串（使用 `implode` 或模板）

#### 文件与目录结构

```
my-project/
    src/                        # 应用源码（PSR-4 标准）
        Controller/             # HTTP 控制器层
            UserController.php
        Service/                # 业务逻辑层
            UserService.php
        Repository/             # 数据访问层
            UserRepository.php
        Model/                  # 数据模型 / Entity
            User.php
        DTO/                    # 数据传输对象
            UserDTO.php
        Exception/              # 自定义异常
            InsufficientBalanceException.php
        Utils/                  # 工具类
            StringHelper.php
    config/                     # 配置文件
        services.php
    migrations/                 # 数据库迁移文件
    tests/                      # 测试文件
        Unit/
            Service/
                UserServiceTest.php
        Fixtures/               # 测试数据
        Helpers/                # 测试工具
    composer.json               # 依赖声明入口
    composer.lock               # 依赖锁文件
    phpunit.xml.dist            # PHPUnit 配置
    .php-cs-fixer.php           # PHP-CS-Fixer 配置
    phpstan.neon                # PHPStan 配置
    README.md
```

- **分层架构**：`Controller`（输入处理）→ `Service`（业务逻辑）→ `Repository`（数据访问），各层通过接口解耦
- **入口文件**：`public/index.php` 仅负责引导和启动，**禁止**包含业务逻辑
- **配置分离**：按环境拆分配置文件（`.env` / `.env.local` / `.env.prod`）
- **DTO 分离**：Entity 与 DTO 严格分离，禁止直接暴露数据库实体给前端
- **每个文件不超过 300 行**，超过时按职责拆分为多个文件
- **异常统一处理**：使用全局异常处理器或框架中间件统一处理异常

### C# / .NET

必须遵守 **.NET Runtime Coding Style**（https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/coding-style.md）与 **C# Language Design**，并遵循以下现代 .NET 最佳实践：

#### 基础规范

- **最低版本**：.NET ≥ 8.0（LTS），C# ≥ 12（支持 primary constructor、collection expression 等新特性）
- **缩进**：4 个空格，禁止 Tab
- **行长**：≤ 100 字符
- **空行**：顶层类之间空 1 行，类内方法之间空 1 行，逻辑块之间空 1 行
- **字符串**：统一使用双引号 `"`，逐字字符串使用 `@""`，原始字符串使用 `"""..."""`
- **行尾**：禁止行尾空格，文件末尾保留一个空行
- **文件作用域命名空间**（C# 10+）：`namespace MyApp.Services;`，**禁止** 大括号包裹
- **nullable 引用类型**（C# 8+）：**必须** 全局启用 `<Nullable>enable</Nullable>`

#### 命名规范

- **命名空间**：`PascalCase`，使用反向域名（如 `MyApp.Services`）
- **类 / 接口 / 结构体 / 枚举 / 记录**：`PascalCase`
- **接口**：`I` 前缀 + `PascalCase`（如 `IUserRepository`）
- **方法 / 属性 / 事件 / 委托**：`PascalCase`
- **私有字段**：`_camelCase`（如 `_userRepository`），禁止使用 `m_` 前缀
- **局部变量 / 参数**：`camelCase`
- **常量（static readonly）**：`PascalCase`（如 `MaxRetryCount`）
- **枚举值**：`PascalCase`（如 `Status.Active`）
- **泛型类型参数**：单个大写字母 `T`、`TKey`、`TValue`
- **异步方法**：以 `Async` 后缀结尾（如 `GetUserAsync`）
- **布尔成员**：`Is`、`Has`、`Can`、`Should`、`Was` 前缀
- **事件处理方法**：`On` 前缀（如 `OnClick`），事件回调使用 `Handle` 前缀
- **私有方法**：`camelCase`（如 `calculateTotal`），**禁止** `_PascalCase`
- **缩写词**：保持大小写规则（2 字母以下全小写：`id`、`io`；3 字母以上首字母大写：`Http`、`Xml`）

```csharp
// ✅ 正确
public class UserService
{
    private const int MaxRetryCount = 3;
    private readonly IUserRepository _userRepository;
    public bool IsActive { get; }
    public async Task<User> GetUserAsync(int userId, CancellationToken ct = default) { /* ... */ }
}

// ❌ 错误
public class user_service
{
    const int maxRetryCount = 3;  // 应为 PascalCase
    private UserRepository UserRepository;  // 应为 _userRepository
}
```

#### 导入规范

```csharp
// 优先使用 Global Using（C# 10+）管理常用命名空间
// 文件内 using 排序：System → 第三方 → 本项目
// 各组之间用空行分隔

using System;
using System.Collections.Generic;
using System.Linq;

using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

using MyApp.Models;
using MyApp.Services;
```

- 使用 `global using`（C# 10+）集中管理常用命名空间，减少重复声明
- **禁止** `using static` 导入非测试类（测试中可使用 `using static Assert`）
- 每个 `using` 语句独占一行，禁止使用大括号分组
- 按 `System` → 第三方 → 本项目排序

#### 类型规范

```csharp
// ✅ 使用 record 定义不可变数据类（C# 9+）
public record UserDto(string Id, string Name, string Email);

// ✅ 使用 record struct 定义值类型（C# 10+）
public readonly record struct Coordinates(double Latitude, double Longitude);

// ✅ 使用 primary constructor（C# 12+）
public class OrderService(IOrderRepository repository, ILogger<OrderService> logger)
{
    // 通过参数名直接使用，无需声明私有字段
}

// ✅ 使用 sealed class 限制继承
public sealed class PaymentProcessor : IPaymentProcessor { }

// ✅ 使用 init-only 属性（C# 9+）
public class Product
{
    public int Id { get; init; }
    public required string Name { get; init; }  // C# 11 required
}

// ✅ 使用 file-scoped namespace（C# 10+）
namespace MyApp.Services;

// ✅ 使用模式匹配（C# 9+）
return shape switch
{
    Circle { Radius: > 0 } c => c.Area,
    Rectangle { Width: var w, Height: var h } => w * h,
    _ => 0
};

// ✅ 使用集合表达式（C# 12+）
int[] numbers = [1, 2, 3, 4, 5];
List<string> names = ["Alice", "Bob"];

// ❌ 禁止：var 遮蔽类型名
var list = new List<int>();  // OK
var result = GetResult();    // 结果类型不明确时，应显式声明类型
```

- **禁止** `enum`，优先使用 `record` 定义有限值集合或 `static class` 定义常量组
- 使用 `record` 替代手写 `Equals`/`GetHashCode`/`ToString`
- 使用 `required`（C# 11+）标记必填属性
- 使用 `Span<T>` / `ReadOnlySpan<T>` 处理切片和字符串操作，减少内存分配
- **禁止** 使用 `var` 当类型不明确时

#### 异步与并发规范

```csharp
// ✅ 异步方法使用 Async 后缀，返回 Task<T> 或 ValueTask<T>
public async Task<User> GetUserAsync(int userId, CancellationToken ct = default)
{
    var user = await _repository.GetByIdAsync(userId, ct);
    return user ?? throw new NotFoundException(nameof(User), userId);
}

// ✅ ConfigureAwait(false) 用于库代码（非 UI 应用）
await _repository.SaveAsync(entity, ct).ConfigureAwait(false);

// ✅ 使用 SemaphoreSlim 限制并发
private readonly SemaphoreSlim _semaphore = new(10);

// ✅ 使用 IAsyncEnumerable 处理流式异步数据
public async IAsyncEnumerable<Order> GetOrdersAsync(
    [EnumeratorCancellation] CancellationToken ct = default)
{
    await foreach (var order in _dataSource.GetOrdersAsync(ct))
    {
        yield return order;
    }
}

// ✅ 使用 ValueTask 避免热路径上的分配
public ValueTask<int> GetHashCodeAsync(string key)
{
    if (_cache.TryGetValue(key, out var cached))
        return new ValueTask<int>(cached);  // 同步完成，无 Task 分配

    return new ValueTask<int>(ComputeHashAsync(key));
}

// ❌ 禁止：async void（除事件处理器外）
// ❌ 禁止：.Result/.Wait() 阻塞异步操作
// ❌ 禁止：Thread.Sleep()，使用 await Task.Delay() 替代
```

- 异步方法始终接受 `CancellationToken` 参数并向下传递
- 库代码使用 `ConfigureAwait(false)`，ASP.NET Core 无需使用
- `ValueTask<T>` 用于可能同步完成的热路径
- **禁止** `async void`（除事件处理器外）
- **禁止** `.Result`、`.Wait()`、`.GetAwaiter().GetResult()` 阻塞异步调用

#### 错误处理

```csharp
// ✅ 使用异常过滤器记录日志（保留原始堆栈）
try
{
    await ProcessPaymentAsync(order, ct);
}
catch (PaymentException ex) when (ex.ErrorType == PaymentError.InsufficientFunds)
{
    _logger.LogWarning(ex, "余额不足: OrderId={OrderId}", order.Id);
    throw new OrderProcessingException("支付失败: 余额不足", order.Id, ex);
}

// ✅ 使用自定义异常类携带上下文
public class OrderProcessingException : Exception
{
    public string OrderId { get; }

    public OrderProcessingException(string message, string orderId, Exception? innerException = null)
        : base(message, innerException)
    {
        OrderId = orderId;
    }
}

// ✅ 使用 Result 模式替代异常（业务流程控制）
public record Result<T>(bool IsSuccess, T? Value, string? Error)
{
    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string error) => new(false, default, error);
}

// ❌ 禁止：捕获 Exception 后静默忽略
// ❌ 禁止：throw ex 丢失堆栈信息（应使用 throw）
```

- 捕获尽可能精确的异常类型，**禁止** `catch (Exception)` 后静默忽略
- 使用异常过滤器（`when`）替代 catch 中的条件判断
- 使用 `throw` 重新抛出，**禁止** `throw ex`（会丢失堆栈）
- 日志记录使用 `_logger.LogError(ex, "操作描述")`，**禁止** `Console.WriteLine()`
- 异常链：使用 `innerException` 参数保留原始异常

#### 文档规范（XML Documentation）

**公共类、公共方法、公共接口必须编写 XML 文档注释**。说明注释必须使用中文：

```csharp
/// <summary>
/// 用户服务类，提供用户相关的业务逻辑操作。
/// </summary>
/// <remarks>
/// 本类负责处理用户注册、查询、更新等核心业务流程。
/// 所有方法均为线程安全的。
/// </remarks>
public class UserService(IUserRepository userRepository, ILogger<UserService> logger)
{
    /// <summary>
    /// 根据用户 ID 查询用户信息。
    /// </summary>
    /// <param name="userId">用户的唯一标识符，必须为正数。</param>
    /// <param name="ct">取消令牌。</param>
    /// <returns>包含用户信息的对象；用户不存在时返回 <c>null</c>。</returns>
    /// <exception cref="ArgumentException">当 <paramref name="userId"/> 为负数时抛出。</exception>
    /// <exception cref="ConnectionException">当数据库连接失败时抛出。</exception>
    public async Task<User?> GetUserAsync(int userId, CancellationToken ct = default)
    {
        // 实现细节...
    }
}
```

- `<summary>`、`<param>`、`<returns>`、`<exception>` 必须完整且使用中文描述
- 使用 `<see cref=""/>` 引用其他类或方法
- 使用 `<c>` 标记代码片段
- TODO 注释格式：`// TODO(负责人): 描述待办事项`，禁止遗留无主 TODO

#### 测试规范

```csharp
// 框架：xUnit（推荐）或 NUnit
// Mock：Moq 或 NSubstitute
// 断言：xUnit Assert.* 或 FluentAssertions
// 命名：Method_Scenario_ExpectedResult 或 Should_Xxx_When_Xxx
// 覆盖率：核心模块 ≥ 80%（dotnet test --collect:"XPlat Code Coverage"）

public class UserServiceTests
{
    private readonly Mock<IUserRepository> _mockRepo = new();
    private readonly UserService _sut;

    public UserServiceTests()
    {
        _sut = new UserService(_mockRepo.Object, Mock.Of<ILogger<UserService>>());
    }

    [Fact]
    public async Task GetUserAsync_ShouldReturnUser_WhenFound()
    {
        // Arrange
        var expectedUser = new UserDto("1", "Alice", "alice@example.com");
        _mockRepo.Setup(x => x.GetByIdAsync(1, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedUser);

        // Act
        var result = await _sut.GetUserAsync(1);

        // Assert
        Assert.Equal(expectedUser, result);
        _mockRepo.Verify(x => x.GetByIdAsync(1, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    public async Task GetUserAsync_ShouldThrow_WhenUserIdInvalid(int userId)
    {
        await Assert.ThrowsAsync<ArgumentException>(
            () => _sut.GetUserAsync(userId));
    }
}
```

#### 依赖与项目管理

```xml
<!-- .csproj — 项目配置入口 -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

```xml
<!-- Directory.Build.props — 全局配置（所有项目共享） -->
<Project>
  <PropertyGroup>
    <LangVersion>12</LangVersion>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>
</Project>
```

- **构建工具**：`dotnet build` / `dotnet run`，**禁止** 手动管理 DLL
- **包管理**：NuGet + Central Package Management（`Directory.Packages.props`）
- **依赖安全**：定期运行 `dotnet list package --vulnerable` 扫描已知漏洞
- **依赖锁定**：使用 `packages.lock.json` 锁定依赖版本

#### 代码质量工具链

| 工具 | 用途 | 优先级 |
|---|---|---|
| `dotnet format` | 代码格式化（EditorConfig 驱动） | **必须** |
| Roslyn Analyzers | 静态分析（内置 + StyleCop.Analyzers） | **必须** |
| xUnit / NUnit | 单元 / 集成测试 | **必须** |
| `dotnet test --collect:"XPlat Code Coverage"` | 覆盖率 | **必须** |
| FluentAssertions | 流式断言 | 推荐 |
| Stryker.NET | 变异测试 | 推荐 |

```ini
# .editorconfig — 代码风格（项目根目录）
root = true

[*.cs]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# 命名规则
dotnet_naming_rule.private_fields_should_be_camel_with_underscore.severity = error
dotnet_naming_rule.private_fields_should_be_camel_with_underscore.symbols = private_fields
dotnet_naming_rule.private_fields_should_be_camel_with_underscore.style = camel_case_underscore

dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private

dotnet_naming_style.camel_case_underscore.capitalization = camel_case
dotnet_naming_style.camel_case_underscore.required_prefix = _

# 代码风格
csharp_style_namespace_declarations = file_scoped:warning
csharp_style_var_for_built_in_types = false:suggestion
csharp_style_var_when_type_is_apparent = true:suggestion
csharp_using_directive_placement = outside_namespace:warning
```

#### 安全规范

- **输入验证**：使用 FluentValidation 或 Data Annotations，**禁止** 跳过校验
- **SQL 注入**：使用 Entity Framework Core / Dapper 参数化查询，**禁止** 字符串拼接 SQL
- **密钥管理**：使用 `IConfiguration` + User Secrets / Azure Key Vault / 环境变量，**禁止** 硬编码
- **反序列化**：**禁止** `BinaryFormatter`（已弃用），使用 `System.Text.Json`
- **依赖安全**：定期运行 `dotnet list package --vulnerable` 扫描已知漏洞
- **CORS**：生产环境必须配置允许的源站白名单，**禁止** `AllowAnyOrigin`
- **日志安全**：**禁止** 在日志中输出密码、Token 等敏感信息

#### 文件与目录结构

```
MyApp/
├── src/
│   ├── MyApp.Api/                    # ASP.NET Core Web API / 控制台
│   │   ├── Controllers/
│   │   ├── Middleware/
│   │   ├── Program.cs                # 入口（Minimal API 或传统 Startup）
│   │   └── MyApp.Api.csproj
│   ├── MyApp.Application/            # 业务逻辑层（CQRS / MediatR 可选）
│   │   ├── Commands/
│   │   ├── Queries/
│   │   ├── Validators/
│   │   └── Interfaces/
│   ├── MyApp.Domain/                 # 领域模型（DDD 可选）
│   │   ├── Entities/
│   │   ├── ValueObjects/
│   │   ├── Events/
│   │   └── Enums/
│   ├── MyApp.Infrastructure/         # 基础设施层
│   │   ├── Persistence/
│   │   ├── ExternalServices/
│   │   └── Repositories/
│   └── MyApp.SharedKernel/           # 共享内核（可选）
│       ├── Exceptions/
│       └── Extensions/
├── tests/
│   ├── MyApp.UnitTests/
│   ├── MyApp.IntegrationTests/
│   └── MyApp.ArchTests/              # 架构测试（可选）
├── Directory.Build.props
├── Directory.Packages.props          # 集中包版本管理
├── .editorconfig
├── global.json                       # SDK 版本锁定
└── MyApp.sln
```

- **分层架构**：`Api`（输入处理）→ `Application`（业务逻辑）→ `Domain`（领域模型）→ `Infrastructure`（数据访问），各层通过接口解耦
- **入口文件**：`Program.cs` 仅负责组装和启动，**禁止** 包含业务逻辑
- **每个文件不超过 300 行**，超过时按职责拆分为多个文件
- **异常统一处理**：使用 `ProblemDetails`（RFC 7807）+ 全局异常中间件统一处理

### Shell / Bash

必须通过 **ShellCheck**，并遵守以下规则：

- **Shebang**：脚本首行必须为 `#!/usr/bin/env bash`
- **严格模式**：脚本开头必须添加 `set -euo pipefail`
- **变量引用**：始终使用 `"${var}"`，禁止裸引用
- **Lint**：使用 `shellcheck`，warning 及以上必须修复
- **函数**：使用 `function_name() { ... }` 格式定义函数
- **注释**：复杂逻辑必须添加注释说明意图
- **临时文件**：使用 `mktemp` 创建临时文件，脚本退出时清理
- **错误处理**：捕获错误并输出有意义的错误信息到 stderr

### Swift

必须遵守 [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/) 与 [The Swift Programming Language](https://docs.swift.org/swift-book/)，并遵循以下现代 Swift 最佳实践：

#### 基础规范

- **最低版本**：Swift ≥ 5.9（支持 macros、parameter packs、conformances 等新特性）
- **格式化**：必须使用 `swift-format` 格式化所有代码，配置文件为 `.swift-format`
- **缩进**：4 个空格，禁止 Tab
- **行长**：≤ 120 字符
- **空行**：顶层函数 / 类之间空 1 行，类内方法之间空 1 行，逻辑块之间空 1 行
- **大括号**：K&R 风格（左大括号不换行），`else`、`catch` 与右大括号同行
- **行尾**：禁止行尾空格，文件末尾保留一个空行
- **Semicolon**：**禁止**手动添加分号
- **括号**：单表达式 `if`/`guard`/`while` **禁止**使用大括号（与 Python 类似）

#### 命名规范

- 类 / 结构体 / 枚举 / 协议 / 扩展 / 类型别名：`PascalCase`
- 函数 / 方法 / 变量 / 参数：`camelCase`
- 常量（`static let` / 全局 `let`）：`camelCase`（Swift 惯例，非 `UPPER_SNAKE_CASE`）
- 枚举值：`camelCase`（Swift 惯例）
- 私有属性：使用 `_` 前缀或直接省略（Swift 原生 `private` 已足够）
- 布尔变量 / 属性：使用 `is`、`has`、`can`、`should` 前缀，如 `isValid`、`hasPermission`
- 代理协议方法：使用 `did` / `will` 前缀，如 `didSelectItem`、`willAppear`
- 缩写词保持大小写规则：`URLSession`、`HTTPClient`、`IDGenerator`、`JSONEncoder`

```swift
// ✅ 正确
class UserService {
    private static let maxRetryCount = 3
    private let userRepository: UserRepository
    var isActive: Bool { true }
    func getFullName() -> String { "" }
}

// ❌ 错误
class user_service {
    static let MaxRetryCount = 3  // 应为 camelCase
    public func active() -> Bool { true }  // 缺少 is 前缀
}
```

#### 导入规范

```swift
// 顺序：Foundation / Apple 框架 → 第三方库 → 本项目模块
// 各组之间用空行分隔

import Foundation
import UIKit

import Alamofire
import SnapKit

import MyProjectCore
import MyProjectModels
```

- 每个 `import` 语句独占一行
- **禁止**：`@testable import` 用于非测试文件
- 避免过度使用 `import`（仅导入实际使用的模块）
- 使用 `@_exported import` 谨慎（仅在模块聚合场景）

#### 类型规范

```swift
// ✅ 使用 struct 定义值类型（优先于 class）
struct User: Codable, Sendable {
    let id: String
    let name: String
    let email: String
}

// ✅ 使用 enum 实现状态机和有限值集合
enum PaymentMethod: String, CaseIterable {
    case creditCard = "credit_card"
    case alipay = "alipay"
    case wechatPay = "wechat_pay"

    var displayName: String {
        switch self {
        case .creditCard: return "信用卡"
        case .alipay: return "支付宝"
        case .wechatPay: return "微信支付"
        }
    }
}

// ✅ 使用 protocol 定义行为契约
protocol UserRepository {
    func findUser(byId id: String) async throws -> User?
    func save(_ user: User) async throws
}

// ✅ 使用 optional 表达可选值
func findUser(byId id: String) -> User? {
    // ...
}

// ❌ 禁止：使用 class 仅作数据容器（应使用 struct）
class User {
    var name: String
    var email: String
}
```

- **优先**：使用 `struct`（值类型），仅在需要引用语义 / 继承时使用 `class`
- **必须**：使用 `enum` 替代字符串常量表示有限值集合
- **优先**：使用 `protocol` 定义行为契约，实现面向协议编程
- **禁止**：使用 `Any` / `AnyObject` 类型（除非确实无法确定类型）
- **推荐**：使用 `some` / `some Protocol` 返回不透明类型（Swift 5.7+）
- **推荐**：使用 `@Sendable` 标注并发安全的闭包（Swift 5.5+）
- **推荐**：使用 `nonisolated` 明确隔离边界

#### 函数与闭包规范

```swift
// ✅ 使用参数标签提高可读性
func fetchUser(byId id: String, from source: APIProvider) async throws -> User {
    // ...
}

// ✅ 使用尾随闭包语法
users.filter { $0.isActive }.map { $0.name }

// ✅ 使用 @discardableResult 标注可忽略返回值
@discardableResult
func saveUser(_ user: User) async throws -> Bool {
    // ...
}

// ✅ 使用 inout 参数（谨慎使用）
func increment(_ value: inout Int) {
    value += 1
}

// ❌ 禁止：过长的参数列表（超过 4 个参数时使用 struct 封装）
func createUser(name: String, email: String, age: Int, phone: String, address: String, city: String) {
    // 应使用 CreateUserRequest struct
}
```

- 参数标签：第一个参数可省略标签，后续参数**必须**有标签
- **推荐**：使用 `_` 省略第一个参数标签（当调用语法更自然时）
- 闭包参数：使用 `$0`、`$1` 简写，复杂逻辑使用具名参数
- **禁止**：函数超过 40 行（应拆分为更小的函数）

#### 文档规范（DocC / 注释）

**公开类型、公开方法、公开协议必须编写文档注释**。说明注释必须使用中文：

```swift
/// 从远程 API 获取用户信息。
///
/// 本方法通过 `userId` 从远程服务获取用户资料数据。
/// 当用户不存在时返回 `nil`，不抛出异常。
///
/// - Parameter userId: 用户的唯一标识符，必须为非空字符串。
/// - Parameter timeout: 请求超时时间，单位为秒，默认值为 30.0。
/// - Returns: 包含用户资料的对象；用户不存在时返回 `nil`。
/// - Throws: `APIError.connectionFailed` 当 API 不可达时抛出。
///
/// ```swift
/// let user = try await fetchUser(byId: "u-123")
/// ```
func fetchUser(
    byId userId: String,
    timeout: TimeInterval = 30.0
) async throws -> User? {
    // 实现细节...
}
```

- 使用 `///` 文档注释，**禁止**使用 `/* */` 块注释进行文档
- 使用 `- Parameter`、`- Returns`、`- Throws` 标记参数和返回值
- 使用 `/// - Note:`、`/// - Important:`、`/// - Warning:` 标记重要说明
- 使用 `/// ```swift` 内嵌代码示例
- 复杂逻辑在函数内部使用行内注释解释意图
- TODO 注释格式：`// TODO(负责人): 描述待办事项`，禁止遗留无主 TODO

#### 错误处理

```swift
// ✅ 使用自定义错误类型表达业务逻辑
enum APIError: Error, LocalizedError {
    case connectionFailed(underlying: Error)
    case notFound(resource: String, id: String)
    case unauthorized(message: String)

    var errorDescription: String? {
        switch self {
        case .connectionFailed(let underlying):
            return "连接失败: \(underlying.localizedDescription)"
        case .notFound(let resource, let id):
            return "\(resource) with id '\(id)' not found"
        case .unauthorized(let message):
            return "未授权: \(message)"
        }
    }
}

// ✅ 使用 do-catch 处理错误
do {
    let user = try await fetchUser(byId: "u-123")
} catch APIError.notFound {
    print("用户不存在")
} catch {
    logger.error("获取用户失败: \(error)")
    throw APIError.connectionFailed(underlying: error)
}

// ✅ 使用 throws + try 处理可失败操作
func processPayment(amount: Decimal) async throws {
    guard amount > 0 else {
        throw PaymentError.invalidAmount
    }
    // ...
}

// ❌ 禁止：空 catch 块
do {
    try riskyOperation()
} catch {
    // 禁止空 catch 块！
}
```

- 使用 `do-catch` 捕获错误，**禁止**静默忽略
- 使用 `try` / `try?` / `try!` 明确错误处理策略
- `try?`：适用于可选值有意义的场景，**禁止**用于关键操作
- `try!`：仅在确信不会失败时使用（如加载应用包内资源）
- 使用 `throws` 传播错误，**禁止**使用 `fatalError` 处理可恢复错误
- 日志记录使用 `os_log` 或第三方日志库，**禁止** `print()` 输出生产日志

#### 测试规范

```swift
// 目录结构
Tests/
    MyProjectTests/
        UserServiceTests.swift
        Models/
            UserTests.swift
        Helpers/
            MockData.swift

// 框架：XCTest + Swift Testing（推荐 Swift 6+）
// Mock：使用 protocol mock 或第三方库（如 Cuckoo、Mockingbird）

import XCTest
@testable import MyProject

final class UserServiceTests: XCTestCase {
    private var sut: UserService!
    private var mockRepository: MockUserRepository!

    override func setUp() {
        super.setUp()
        mockRepository = MockUserRepository()
        sut = UserService(repository: mockRepository)
    }

    override func tearDown() {
        sut = nil
        mockRepository = nil
        super.tearDown()
    }

    func testFetchUserShouldReturnUserWhenFound() async throws {
        // Arrange
        let expectedUser = User(id: "u-001", name: "Alice", email: "alice@example.com")
        mockRepository.stubbedResult = expectedUser

        // Act
        let user = try await sut.fetchUser(byId: "u-001")

        // Assert
        XCTAssertEqual(user?.name, "Alice")
    }

    func testFetchUserShouldReturnNilWhenNotFound() async throws {
        // Arrange
        mockRepository.stubbedResult = nil

        // Act
        let user = try await sut.fetchUser(byId: "nonexistent")

        // Assert
        XCTAssertNil(user)
    }
}
```

- **框架**：`XCTest`（经典）或 Swift Testing（Swift 6+，推荐使用 `@Test` 宏）
- **文件命名**：`<ClassName>Tests.swift`，与被测文件同目录或在 `Tests/` 下
- **函数命名**：`test<方法名><场景><预期结果>`，如 `testFetchUserShouldReturnUserWhenFound`
- **断言**：使用 `XCTAssert*` 系列方法
- **覆盖率**：核心模块要求覆盖率 ≥ 80%
- **Mock**：使用 protocol mock 或第三方库，mock 外部依赖
- **测试隔离**：每个测试用例独立，使用 `setUp()` / `tearDown()` 清理状态
- **异步测试**：使用 `async` 测试方法测试异步代码

#### 依赖与项目管理

```swift
// Package.swift — SPM 依赖声明（推荐）
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyProject",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.9.0"),
        .package(url: "https://github.com/SnapKit/SnapKit.git", from: "5.7.0"),
    ],
    targets: [
        .target(
            name: "MyProject",
            dependencies: ["Alamofire", "SnapKit"]
        ),
        .testTarget(
            name: "MyProjectTests",
            dependencies: ["MyProject"]
        ),
    ]
)
```

- **包管理工具**：优先使用 Swift Package Manager（SPM），其次 CocoaPods / Carthage
- **SPM 优先**：Apple 官方推荐，与 Xcode 深度集成
- **锁文件**：SPM 自动生成 `Package.resolved`，**禁止**删除
- **依赖更新**：使用 Xcode 菜单或 `swift package update` 更新依赖
- **安全审计**：使用 `swift package audit` 扫描已知漏洞（SPM 插件）
- **平台版本**：在 `Package.swift` 中明确声明最低平台版本

#### 代码质量工具链

| 工具 | 用途 | 优先级 |
|---|---|---|
| `swift-format` | 代码格式化 | **必须** |
| `SwiftLint` | Lint 检查（代码风格 + 最佳实践） | **必须** |
| `XCTest` / Swift Testing | 单元 / 集成测试 | **必须** |
| `xcrun xctrace` | 性能测试 | **必须** |
| `Xcode Build Settings` | 编译时静态分析 | **必须** |
| `Periphery` | 未使用代码检测 | 推荐 |
| `DocC` | 文档生成 | 推荐 |

```yaml
# .swiftlint.yml — SwiftLint 配置
disabled_rules:
  - trailing_whitespace

opt_in_rules:
  - closure_spacing
  - empty_count
  - explicit_init
  - fatal_error_message
  - first_where
  - force_unwrapping
  - implicitly_unwrapped_optional
  - operator_usage_whitespace
  - overridden_super_call
  - private_outlet
  - sorted_imports

excluded:
  - Pods
  - .build
  - DerivedData

line_length:
  warning: 120
  error: 200
```

#### 并发与性能

```swift
// ✅ 使用 async/await 进行异步编程（Swift 5.5+）
func fetchUserData() async throws -> User {
    let user = try await apiClient.fetchUser()
    let posts = try await apiClient.fetchPosts(for: user.id)
    return user.withPosts(posts)
}

// ✅ 使用 Task 管理并发任务
Task {
    let user = try await fetchUser()
    await MainActor.run {
        self.updateUI(with: user)
    }
}

// ✅ 使用 actor 保护共享状态（Swift 5.5+）
actor CacheManager {
    private var cache: [String: Any] = [:]

    func get<T>(_ key: String, as type: T.Type) -> T? {
        cache[key] as? type
    }

    func set(_ key: String, value: Any) {
        cache[key] = value
    }
}

// ✅ 使用 TaskGroup 实现结构化并发
func fetchAllUsers(ids: [String]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask { try await self.fetchUser(byId: id) }
        }
        return try await group.reduce(into: [User]()) { $0.append($1) }
    }
}

// ❌ 禁止：使用 DispatchQueue 进行新项目开发（应使用 async/await）
DispatchQueue.global().async {
    // 旧式并发，新项目应使用 async/await
}
```

- **优先**：使用 `async/await` 替代 GCD / OperationQueue 进行异步编程
- **优先**：使用 `actor` 替代锁保护共享可变状态
- **推荐**：使用 `@MainActor` 确保 UI 更新在主线程
- **推荐**：使用 `Task` / `TaskGroup` 管理并发任务
- **禁止**：在新项目中使用 `DispatchQueue`（遗留代码除外）
- **禁止**：在主线程执行耗时操作（网络请求、文件 I/O、大量计算）
- **性能分析**：使用 Instruments 定位性能瓶颈

#### 文件与目录结构

```
MyProject/
    Sources/
        MyProject/
            App/
                MyApp.swift              # App 入口（@main）
            Models/
                User.swift
            ViewModels/
                UserViewModel.swift
            Views/
                UserListView.swift
                UserDetailView.swift
            Services/
                APIService.swift
                CacheService.swift
            Utils/
                Logger.swift
                Extensions/
                    String+Extensions.swift
    Tests/
        MyProjectTests/
            UserServiceTests.swift
            Models/
                UserTests.swift
    Resources/
        Assets.xcassets
        Localizable.strings
    Package.swift                          # SPM 依赖配置
    .swift-format                          # 格式化配置
    .swiftlint.yml                         # Lint 配置
    README.md
```

- **模块化**：每个文件导出单一职责的模块，文件不超过 300 行
- **MVVM 架构**：`Model`（数据模型）→ `ViewModel`（业务逻辑）→ `View`（UI 层）
- **Services 层**：网络请求、缓存、数据库等基础服务
- **Extensions**：按功能拆分扩展文件，`String+Extensions.swift`、`Date+Extensions.swift`
- **Assets**：统一管理图片、颜色等资源（使用 Asset Catalog）

#### 安全规范

- **输入验证**：所有外部输入必须校验（使用 `guard let` / `guard` 提前退出）
- **内存安全**：优先使用值类型（`struct`），避免引用类型导致的竞态条件
- **密钥管理**：使用 Keychain 或环境变量，**禁止**硬编码密钥到源码
- **网络安全**：使用 `URLSession` 的 TLS 验证，**禁止**禁用证书验证
- **数据加密**：敏感数据使用 `CryptoKit` 进行加密
- **依赖安全**：使用 SPM 的 `swift package audit` 扫描已知漏洞
- **反序列化**：使用 `Codable` 进行安全的 JSON 解析，**禁止**使用 `JSONSerialization` 处理不受信任的数据
- **用户默认值**：**禁止**在 `UserDefaults` 中存储敏感信息（应使用 Keychain）
- **日志安全**：**禁止**在日志中输出密码、Token 等敏感信息

### Kotlin

必须遵守 [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html) 与 [Android Kotlin Style Guide](https://developer.android.com/kotlin/style-guide)，并遵循以下现代 Kotlin 最佳实践：

#### 基础规范

- **最低版本**：Kotlin ≥ 1.9（支持 data object、enum entries、提前返回等新特性）
- **格式化**：必须使用 `ktlint` 格式化所有代码，配置文件为 `.editorconfig`
- **缩进**：4 个空格，禁止 Tab
- **行长**：≤ 120 字符
- **空行**：顶层函数 / 类之间空 1 行，类内方法之间空 1 行，逻辑块之间空 1 行
- **大括号**：K&R 风格（左大括号不换行），`else`、`catch`、`finally` 与右大括号同行
- **行尾**：禁止行尾空格，文件末尾保留一个空行
- **Semicolon**：**禁止**手动添加分号
- **表达式函数**：单表达式函数优先使用 `=` 语法，**禁止**使用 `Unit` 返回类型的单表达式函数体

```kotlin
// ✅ 正确
fun add(a: Int, b: Int): Int = a + b

// ❌ 错误
fun add(a: Int, b: Int): Int {
    return a + b  // 单表达式应使用 = 语法
}
```

#### 命名规范

- 类 / 接口 / 对象 / 注解 / 枚举：`PascalCase`
- 函数 / 方法：`camelCase`
- 变量 / 参数：`camelCase`
- 常量（`const val` / 顶层 `val`）：`UPPER_SNAKE_CASE`（仅编译期常量）或 `camelCase`（运行时常量）
- 枚举值：`PascalCase`（Kotlin 惯例，非 `UPPER_SNAKE_CASE`）
- 私有属性：使用 `_` 前缀表示 backing field
- 布尔变量 / 属性：使用 `is`、`has`、`can`、`should` 前缀，如 `isValid`、`hasPermission`
- 扩展函数：与被扩展类型语义相关，放在扩展文件中
- 缩写词保持大小写规则：`HTTPClient`、`URLParser`、`IDGenerator`、`JSONEncoder`

```kotlin
// ✅ 正确
class UserService {
    companion object {
        private const val MAX_RETRY_COUNT = 3  // 编译期常量
    }
    private val maxDelay = 5000L  // 运行时常量，camelCase
    var isActive: Boolean = false
    fun getFullName(): String = ""
}

// ❌ 错误
class user_service {
    val maxRetryCount = 3  // 应为 MAX_RETRY_COUNT 或 maxRetryCount
    fun active(): Boolean = true  // 缺少 is 前缀
}
```

#### 导入规范

```kotlin
// 顺序：标准库 → 第三方库 → 本项目包
// 各组之间用空行分隔

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

import io.ktor.client.HttpClient
import io.ktor.client.engine.okhttp.OkHttp

import com.example.project.model.User
import com.example.project.repository.UserRepository
```

- 每个 `import` 语句独占一行
- **禁止**：通配符导入 `import xxx.*`（除非是测试 mock 场景中的 `MockK` 匹配器）
- **禁止**：循环依赖；如不可避免，使用接口抽象或依赖注入解耦
- 使用 IDE 自动管理导入排序（`.editorconfig` 配置 `ktlint` 规则）

#### 类型规范

```kotlin
// ✅ 使用 data class 定义不可变数据类
data class User(
    val id: String,
    val name: String,
    val email: String,
)

// ✅ 使用 sealed class / sealed interface 定义密封类层次
sealed interface Shape {
    data class Circle(val radius: Double) : Shape
    data class Rectangle(val width: Double, val height: Double) : Shape
}

// ✅ 使用 enum class 实现有限值集合（强类型枚举）
enum class PaymentMethod(val displayName: String) {
    CreditCard("信用卡"),
    Alipay("支付宝"),
    WechatPay("微信支付"),
}

// ✅ 使用 data object 定义单例值（Kotlin 1.9+）
data object None

// ✅ 使用 value class 创建内联值类（零开销抽象）
@JvmInline
value class UserId(val value: String)

// ✅ 使用 nullable 类型表达可选值，优先使用 `?.` 和 `?:` 运算符
fun findUser(id: String): User? = null

// ✅ 使用 type alias 简化复杂类型
typealias UserMap = Map<String, User>
typealias Callback = (Result<User>) -> Unit

// ❌ 禁止：使用 `!!` 非空断言（除非确信不为空）
val user: User = findUser(id)!!  // 应使用 ?.let 或 ?: return

// ❌ 禁止：使用 Java 风格的 `Optional`
// 应使用 Kotlin 的 nullable 类型 `T?`
```

- **优先**：使用 `data class` 定义数据持有类，自动生成 `equals`、`hashCode`、`toString`、`copy`
- **必须**：使用 `enum class`（强类型枚举）替代传统 `enum`
- **优先**：使用 `sealed class/interface` 限制继承层次（配合 `when` 表达式实现穷举检查）
- **必须**：使用 nullable 类型 `T?` 表达可选值，**禁止** `!!` 非空断言（除非确信安全）
- **推荐**：使用 `value class`（`@JvmInline`）替代原始类型包装，实现零开销抽象
- **禁止**：使用 `java.util.Optional`，应使用 Kotlin 原生 nullable 类型

#### 函数与闭包规范

```kotlin
// ✅ 使用默认参数替代方法重载
fun fetchUser(
    id: String,
    timeout: Long = 30_000L,
    retries: Int = 3,
): User? = null

// ✅ 使用命名参数提高可读性
val user = fetchUser(id = "u-001", retries = 1)

// ✅ 使用尾随闭包语法
listOf(1, 2, 3).filter { it > 1 }.map { it * 2 }

// ✅ 使用作用域函数（let/also/with/apply/run）
val user = User(id = "u-001", name = "Alice").apply {
    email = "alice@example.com"
}

// ✅ 使用高阶函数和 lambda
inline fun <T> measureTime(block: () -> T): T {
    val start = System.nanoTime()
    val result = block()
    println("Elapsed: ${(System.nanoTime() - start) / 1_000_000}ms")
    return result
}

// ✅ 使用 receiver 函数类型（DSL 构建器）
fun buildUser(block: UserBuilder.() -> Unit): User = UserBuilder().apply(block).build()

// ❌ 禁止：使用 `it` 隐式参数超过一层嵌套
listOf(1, 2, 3).forEach {
    listOf("a", "b").forEach {
        println("$it")  // it 语义模糊，应使用具名参数
    }
}
```

- 参数标签：第一个参数可省略标签，后续参数**推荐**使用命名参数
- 作用域函数选择：`let`（空安全转换）、`also`（附加操作）、`with`（多次操作同一对象）、`apply`（对象配置）、`run`（对象操作 + 结果）
- **推荐**：使用 `inline` 修饰符优化高阶函数和 lambda 的性能（避免 SAM 装箱）
- **禁止**：函数超过 40 行（应拆分为更小的函数）

#### 文档规范（KDoc）

**公共类、公共函数、公共接口必须编写 KDoc 注释**。说明注释必须使用中文：

```kotlin
/**
 * 从远程 API 获取用户信息。
 *
 * 本方法通过 [userId] 从远程服务获取用户资料数据。
 * 当用户不存在时返回 `null`，不抛出异常。
 *
 * @param userId 用户的唯一标识符，必须为非空字符串。
 * @param timeout 请求超时时间，单位为毫秒，默认值为 30000L。
 * @return 包含用户资料的对象；用户不存在时返回 `null`。
 * @throws ConnectionException 当 API 不可达时抛出。
 *
 * ```kotlin
 * val user = fetchUser(userId = "u-123")
 * ```
 */
fun fetchUser(
    userId: String,
    timeout: Long = 30_000L,
): User? {
    // 实现细节...
}
```

- 使用 `[ClassName]` 引用其他类或方法，使用 `` ` `` 标记代码片段
- `@param`、`@return`、`@throws` 必须完整且使用中文描述
- 复杂逻辑在函数内部使用行内注释解释意图（而非解释"做了什么"）
- TODO 注释格式：`// TODO(负责人): 描述待办事项`，禁止遗留无主 TODO

#### 错误处理

```kotlin
// ✅ 使用自定义异常表达业务逻辑
class InsufficientBalanceException(
    val accountId: String,
    val currentBalance: Double,
    val requiredAmount: Double,
) : RuntimeException(
    "账户 $accountId 余额不足: 当前 $currentBalance, 需要 $requiredAmount"
)

// ✅ 使用 try-catch 处理可恢复的错误
fun processPayment(amount: Double): Result<Unit> = runCatching {
    if (amount <= 0) throw IllegalArgumentException("金额必须为正数")
    // 业务逻辑...
}

// ✅ 使用 Result 类型替代异常（业务流程控制）
fun findUser(id: String): Result<User> = runCatching {
    repository.findById(id) ?: throw NotFoundException("User", id)
}

// ✅ 使用密封类表示错误状态
sealed interface ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>
    data class Failure(val error: ApiError) : ApiResult<Nothing>
}

// ❌ 禁止：空 catch 块
try {
    riskyOperation()
} catch (e: Exception) {
    // 禁止空 catch 块！
}
```

- **可恢复错误**：使用 `Result<T>`（`runCatching`）或自定义异常
- **业务流程控制**：使用密封类 `sealed interface` 表示成功 / 失败状态
- 捕获尽可能精确的异常类型，**禁止** `catch (e: Exception) { /* 空 */ }`
- 使用 `logger.error()` 记录异常，**禁止** `println()` / `print()` 输出生产错误日志
- 异常链：使用 `cause` 参数保留原始异常

#### 测试规范

```kotlin
// 目录结构
src/
    main/kotlin/
        com/example/project/
            service/
                UserService.kt
    test/kotlin/
        com/example/project/
            service/
                UserServiceTest.kt    // 与被测文件对应
    testFixtures/                      // 测试数据（可选）
```

- **框架**：JUnit 5（`jupiter`），推荐配合 MockK 或 Kotest
- **文件命名**：`<ClassName>Test.kt`，与被测类同包名
- **函数命名**：`should<预期行为>When<条件>()` 或 `test<方法名>_<场景>()`
- **断言**：使用 JUnit `Assertions.*` 或 Kotest `shouldBe` / `should` 风格
- **覆盖率**：核心模块要求覆盖率 ≥ 80%（JaCoCo）
- **Mock**：使用 MockK（`mockk` / `coEvery`），mock 外部依赖
- **参数化测试**：使用 JUnit 5 `@ParameterizedTest` 或 Kotest `forAll` / `propertyTest`

```kotlin
import io.kotest.assertions.assertSoftly
import io.kotest.matchers.shouldBe
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class UserServiceTest {

    private val repository = mockk<UserRepository>()
    private val service = UserService(repository)

    @Test
    fun `should return user when found`() = runTest {
        // Arrange
        val expectedUser = User(id = "u-001", name = "Alice")
        coEvery { repository.findById("u-001") } returns expectedUser

        // Act
        val user = service.findById("u-001")

        // Assert
        user?.name shouldBe "Alice"
    }

    @Test
    fun `should return null when user not found`() = runTest {
        coEvery { repository.findById("nonexistent") } returns null

        val user = service.findById("nonexistent")

        user shouldBe null
    }

    @Test
    fun `should validate user data`() {
        assertSoftly {
            "Alice".length shouldNotBe 0
            "u-001" shouldNotBe blank()
        }
    }
}
```

#### 依赖与项目管理

```kotlin
// build.gradle.kts — 唯一的依赖声明入口
plugins {
    kotlin("jvm") version "1.9.22"
    kotlin("plugin.serialization") version "1.9.22"
}

group = "com.example"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // 实现依赖
    implementation("io.ktor:ktor-server-core:2.3.7")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")

    // 测试依赖
    testImplementation("io.kotest:kotest-assertions-core:5.8.0")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation(kotlin("test"))
}

kotlin {
    jvmToolchain(17)
}
```

```toml
// gradle/libs.versions.toml — 版本目录（推荐，统一管理依赖版本）
[versions]
kotlin = "1.9.22"
ktor = "2.3.7"
coroutines = "1.7.3"

[libraries]
ktor-core = { module = "io.ktor:ktor-server-core", version.ref = "ktor" }
coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
```

- **构建工具**：必须使用 Gradle（Kotlin DSL `build.gradle.kts`），**禁止** Maven
- **依赖管理**：使用 Version Catalog（`gradle/libs.versions.toml`）统一管理版本
- **锁定文件**：使用 `gradle.lockfile` 锁定依赖版本，提交到版本控制
- **依赖安全**：定期运行 `gradle dependencyCheckAnalyze`（OWASP）扫描已知漏洞
- **JVM 工具链**：使用 `jvmToolchain()` 指定 JDK 版本，确保编译环境一致

#### 代码质量工具链

```ini
# .editorconfig — 代码风格（ktlint 驱动）
root = true

[*.{kt,kts}]
indent_size = 4
max_line_length = 120
ktlint_code_style = official

# 自定义规则
ij_kotlin_allow_trailing_comma = true
ij_kotlin_allow_trailing_comma_on_call_site = true
```

```yaml
# detekt.yml — 静态分析配置
build:
  maxIssues: 0  # 发现 issue 时构建失败

complexity:
  LongMethod:
    threshold: 60
  LongParameterList:
    functionThreshold: 8
  ComplexMethod:
    threshold: 15

style:
  MaxLineLength:
    maxLineLength: 120
```

| 工具 | 用途 | 优先级 |
|---|---|---|
| `ktlint` | 代码格式化（Kotlin Coding Conventions） | **必须** |
| `detekt` | 静态分析（代码复杂度、潜在 Bug、代码气味） | **必须** |
| JUnit 5 + MockK | 单元 / 集成测试 | **必须** |
| JaCoCo | 测试覆盖率报告 | **必须** |
| `gradle lint` | Gradle 构建脚本检查 | 推荐 |
| `dependency-check` | 依赖安全漏洞扫描 | 推荐 |

#### 安全规范

- **输入验证**：所有外部输入必须校验（使用 `require` / `check` 或自定义验证）
  ```kotlin
  fun createUser(name: String, email: String): User {
      require(name.isNotBlank()) { "名称不能为空" }
      require(email.contains("@")) { "邮箱格式无效" }
      // ...
  }
  ```
- **SQL 注入**：使用 Exposed / MyBatis 参数化查询，**禁止**字符串拼接 SQL
  ```kotlin
  // ✅ 正确：参数化查询
  User.find { Users.email eq email }.singleOrNull()

  // ❌ 禁止：字符串拼接 SQL
  val sql = "SELECT * FROM users WHERE email = '$email'"
  ```
- **密钥管理**：使用环境变量或密钥管理服务（如 AWS Secrets Manager），**禁止**硬编码密钥
- **依赖安全**：定期运行 OWASP Dependency Check 扫描已知漏洞
- **反序列化**：使用 `kotlinx.serialization`，**禁止**使用 Java 原生反序列化
- **文件操作**：使用 `Path` API（`kotlin.io.path`），校验路径防止目录穿越
- **SSRF 防护**：对外部 URL 请求进行白名单校验
- **日志安全**：**禁止**在日志中输出密码、Token 等敏感信息

#### 协程与并发

```kotlin
// ✅ 使用 coroutineScope + launch/async 管理并发
suspend fun fetchUserData(userId: String): User = coroutineScope {
    val userDeferred = async { fetchUser(userId) }
    val postsDeferred = async { fetchUserPosts(userId) }
    userDeferred.await().withPosts(postsDeferred.await())
}

// ✅ 使用 Dispatchers 控制线程调度
suspend fun processData(data: List<Item>): List<Result> =
    withContext(Dispatchers.Default) {
        data.map { process(it) }
    }

// ✅ 使用 Flow 处理异步数据流
fun observeUsers(): Flow<User> = callbackFlow {
    val listener = object : UserListener {
        override fun onUserUpdated(user: User) {
            trySend(user)
        }
    }
    registerListener(listener)
    awaitClose { unregisterListener(listener) }
}

// ✅ 使用 StateFlow 管理 UI 状态
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()
}

// ✅ 使用 SupervisorJob 隔离子协程失败
fun fetchAllUsers(ids: List<String>) = supervisorScope {
    ids.map { id ->
        async { fetchUser(id) }  // 单个失败不影响其他
    }.awaitAll()
}

// ❌ 禁止：在 GlobalScope 中启动协程（生命周期不可控）
GlobalScope.launch { /* ... */ }  // 应使用 viewModelScope / lifecycleScope

// ❌ 禁止：在协程中使用 Thread.sleep
delay(1000)  // ✅ 正确
Thread.sleep(1000)  // ❌ 阻塞线程
```

- **优先**：使用 `suspend` 函数替代回调，使用 `Flow` 替代 `LiveData` / `Observable`
- **必须**：使用结构化并发（`coroutineScope` / `supervisorScope`），**禁止** `GlobalScope`
- **推荐**：使用 `StateFlow` / `SharedFlow` 替代 `MutableLiveData`
- **推荐**：使用 `runTest` + `TestCoroutineDispatcher` 测试协程代码
- **禁止**：在协程中使用阻塞操作（`Thread.sleep`、`InputStream.read`），应使用挂起版本
- **超时控制**：使用 `withTimeout` / `withTimeoutOrNull` 控制协程超时
- **取消传播**：确保协程支持取消（避免在挂起点之间执行长时间 CPU 计算）

#### 文件与目录结构

```
my-project/
    src/
        main/kotlin/
            com/example/project/
                Application.kt            # 应用入口（@main 或 main 函数）
                config/                   # 配置类
                    AppConfig.kt
                controller/               # HTTP 控制器层（Ktor / Spring MVC）
                    UserController.kt
                service/                  # 业务逻辑层
                    UserService.kt
                    impl/
                        UserServiceImpl.kt
                repository/               # 数据访问层
                    UserRepository.kt
                model/                    # 数据模型
                    User.kt
                    dto/
                        UserDTO.kt
                exception/                # 自定义异常
                    NotFoundException.kt
                utils/                    # 工具类
                    Extensions.kt
                di/                       # 依赖注入模块（Koin / Dagger）
                    AppModule.kt
        main/resources/
            application.yml
            application-dev.yml
            application-prod.yml
        test/kotlin/
            com/example/project/
                service/
                    UserServiceTest.kt
                controller/
                    UserControllerTest.kt
        testFixtures/                     # 测试数据（可选）
    build.gradle.kts                      # 构建配置入口
    gradle/
        libs.versions.toml                # 版本目录（推荐）
    settings.gradle.kts                   # 项目设置
    gradle.properties                     # Gradle 属性
    gradlew / gradlew.bat                 # Gradle Wrapper
    detekt.yml                            # detekt 配置
    .editorconfig                         # ktlint / IDE 配置
    README.md
```

- **分层架构**：`controller`（输入处理）→ `service`（业务逻辑）→ `repository`（数据访问），各层通过接口解耦
- **入口文件**：`Application.kt` 仅负责组装和启动，**禁止**包含业务逻辑
- **配置分离**：按环境拆分配置文件（`application-{profile}.yml`）
- **DTO 分离**：Entity 与 DTO 严格分离，禁止直接暴露数据库实体给前端
- **每个文件不超过 300 行**，超过时按职责拆分为多个文件
- **异常统一处理**：使用异常过滤器或中间件统一处理异常

### iOS (Apple Platform)

必须遵守 [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) 与 [Apple Platform Security Guide](https://support.apple.com/guide/security/)，并遵循以下 iOS/macOS 平台开发最佳实践：

#### 基础规范

- **最低版本**：iOS >= 17.0（支持 SwiftData、Observable Macro、TipKit 等新特性）；macOS >= 14.0
- **Xcode 版本**：使用最新稳定版 Xcode（>= 15.0），启用 `SWIFT_STRICT_CONCURRENCY = complete`
- **Swift 版本**：Swift >= 5.9，推荐启用 Swift 6 语言模式（`SWIFT_VERSION = 6`）
- **部署目标**：通过 `IPHONEOS_DEPLOYMENT_TARGET` 统一管理，**禁止**在代码中硬编码版本判断
- **构建配置**：使用 `.xcconfig` 文件管理构建设置，**禁止**仅通过 Xcode GUI 配置
- **代码签名**：使用 Automatic Signing，团队内统一 Provisioning Profile 管理

#### 项目结构

```
MyProject/
    MyProject/
        App/
            MyApp.swift                      # App 入口（@main）
            AppDelegate.swift                 # AppDelegate（如需要）
        Features/                            # 功能模块（按业务拆分）
            Home/
                HomeView.swift
                HomeViewModel.swift
                HomeCoordinator.swift
            Profile/
                ProfileView.swift
                ProfileViewModel.swift
        Core/                                # 核心层
            Network/
                APIClient.swift
                Endpoint.swift
            Storage/
                CoreDataStack.swift
                SwiftDataModel.swift
            Extensions/
                String+Extensions.swift
                Date+Extensions.swift
        DesignSystem/                        # 设计系统
            Components/
            Theme/
            Resources/
                Assets.xcassets
                Localizable.strings
        Resources/
            Info.plist
    MyProjectTests/
        UnitTests/
        IntegrationTests/
    MyProjectUITests/
    Package.swift
    MyProject.xcodeproj
    .swiftlint.yml
```

- **模块化**：按功能（Feature）拆分模块，每个模块包含独立的 View、ViewModel、Coordinator
- **资源管理**：使用 Asset Catalog 管理图片、颜色、SF Symbols
- **国际化**：使用 `String(localized:)` API，**禁止**硬编码用户可见字符串

#### UI 框架规范

**新项目优先使用 SwiftUI，遗留项目可使用 UIKit 兼容方案。**

##### SwiftUI 规范

```swift
// 使用 @Observable 宏（iOS 17+）
@Observable
class UserViewModel {
    var users: [User] = []
    var isLoading = false

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        users = try await apiClient.fetchUsers()
    }
}

// 使用 @State、@Binding 管理视图状态
struct UserListView: View {
    @State private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            UserRowView(user: user)
        }
        .task { await viewModel.loadUsers() }
    }
}

// 使用 NavigationStack（iOS 16+）
NavigationStack {
    UserListView()
        .navigationDestination(for: Route.self) { route in
            detailView(for: route)
        }
}
```

- **状态管理**：使用 `@Observable`（iOS 17+）或 `@StateObject` / `@ObservedObject`
- **导航**：使用 `NavigationStack` + `navigationDestination`，**禁止**使用已弃用的 `NavigationView`
- **列表**：使用 `LazyVStack` / `LazyHStack` 实现懒加载，**禁止**在 `List` 中嵌套滚动视图
- **动画**：使用 `.animation()` 修饰符，**禁止**使用 `UIView.animate` 在 SwiftUI 中

##### UIKit 规范（遗留项目兼容）

```swift
// 使用 programmatic UI，新页面禁止使用 Storyboard
class UserViewController: UIViewController {
    private let tableView = UITableView()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
    }

    private func setupUI() {
        view.addSubview(tableView)
        tableView.dataSource = self
        tableView.delegate = self
        tableView.register(UserCell.self, forCellReuseIdentifier: UserCell.reuseID)
    }
}

// 使用 Auto Layout + SnapKit
private func setupConstraints() {
    tableView.snp.makeConstraints { make in
        make.edges.equalToSuperview()
    }
}
```

- **新页面禁止使用 Storyboard**，使用纯代码布局
- **使用 SnapKit** 简化 Auto Layout 约束
- **Cell 注册**：使用 `register(_:forCellReuseIdentifier:)`，**禁止**在 `cellForRow` 中创建 Cell

#### 架构模式

**推荐使用 MVVM-C（MVVM + Coordinator）或 The Composable Architecture（TCA）：**

```
View（SwiftUI/UIKit）
    -> 绑定
ViewModel（@Observable / ObservableObject）
    -> 调用
UseCase（业务逻辑）
    -> 依赖
Repository（数据访问）
    -> 实现
DataSource（API / CoreData / UserDefaults）
```

- **View 层**：仅负责 UI 渲染和用户交互，**禁止**包含业务逻辑
- **ViewModel 层**：管理 UI 状态，处理用户操作，**禁止**直接引用 UIKit/SwiftUI 类型
- **Coordinator 层**：管理页面导航和模块间通信，**禁止**在 ViewModel 中直接 push ViewController
- **依赖注入**：使用 Protocol 定义依赖，通过构造函数注入，**禁止**使用单例模式（除 App 级服务）

#### 内存与性能管理

- **ARC 管理**：使用 `[weak self]` / `[unowned self]` 打破循环引用
  ```swift
  // 在闭包中使用 [weak self]
  service.fetchData { [weak self] result in
      guard let self else { return }
      self.updateUI(with: result)
  }
  ```
- **内存泄漏检测**：使用 Instruments 的 Leaks 和 Allocations 工具
- **主线程保护**：使用 `@MainActor` 确保 UI 更新在主线程
  ```swift
  @MainActor
  func updateUI(with data: [Item]) {
      self.items = data  // 保证在主线程执行
  }
  ```
- **图片缓存**：使用 `NSCache` 或第三方库（如 Kingfisher），**禁止**在内存中存储大量未压缩图片
- **预加载与懒加载**：使用 `Prefetching` 和 `onAppear` 实现列表项预加载
- **App 启动优化**：减少 `didFinishLaunchingWithOptions` 中的同步操作，使用后台线程初始化非必要服务

#### 网络与数据层

```swift
// 使用 async/await + URLSession
protocol APIClientProtocol {
    func fetch<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

struct APIClient: APIClientProtocol {
    private let session: URLSession
    private let decoder: JSONDecoder

    func fetch<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let (data, response) = try await session.data(for: endpoint.urlRequest)
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }
        return try decoder.decode(T.self, from: data)
    }
}
```

- **使用 async/await** 替代 completion handler，**禁止**使用回调地狱
- **网络层封装**：定义 `Endpoint` 协议统一管理 API 路径、参数、请求方法
- **错误处理**：定义 `APIError` 枚举，区分网络错误、服务器错误、解析错误
- **重试机制**：使用指数退避策略，配置最大重试次数
- **Mock 与测试**：通过 Protocol 实现 API Mock，**禁止**在测试中调用真实 API

#### 依赖与包管理

- **优先使用 SPM**（Swift Package Manager），**禁止**在新项目中使用 CocoaPods
- **SPM 配置**：在 `Package.swift` 中声明依赖，Xcode 自动解析版本
- **版本锁定**：`Package.resolved` 必须提交到版本控制
- **CocoaPods 兼容**：如必须使用 CocoaPods，`Podfile` 和 `Podfile.lock` 均需提交
- **依赖评估**：新增依赖前检查 Stars 数、最近更新时间、Issue 响应速度

#### 平台安全

- **Keychain 使用**：敏感数据（Token、密码）必须存储在 Keychain，**禁止**使用 `UserDefaults`
  ```swift
  // 使用 Keychain 存储 Token
  let keychain = Keychain(service: "com.app.auth")
  try keychain.set(token, key: "access_token")
  ```
- **App Transport Security**：**禁止**在生产环境禁用 ATS（`NSAppTransportSecurity`）
- **隐私权限**：遵循最小权限原则，仅在需要时请求权限，配置 `NSPrivacyUsageDescription`
- **生物认证**：使用 `LocalAuthentication` 框架实现 Face ID / Touch ID
- **数据保护**：使用 `CryptoKit` 进行端到端加密，**禁止**使用已弃用的 CommonCrypto
- **Secure Enclave**：高敏感密钥存储在 Secure Enclave 中

#### 测试规范

```swift
// 单元测试
import XCTest
@testable import MyProject

final class UserRepositoryTests: XCTestCase {
    private var sut: UserRepository!
    private var mockAPIClient: MockAPIClient!

    override func setUp() {
        super.setUp()
        mockAPIClient = MockAPIClient()
        sut = UserRepository(apiClient: mockAPIClient)
    }

    override func tearDown() {
        sut = nil
        mockAPIClient = nil
        super.tearDown()
    }

    func testFetchUsersShouldReturnUsers() async throws {
        // Arrange
        mockAPIClient.stubbedResult = [User.mock]
        // Act
        let users = try await sut.fetchUsers()
        // Assert
        XCTAssertEqual(users.count, 1)
        XCTAssertEqual(users.first?.name, "Alice")
    }
}
```

- **单元测试框架**：XCTest + Swift Testing（推荐 Swift 6+）
- **UI 测试**：使用 XCUITest，**禁止**使用 EarlGrey（已弃用）
- **快照测试**：使用 swift-snapshot-testing 验证 UI 回归
- **覆盖率**：核心模块要求覆盖率 >= 80%
- **Mock**：通过 Protocol 实现依赖 Mock，**禁止**使用 OHMock 等运行时 Mock

#### 代码质量工具链

| 工具 | 用途 | 优先级 |
|---|---|---|
| `swift-format` | 代码格式化 | **必须** |
| `SwiftLint` | Lint 检查（代码风格 + 最佳实践） | **必须** |
| `Xcode Build Settings` | 编译时静态分析（Strict Concurrency） | **必须** |
| `XCTest` / Swift Testing | 单元 / 集成测试 | **必须** |
| `Instruments` | 性能分析（Leaks、Allocations、Time Profiler） | **必须** |
| `Periphery` | 未使用代码检测 | 推荐 |
| `DocC` | 文档生成 | 推荐 |

#### 提交与版本管理

- **分支策略**：使用 Git Flow（`main` -> `develop` -> `feature/*`）
- **语义化版本**：遵循 SemVer（`MAJOR.MINOR.PATCH`）
- **TestFlight**：所有版本必须通过 TestFlight 分发测试后再上架
- **Fastlane**：使用 Fastlane 自动化构建、测试、上架流程
- **CI/CD**：使用 Xcode Cloud 或 GitHub Actions 实现持续集成

### Android

必须遵守 [Android Kotlin Style Guide](https://developer.android.com/kotlin/style-guide) 与 [Android API Guidelines](https://developer.android.com/guide/topics/quality-guidelines)，并遵循以下 Android 平台开发最佳实践：

#### 基础规范

- **最低版本**：minSdk >= 24（Android 7.0，覆盖 99%+ 活跃设备）；targetSdk >= 35（Android 15）
- **Kotlin 版本**：Kotlin >= 2.0（支持 K2 编译器、多平台改进）
- **AGP 版本**：Android Gradle Plugin >= 8.5（支持 Configuration Cache、Build Analyzer）
- **JDK**：使用 JDK 17 编译（`jvmToolchain(17)`）
- **编译选项**：启用 `isCoreLibraryDesugaringEnabled = true`（Java 8+ API 兼容）
- **构建变体**：区分 `debug` / `staging` / `release` 三种 Build Type

#### 项目结构

```
my-project/
    app/
        src/
            main/
                java/com/example/project/
                    MyApplication.kt              # Application 入口
                    MainActivity.kt               # 主 Activity
                    di/                           # 依赖注入
                        AppModule.kt
                    feature/                      # 功能模块
                        home/
                            HomeScreen.kt
                            HomeViewModel.kt
                            HomeNavigation.kt
                        profile/
                            ProfileScreen.kt
                            ProfileViewModel.kt
                    core/                         # 核心层
                        data/
                            remote/
                                ApiService.kt
                                dto/
                            local/
                                AppDatabase.kt
                                dao/
                        domain/
                            repository/
                            model/
                        ui/
                            theme/
                                Color.kt
                                Theme.kt
                                Type.kt
                            components/
                res/
                    values/
                        strings.xml
                    drawable/
                    layout/                      # XML 布局（如需要）
                AndroidManifest.xml
            androidTest/                         # 仪器测试
            test/                                # 单元测试
        build.gradle.kts
    gradle/
        libs.versions.toml                       # 版本目录
    settings.gradle.kts
    build.gradle.kts
```

- **模块化**：按功能（Feature）拆分 Gradle 模块，使用 `:feature:*`、`:core:*` 命名
- **资源管理**：使用 `strings.xml` 集中管理字符串，使用 Material Theme 管理颜色和字体
- **AndroidManifest**：声明最小必要权限，使用 `<queries>` 声明隐式 Intent 查询

#### UI 框架规范

**新项目必须使用 Jetpack Compose，遗留项目可兼容 XML 布局。**

##### Jetpack Compose 规范

```kotlin
// 使用 Composable 函数定义 UI
@Composable
fun UserListScreen(
    viewModel: UserViewModel = hiltViewModel(),
    onUserClick: (String) -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserUiState.Loading -> LoadingIndicator()
        is UserUiState.Success -> UserList(
            users = state.users,
            onUserClick = onUserClick,
        )
        is UserUiState.Error -> ErrorRetry(
            message = state.message,
            onRetry = viewModel::retry,
        )
    }
}

// 使用 Material 3 组件
@Composable
fun UserCard(user: User) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = { /* ... */ },
    ) {
        ListItem(
            headlineContent = { Text(user.name) },
            supportingContent = { Text(user.email) },
            leadingContent = { AsyncImage(model = user.avatarUrl) },
        )
    }
}
```

- **状态管理**：使用 `collectAsStateWithLifecycle()` 收集 Flow，配合 Lifecycle-aware
- **列表**：使用 `LazyColumn` / `LazyRow`，提供 `key` 参数优化重组
- **导航**：使用 Navigation Compose（`NavHost` + `composable`），**禁止**使用已弃用的导航方式
- **主题**：使用 Material 3 `MaterialTheme`，通过 `colorScheme` / `typography` 自定义
- **预览**：每个 Composable 必须提供 `@Preview`，使用 `@PreviewParameter` 参数化预览

##### XML 布局兼容（遗留项目）

- **新页面禁止使用 XML 布局**，使用 Jetpack Compose
- **旧页面迁移**：使用 `ComposeView` 在 XML 布局中嵌入 Compose 组件
- **禁止**：在 XML 布局中使用 `TwoWayBinding`（应使用 StateFlow + Compose）

#### 架构模式

**推荐使用 MVVM + Clean Architecture + Unidirectional Data Flow：**

```
Screen（Composable）
    -> 状态提升
ViewModel（@HiltViewModel）
    -> 调用
UseCase（Domain 层）
    -> 依赖
Repository（接口）
    -> 实现
DataSource（Remote / Local）
```

```kotlin
// ViewModel 使用 StateFlow 暴露状态
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUsersUseCase: GetUsersUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init { loadUsers() }

    private fun loadUsers() {
        viewModelScope.launch {
            getUsersUseCase()
                .catch { _uiState.value = UserUiState.Error(it.message) }
                .collect { _uiState.value = UserUiState.Success(it) }
        }
    }
}
```

- **View 层**：仅负责 UI 渲染，**禁止**包含业务逻辑或直接访问数据层
- **ViewModel 层**：使用 `viewModelScope` 管理协程，**禁止**持有 `Context` 或 `Activity` 引用
- **UseCase 层**：封装业务逻辑，**禁止**直接操作 UI 或 Android 框架类
- **Repository 层**：统一数据访问入口，协调 Remote 和 Local 数据源

#### 组件与生命周期

- **Activity**：单一 Activity 架构，使用 Navigation Component 管理页面
- **Fragment**：使用 `by viewModels()` 委托获取 ViewModel，**禁止**在 Fragment 中直接创建 ViewModel
- **生命周期感知**：使用 `repeatOnLifecycle` 收集 Flow，**禁止**在 `onCreate` 中直接收集
- **SavedStateHandle**：关键 UI 状态使用 `SavedStateHandle` 保存，应对进程终止恢复

#### 依赖管理

- **Compose BOM**：使用 Compose Bill of Materials 统一 Compose 版本，**禁止**手动指定各 Compose 库版本
- **版本目录**：使用 `libs.versions.toml` 统一管理所有依赖版本
- **Hilt**：推荐使用 Hilt 作为 DI 框架，**禁止**在新项目中使用 Dagger 或手动 DI
- **锁定文件**：使用 `gradle.lockfile` 锁定依赖版本，提交到版本控制
- **依赖安全**：定期运行 OWASP Dependency Check 扫描已知漏洞

#### 网络与数据层

```kotlin
// 使用 Retrofit + Kotlinx Serialization
@Serializable
data class UserDto(
    val id: String,
    val name: String,
    val email: String,
)

interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<UserDto>
}

// 使用 Room 本地数据库
@Database(entities = [UserEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<UserEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertUsers(users: List<UserEntity>)
}
```

- **序列化**：使用 `kotlinx.serialization`，**禁止**使用 Gson 或 Jackson
- **离线优先**：Room 作为本地缓存，网络数据写入 Room 后通过 Flow 通知 UI
- **分页**：使用 Paging 3（`Pager` + `PagingData`）处理分页加载
- **错误处理**：定义 `Result<T>` 密封类统一处理成功/失败状态

#### 平台安全

- **网络安全**：配置 `network_security_config.xml`，**禁止**在生产环境禁用 SSL 验证
- **权限管理**：使用 Accompanist Permissions 或自定义权限请求流程，遵循最小权限原则
- **数据存储**：敏感数据使用 EncryptedSharedPreferences 或 Jetpack Security，**禁止**使用明文 SharedPreferences
- **ProGuard / R8**：Release 构建必须启用代码混淆，保留必要的序列化类
- **App Sandbox**：使用 Scoped Storage 访问共享存储，**禁止**使用 `MANAGE_EXTERNAL_STORAGE`
- **生物认证**：使用 `BiometricPrompt` API 实现生物认证

#### 测试规范

```kotlin
// 单元测试
class GetUsersUseCaseTest {

    private val repository = mockk<UserRepository>()
    private val useCase = GetUsersUseCase(repository)

    @Test
    fun `should return users when repository succeeds`() = runTest {
        val expectedUsers = listOf(User(id = "1", name = "Alice"))
        coEvery { repository.getUsers() } returns flowOf(expectedUsers)

        useCase().collect { users ->
            assertEquals(expectedUsers, users)
        }
    }
}
```

- **单元测试框架**：JUnit 5 + MockK + Turbine（Flow 测试）
- **UI 测试框架**：Compose Testing（`createComposeRule()`）+ Espresso（XML 遗留页面）
- **覆盖率**：核心模块要求覆盖率 >= 80%（JaCoCo）
- **参数化测试**：使用 JUnit 5 `@ParameterizedTest` 或 Kotest `forAll`
- **集成测试**：使用 `HiltAndroidTest` + `@UninstallModules` 测试 DI 配置
- **截图测试**：使用 Roborazzi 或 Paparazzi 进行 UI 回归测试

#### 代码质量工具链

| 工具 | 用途 | 优先级 |
|---|---|---|
| `ktlint` | 代码格式化 | **必须** |
| `detekt` | 静态分析（代码复杂度、潜在 Bug） | **必须** |
| `Android Lint` | 平台特定检查（API 兼容性、性能、安全） | **必须** |
| JUnit 5 + MockK | 单元测试 | **必须** |
| Compose Testing | UI 测试 | **必须** |
| JaCoCo | 测试覆盖率报告 | **必须** |
| `dependency-check` | 依赖安全漏洞扫描 | 推荐 |
| `Paparazzi` | 截图测试 | 推荐 |

#### 提交与版本管理

- **分支策略**：使用 Git Flow（`main` -> `develop` -> `feature/*`）
- **语义化版本**：遵循 SemVer（`MAJOR.MINOR.PATCH`），`versionCode` 递增
- **Play Console**：使用 Internal Testing -> Closed Testing -> Open Testing -> Production 渠道
- **Fastlane**：使用 Fastlane 自动化构建、测试、上架流程
- **CI/CD**：使用 GitHub Actions 或 Bitrise 实现持续集成
- **Baseline Profiles**：使用 Baseline Profiles 优化应用启动性能
- **R8 完整模式**：Release 构建启用 `android.enableR8.fullMode = true`

## 行为规则

1. 始终以友好、专业的语气回复
2. 回复内容使用中文
3. 代码示例使用 Markdown 代码块格式
4. 如果不确定，明确说明并提供可能的方向
5. **重申：你的文本输出不会被任何人看到（参见文件开头"最重要的规则"）。必须通过 curl 发布评论，否则用户收不到回复。**

## CNB 平台特性

- CNB 不是 GitHub，不要混淆平台术语
- API 地址通过 `CNB_API_ENDPOINT` 环境变量获取
- Token 通过 `CNB_TOKEN` 环境变量获取

## 工作流程

### 收到 PR 相关请求时
1. 如需评审 → 使用 `code-review` 技能，按指引执行
2. 如需总结 → 使用 `pr-summary` 技能，按指引执行
3. 如需诊断 CI 失败 → 使用 `diagnose-ci-pipeline` 技能

### 收到编码请求时
1. 使用 `code-commit` 技能，修改代码后必须完成 git add/commit/push，必要时创建 PR

### 收到 CNB 平台操作请求时
1. **优先使用 `cnb` 命令**：先 `cnb --help` 查看可用模块，再执行对应工具
2. **`cnb` 无法满足时**：参考 `instructions/cnb-openapi.md` 和 `instructions/references/` 中的文档，使用 curl 直接调用 API（不要在 curl 前加 bash 前缀）

### 收到 CNB 平台使用问题时
1. 使用 `cnb-knowledge-base` 技能查询官方文档

### 收到流水线配置请求时
1. 使用 `cnb-pipeline` 技能生成或修改 `.cnb.yml`

### 收到 Tapd 相关请求时
1. 使用 `tapd-resource-fetcher` 技能获取 Tapd 资源数据

### 收到任何请求时的最终步骤
1. 使用 cnb-api 技能的快捷命令发布评论（如 `cnb issues comment` 或 `cnb pulls comment`）
2. **不要跳过这一步！不发布评论就等于没有回复用户。**

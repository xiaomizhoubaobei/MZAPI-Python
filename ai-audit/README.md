# AI 审计测试示例

本目录提供 **AI 审计（AI 漏洞分流）** 的测试用示例，用于在你的仓库上验证
`GitHub Security Lab Taskflow Agent` 框架的 AI 告警分流链路。

> ⚠️ **说明**：本示例为**测试/演示用途**，供你参考如何把文章
> 《借助 GitHub Security Lab Taskflow Agent 的 AI 支持漏洞分流》中的方法论落地到你自己的仓库。
>
> ✅ `alert_triage_example.yaml` 已按官方框架 `doc/GRAMMAR.md` 语法编写并针对本项目（**Python**）适配：
> 使用 `seclab-taskflow-agent` 头部 + `filetype: taskflow`、顶层 `taskflow` key、
> `agents` 引用 personalities、`repeat_prompt`/`over` 批量循环、`run` shell 任务
> 与 `outputs` JSON Schema 校验等标准语法。

---

## 一、这套 AI 审计在做什么

你的仓库已配置 `.github/workflows/codeql.yml`（CodeQL 静态扫描），它会扫出安全告警。
AI 审计的作用是：用 **LLM + Taskflow Agent** 对这批 CodeQL 告警做**自动分流**，
剔除误报（False Positive），对真实漏洞生成带精确文件/行号引用的报告，并**自动创建
真实 Issue** 供开发跟进修复。

```
CodeQL 扫出安全告警
     │
     ▼
LLM + Taskflow Agent 逐个审计
  ├─ ① 信息收集：调 GitHub API 拿触发事件/权限/上下文
  ├─ ② 审计：剔除误报（攻击者能否触发？是否特权上下文？）
  ├─ ③ 生成漏洞报告（带精确文件+行号引用）
  ├─ ④ 校验：报告不完整/不一致=幻觉，直接驳回
  ├─ ⑤ 创建真实 Issue：仅对真实漏洞自动创建 GitHub Issue（自动去重）
  └─ ⑥ 知识回流：人工驳回原因回流给 LLM，持续改进
```

本目录的 `alert_triage_example.yaml` 即对应上面的 6 阶段流程。

> ⚠️ 第 ⑤ 步会**真实创建 Issue**。若你只想看分流结果、不修改仓库，
> 请把 `alert_triage_example.yaml` 中第 ⑤ 步「创建真实 Issue」任务整体注释掉。

---

## 二、目录结构

```
ai-audit/
├── README.md                        # 本说明
├── __init__.py                      # 使 ai_audit 成为可导入 Python 包（框架 importlib.resources 必需）
├── alert_triage_example.yaml        # 6 阶段 AI 审计 taskflow（官方 GRAMMAR 语法）
├── model_config.yaml                # OpenAI 兼容上游模型配置（模型名 + api_type: chat_completions）
├── model_config.py                  # [参考] model_config.yaml 的说明文档（框架不读取）
└── personalities/
    ├── __init__.py                  # 使 personalities 成为可导入子包
    └── python_auditer.yaml          # 项目自带的 Python 审计人格（personality）
```

> ⚠️ **为什么必须有 `__init__.py`？** 框架通过
> `importlib.resources.files(package)` 加载 taskflow / personality / model_config，
> 它要求目标目录是**可导入的 Python 包**。因此本目录（复制后名为 `ai_audit`）
> 及其 `personalities/` 子目录都必须包含 `__init__.py`，否则会报
> `No module named 'ai_audit'`。若目录被当作 PEP 420 命名空间包（无 `__init__.py`）
> 处理，在不同 Python 环境 / hatch 环境下不一定能稳定被 `importlib.resources` 解析，
> 显式提供 `__init__.py` 是最稳妥的做法。

**为什么需要自带的 Python 人格？** 官方框架默认自带的安全审计人格是
`seclab_taskflow_agent.personalities.c_auditer`，它是针对 **C 语言**设计的
（系统提示词明确"Find vulnerabilities in any provided C code"）。
本项目是 **Python** 仓库（`mzapi/**`），为获得正确的审计结果，示例改用项目自带的
`ai_audit.personalities.python_auditer`（面向 Python / MCP Server 的审计人格），
并复用了官方 `codeql` + `memcache` 两个 toolbox。

---

## 三、运行前提（需要你配置）

| 前提 | 说明 | 状态 |
|------|------|------|
| 仓库已开启 CodeQL 扫描 | `.github/workflows/codeql.yml` 已存在 | ✅ 已具备 |
| `seclab-taskflow-agent` 框架 | 需部署框架本体 | ❌ 需部署 |
| LLM 模型（支持函数调用） | 任意 OpenAI 兼容上游：DeepSeek / 通义千问 / Moonshot / 本地 vLLM 等 | ❌ 需配置（`AI_API_ENDPOINT` + `AI_API_TOKEN`） |
| GitHub PAT（读告警 + 写 Issue） | 读 CodeQL 告警、创建真实 Issue 用 | ❌ 需你提供 |
| MCP Server（GitHub API） | 框架信息收集用 | ❌ 需配置 |

---

## 四、部署与运行

> 框架通过 **Python 模块路径**加载 taskflow / personality（`packagename.filename`）。
> 因此需要把本目录（含 personalities）放到框架能解析到包路径的地方。

### 方式一：复制到框架仓库根目录（推荐，最省事）

1. 部署框架与 taskflows：

```bash
git clone https://github.com/GitHubSecurityLab/seclab-taskflow-agent
git clone https://github.com/GitHubSecurityLab/seclab-taskflows
cd seclab-taskflow-agent
```

2. 把本目录复制到框架仓库**根目录**，**目录名使用下划线 `ai_audit`**（模块路径不能用连字符）：

```bash
# 从本项目仓库复制到框架仓库根目录
cp -r <本项目>/ai-audit ai_audit
# 得到 ai_audit/alert_triage_example.yaml
#       ai_audit/personalities/python_auditer.yaml
```

> ⚠️ **为什么是根目录而不是 `examples/`？** 框架通过
> `importlib.resources.files(package)` 按 **Python 模块路径**加载 taskflow / personality / model_config，
> 而运行命令使用 `-t ai_audit.alert_triage_example` / `-m ai_audit.model_config` 引用**顶层模块
> `ai_audit`**。因此目录必须放到框架仓库根目录（该目录在 `sys.path` 上）使其可作为 `ai_audit`
> 导入；如果放进 `examples/`，会变成 `examples.ai_audit`，模块路径对不上，导致
> `No module named 'ai_audit'`。若坚持放 `examples/`，则所有引用需改为 `examples.ai_audit.*`。

3. 按官方配置指南配好 LLM 模型 + GitHub PAT + MCP Server。
   示例的 `alerts` 任务会通过 GitHub Code Scanning API 拉取**最新 CodeQL 告警**，
   因此需要导出 `GITHUB_TOKEN`（PAT，需含 `security_events` 读权限 + `repo/issues` 写权限，
   后者用于第 ⑤ 步创建真实 Issue）；如需指定其它仓库，可额外设置 `GITHUB_REPOSITORY=owner/repo`。

4. 运行（注意模块路径前缀 `ai_audit.`，并通过 `-m` 显式指定模型配置）：

```bash
# 方式 A：仅设环境变量（端点与密钥来自 AI_API_ENDPOINT / AI_API_TOKEN，模型用框架默认）
AI_API_ENDPOINT=https://api.deepseek.com/v1 \
AI_API_TOKEN=<你的APIKey> \
GITHUB_TOKEN=<你的PAT> \
hatch run main -t ai_audit.alert_triage_example

# 方式 B：显式指定 model_config（推荐，声明模型名 + api_type: chat_completions，更稳）
AI_API_ENDPOINT=https://api.deepseek.com/v1 \
AI_API_TOKEN=<你的APIKey> \
GITHUB_TOKEN=<你的PAT> \
hatch run main -t ai_audit.alert_triage_example \
    -m ai_audit.model_config
```

> `model_config.yaml` 是框架实际读取的模型配置文件（`-m` 参数指定模块路径，
> 框架自动追加 `.yaml` 后缀查找）。`endpoint`/`token` 由环境变量
> `AI_API_ENDPOINT`/`AI_API_TOKEN` 提供，密钥不会硬编码进仓库。
> 修改模型名 / 厂商时直接改该文件 `models:` 映射中的模型 ID 即可。
> `model_config.py` 仅为说明文档（含背景与配置思路），框架运行时不读取它。

> 定时运行（如 GitHub Actions `schedule` cron 或你的 CI 定时任务）直接执行上面这条命令，
> 即可在每次运行时消费仓库**当时最新**的 CodeQL 告警，无需手动维护告警列表。

#### 用 GitHub Actions 定时自动运行（推荐）

本仓库已内置 `.github/workflows/ai-audit-scheduled.yml`，可直接定时（或手动）运行 AI 审计：

- **自动触发**：默认监听 `codeql.yml`（name: "CodeQL"）的 `completed` 事件，
  在 CodeQL 扫完后确定性地运行，保证消费最新告警；同时保留 `workflow_dispatch` 手动触发。
- **手动触发**：在仓库 **Actions → AI 审计（CodeQL 完成后自动分流）→ Run workflow** 手动跑一次用于验证。

**所需 Secrets**（仓库 **Settings → Secrets and variables → Actions**）：

| Secret | 必填 | 用途 |
|--------|------|------|
| `AI_API_ENDPOINT` | ✅ | 上游 base_url（OpenAI 兼容口，如 `https://api.deepseek.com/v1`，或本地 vLLM / Ollama 的 OpenAI 兼容地址） |
| `AI_API_TOKEN` | ✅ | 对应厂商的 API Key（需支持函数调用） |
| `GH_PAT` | ✅ | GitHub PAT，需 `security_events` 读权限（读 CodeQL 告警） + `repo/issues` 写权限（创建真实 Issue） |
| `MCP_CONFIG` | 可选 | MCP Server（GitHub API）配置 |

> 📌 框架只识别 `AI_API_ENDPOINT` / `AI_API_TOKEN`（即 `AsyncOpenAI(base_url=..., api_key=...)`），
> 不读取 `OPENAI_API_KEY` / `OPENAI_MODEL`。模型名通过 `model_config.yaml`（`-m ai_audit.model_config`）显式声明，
> 并指定 `api_type: chat_completions`（OpenAI 兼容标准协议）。

> ⚠️ 由于示例会为真实漏洞**创建 Issue**，`GH_PAT` 必须具有仓库的 `issues` 写权限，
> 否则第 ⑤ 步会失败（可注释该步降级为只输出分流结果）。

> 首次使用建议先 `workflow_dispatch` 手动跑一次，确认链路正常后再依赖自动触发。

### 方式二：把 `ai_audit` 作为可导入包安装

如果你更希望像普通包一样使用，把 `ai-audit` 目录命名为 `ai_audit` 并安装进 Python 环境，
使其可通过 `ai_audit.personalities.python_auditer` 解析，然后把
`alert_triage_example.yaml` 中的 agents 引用改为
`ai_audit.personalities.python_auditer` 即可。

---

## 五、先在一个告警验证

先在一个 CodeQL 告警上跑通，验证链路后再铺开到全部告警：

1. 示例开头 `alerts` 任务已改为从 GitHub Code Scanning API 拉取**最新 CodeQL 告警**
   （`state=open&tool_name=CodeQL`），并映射成下游需要的
   `alert_number / rule / path / message` 结构，无需手动维护告警列表。
2. 观察 6 个阶段输出是否符合预期，重点看**校验阶段**是否把不完整的报告驳回。
3. 确认无误后开启第 ⑤ 步（若已在任务流中启用），即可对真实漏洞自动创建 Issue。

---

## 六、本示例的特点

- **针对 Python**：适配本仓库 `mzapi/**` 的 Python 代码审计场景。
- **6 阶段闭环**：信息收集 → 审计 → 报告 → 校验 → 创建真实 Issue → 知识回流。
- **防幻觉校验**：报告不完整/不一致直接驳回，避免 LLM 编造漏洞。
- **真实 Issue 创建**：仅对判定为真实漏洞的告警自动创建 GitHub Issue（标题带 `[AI审计]` 前缀，
  并打 `bug`/`security`/`ai-audit` 标签），自动去重避免重复创建。

---

> 📌 本示例由 CNB NPC CodeBuddy 为 `XMZZUZHI/MZAPI/python` 生成的测试用示例，
> 供你评估 AI 审计链路。请结合你的实际业务代码调整审计规则。

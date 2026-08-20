# AI 审计测试示例

本目录提供 **AI 审计（AI 漏洞分流）** 的测试用示例，用于在你的仓库上验证
`GitHub Security Lab Taskflow Agent` 框架的 AI 告警分流链路。

> ⚠️ **说明**：本示例为**测试/演示用途**，供你参考如何把文章
> 《借助 GitHub Security Lab Taskflow Agent 的 AI 支持漏洞分流》中的方法论落地到你自己的仓库。
> 正式投入使用前，请仔细审查并按照官方框架语法（GRAMMAR）调整。

---

## 一、这套 AI 审计在做什么

你的仓库已配置 `.github/workflows/codeql.yml`（CodeQL 静态扫描），它会扫出安全告警。
AI 审计的作用是：用 **LLM + Taskflow Agent** 对这批 CodeQL 告警做**自动分流**，
剔除误报（False Positive），对真实漏洞生成带精确文件/行号引用的报告。

```
CodeQL 扫出安全告警
     │
     ▼
LLM + Taskflow Agent 逐个审计
  ├─ ① 信息收集：调 GitHub API 拿触发事件/权限/上下文
  ├─ ② 审计：剔除误报（攻击者能否触发？是否特权上下文？）
  ├─ ③ 生成漏洞报告（带精确文件+行号引用）
  ├─ ④ 校验：报告不完整/不一致=幻觉，直接驳回
  └─ ⑤ 知识回流：人工驳回原因回流给 LLM，持续改进
```

本目录的 `alert_triage_example.yaml` 即对应上面的 5 阶段流程。

---

## 二、运行前提（需要你配置）

| 前提 | 说明 | 状态 |
|------|------|------|
| 仓库已开启 CodeQL 扫描 | `.github/workflows/codeql.yml` 已存在 | ✅ 已具备 |
| `seclab-taskflow-agent` 框架 | 需部署框架本体 | ❌ 需部署 |
| LLM 模型（支持函数调用） | 本示例固定为 `deepseek-v4-flash` | ⚠️ 需配置密钥 |
| GitHub PAT（读告警权限） | 框架读取 CodeQL 告警用 | ❌ 需你提供 |
| MCP Server（GitHub API） | 框架信息收集用 | ❌ 需配置 |

## 三、如何使用本示例

```bash
# 1. 部署框架
git clone https://github.com/GitHubSecurityLab/seclab-taskflow-agent
git clone https://github.com/GitHubSecurityLab/seclab-taskflows

# 2. 按官方配置指南配好 LLM 模型（本示例固定为 deepseek-v4-flash）+ GitHub PAT + MCP Server

# 3. 运行本示例（将本文件的 taskflow 交给框架执行）
#    具体命令请参照框架官方 README / GRAMMAR 文档

# 4. 先在一个 CodeQL 告警上跑通，验证链路后再铺开到全部告警
```

## 四、本示例的特点

- **针对 Python**：适配本仓库 `mzapi/**` 的 Python 代码审计场景。
- **5 阶段闭环**：信息收集 → 审计 → 报告 → 校验 → 知识回流，与官方方法论一致。
- **防幻觉校验**：报告不完整/不一致直接驳回，避免 LLM 编造漏洞。
- **测试安全**：示例中不实际创建 Issue，仅输出结果，方便你先安全验证。

---

> 📌 **模型固定说明**：本示例的 LLM 模型已固定为 `deepseek-v4-flash`，
> 请在框架的模型配置中填入对应的 API Key / Endpoint。
>
> 📌 本示例由 CNB NPC CodeBuddy 为 `XMZZUZHI/MZAPI/python` 生成的测试用示例，
> 供你评估 AI 审计链路。请结合你的实际业务代码调整审计规则。

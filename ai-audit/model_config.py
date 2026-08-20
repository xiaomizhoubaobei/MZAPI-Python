# =============================================================================
# OpenAI 兼容上游模型配置（model_config）— 参考文档
# =============================================================================
# ⚠️ 注意：框架的 -m 参数只读取 .yaml 文件（model_config.yaml），本 .py 文件
#         仅为配置说明与历史参考，框架运行时不读取它。实际配置请修改
#         同目录下的 model_config.yaml。
#
# 用途：为 AI 审计 taskflow（alert_triage_example.yaml）显式声明要使用的
#       模型与 API 类型，替代裸依赖框架默认值，保证链路稳定可复现。
#
# 背景：本框架底层基于 OpenAI Agents Python SDK，直接构造 AsyncOpenAI 客户端：
#       client = AsyncOpenAI(base_url=<endpoint>, api_key=<token>)
#       其中 endpoint 与 token 的来源有二：
#         1) 环境变量：AI_API_ENDPOINT / AI_API_TOKEN（或 COPILOT_TOKEN）
#         2) 本 model_config 文件里按模型显式指定 endpoint / token（token 指向某环境变量名）
#       对未知端点会兜底为通用 custom provider，因此任何实现了 OpenAI
#       /v1/chat/completions 协议的上游都能直接接入：
#         - 本地 vLLM / Ollama 的 OpenAI 兼容口
#         - DeepSeek / 通义千问(Qwen) / Moonshot 等国产厂商的 OpenAI 兼容接口
#
# 使用方式（在运行命令中通过 -m 指定本模块路径）：
#   hatch run main -t ai_audit.alert_triage_example \
#       -m ai_audit.model_config
#
# 前提：所选上游必须支持函数调用（tool calling），因为 AI 审计 taskflow
#       依赖工具调用；框架对自定义 provider 默认按"支持"乐观处理，
#       建议先在单个告警上跑通验证。
#
# 适配语言：Python
# 框架：GitHubSecurityLab/seclab-taskflow-agent
# =============================================================================

# 模型名：请按你的上游厂商调整。
#  - DeepSeek：      deepseek-v4-flash（固定使用该模型）
#  - 通义千问 Qwen： qwen-plus / qwen-max
#  - Moonshot：      moonshot-v1-8k / kimi-k2 等
#  - 本地 vLLM：     你部署的 model 名称
MODEL_NAME = "deepseek-v4-flash"

# API 类型：chat_completions 走 OpenAIChatCompletionsModel（OpenAI 兼容标准协议）
API_TYPE = "chat_completions"

# 端点环境变量名：运行时从该环境变量读取上游 base_url（如 https://api.deepseek.com/v1）
ENDPOINT_ENV = "AI_API_ENDPOINT"

# Token 环境变量名：运行时从该环境变量读取对应厂商的 API Key
TOKEN_ENV = "AI_API_TOKEN"


def get_model_config():
    """返回框架可识别的模型配置结构。

    端点（endpoint）与密钥（token）均以"环境变量名"形式声明，
    运行时由框架从进程环境读取并解析，避免把密钥硬编码进仓库。
    """
    return {
        "model": MODEL_NAME,
        "api_type": API_TYPE,
        "endpoint_env": ENDPOINT_ENV,
        "token_env": TOKEN_ENV,
    }

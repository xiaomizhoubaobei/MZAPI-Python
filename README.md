# MZAPI - 多云服务统一 API 接口库

MZAPI (Multi-cloud API) 是一个集成多家云服务商 API 的多云统一接口库，提供统一、简洁的 Python SDK，让开发者可以用一致的方式调用腾讯云、阿里云、华为云等不同服务商的 API。

## ✨ 特性

- 🌐 **多云统一**：一套接口，对接多家云服务商
- 📦 **轻量易用**：简洁的 API 设计，快速上手
- 🔐 **安全可靠**：完整的认证与签名机制
- ⚡ **异步支持**：同步/异步双模式
- 🛡️ **稳定健壮**：熔断、重试、预连接优化

## 📦 安装

```bash
pip install mzapi-multicloud-sdk
```

## 🚀 快速开始

### 腾讯云 OCR

```python
from mzapi.tencentcloud import GeneralBasicOCR

client = GeneralBasicOCR(
    secret_id="your_secret_id",
    secret_key="your_secret_key",
)
result = client.recognize(image_base64="base64_encoded_image")
```

### 阿里云 OCR

```python
from mzapi.aliyun.ocr import RecognizeAllText

client = RecognizeAllText(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    endpoint="ocr-api.cn-hangzhou.aliyuncs.com",
)
result = client.recognize(url="https://example.com/image.jpg")
```

## 📚 支持的云服务

| 云服务商 | 服务 | 说明 |
|---------|------|------|
| 腾讯云 | OCR | 通用印刷体识别 |
| 阿里云 | OCR | 识别全部文字 |
| 华为云 | OCR | 光学字符识别 |

## 🔧 开发指南

### 环境要求

- Python >= 3.10

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/xiaomizhoubaobei/MZAPI-Python.git
cd MZAPI-Python

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/
```

## 📄 许可证

本项目采用 [MPL-2.0](LICENSE) 许可证。

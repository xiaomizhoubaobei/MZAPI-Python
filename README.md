# MZAPI Python SDK

[![PyPI version](https://img.shields.io/pypi/v/mzapi-python.svg)](https://pypi.org/project/mzapi-python/)
[![Python Version](https://img.shields.io/pypi/pyversions/mzapi-python.svg)](https://pypi.org/project/mzapi-python/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/xiaomizhoubaobei/MZAPI-Python/blob/main/LICENSE)

MZAPI Python SDK 是一个用于访问和使用MZAPI服务的Python库。

## 安装

使用pip安装:

```bash
pip install mzapi-python
```

## 功能特性

目前支持的功能:

### 腾讯云OCR服务
- **GeneralBasicOCR**: 通用文字识别
  - 支持多种场景模板:
    - `General`: 通用场景
    - `OnlineTaxiItinerary`: 网约车行程单  
    - `RideHailingDriverLicense`: 网约车驾驶证
    - `RideHailingTransportLicense`: 网约车运输证
    - `WayBill`: 快递运单
    - `AccountOpeningPermit`: 银行开户许可证
    - `InvoiceEng`: 国际发票模板
    - `Coin`: 钱币识别模板
    - `OnboardingDocuments`: 入职材料识别
    - `PropertyOwnershipCertificate`: 房产证识别
    - `RealEstateCertificate`: 不动产权证识别
    - `HouseEncumbranceCertificate`: 他权证识别
    - `CarInsurance`: 车险保单
    - `MultiRealEstateCertificate`: 房产证、不动产证、产权证等材料合一模板
  - 支持图片和PDF识别
  - 自动验证输入参数和图片格式
  - 完善的错误处理机制

- 腾讯云图像识别服务 (TIIA)
  - GeneralBasicOCR: 通用文字识别(支持图片和PDF)
    - 支持多种场景模板(通用、网约车行程单、快递运单等)
    - 支持图片URL和Base64两种输入方式
    - 完善的日志记录(debug/info/warning/error)

## 快速开始
### 通用文字识别示例
```python
from mzapi.tencent.ocr import GeneralBasicOCR

# 初始化OCR客户端
ocr_client = GeneralBasicOCR(
    secret_id="您的腾讯云SecretId",
    secret_key="您的腾讯云SecretKey"
)

# 使用图片URL进行识别(通用场景)
result = ocr_client.recognize(
    image_url="https://example.com/document.jpg",
    config_id="General"  # 可选，默认为"General"
)
print(result)

# 使用特定场景模板(如网约车行程单)
result = ocr_client.recognize(
    image_url="https://example.com/taxi_receipt.jpg",
    config_id="OnlineTaxiItinerary"
)
print(result)
```
```

## 日志记录

GeneralBasicOCR内置了完善的日志系统，支持以下日志级别：
- DEBUG: 详细调试信息(如请求参数)
- INFO: 关键操作信息(如初始化完成)
- WARNING: 潜在问题警告(如参数验证失败)
- ERROR: 错误信息(如API调用失败)

示例配置日志级别：
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 要求

- Python >= 3.7
- 腾讯云账号及有效的SecretId/SecretKey

## 最佳实践

1. **性能优化**:
- 对于大文件，优先使用URL方式而非Base64
- 合理选择场景模板提高识别准确率
- 批量处理时添加适当延迟(建议1秒/次)

2.**安全建议**:
- 不要将SecretId/SecretKey硬编码在代码中
- 使用临时密钥(Token)进行生产环境调用

## 开发

### 安装开发依赖
```bash
pip install mzapi-python
```

## 文档

详细文档请访问: [https://docs.mizhoubaobei.top](https://docs.mizhoubaobei.top)

## 版本信息

当前版本: 0.0.2

## 作者

- 祁潇潇 (qixiaoxin@stu.sqxy.edu.cn)

## 许可证

GPL-V3 License

本项目采用 GNU 通用公共许可证第3版 (GPL-V3) 进行许可。这意味着：

- 您可以自由地使用、修改和分发本软件。
- 如果您分发修改后的版本，您必须以相同的许可证（GPL-V3）发布您的修改。
- 您必须公开您对本软件的修改。
- 您必须保留原始版权声明。

完整的许可证文本可在[此处](https://www.gnu.org/licenses/gpl-3.0.html)查看。

## 相关链接

- [GitHub 仓库](https://github.com/xiaomizhoubaobei/MZAPI-Python)
- [问题反馈](https://github.com/xiaomizhoubaobei/MZAPI-Python/issues)
- [PyPI 项目页面](https://pypi.org/project/mzapi-python)
- [下载页面](https://pypi.org/project/mzapi-python/#files)
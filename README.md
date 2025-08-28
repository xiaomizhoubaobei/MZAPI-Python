# MZAPI Python SDK

MZAPI的Python SDK，提供简单易用的API接口。

## 安装

```bash
pip install mzapi-python
```

## 使用方法

```python
from mzapi import MZAPI

# 初始化客户端
client = MZAPI()

# 使用API
# TODO: 添加具体的使用示例
```

## 开发

### 安装开发依赖

```bash
pip install -e .[dev]
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black .
```

## 发布

本项目使用GitHub Actions自动发布到PyPI。

### 自动发布

1. 创建一个新的GitHub Release
2. GitHub Actions会自动构建并发布到PyPI

### 手动发布

也可以通过GitHub Actions的"workflow_dispatch"手动触发发布。

## 配置说明

### PyPI Token设置

需要在GitHub仓库的Settings > Secrets and variables > Actions中添加以下密钥：

- `PYPI_API_TOKEN`: 你的PyPI API Token

### 获取PyPI API Token

1. 登录 [PyPI](https://pypi.org/)
2. 进入Account settings > API tokens
3. 创建新的API token
4. 将token添加到GitHub Secrets中

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
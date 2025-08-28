#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MZAPI Python SDK

A Python SDK for MZAPI services.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# 导入主要类和函数，使它们可以直接从mzapi包导入
from .client import MZAPIClient
from .exceptions import MZAPIError, MZAPIConnectionError, MZAPIAuthError
from .models import APIResponse

# 定义包的公共接口
__all__ = [
    "MZAPIClient",
    "MZAPIError", 
    "MZAPIConnectionError",
    "MZAPIAuthError",
    "APIResponse",
    "__version__",
]

# 包级别的配置
DEFAULT_TIMEOUT = 30
DEFAULT_BASE_URL = "https://api.mzapi.com"

def get_version():
    """获取SDK版本号"""
    return __version__

def create_client(api_key=None, base_url=None, timeout=None):
    """
    创建MZAPI客户端的便捷函数
    
    Args:
        api_key (str): API密钥
        base_url (str): API基础URL
        timeout (int): 请求超时时间（秒）
    
    Returns:
        MZAPIClient: 配置好的客户端实例
    """
    return MZAPIClient(
        api_key=api_key,
        base_url=base_url or DEFAULT_BASE_URL,
        timeout=timeout or DEFAULT_TIMEOUT
    )
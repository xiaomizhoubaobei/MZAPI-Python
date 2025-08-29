#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MZAPI Python SDK

一个MZAPI的python的SDK
"""

__version__ = "0.0.3"
__author__ = "祁潇潇"
__email__ = "qixiaoxin@stu.sqxy.edu.cn"

# 导入主要类和函数，使它们可以直接从mzapi包导入
# 定义包的公共接口

def get_version():
    """获取SDK版本号"""
    return __version__
def get_author():
    """获取SDK作者"""
    return __author__
def get_email():
    """获取SDK作者邮箱"""
    return __email__
from .tencent import *

__all__ = [GeneralBasicOCR]

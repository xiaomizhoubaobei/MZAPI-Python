#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MZAPI Python SDK

一个MZAPI的python的SDK
"""

__version__ = "0.0.2"
__author__ = "祁潇潇"
__email__ = "qixiaoxin@stu.sqxy.edu.cn"

# 导入主要类和函数，使它们可以直接从mzapi包导入
# 定义包的公共接口

def get_version():
    """获取SDK版本号"""
    return __version__
from .tencent import *

__all__ = ['DetectLabelPro']

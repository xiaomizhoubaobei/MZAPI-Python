# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION - DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0.
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-exceptions-2026-qxx"


"""
异常定义模块

定义 darabonba 运行时使用的各类异常，包括通用异常、响应异常、
参数校验异常、必填参数异常以及重试相关异常。
"""

from mzapi.utlis.aliyunauth.darabonba.policy.retry import RetryPolicyContext
from typing import Any, Optional


class DaraException(Exception):
    """darabonba 通用异常基类，从字典中解析错误码、消息与数据等字段。"""
    def __init__(self, dic):
        super().__init__(dic)
        self.code = dic.get("code")
        self.detail = dic.get("detail")
        self.message = dic.get("message")
        self.data = dic.get("data")
        self.description = dic.get("description")
        self.accessDeniedDetail = dic.get("accessDeniedDetail")
        if isinstance(dic.get("data"), dict) and dic.get("data").get("statusCode") is not None:
            self.statusCode = dic.get("data").get("statusCode")
        self.name = 'DaraException'

    def __str__(self):
        return f'Error: {self.code} {self.message} Response: {self.data}'

class ResponseException(DaraException):
    """响应异常，携带 HTTP 状态码、重试等待时间与堆栈信息。"""

    def __init__(self,
                 code: Optional[str] = None,
                 message: Optional[str] = None,
                 status_code: Optional[int] = None,
                 retry_after: Optional[int] = None,
                 data: Optional[dict] = None,
                 access_denied_detail: Optional[dict] = None,
                 description: Optional[str] = None,
                 detail: Optional[str] = None,
                 stack: Optional[str] = None):
        if data and status_code is not None:
            data['statusCode'] = status_code
        super().__init__({
            'code': code,
            'message': message,
            'data': data,
            'description': description,
            'detail': detail,
            'accessDeniedDetail': access_denied_detail
        })
        
        self.name = 'ResponseException'
        self.status_code = status_code
        self.retry_after = retry_after
        self.stack = stack

class ValidateException(Exception):
    """参数校验异常，用于字段格式或取值范围不合法时。"""


class RequiredArgumentException(Exception):
    """必填参数缺失异常，指明缺失的参数名。"""

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return f'"{self.arg}" is required.'


class RetryError(Exception):
    """可重试错误，用于网络等临时性故障场景。"""

    def __init__(self, message):
        
        super().__init__({"message":message})
        
        self.message = message
        self.data = None
        self.name = 'RetryError'

class UnretryableException(Exception):
    """不可重试异常，内部保留原始请求与上下文信息。"""

    def __init__(
            self,
            _context: RetryPolicyContext
    ):
        if isinstance(_context.exception, ResponseException):
            raise _context.exception

        self.inner_exception = _context.exception
        self.http_request = _context.http_request
        self.name = 'UnretryableException'
        super().__init__(str(self.inner_exception) if self.inner_exception else 'Unretryable exception')
        

    def __str__(self):
        return str(self.inner_exception)
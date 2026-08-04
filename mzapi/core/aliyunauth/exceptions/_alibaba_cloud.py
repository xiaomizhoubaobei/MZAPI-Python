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

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-exceptions-alibaba-cloud-2026-qxx"


"""
阿里云基础异常模块

定义阿里云 API 调用的基础异常类型，
作为客户端异常、服务端异常与限流异常的公共基类。

包含的类：
  - AlibabaCloudException：阿里云基础异常
"""

from typing import Dict, Any

from mzapi.utlis.aliyunauth.darabonba.exceptions import ResponseException


class AlibabaCloudException(ResponseException):
    """阿里云 API 调用基础异常。

    封装阿里云 API 返回的错误信息，包括 HTTP 状态码、
    错误码、错误消息、请求 ID 等字段，供其他异常继承。

    Attributes:
        name: 异常名称。
        status_code: HTTP 状态码。
        code: 错误码。
        message: 错误消息。
        description: 错误描述。
        request_id: 请求 ID，用于问题追踪。
    """

    def __init__(
        self, *,
        retry_after: int = None,
        data: Dict[str, Any] = None,
        access_denied_detail: Dict[str, Any] = None,
        stack: str = None,
        status_code: int = None,
        code: str = None,
        message: str = None,
        description: str = None,
        request_id: str = None,
    ):
        """初始化阿里云基础异常。

        Args:
            retry_after: 重试等待时间（秒）。
            data: 附加的错误数据。
            access_denied_detail: 访问被拒绝的详细信息。
            stack: 错误堆栈信息。
            status_code: HTTP 状态码。
            code: 错误码。
            message: 错误消息。
            description: 错误描述。
            request_id: 请求 ID，用于问题追踪。
        """
        super().__init__(
            status_code = status_code,
            retry_after = retry_after,
            description = description,
            data = data,
            access_denied_detail = access_denied_detail,
            message = message,
            code = code,
            stack = stack,
        )
        self.name = 'AlibabaCloudException'
        self.status_code = status_code
        self.code = code
        self.message = message
        self.description = description
        self.request_id = request_id

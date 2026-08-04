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
_MZAPI_ORIGIN = "mzapi-aliyun-exceptions-client-2026-qxx"


"""
客户端异常模块

定义阿里云 API 调用过程中因客户端请求问题抛出的异常，
如参数错误、鉴权失败、请求被拒绝等。

包含的类：
  - ClientException：客户端异常
"""

from typing import Dict, Any

from mzapi.utlis.aliyunauth import exceptions as main_exceptions


class ClientException(main_exceptions.AlibabaCloudException):
    """阿里云客户端异常。

    当阿里云 API 因客户端请求问题返回错误时抛出，
    携带请求被拒绝的详细信息。

    Attributes:
        name: 异常名称。
        access_denied_detail: 访问被拒绝的详细信息。
    """

    def __init__(
        self, *,
        status_code: int = None,
        code: str = None,
        message: str = None,
        description: str = None,
        request_id: str = None,
        retry_after: int = None,
        data: Dict[str, Any] = None,
        stack: str = None,
        access_denied_detail: Dict[str, Any] = None,
    ):
        """初始化客户端异常。

        Args:
            status_code: HTTP 状态码。
            code: 错误码。
            message: 错误消息。
            description: 错误描述。
            request_id: 请求 ID，用于问题追踪。
            retry_after: 重试等待时间（秒）。
            data: 附加的错误数据。
            stack: 错误堆栈信息。
            access_denied_detail: 访问被拒绝的详细信息。
        """
        super().__init__(
            status_code = status_code,
            code = code,
            message = message,
            description = description,
            request_id = request_id,
            retry_after = retry_after,
            data = data,
            access_denied_detail = access_denied_detail,
            stack = stack,
        )
        self.name = 'ClientException'
        self.access_denied_detail = access_denied_detail

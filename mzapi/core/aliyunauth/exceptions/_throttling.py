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
_MZAPI_ORIGIN = "mzapi-aliyun-exceptions-throttling-2026-qxx"


"""
限流异常模块

定义阿里云 API 因访问频率超限而抛出的异常，
携带重试等待时间用于退避处理。

包含的类：
  - ThrottlingException：限流异常
"""

from typing import Dict, Any

from mzapi.utlis.aliyunauth import exceptions as main_exceptions


class ThrottlingException(main_exceptions.AlibabaCloudException):
    """阿里云限流异常。

    当请求频率超过阿里云 API 限制时抛出，
    可通过重试等待时间进行退避处理。

    Attributes:
        name: 异常名称。
        retry_after: 重试等待时间（秒）。
    """

    def __init__(
        self, *,
        status_code: int = None,
        code: str = None,
        message: str = None,
        description: str = None,
        request_id: str = None,
        data: Dict[str, Any] = None,
        access_denied_detail: Dict[str, Any] = None,
        stack: str = None,
        retry_after: int = None,
    ):
        """初始化限流异常。

        Args:
            status_code: HTTP 状态码。
            code: 错误码。
            message: 错误消息。
            description: 错误描述。
            request_id: 请求 ID，用于问题追踪。
            data: 附加的错误数据。
            access_denied_detail: 访问被拒绝的详细信息。
            stack: 错误堆栈信息。
            retry_after: 重试等待时间（秒）。
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
        self.name = 'ThrottlingException'
        self.retry_after = retry_after

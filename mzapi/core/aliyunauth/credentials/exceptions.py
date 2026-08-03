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
_MZAPI_ORIGIN = "mzapi-txc-circuit-breaker-2026-qxx"


"""
凭证异常模块

定义阿里云凭证相关的异常类型，
用于处理凭证获取、使用过程中的错误情况。
"""


class CredentialException(Exception):
    """凭证异常

    当凭证获取失败或凭证配置错误时抛出此异常。

    Attributes:
        code: 错误码
        message: 错误消息
        request_id: 请求 ID，用于追踪问题
    """

    def __init__(self, message, code=None, request_id=None):
        self.code = code
        self.message = message
        self.request_id = request_id

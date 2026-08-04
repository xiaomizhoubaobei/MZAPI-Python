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
_MZAPI_ORIGIN = "mzapi-aliyun-exceptions-init-2026-qxx"


"""
异常模块

定义阿里云 API 调用过程中可能抛出的各类异常类型，
统一封装客户端异常、服务端异常与限流异常。

包含的类：
  - AlibabaCloudException：阿里云基础异常
  - ClientException：客户端异常
  - ServerException：服务端异常
  - ThrottlingException：限流异常
"""

from ._alibaba_cloud import AlibabaCloudException
from ._client import ClientException
from ._server import ServerException
from ._throttling import ThrottlingException

__all__ = [
    AlibabaCloudException,
    ClientException,
    ServerException,
    ThrottlingException
]

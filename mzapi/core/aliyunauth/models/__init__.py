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
# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.

"""
阿里云认证数据模型模块

定义阿里云认证场景所需数据模型的统一入口，
导出 SSE（Server-Sent Events，服务器推送事件）响应模型以及
通用请求参数、配置、全局参数与开放 API 请求等模型，供上层模块导入使用。
"""

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-models-init-2026-qxx"

from ..utils_models import Params, Config, GlobalParameters, OpenApiRequest
from ._sseresponse import SSEResponse

__all__ = [
    SSEResponse,
    Params,
    Config,
    GlobalParameters,
    OpenApiRequest
]

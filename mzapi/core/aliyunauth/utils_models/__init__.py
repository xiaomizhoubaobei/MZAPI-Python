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

"""阿里云认证 utils_models 包初始化模块

统一导出 utils_models 包内定义的数据模型类，供上层模块导入使用。

包含的类：
  - GlobalParameters：全局参数模型，承载附加请求头与查询参数。
  - Config：客户端初始化配置模型。
  - Params：API 请求参数模型。
  - OpenApiRequest：开放 API 请求模型。
"""

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-utils-models-init-2026-qxx"

from ._global_parameters import GlobalParameters
from ._config import Config
from ._params import Params
from ._open_api_request import OpenApiRequest

__all__ = [
    GlobalParameters,
    Config,
    Params,
    OpenApiRequest
]

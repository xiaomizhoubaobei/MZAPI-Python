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

"""开放 API 请求模型模块

定义开放 API 调用所需的请求模型 OpenApiRequest，
承载请求头、查询参数、请求体与二进制流等字段。

包含的类：
  - OpenApiRequest：开放 API 请求模型。
"""

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-utils-models-open-api-request-2026-qxx"

from darabonba.model import DaraModel
from typing import Dict, Any, BinaryIO


class OpenApiRequest(DaraModel):
    """开放 API 请求模型，表示一次开放 API 调用的请求参数集合。"""

    def __init__(
        self, 
        headers: Dict[str, str] = None,
        query: Dict[str, str] = None,
        body: Any = None,
        stream: BinaryIO = None,
        host_map: Dict[str, str] = None,
        endpoint_override: str = None,
    ):
        self.headers = headers
        self.query = query
        self.body = body
        self.stream = stream
        self.host_map = host_map
        self.endpoint_override = endpoint_override

    def validate(self):
        """校验字段（本模型无必需字段，无需额外校验）。"""
        pass

    def to_map(self):
        """将请求对象序列化为字典，值为空的字段将被跳过。"""
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.query is not None:
            result['query'] = self.query
        if self.body is not None:
            result['body'] = self.body
        if self.stream is not None:
            result['stream'] = self.stream
        if self.host_map is not None:
            result['hostMap'] = self.host_map
        if self.endpoint_override is not None:
            result['endpointOverride'] = self.endpoint_override
        return result

    def from_map(self, m: dict = None):
        """从字典反序列化请求对象。

        Args:
            m: 包含请求字段的字典。

        Returns:
            当前 OpenApiRequest 对象。
        """
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('query') is not None:
            self.query = m.get('query')
        if m.get('body') is not None:
            self.body = m.get('body')
        if m.get('stream') is not None:
            self.stream = m.get('stream')
        if m.get('hostMap') is not None:
            self.host_map = m.get('hostMap')
        if m.get('endpointOverride') is not None:
            self.endpoint_override = m.get('endpointOverride')
        return self


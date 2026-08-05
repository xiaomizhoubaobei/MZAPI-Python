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
SSE 响应数据模型模块

定义阿里云认证场景下的 SSE（Server-Sent Events，服务器推送事件）响应模型，
包含响应头、HTTP 状态码及事件对象等字段，
并提供字段校验与字典序列化/反序列化能力。
"""

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-models-sseresponse-2026-qxx"

from typing import Dict

from ..darabonba.event import Event as SSEEvent
from ..darabonba.model import DaraModel


class SSEResponse(DaraModel):
    """SSE 响应模型，表示一次服务器推送事件响应。

    用于承载流式推送过程中返回的响应头、HTTP 状态码及事件对象，
    是阿里云认证场景中解析 SSE 数据的统一载体。
    """
    def __init__(
        self, *,
        headers: Dict[str, str] = None,
        status_code: int = None,
        event: SSEEvent = None,
    ):
        self.headers = headers
        # HTTP Status Code
        self.status_code = status_code
        self.event = event

    def validate(self):
        """校验响应模型中的必需字段：headers、status_code、event。"""
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.event, 'event')

    def to_map(self):
        """将响应对象序列化为字典（值为空的字段将被跳过）。"""
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.headers is not None:
            result['headers'] = self.headers

        if self.status_code is not None:
            result['statusCode'] = self.status_code

        if self.event is not None:
            result['event'] = self.event.to_map()

        return result

    def from_map(self, m: dict = None):
        """从字典反序列化响应对象。

        Args:
            m: 包含响应字段的字典。

        Returns:
            当前 SSEResponse 对象。
        """
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')

        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')

        if m.get('event') is not None:
            temp_model = SSEEvent()
            self.event = temp_model.from_map(m.get('event'))

        return self

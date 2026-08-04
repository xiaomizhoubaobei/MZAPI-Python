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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-event-2026-qxx"


"""
事件数据模型模块

定义 SSE（Server-Sent Events）场景下的事件对象，包含事件标识、
事件类型、数据载荷与重试次数等字段。
"""

from mzapi.utlis.aliyunauth.darabonba.model import DaraModel


class Event(DaraModel):
    """事件模型，表示一条 SSE 事件消息。"""
    def __init__(
        self,
        id: str = None,
        event: str = None,
        data: str = None,
        retry: int = None,
    ):
        self.id = id
        self.event = event
        self.data = data
        self.retry = retry

    def validate(self):
        """校验必需字段：id、event、data、retry 均不可为空。"""
        self.validate_required(self.id, 'id')
        self.validate_required(self.event, 'event')
        self.validate_required(self.data, 'data')
        self.validate_required(self.retry, 'retry')

    def to_map(self):
        """将事件对象序列化为字典（跳过值为空的字段）。"""
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.event is not None:
            result['event'] = self.event
        if self.data is not None:
            result['data'] = self.data
        if self.retry is not None:
            result['retry'] = self.retry
        return result

    def from_map(self, m: dict = None):
        """从字典反序列化事件对象。

        Args:
            m: 包含事件字段的字典。

        Returns:
            当前 Event 对象。
        """
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('event') is not None:
            self.event = m.get('event')
        if m.get('data') is not None:
            self.data = m.get('data')
        if m.get('retry') is not None:
            self.retry = m.get('retry')
        return self
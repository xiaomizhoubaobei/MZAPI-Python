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

"""全局参数模型模块

定义阿里云 API 调用所需的全局参数模型 GlobalParameters，
承载附加的请求头与查询参数。

包含的类：
  - GlobalParameters：全局参数模型。
"""

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-utils-models-global-parameters-2026-qxx"

from darabonba.model import DaraModel
from typing import Dict


class GlobalParameters(DaraModel):
    """全局参数模型，表示附加到请求的全局请求头与查询参数。"""

    def __init__(
        self, 
        headers: Dict[str, str] = None,
        queries: Dict[str, str] = None,
    ):
        self.headers = headers
        self.queries = queries

    def validate(self):
        """校验字段（本模型无必需字段，无需额外校验）。"""
        pass

    def to_map(self):
        """将全局参数对象序列化为字典，值为空的字段将被跳过。"""
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.queries is not None:
            result['queries'] = self.queries
        return result

    def from_map(self, m: dict = None):
        """从字典反序列化全局参数对象。

        Args:
            m: 包含全局参数字段的字典。

        Returns:
            当前 GlobalParameters 对象。
        """
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('queries') is not None:
            self.queries = m.get('queries')
        return self


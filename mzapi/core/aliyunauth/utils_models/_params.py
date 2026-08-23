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

"""API 请求参数模型模块

定义阿里云 API 调用的请求参数模型 Params，
承载 Action、Version、Protocol 等请求元数据，
并提供必需字段校验与字典序列化/反序列化能力。

包含的类：
  - Params：API 请求参数模型。
"""

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-utils-models-params-2026-qxx"

from darabonba.model import DaraModel


class Params(DaraModel):
    """API 请求参数模型，描述一次 API 调用的请求元数据。"""

    def __init__(
        self,
        action: str = None,
        version: str = None,
        protocol: str = None,
        pathname: str = None,
        method: str = None,
        auth_type: str = None,
        body_type: str = None,
        req_body_type: str = None,
        style: str = None,
    ):
        self.action = action
        self.version = version
        self.protocol = protocol
        self.pathname = pathname
        self.method = method
        self.auth_type = auth_type
        self.body_type = body_type
        self.req_body_type = req_body_type
        self.style = style

    def validate(self):
        """校验请求参数中的必需字段，缺少必需字段时抛出异常。"""
        self.validate_required(self.action, 'action')
        self.validate_required(self.version, 'version')
        self.validate_required(self.protocol, 'protocol')
        self.validate_required(self.pathname, 'pathname')
        self.validate_required(self.method, 'method')
        self.validate_required(self.auth_type, 'auth_type')
        self.validate_required(self.body_type, 'body_type')
        self.validate_required(self.req_body_type, 'req_body_type')

    def to_map(self):
        """将请求参数对象序列化为字典，值为空的字段将被跳过。"""
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.action is not None:
            result['action'] = self.action
        if self.version is not None:
            result['version'] = self.version
        if self.protocol is not None:
            result['protocol'] = self.protocol
        if self.pathname is not None:
            result['pathname'] = self.pathname
        if self.method is not None:
            result['method'] = self.method
        if self.auth_type is not None:
            result['authType'] = self.auth_type
        if self.body_type is not None:
            result['bodyType'] = self.body_type
        if self.req_body_type is not None:
            result['reqBodyType'] = self.req_body_type
        if self.style is not None:
            result['style'] = self.style
        return result

    def from_map(self, m: dict = None):
        """从字典反序列化请求参数对象。

        Args:
            m: 包含请求参数字段的字典。

        Returns:
            当前 Params 对象。
        """
        m = m or dict()
        if m.get('action') is not None:
            self.action = m.get('action')
        if m.get('version') is not None:
            self.version = m.get('version')
        if m.get('protocol') is not None:
            self.protocol = m.get('protocol')
        if m.get('pathname') is not None:
            self.pathname = m.get('pathname')
        if m.get('method') is not None:
            self.method = m.get('method')
        if m.get('authType') is not None:
            self.auth_type = m.get('authType')
        if m.get('bodyType') is not None:
            self.body_type = m.get('bodyType')
        if m.get('reqBodyType') is not None:
            self.req_body_type = m.get('reqBodyType')
        if m.get('style') is not None:
            self.style = m.get('style')
        return self

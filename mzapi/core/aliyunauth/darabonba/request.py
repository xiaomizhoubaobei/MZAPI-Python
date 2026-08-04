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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-request-2026-qxx"


"""
HTTP 请求模型模块

定义 darabonba 风格的 HTTP 请求对象 DaraRequest，
包含 query、protocol、port、method、headers、pathname、body 等字段，
并支持属性赋值时自动回退为默认值。
"""


class DaraRequest:
    """darabonba HTTP 请求对象，维护请求的元数据与载荷。"""

    _PROPERTY_DEFAULT_MAP = {
        'query': {},
        'protocol': 'http',
        'port': 80,
        'method': 'GET',
        'headers': {},
        'pathname': "",
        'body': None,
    }

    def __init__(self):
        self.query = {}
        self.protocol = "http"
        self.port = 80
        self.method = "GET"
        self.headers = {}
        self.pathname = ""
        self.body = None

    def __setattr__(self, key, value):
        """属性赋值：当赋值为空时回退为该属性的默认值。"""
        if key in self._PROPERTY_DEFAULT_MAP:
            if not value:
                if isinstance(self._PROPERTY_DEFAULT_MAP[key], (list, dict)):
                    self.__dict__[key] = self._PROPERTY_DEFAULT_MAP[key].copy()
                else:
                    self.__dict__[key] = self._PROPERTY_DEFAULT_MAP[key]
                return
        self.__dict__[key] = value

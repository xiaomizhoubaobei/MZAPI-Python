# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-hwc-region-2026-qxx"

"""华为云区域对象

提供 Region 类，封装区域 ID 和端点列表。"""

import warnings
from typing import List


class Region:
    def __init__(self, *args, **kwargs):
        """
        有两种方式初始化区域对象。

        第一种方式，指定一个区域和一个端点：
        region1 = Region(id="region-id", endpoint="region-endpoint")

        第二种方式，指定一个区域和多个端点：
        region2 = Region("region-id", "endpoint1", "endpoint2")

        不建议混合使用两种初始化方式。
        如果混合使用，第一种方式优先于第二种方式。
        """
        self._id = None
        self._endpoints = None

        if len(args) > 1:
            self._id = args[0]
            self._endpoints = list(args[1:])

        if kwargs:
            if "id" in kwargs:
                self._id = kwargs.get("id")
            if "endpoint" in kwargs:
                self._endpoints = [kwargs.get("endpoint")]

        if not self._id:
            raise ValueError("id is required")
        if not self.endpoints:
            raise ValueError("at lease one endpoint is required")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, _id):
        self._id = _id

    @property
    def endpoint(self):
        warnings.warn("自 3.1.27 版本起，由于支持多端点功能，请使用 endpoints 代替",
                      DeprecationWarning)
        return self.endpoints[0] if self.endpoints else None

    @endpoint.setter
    def endpoint(self, endpoint):
        warnings.warn("自 3.1.27 版本起，由于支持多端点功能，请使用 endpoints 代替",
                      DeprecationWarning)
        self.endpoints = [endpoint]

    @property
    def endpoints(self):
        return self._endpoints

    @endpoints.setter
    def endpoints(self, endpoints):
        self._endpoints = endpoints

    def with_endpoint_override(self, *args: str):
        return self.with_endpoints_override(list(args))

    def with_endpoints_override(self, endpoints: List[str]):
        self.endpoints = endpoints
        return self

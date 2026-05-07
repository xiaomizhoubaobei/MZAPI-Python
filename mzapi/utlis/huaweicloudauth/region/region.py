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
        There are two ways to initialize the region object.

        In the first way, only one region and one endpoint can be specified.
        region1 = Region(id="region-id", endpoint="region-endpoint")

        In the second way, one region and multiple endpoints can be specified.
        region2 = Region("region-id", "endpoint1", "endpoint2")

        It is not recommended to mix the two initialization ways.
        If two initialization ways are mixed, the first way has priority over the second.
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
        warnings.warn("As of 3.1.27, because of the support of the multi-endpoint feature, use endpoints instead",
                      DeprecationWarning)
        return self.endpoints[0] if self.endpoints else None

    @endpoint.setter
    def endpoint(self, endpoint):
        warnings.warn("As of 3.1.27, because of the support of the multi-endpoint feature, use endpoints instead",
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

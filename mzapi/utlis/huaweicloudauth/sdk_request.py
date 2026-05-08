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
_MZAPI_ORIGIN = "mzapi-hwc-sdk-request-2026-qxx"

"""华为云 SDK 请求对象

封装 HTTP 请求的方法、路径、参数、请求体等信息。
"""

from typing import List, Tuple, Dict, Any

from huaweicloudsdkcore.signer.algorithm import SigningAlgorithm


class SdkRequest:
    def __init__(self,
                 method: str = 'GET',
                 schema: str = None,
                 host: str = None,
                 resource_path: str = None,
                 uri: str = None,
                 query_params: List[Tuple[str, object]] = None,
                 header_params: Dict[str, str] = None,
                 body: Any = None,
                 stream: bool = False,
                 signing_algorithm: SigningAlgorithm = SigningAlgorithm.get_default()):
        self._method = method
        self._schema = schema
        self._host = host
        self._resource_path = resource_path
        self._uri = uri
        self._query_params = query_params
        self._header_params = header_params
        self._body = body
        self._stream = stream
        self._signing_algorithm = signing_algorithm

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def resource_path(self):
        return self._resource_path

    @resource_path.setter
    def resource_path(self, resource_path):
        self._resource_path = resource_path

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        self._uri = uri

    @property
    def query_params(self):
        return self._query_params

    @query_params.setter
    def query_params(self, query_params: List[Tuple[str, object]]):
        self._query_params = query_params

    @property
    def header_params(self):
        return self._header_params

    @header_params.setter
    def header_params(self, header_params):
        self._header_params = header_params

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        self._body = body

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, stream):
        self._stream = stream

    @property
    def signing_algorithm(self):
        return self._signing_algorithm

    @signing_algorithm.setter
    def signing_algorithm(self, signing_algorithm):
        self._signing_algorithm = signing_algorithm

    @property
    def url(self):
        return "%s://%s%s" % (self.schema, self.host, self.uri)

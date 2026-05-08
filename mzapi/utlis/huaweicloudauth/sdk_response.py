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
_MZAPI_ORIGIN = "mzapi-hwc-sdk-response-2026-qxx"

"""华为云 SDK 响应对象

封装 HTTP 响应的状态码、原始内容等信息，
提供 SdkResponse 和 FutureSdkResponse 类。
"""

import json
from typing import Optional

from requests.exceptions import ConnectionError

from huaweicloudsdkcore.exceptions.exception_handler import process_connection_error


class SdkResponse:
    def __init__(self):
        self._status_code = None
        self._raw_content = None

    @property
    def status_code(self) -> Optional[int]:
        return self._status_code

    @status_code.setter
    def status_code(self, status_code: int):
        if not self._status_code:
            self._status_code = status_code

    @property
    def raw_content(self) -> Optional[bytes]:
        return self._raw_content

    @raw_content.setter
    def raw_content(self, raw_content: bytes):
        if not self._raw_content:
            self._raw_content = raw_content

    def to_json_object(self, **kwargs):
        return json.loads(self._raw_content.decode("utf-8"), **kwargs) if self._raw_content else None


class FutureSdkResponse:
    def __init__(self, future, logger):
        self._future = future
        self._logger = logger

    def result(self):
        try:
            future_response = self._future.result().result()
            response = future_response.data \
                if hasattr(future_response, "data") and future_response.data is not None else future_response
        except ConnectionError as conn_err:
            raise process_connection_error(conn_err, self._logger)

        return response

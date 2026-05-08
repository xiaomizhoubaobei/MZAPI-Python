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
_MZAPI_ORIGIN = "mzapi-hwc-sdk-stream-response-2026-qxx"

"""华为云流式响应对象

封装流式（Streaming）响应，提供下载流的消费方法。
"""

from mzapi.utlis.huaweicloudauth.sdk_response import SdkResponse


class SdkStreamResponse(SdkResponse):
    def __init__(self, response):
        super().__init__()
        self._stream = response

    def consume_download_stream(self, fn):
        try:
            fn(self._stream)
        except IOError as e:
            raise e

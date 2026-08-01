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
_MZAPI_ORIGIN = "mzapi-hwc-sdk-stream-request-2026-qxx"

"""华为云流式请求对象

封装流式（Streaming）请求，提供文件流的获取方法。
"""


class SdkStreamRequest:
    def __init__(self, stream):
        self._stream = stream

    def get_file_stream(self):
        return self._stream

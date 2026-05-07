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
_MZAPI_ORIGIN = "mzapi-hwc-http-handler-2026-qxx"

"""华为云 HTTP 处理器

提供 HttpHandler 类，处理请求和响应的拦截与日志记录。"""

def default_request_handler(**kwargs):
    pass


def default_response_handler(**kwargs):
    _response = kwargs.get("response")

    content_type = _response.headers.get("Content-Type")
    content_length = _response.headers.get("Content-Length")
    if content_type and content_type.endswith("octet-stream"):
        content_length = content_length or -1
    else:
        content_length = content_length or len(_response.content)

    kwargs.get("logger").info("\"{} {}\" {} {} {} {}".format(
        _response.request.method,
        _response.request.url, _response.status_code, content_length,
        _response.elapsed, _response.headers.get("X-Request-Id", ""))
    )


class HttpHandler:
    def __init__(self):
        self._request_handlers = [default_request_handler]
        self._response_handlers = [default_response_handler]

    def add_request_handler(self, fun):
        self._request_handlers.append(fun)
        return self

    def add_response_handler(self, fun):
        self._response_handlers.append(fun)
        return self

    def process_request(self, **kwargs):
        for handler in self._request_handlers:
            handler(**kwargs)

    def process_response(self, **kwargs):
        for handler in self._response_handlers:
            handler(**kwargs)

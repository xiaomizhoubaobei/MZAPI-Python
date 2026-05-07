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
_MZAPI_ORIGIN = "mzapi-txc-http-request-async-2026-qxx"



"""
腾讯云异步 HTTP 请求模块

实现基于 httpx 库的异步 HTTP 通信功能。

主要组件：
  - ApiRequest：别名为 httpx.Request
  - ApiResponse：别名为 httpx.Response
  - RequestPrettyFormatter：请求格式化器
  - ResponsePrettyFormatter：响应格式化器
"""

import httpx

__all__ = ["ApiRequest", "ApiResponse", "RequestPrettyFormatter", "ResponsePrettyFormatter"]

ApiRequest = httpx.Request
ApiResponse = httpx.Response


class RequestPrettyFormatter(object):
    def __init__(self, req: ApiRequest, format_body=True, delimiter="\n"):
        self._req = req
        self._format_body = format_body
        self._delimiter = delimiter

    def __str__(self):
        lines = ["%s %s" % (self._req.method, self._req.url)]
        for k, v in self._req.headers.items():
            lines.append("%s: %s" % (k, v))
        lines.append("")
        if self._format_body:
            try:
                lines.append(self._req.content.decode("utf-8"))
            except UnicodeDecodeError:
                # binary body
                import base64
                lines.append("base64_body:" + base64.standard_b64encode(self._req.content).decode())
        return self._delimiter.join(lines)


class ResponsePrettyFormatter(object):
    def __init__(self, resp: ApiResponse, format_body=True, delimiter="\n"):
        self._resp = resp
        self._format_body = format_body
        self._delimiter = delimiter

    def __str__(self):
        lines = ['%s %d %s' % (self.str_ver(self._resp.http_version), self._resp.status_code, self._resp.reason_phrase)]
        for k, v in self._resp.headers.items():
            lines.append('%s: %s' % (k, v))
        return self._delimiter.join(lines)

    async def astr(self):
        lines = ['%s %d %s' % (self.str_ver(self._resp.http_version), self._resp.status_code, self._resp.reason_phrase)]
        for k, v in self._resp.headers.items():
            lines.append('%s: %s' % (k, v))
        if self._format_body:
            lines.append('')
            lines.append((await self._resp.aread()).decode("utf-8"))
        return self._delimiter.join(lines)

    @staticmethod
    def str_ver(ver):
        if ver == 10:
            return "HTTP/1.0"
        elif ver == 11:
            return "HTTP/1.1"
        elif ver == 20:
            return "HTTP/2.0"
        else:
            return str(ver)

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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-url-2026-qxx"


"""
URL 工具模块

提供 URL 的解析、各组成部分访问（路径、协议、主机、端口、查询等）
以及编码（url_encode、percent_encode、path_encode）能力。
"""

import re
from urllib.parse import urlparse, urlunparse, quote

PORT_MAP = {
    "ftp": "21",
    "gopher": "70",
    "http": "80",
    "https": "443",
    "ws": "80",
    "wss": "443"
}


class Url:
    """URL 对象，基于 urlparse 封装，提供 URL 各组成部分的便捷访问。"""

    def __init__(self, url_str):
        self._url = urlparse(url_str)

    @staticmethod
    def new_url(url_str):
        """根据 URL 字符串创建 Url 对象。

        Args:
            url_str: URL 字符串。

        Returns:
            Url 对象。
        """
        try:
            return Url(url_str)
        except Exception as e:
            raise e

    def path(self):
        """返回 URL 的路径（含查询字符串）。"""
        if not self._url.query:
            return self._url.path
        return f"{self._url.path}?{self._url.query}"

    def pathname(self):
        """返回 URL 的路径（不含查询字符串）。"""
        return self._url.path

    def protocol(self):
        """返回 URL 的协议（scheme）。"""
        return self._url.scheme

    def hostname(self):
        """返回 URL 的主机名。"""
        return self._url.hostname

    def host(self):
        """返回 URL 的主机名与端口（若存在）。"""
        if self._url.port:
            return f"{self._url.hostname}:{self._url.port}"
        return self._url.hostname

    def port(self):
        """返回 URL 的端口，未显式指定时返回协议默认端口。"""
        if self._url.port:
            return str(self._url.port)
        return PORT_MAP.get(self.protocol(), "")

    def hash(self):
        """返回 URL 的锚点（fragment）。"""
        return self._url.fragment

    def search(self):
        """返回 URL 的查询字符串。"""
        return self._url.query

    def href(self):
        """返回完整还原的 URL 字符串。"""
        return urlunparse(self._url)

    def auth(self):
        """返回 URL 的用户名与密码认证信息（user:pass）。"""
        if self._url.username or self._url.password:
            return f"{self._url.username}:{self._url.password or ''}"
        return ""

    @staticmethod
    def parse(url_str):
        """解析 URL 字符串并返回 Url 对象。"""
        return Url.new_url(url_str)

    @staticmethod
    def url_encode(url_str):
        """对 URL 字符串进行逐段百分号编码。

        Args:
            url_str: 待编码的 URL 字符串。

        Returns:
            编码后的字符串；空输入返回空串。
        """
        if not url_str:
            return ""
        parts = url_str.split('/')
        encoded_parts = [quote(part, safe='') for part in parts]
        encoded_url = '/'.join(encoded_parts)
        encoded_url = encoded_url.replace("+", "%20").replace("*", "%2A").replace("%7E", "~")
        return encoded_url

    @staticmethod
    def percent_encode(uri):
        """对 URI 进行百分号编码。

        Args:
            uri: 待编码的 URI 字符串。

        Returns:
            编码后的字符串；空输入返回空串。
        """
        if not uri:
            return ""
        encoded_uri = quote(uri, safe='')
        encoded_uri = encoded_uri.replace("+", "%20").replace("*", "%2A").replace("%7E", "~")
        return encoded_uri

    @staticmethod
    def path_encode(path):
        """对 URL 路径进行逐段百分号编码（保留根路径）。

        Args:
            path: 待编码的路径字符串。

        Returns:
            编码后的路径；空或根路径返回原值。
        """
        if not path or path == "/":
            return path
        parts = path.split('/')
        encoded_parts = [quote(part, safe='') for part in parts]
        encoded_path = '/'.join(encoded_parts)
        encoded_path = encoded_path.replace("+", "%20").replace("*", "%2A").replace("%7E", "~")
        return encoded_path

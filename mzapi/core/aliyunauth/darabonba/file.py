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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-file-2026-qxx"


"""
文件操作工具模块

提供文件存在性判断、长度获取、创建/修改时间查询、读写与流式读写等能力。
"""

import os
from datetime import datetime
from mzapi.utlis.aliyunauth.darabonba.date import Date


class File:
    """文件对象，封装对指定路径文件的基础操作。"""

    def __init__(self, path: str):
        self._path = path
        self._file = None

    @staticmethod
    def exists(path: str) -> bool:
        """判断指定路径的文件是否存在。

        Args:
            path: 文件路径。

        Returns:
            存在返回 True，否则返回 False。
        """
        return os.path.exists(path)

    def path(self) -> str:
        """返回文件路径。"""
        return self._path

    def length(self) -> int:
        """返回文件大小（字节数）。"""
        return os.path.getsize(self._path)

    def create_time(self) -> Date:
        """返回文件创建时间。

        Returns:
            以 Date 对象表示的创建时间。
        """
        ctime = os.path.getctime(self._path)
        return Date(datetime.fromtimestamp(ctime).isoformat())

    def modify_time(self) -> Date:
        """返回文件最后修改时间。

        Returns:
            以 Date 对象表示的修改时间。
        """
        mtime = os.path.getmtime(self._path)
        return Date(datetime.fromtimestamp(mtime).isoformat())

    def read(self, size: int) -> bytes:
        """从文件读取指定大小的字节数据，读完后自动关闭文件句柄。

        Args:
            size: 读取的字节数。

        Returns:
            读取到的字节数据；读到文件末尾时返回空字节串。
        """
        if self._file is None:
            self._file = open(self._path, 'rb')

        data = self._file.read(size)
        if not data:
            self._file.close()
            self._file = None
        return data

    def write(self, data: bytes) -> None:
        """以追加模式向文件写入字节数据。

        Args:
            data: 待写入的字节数据。
        """
        with open(self._path, 'ab') as f:
            f.write(data)

    @staticmethod
    def create_read_stream(path: str):
        """创建一个文件读流（二进制只读模式）。"""
        return open(path, 'rb')

    @staticmethod
    def create_write_stream(path: str):
        """创建一个文件写流（二进制追加模式）。"""
        return open(path, 'ab')
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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-bytes-2026-qxx"


"""
字节工具模块

提供字节数据在多种编码（base64、hex、utf-8/16/32、binary）之间转换的能力。

包含的类：
  - Bytes：字节转换工具类，根据指定编码将字符串或字节数据转换为字节对象
"""

import base64
from typing import Union


class Bytes:
    """字节转换工具类，支持多种编码格式之间的转换。"""

    @staticmethod
    def from_(data: Union[str, bytes], encoding: str) -> bytes:
        """根据指定编码将输入数据转换为字节对象。

        Args:
            data: 待转换的数据，可以是字符串或字节对象。
            encoding: 编码方式，支持 base64、hex、utf-8、utf-16、utf-32、binary。

        Returns:
            转换后的字节对象。

        Raises:
            ValueError: 当编码方式不受支持时抛出。
        """
        if encoding == 'base64':
            if isinstance(data, str):
                data = data.encode('utf-8')
            return base64.b64decode(data)
        elif encoding == 'hex':
            if isinstance(data, str):
                return bytes.fromhex(data)
        elif encoding == 'utf-8':
            if isinstance(data, bytes):
                return data
            if isinstance(data, str):
                return data.encode('utf-8')
        elif encoding == 'utf-16':
            if isinstance(data, bytes):
                return data.decode('utf-16').encode('utf-16')
        elif encoding == 'utf-32':
            if isinstance(data, bytes):
                return data.decode('utf-32').encode('utf-32')
        elif encoding == 'binary':
            if isinstance(data, str):
                return bytes(int(data[i:i+8], 2) for i in range(0, len(data), 8))

        raise ValueError(f"Unsupported encoding: {encoding}")

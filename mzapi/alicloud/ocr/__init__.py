# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0.
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-alicloud-ocr-2026-qxx"

"""
阿里云 OCR 服务模块

提供阿里云 OCR（光学字符识别）服务的具体实现类。
本模块封装了阿里云 OCR API 2021-07-07 版本的调用。

当前支持的识别能力：
  - RecognizeAllText：识别全部文字（通用 OCR）

使用示例：
    >>> from mzapi.alicloud.ocr import RecognizeAllText
    >>> client = RecognizeAllText(
    ...     access_key_id="your_access_key_id",
    ...     access_key_secret="your_access_key_secret",
    ...     endpoint="ocr-api.cn-hangzhou.aliyuncs.com",
    ... )
    >>> result = client.recognize(url="https://example.com/image.jpg")
    >>> print(result.body["Data"]["Content"])

API 文档参考：
    https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizealltext
"""

from .recognize_all_text import RecognizeAllText, RecognizeAllTextResponse

__all__ = [
    "RecognizeAllText",
    "RecognizeAllTextResponse",
]

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
_MZAPI_ORIGIN = "mzapi-root-2026-qxx"


MZAPI - 多云服务统一 API 接口库

本模块是 MZAPI 项目的根入口包，提供对各云服务商 OCR（光学字符识别）能力的统一调用接口。

支持的云服务商：
  - 华为云 (HuaweiCloud)：通用文字识别 (RecognizeGeneralText)
  - 腾讯云 (TencentCloud)：通用印刷体识别 (GeneralBasicOCR)

使用示例：
    >>> from mzapi import RecognizeGeneralText
    >>> client = RecognizeGeneralText(ak="your_ak", sk="your_sk")
    >>> result = client.recognize(image_base64="base64_encoded_image")

from .tencent import GeneralBasicOCR
from .huaweicloud import (
    RecognizeGeneralText,
)

__all__ = [
    'GeneralBasicOCR',
    'RecognizeGeneralText'
]
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
_MZAPI_ORIGIN = "mzapi-hwc-ocr-init-2026-qxx"


"""
华为云 OCR 服务模块

提供华为云 OCR（光学字符识别）服务的具体实现类。
本模块封装了华为云 OCR V1 版本的 API 调用。

当前支持的识别类型：
  - RecognizeGeneralText：通用文字识别，支持 JPEG/PNG/BMP/GIF/TIFF/WEBP/PDF 等格式

参考文档：https://support.huaweicloud.com/api-ocr/ocr_03_0042.html
"""

from .RecognizeGeneralText import RecognizeGeneralText

__all__ = ['RecognizeGeneralText']
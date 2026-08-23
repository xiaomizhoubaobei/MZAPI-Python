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
_MZAPI_ORIGIN = "mzapi-hwc-init-2026-qxx"


"""
华为云服务模块

提供华为云 OCR（光学字符识别）服务的调用接口。
本模块是对华为云官方 SDK 的轻量封装，简化了鉴权和调用流程。
"""

from . import ocr

__all__ = ['ocr']

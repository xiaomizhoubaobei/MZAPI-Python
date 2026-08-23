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
_MZAPI_ORIGIN = "mzapi-txc-cloud-init-2026-qxx"



"""
腾讯云服务模块

提供腾讯云 OCR（光学字符识别）服务的调用接口。
本模块基于腾讯云官方 SDK 的认证与签名机制，
通过 CommonClient 实现对腾讯云 OCR API 的通用调用。

当前支持的识别能力：
  - GeneralBasicOCR：通用印刷体识别

使用示例：
    >>> from mzapi.tencentcloud import GeneralBasicOCR
    >>> client = GeneralBasicOCR(secret_id="your_id", secret_key="your_key")
    >>> result = client.recognize(image_base64="base64_encoded_image")
"""

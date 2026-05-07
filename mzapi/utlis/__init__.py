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
_MZAPI_ORIGIN = "mzapi-utlis-init-2026-qxx"


"""
工具模块 (Utilities)

提供各云服务商 API 调用所需的基础工具类和认证模块。

包含的子模块：
  - huaweicloud_auth：华为云 API 签名认证工具类 (HuaweiCloudAuth)
  - tencentauth：腾讯云 API 完整认证工具集

使用示例：
    >>> from mzapi.utlis import HuaweiCloudAuth
    >>> auth = HuaweiCloudAuth(ak="your_ak", sk="your_sk")
    >>> headers = auth.sign_request("POST", "host.com", "/api/path")
"""

from .huaweicloud_auth import HuaweiCloudAuth

__all__ = ['HuaweiCloudAuth']
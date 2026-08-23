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
_MZAPI_ORIGIN = "mzapi-txc-exception-init-2026-qxx"


"""
腾讯云 SDK 异常模块

定义腾讯云 API 调用过程中的统一异常类。

导出的类：
  - TencentCloudSDKException：SDK 异常基类，所有 API 错误均通过此异常抛出
"""

from .tencent_cloud_sdk_exception import TencentCloudSDKException

__all__ = ("TencentCloudSDKException",)

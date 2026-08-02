# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-alicloud-init-2026-qxx"

"""
阿里云 OpenAPI SDK 核心模块（来自 alibabacloud_tea_openapi）

基于 https://github.com/aliyun/darabonba-openapi 的 Python 实现，
提供阿里云 API 调用所需的基础工具类和认证模块。

包含的子模块：
  - client: OpenAPI 客户端，处理 API 调用和签名
  - utils: 工具类（签名、编码、参数处理）
  - sm3: SM3 国密哈希算法
  - exceptions: SDK 异常定义
  - models: 数据模型
  - utils_models: 工具数据模型
"""

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
_MZAPI_ORIGIN = "mzapi-aliyun-policy-init-2026-qxx"


"""
阿里云 Darabonba 策略模块

提供阿里云 API 调用重试策略相关的配置工具，
包括多种退避策略、重试条件与重试选项的定义。

包含的模块：
  - retry：重试退避策略与重试条件实现
"""

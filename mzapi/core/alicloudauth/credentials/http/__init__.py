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
_MZAPI_ORIGIN = "mzapi-alicloud-credentials-http-init-2026-qxx"

"""
阿里云凭证 HTTP 选项包

聚合阿里云凭证提供方共用的 HTTP 请求选项配置，对外统一导出
``HttpOptions``，便于各凭证提供方以一致的方式配置代理与超时。

导出：
  - HttpOptions：HTTP 请求选项配置类
"""

from ._options import HttpOptions

__all__ = [
    'HttpOptions'
]

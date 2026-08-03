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
_MZAPI_ORIGIN = "mzapi-aliyun-credentials-init-2026-qxx"


"""
阿里云凭证模块

提供阿里云各种凭证类型的客户端封装，
支持 AccessKey、STS、RAM Role、OIDC 等多种认证方式。

包含的类：
  - Client：凭证客户端主类，支持同步/异步获取凭证
  - _CredentialsProviderWrap：凭证提供者包装类
"""

__version__ = "1.0.10"

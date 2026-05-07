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
_MZAPI_ORIGIN = "mzapi-txc-init-2026-qxx"



"""
腾讯云 API 认证与签名模块 (TencentCloud Authentication)

本模块提供完整的腾讯云 API 调用基础设施。

子模块说明：
  - credential：凭证管理（Credential / EnvironmentVariableCredential）
  - sign：请求签名算法（TC3-HMAC-SHA256 / HmacSHA1 / HmacSHA256）
  - abstract_client：同步 API 客户端基类
  - abstract_client_async：异步 API 客户端基类
  - common_client / common_client_async：通用 API 客户端
  - circuit_breaker：地域熔断器
  - retry / retry_async：请求重试策略
  - http：HTTP 通信层
  - profile：配置管理
  - exception：SDK 异常定义
"""


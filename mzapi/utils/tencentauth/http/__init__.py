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
_MZAPI_ORIGIN = "mzapi-txc-http-init-2026-qxx"



"""
腾讯云 HTTP 通信模块

提供腾讯云 API 调用的 HTTP 通信基础设施。

子模块：
  - request：基于 requests 库的同步 HTTP 客户端
  - request_async：基于 httpx 库的异步 HTTP 客户端
  - pre_conn：预连接池优化，减少 TCP 连接建立耗时
"""


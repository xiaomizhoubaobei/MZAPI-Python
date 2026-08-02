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
_MZAPI_ORIGIN = "mzapi-alicloud-credentials-http-options-2026-qxx"

"""
HTTP 选项配置模块

为阿里云凭证提供方（Credentials Provider）提供统一的 HTTP 请求配置项，
用于控制凭证获取过程中的代理、连接超时与读取超时等行为。

包含的类：
  - HttpOptions：HTTP 请求选项配置类
"""


class HttpOptions:
    """HTTP 请求选项配置类。

    封装阿里云凭证提供方在拉取凭证时所需的 HTTP 请求参数，
    通过关键字参数注入，未指定的项保持 ``None`` 以使用调用方默认值。

    典型用法::

        options = HttpOptions(proxy='http://127.0.0.1:8080',
                              connect_timeout=5,
                              read_timeout=10)

    属性说明：
      - proxy: HTTP/HTTPS 代理地址，为 ``None`` 时不使用代理
      - connect_timeout: 建立 TCP 连接的超时时间（秒）
      - read_timeout: 读取响应数据的超时时间（秒）
    """

    def __init__(self,
                 *,
                 proxy: str = None,
                 connect_timeout: int = None,
                 read_timeout: int = None):
        """初始化 HTTP 请求选项。

        所有参数均为关键字参数，按需传入，未提供者保持 ``None``，
        由具体凭证提供方在发起请求时回退到其默认配置。

        Args:
            proxy: 代理服务器地址，例如 ``http://127.0.0.1:8080``；
                为 ``None`` 时不使用代理。
            connect_timeout: 建立 TCP 连接的超时时间（秒）；
                为 ``None`` 时使用默认连接超时。
            read_timeout: 读取响应数据的超时时间（秒）；
                为 ``None`` 时使用默认读取超时。
        """
        self.proxy = proxy
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

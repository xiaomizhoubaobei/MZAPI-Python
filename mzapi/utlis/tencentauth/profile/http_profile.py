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

"""
腾讯云 HTTP Profile 配置

基于腾讯云官方 SDK (tencentcloud-sdk-python) 的 HttpProfile 实现。
"""

from ..exception.tencent_cloud_sdk_exception import TencentCloudSDKException


class HttpProfile(object):
    """HTTP 请求配置

    :param protocol: 请求协议，http 或 https，默认 https
    :type protocol: str
    :param endpoint: API 域名，如 cvm.tencentcloudapi.com
    :type endpoint: str
    :param reqMethod: HTTP 方法，可选值：GET, POST，默认 POST
    :type reqMethod: str
    :param reqTimeout: 请求超时时间（秒），默认 60
    :type reqTimeout: int
    :param keepAlive: 是否开启 Keep-Alive
    :type keepAlive: bool
    :param proxy: 自定义代理服务器，格式：http(s)://{user}:{password}@{ip}:{port}
    :type proxy: str
    :param rootDomain: 根域名，默认 tencentcloudapi.com
    :type rootDomain: str
    :param certification: 自定义证书路径或禁用证书验证
    :type certification: str or bool
    """

    scheme = "https"

    def __init__(
        self,
        protocol=None,
        endpoint=None,
        reqMethod="POST",
        reqTimeout=60,
        keepAlive=False,
        proxy=None,
        rootDomain=None,
        certification=None,
    ):
        self.endpoint = endpoint
        self.reqTimeout = 60 if reqTimeout is None else reqTimeout
        self.reqMethod = "POST" if reqMethod is None else reqMethod
        self.protocol = protocol or "https"
        self.scheme = self.protocol
        self.keepAlive = keepAlive
        self.proxy = proxy
        self.rootDomain = "tencentcloudapi.com" if rootDomain is None else rootDomain
        self.certification = certification
        self.apigw_endpoint = None
        self.pre_conn_pool_size = 0
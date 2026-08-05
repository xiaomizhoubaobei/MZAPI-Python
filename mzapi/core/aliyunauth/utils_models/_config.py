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
# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.

"""客户端初始化配置模型模块

定义阿里云认证客户端的初始化配置模型 Config，
承载 AccessKey 凭证、协议、代理、证书、超时与重试等初始化参数，
并提供字段校验与字典序列化/反序列化能力。

包含的类：
  - Config：客户端初始化配置模型。
"""

from __future__ import annotations

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-utils-models-config-2026-qxx"

from darabonba.model import DaraModel
from alibabacloud_credentials.client import Client
from mzapi.utlis.aliyunauth import utils_models as main_models
from darabonba.policy.retry import RetryOptions


class Config(DaraModel):
    """客户端初始化配置模型，定义创建阿里云认证客户端所需的初始化参数。

    支持 AccessKey 凭证、网络协议、代理、证书、连接池、重试选项
    与 TLS 版本等配置项，用于初始化认证客户端。
    """

    def __init__(
        self,
        access_key_id: str = None,
        access_key_secret: str = None,
        security_token: str = None,
        bearer_token: str = None,
        protocol: str = None,
        method: str = None,
        region_id: str = None,
        read_timeout: int = None,
        connect_timeout: int = None,
        http_proxy: str = None,
        https_proxy: str = None,
        credential: Client = None,
        endpoint: str = None,
        no_proxy: str = None,
        max_idle_conns: int = None,
        network: str = None,
        user_agent: str = None,
        suffix: str = None,
        socks_5proxy: str = None,
        socks_5net_work: str = None,
        endpoint_type: str = None,
        open_platform_endpoint: str = None,
        type: str = None,
        signature_version: str = None,
        signature_algorithm: str = None,
        global_parameters: main_models.GlobalParameters = None,
        key: str = None,
        cert: str = None,
        ca: str = None,
        disable_http_2: bool = None,
        retry_options: RetryOptions = None,
        tls_min_version: str = None,
    ):
        # accesskey id
        self.access_key_id = access_key_id
        # accesskey secret
        self.access_key_secret = access_key_secret
        # security token
        self.security_token = security_token
        # bearer token
        self.bearer_token = bearer_token
        # http protocol
        self.protocol = protocol
        # http method
        self.method = method
        # region id
        self.region_id = region_id
        # read timeout
        self.read_timeout = read_timeout
        # connect timeout
        self.connect_timeout = connect_timeout
        # http proxy
        self.http_proxy = http_proxy
        # https proxy
        self.https_proxy = https_proxy
        # credential
        self.credential = credential
        # endpoint
        self.endpoint = endpoint
        # proxy white list
        self.no_proxy = no_proxy
        # max idle conns
        self.max_idle_conns = max_idle_conns
        # network for endpoint
        self.network = network
        # user agent
        self.user_agent = user_agent
        # suffix for endpoint
        self.suffix = suffix
        # socks5 proxy
        self.socks_5proxy = socks_5proxy
        # socks5 network
        self.socks_5net_work = socks_5net_work
        # endpoint type
        self.endpoint_type = endpoint_type
        # OpenPlatform endpoint
        self.open_platform_endpoint = open_platform_endpoint
        # credential type
        self.type = type
        # Signature Version
        self.signature_version = signature_version
        # Signature Algorithm
        self.signature_algorithm = signature_algorithm
        # Global Parameters
        self.global_parameters = global_parameters
        # privite key for client certificate
        self.key = key
        # client certificate
        self.cert = cert
        # server certificate
        self.ca = ca
        # disable HTTP/2
        self.disable_http_2 = disable_http_2
        # retry options
        self.retry_options = retry_options
        # TLS Minimum Version
        self.tls_min_version = tls_min_version

    def validate(self):
        """校验字段，当存在全局参数时递归校验其合法性。"""
        if self.global_parameters:
            self.global_parameters.validate()

    def to_map(self):
        """将配置对象序列化为字典，值为空的字段将被跳过。"""
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_key_id is not None:
            result['accessKeyId'] = self.access_key_id
        if self.access_key_secret is not None:
            result['accessKeySecret'] = self.access_key_secret
        if self.security_token is not None:
            result['securityToken'] = self.security_token
        if self.bearer_token is not None:
            result['bearerToken'] = self.bearer_token
        if self.protocol is not None:
            result['protocol'] = self.protocol
        if self.method is not None:
            result['method'] = self.method
        if self.region_id is not None:
            result['regionId'] = self.region_id
        if self.read_timeout is not None:
            result['readTimeout'] = self.read_timeout
        if self.connect_timeout is not None:
            result['connectTimeout'] = self.connect_timeout
        if self.http_proxy is not None:
            result['httpProxy'] = self.http_proxy
        if self.https_proxy is not None:
            result['httpsProxy'] = self.https_proxy
        if self.credential is not None:
            result['credential'] = self.credential
        if self.endpoint is not None:
            result['endpoint'] = self.endpoint
        if self.no_proxy is not None:
            result['noProxy'] = self.no_proxy
        if self.max_idle_conns is not None:
            result['maxIdleConns'] = self.max_idle_conns
        if self.network is not None:
            result['network'] = self.network
        if self.user_agent is not None:
            result['userAgent'] = self.user_agent
        if self.suffix is not None:
            result['suffix'] = self.suffix
        if self.socks_5proxy is not None:
            result['socks5Proxy'] = self.socks_5proxy
        if self.socks_5net_work is not None:
            result['socks5NetWork'] = self.socks_5net_work
        if self.endpoint_type is not None:
            result['endpointType'] = self.endpoint_type
        if self.open_platform_endpoint is not None:
            result['openPlatformEndpoint'] = self.open_platform_endpoint
        if self.type is not None:
            result['type'] = self.type
        if self.signature_version is not None:
            result['signatureVersion'] = self.signature_version
        if self.signature_algorithm is not None:
            result['signatureAlgorithm'] = self.signature_algorithm
        if self.global_parameters is not None:
            result['globalParameters'] = self.global_parameters.to_map()

        if self.key is not None:
            result['key'] = self.key
        if self.cert is not None:
            result['cert'] = self.cert
        if self.ca is not None:
            result['ca'] = self.ca
        if self.disable_http_2 is not None:
            result['disableHttp2'] = self.disable_http_2
        if self.retry_options is not None:
            result['retryOptions'] = self.retry_options.to_map()

        if self.tls_min_version is not None:
            result['tlsMinVersion'] = self.tls_min_version
        return result

    def from_map(self, m: dict = None):
        """从字典反序列化配置对象。

        Args:
            m: 包含配置字段的字典。

        Returns:
            当前 Config 对象。
        """
        m = m or dict()
        if m.get('accessKeyId') is not None:
            self.access_key_id = m.get('accessKeyId')
        if m.get('accessKeySecret') is not None:
            self.access_key_secret = m.get('accessKeySecret')
        if m.get('securityToken') is not None:
            self.security_token = m.get('securityToken')
        if m.get('bearerToken') is not None:
            self.bearer_token = m.get('bearerToken')
        if m.get('protocol') is not None:
            self.protocol = m.get('protocol')
        if m.get('method') is not None:
            self.method = m.get('method')
        if m.get('regionId') is not None:
            self.region_id = m.get('regionId')
        if m.get('readTimeout') is not None:
            self.read_timeout = m.get('readTimeout')
        if m.get('connectTimeout') is not None:
            self.connect_timeout = m.get('connectTimeout')
        if m.get('httpProxy') is not None:
            self.http_proxy = m.get('httpProxy')
        if m.get('httpsProxy') is not None:
            self.https_proxy = m.get('httpsProxy')
        if m.get('credential') is not None:
            self.credential = m.get('credential')
        if m.get('endpoint') is not None:
            self.endpoint = m.get('endpoint')
        if m.get('noProxy') is not None:
            self.no_proxy = m.get('noProxy')
        if m.get('maxIdleConns') is not None:
            self.max_idle_conns = m.get('maxIdleConns')
        if m.get('network') is not None:
            self.network = m.get('network')
        if m.get('userAgent') is not None:
            self.user_agent = m.get('userAgent')
        if m.get('suffix') is not None:
            self.suffix = m.get('suffix')
        if m.get('socks5Proxy') is not None:
            self.socks_5proxy = m.get('socks5Proxy')
        if m.get('socks5NetWork') is not None:
            self.socks_5net_work = m.get('socks5NetWork')
        if m.get('endpointType') is not None:
            self.endpoint_type = m.get('endpointType')
        if m.get('openPlatformEndpoint') is not None:
            self.open_platform_endpoint = m.get('openPlatformEndpoint')
        if m.get('type') is not None:
            self.type = m.get('type')
        if m.get('signatureVersion') is not None:
            self.signature_version = m.get('signatureVersion')
        if m.get('signatureAlgorithm') is not None:
            self.signature_algorithm = m.get('signatureAlgorithm')
        if m.get('globalParameters') is not None:
            temp_model = main_models.GlobalParameters()
            self.global_parameters = temp_model.from_map(m.get('globalParameters'))

        if m.get('key') is not None:
            self.key = m.get('key')
        if m.get('cert') is not None:
            self.cert = m.get('cert')
        if m.get('ca') is not None:
            self.ca = m.get('ca')
        if m.get('disableHttp2') is not None:
            self.disable_http_2 = m.get('disableHttp2')
        if m.get('retryOptions') is not None:
            temp_model = RetryOptions()
            self.retry_options = temp_model.from_map(m.get('retryOptions'))

        if m.get('tlsMinVersion') is not None:
            self.tls_min_version = m.get('tlsMinVersion')
        return self


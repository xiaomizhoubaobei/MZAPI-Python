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
_MZAPI_ORIGIN = "mzapi-aliyun-tea-util-models-2026-qxx"


"""
阿里云 Tea 工具包模型模块

定义阿里云认证场景下 tea-util 工具包所需的运行时配置模型，
包含扩展参数与运行时选项两类模型，提供字段校验以及
字典序列化/反序列化能力。

包含的类：
  - ExtendsParameters：扩展参数模型，承载附加的请求头与查询参数。
  - RuntimeOptions：运行时选项模型，配置重试、超时、代理、证书等运行参数。
"""

from Tea.model import TeaModel
from typing import Dict


class ExtendsParameters(TeaModel):
    """扩展参数模型，表示请求中附加的请求头与查询参数。"""

    def __init__(
        self,
        headers: Dict[str, str] = None,
        queries: Dict[str, str] = None,
    ):
        self.headers = headers
        self.queries = queries

    def validate(self):
        """校验字段（本模型无必需字段，无需额外校验）。"""
        pass

    def to_map(self):
        """将扩展参数对象序列化为字典，值为空的字段将被跳过。"""
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.queries is not None:
            result['queries'] = self.queries
        return result

    def from_map(self, m: dict = None):
        """从字典反序列化扩展参数对象。

        Args:
            m: 包含扩展参数字段的字典。

        Returns:
            当前 ExtendsParameters 对象。
        """
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('queries') is not None:
            self.queries = m.get('queries')
        return self


class RuntimeOptions(TeaModel):
    """运行时选项模型，配置请求执行过程中的各项运行参数。

    支持重试策略、超时时间、代理地址、TLS 证书、连接池大小、
    本地地址与 SOCKS5 代理等运行参数的配置，用于控制 API 调用的
    底层执行行为。
    """

    def __init__(
        self,
        autoretry: bool = None,
        ignore_ssl: bool = None,
        max_attempts: int = None,
        backoff_policy: str = None,
        backoff_period: int = None,
        read_timeout: int = None,
        connect_timeout: int = None,
        http_proxy: str = None,
        https_proxy: str = None,
        no_proxy: str = None,
        max_idle_conns: int = None,
        local_addr: str = None,
        socks_5proxy: str = None,
        socks_5net_work: str = None,
        keep_alive: bool = None,
        key: str = None,
        cert: str = None,
        ca: str = None,
        extends_parameters: ExtendsParameters = None,
    ):
        # whether to try again
        self.autoretry = autoretry
        # ignore SSL validation
        self.ignore_ssl = ignore_ssl
        # privite key for client certificate
        self.key = key
        # client certificate
        self.cert = cert
        # server certificate
        self.ca = ca
        # maximum number of retries
        self.max_attempts = max_attempts
        # backoff policy
        self.backoff_policy = backoff_policy
        # backoff period
        self.backoff_period = backoff_period
        # read timeout
        self.read_timeout = read_timeout
        # connect timeout
        self.connect_timeout = connect_timeout
        # http proxy url
        self.http_proxy = http_proxy
        # https Proxy url
        self.https_proxy = https_proxy
        # agent blacklist
        self.no_proxy = no_proxy
        # maximum number of connections
        self.max_idle_conns = max_idle_conns
        # local addr
        self.local_addr = local_addr
        # SOCKS5 proxy
        self.socks_5proxy = socks_5proxy
        # SOCKS5 netWork
        self.socks_5net_work = socks_5net_work
        # whether to enable keep-alive
        self.keep_alive = keep_alive
        # Extends Parameters
        self.extends_parameters = extends_parameters

    def validate(self):
        """校验运行时选项模型，嵌套校验扩展参数模型。"""
        if self.extends_parameters:
            self.extends_parameters.validate()

    def to_map(self):
        """将运行时选项对象序列化为字典，值为空的字段将被跳过。"""
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.autoretry is not None:
            result['autoretry'] = self.autoretry
        if self.ignore_ssl is not None:
            result['ignoreSSL'] = self.ignore_ssl
        if self.key is not None:
            result['key'] = self.key
        if self.cert is not None:
            result['cert'] = self.cert
        if self.ca is not None:
            result['ca'] = self.ca
        if self.max_attempts is not None:
            result['max_attempts'] = self.max_attempts
        if self.backoff_policy is not None:
            result['backoff_policy'] = self.backoff_policy
        if self.backoff_period is not None:
            result['backoff_period'] = self.backoff_period
        if self.read_timeout is not None:
            result['readTimeout'] = self.read_timeout
        if self.connect_timeout is not None:
            result['connectTimeout'] = self.connect_timeout
        if self.http_proxy is not None:
            result['httpProxy'] = self.http_proxy
        if self.https_proxy is not None:
            result['httpsProxy'] = self.https_proxy
        if self.no_proxy is not None:
            result['noProxy'] = self.no_proxy
        if self.max_idle_conns is not None:
            result['maxIdleConns'] = self.max_idle_conns
        if self.local_addr is not None:
            result['localAddr'] = self.local_addr
        if self.socks_5proxy is not None:
            result['socks5Proxy'] = self.socks_5proxy
        if self.socks_5net_work is not None:
            result['socks5NetWork'] = self.socks_5net_work
        if self.keep_alive is not None:
            result['keepAlive'] = self.keep_alive
        if self.extends_parameters is not None:
            result['extendsParameters'] = self.extends_parameters.to_map()
        return result

    def from_map(self, m: dict = None):
        """从字典反序列化运行时选项对象。

        Args:
            m: 包含运行时选项字段的字典。

        Returns:
            当前 RuntimeOptions 对象。
        """
        m = m or dict()
        if m.get('autoretry') is not None:
            self.autoretry = m.get('autoretry')
        if m.get('ignoreSSL') is not None:
            self.ignore_ssl = m.get('ignoreSSL')
        if m.get('key') is not None:
            self.key = m.get('key')
        if m.get('cert') is not None:
            self.cert = m.get('cert')
        if m.get('ca') is not None:
            self.ca = m.get('ca')
        if m.get('max_attempts') is not None:
            self.max_attempts = m.get('max_attempts')
        if m.get('backoff_policy') is not None:
            self.backoff_policy = m.get('backoff_policy')
        if m.get('backoff_period') is not None:
            self.backoff_period = m.get('backoff_period')
        if m.get('readTimeout') is not None:
            self.read_timeout = m.get('readTimeout')
        if m.get('connectTimeout') is not None:
            self.connect_timeout = m.get('connectTimeout')
        if m.get('httpProxy') is not None:
            self.http_proxy = m.get('httpProxy')
        if m.get('httpsProxy') is not None:
            self.https_proxy = m.get('httpsProxy')
        if m.get('noProxy') is not None:
            self.no_proxy = m.get('noProxy')
        if m.get('maxIdleConns') is not None:
            self.max_idle_conns = m.get('maxIdleConns')
        if m.get('localAddr') is not None:
            self.local_addr = m.get('localAddr')
        if m.get('socks5Proxy') is not None:
            self.socks_5proxy = m.get('socks5Proxy')
        if m.get('socks5NetWork') is not None:
            self.socks_5net_work = m.get('socks5NetWork')
        if m.get('keepAlive') is not None:
            self.keep_alive = m.get('keepAlive')
        if m.get('extendsParameters') is not None:
            temp_model = ExtendsParameters()
            self.extends_parameters = temp_model.from_map(m['extendsParameters'])
        return self



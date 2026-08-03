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
_MZAPI_ORIGIN = "mzapi-aliyun-uri-2026-qxx"


"""
URI 凭证提供者模块

提供通过指定 URI 获取阿里云凭证的功能。
从外部 HTTP 服务获取临时凭证，适用于自定义凭证源场景。

包含的类：
  - URLCredentialsProvider：URI 凭证提供者，实现 ICredentialsProvider 接口

特性：
  - 支持自定义 URI 获取凭证
  - 支持 HTTP/HTTPS 协议
  - 自动处理凭证刷新

环境变量：
  - ALIBABA_CLOUD_CREDENTIALS_URI：凭证获取 URI 地址

返回格式：
  URI 服务应返回如下 JSON 格式：
  {
      "Code": "Success",
      "AccessKeyId": "...",
      "AccessKeySecret": "...",
      "SecurityToken": "...",
      "Expiration": "2024-01-01T00:00:00Z"
  }
"""

import calendar
import json
import time
from urllib.parse import urlparse, parse_qs

from .refreshable import Credentials, RefreshResult, RefreshCachedSupplier
from ..http import HttpOptions
from Tea.core import TeaCore
from .refreshable import ICredentialsProvider
from ... import auth_util as au
from ... import parameter_helper as ph
from ..exceptions import CredentialException


def _get_stale_time(expiration: int) -> int:
    """计算凭证过期前进入过期状态的时间

    Args:
        expiration: 凭证过期时间戳

    Returns:
        int: 过期状态开始时间戳
    """
    if expiration < 0:
        return int(time.mktime(time.localtime())) + 60 * 60
    return expiration - 15 * 60


class URLCredentialsProvider(ICredentialsProvider):
    """URI 凭证提供者

    通过指定的 URI 地址从外部服务获取临时凭证。
    适用于需要使用自定义凭证获取服务的场景。

    Class Attributes:
        DEFAULT_CONNECT_TIMEOUT: 默认连接超时（毫秒），默认 5000ms
        DEFAULT_READ_TIMEOUT: 默认读取超时（毫秒），默认 10000ms
    """

    DEFAULT_CONNECT_TIMEOUT = 5000
    DEFAULT_READ_TIMEOUT = 10000

    def __init__(self, *,
                 uri: str = None,
                 protocol: str = 'http',
                 http_options: HttpOptions = None):
        """初始化 URI 凭证提供者

        Args:
            uri: 凭证获取 URI 地址，默认从环境变量 ALIBABA_CLOUD_CREDENTIALS_URI 读取
            protocol: 协议类型，默认 'http'
            http_options: HTTP 请求选项配置

        Raises:
            ValueError: 当 uri 为空时抛出
        """
        self._uri = uri or au.environment_credentials_uri
        if self._uri is None or self._uri == '':
            raise ValueError('uri or environment variable ALIBABA_CLOUD_CREDENTIALS_URI cannot be empty')
        self._protocol = protocol

        self._http_options = http_options if http_options is not None else HttpOptions()
        self._runtime_options = {
            'connectTimeout': self._http_options.connect_timeout if self._http_options.connect_timeout is not None else URLCredentialsProvider.DEFAULT_CONNECT_TIMEOUT,
            'readTimeout': self._http_options.read_timeout if self._http_options.read_timeout is not None else URLCredentialsProvider.DEFAULT_READ_TIMEOUT,
            'httpsProxy': self._http_options.proxy
        }
        self._credentials_cache = RefreshCachedSupplier(
            refresh_callable=self._refresh_credentials,
            refresh_callable_async=self._refresh_credentials_async,
        )

    def get_credentials(self) -> Credentials:
        """获取凭证同步方法

        Returns:
            Credentials: 包含临时凭证的对象
        """
        return self._credentials_cache._sync_call()

    async def get_credentials_async(self) -> Credentials:
        """获取凭证异步方法

        Returns:
            Credentials: 凭证对象
        """
        return await self._credentials_cache._async_call()

    def _refresh_credentials(self) -> RefreshResult[Credentials]:
        """刷新凭证（同步版本）

        从配置的 URI 获取新的临时凭证。

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        r = urlparse(self._uri)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme or self._protocol or 'http'
        tea_request.method = 'GET'
        tea_request.pathname = r.path
        for key, values in parse_qs(r.query).items():
            for value in values:
                tea_request.query[key] = value

        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from {self._uri},  http_code={str(response.status_code)}, result: {response.body.decode("utf-8")}')

        body = response.body.decode('utf-8')

        dic = json.loads(body)
        content_code = dic.get('Code')

        if content_code != "Success" or 'AccessKeyId' not in dic or 'AccessKeySecret' not in dic or 'SecurityToken' not in dic or 'Expiration' not in dic:
            raise CredentialException(
                f'error retrieving credentials from {self._uri} result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(dic.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=dic.get('AccessKeyId'),
            access_key_secret=dic.get('AccessKeySecret'),
            security_token=dic.get('SecurityToken'),
            expiration=expiration,
            provider_name=self.get_provider_name()
        )
        return RefreshResult(value=credentials,
                             stale_time=_get_stale_time(expiration))

    async def _refresh_credentials_async(self) -> RefreshResult[Credentials]:
        """刷新凭证（异步版本）

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象
        """
        r = urlparse(self._uri)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme or self._protocol or 'http'
        tea_request.method = 'GET'
        tea_request.pathname = r.path
        for key, values in parse_qs(r.query).items():
            for value in values:
                tea_request.query[key] = value

        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from {self._uri},  http_code={str(response.status_code)}, result: {response.body.decode("utf-8")}')

        body = response.body.decode('utf-8')

        dic = json.loads(body)
        content_code = dic.get('Code')

        if content_code != "Success" or 'AccessKeyId' not in dic or 'AccessKeySecret' not in dic or 'SecurityToken' not in dic or 'Expiration' not in dic:
            raise CredentialException(
                f'error retrieving credentials from {self._uri} result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(dic.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=dic.get('AccessKeyId'),
            access_key_secret=dic.get('AccessKeySecret'),
            security_token=dic.get('SecurityToken'),
            expiration=expiration,
            provider_name=self.get_provider_name()
        )
        return RefreshResult(value=credentials,
                             stale_time=_get_stale_time(expiration))

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'credential_uri'
        """
        return 'credential_uri'

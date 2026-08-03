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
_MZAPI_ORIGIN = "mzapi-aliyun-cloud-sso-2026-qxx"


"""
CloudSSO 凭证提供者模块

提供通过阿里云 CloudSSO 服务获取临时凭证的功能。
适用于需要通过阿里云控制台或 CLI 登录 CloudSSO 后获取临时凭证的场景。

包含的类：
  - CloudSSOCredentialsProvider：CloudSSO 凭证提供者，实现 ICredentialsProvider 接口

特性：
  - 支持通过 CloudSSO 登录获取临时凭证
  - 支持自动凭证刷新
  - 支持自定义 HTTP 请求选项
"""

import calendar
import json
import time
from urllib.parse import urlparse

from .refreshable import Credentials, RefreshResult, RefreshCachedSupplier
from ..http import HttpOptions
from Tea.core import TeaCore
from alibabacloud_credentials_api import ICredentialsProvider
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


class CloudSSOCredentialsProvider(ICredentialsProvider):
    """CloudSSO 凭证提供者

    通过阿里云 CloudSSO 服务获取临时凭证。
    需要预先通过 CLI 或控制台完成 CloudSSO 登录。

    Class Attributes:
        DEFAULT_CONNECT_TIMEOUT: 默认连接超时（毫秒），默认 5000ms
        DEFAULT_READ_TIMEOUT: 默认读取超时（毫秒），默认 10000ms
    """

    DEFAULT_CONNECT_TIMEOUT = 5000
    DEFAULT_READ_TIMEOUT = 10000

    def __init__(self, *,
                 sign_in_url: str = None,
                 account_id: str = None,
                 access_config: str = None,
                 access_token: str = None,
                 access_token_expire: int = 0,
                 http_options: HttpOptions = None):
        """初始化 CloudSSO 凭证提供者

        Args:
            sign_in_url: CloudSSO 登录 URL
            account_id: CloudSSO 账户 ID
            access_config: CloudSSO 访问配置
            access_token: CloudSSO 访问令牌
            access_token_expire: 访问令牌过期时间戳
            http_options: HTTP 请求选项配置

        Raises:
            ValueError: 当 access_token 为空或过期，或必要参数缺失时抛出
        """
        self._sign_in_url = sign_in_url
        self._account_id = account_id
        self._access_config = access_config
        self._access_token = access_token
        self._access_token_expire = access_token_expire

        if self._access_token is None or self._access_token_expire == 0 or self._access_token_expire - int(
                time.mktime(time.localtime())) <= 0:
            raise ValueError(
                'CloudSSO access token is empty or expired, please re-login with cli')
        if self._sign_in_url is None or self._account_id is None or self._access_config is None:
            raise ValueError(
                'CloudSSO sign in url or account id or access config is empty')

        self._http_options = http_options if http_options is not None else HttpOptions()
        self._runtime_options = {
            'connectTimeout': self._http_options.connect_timeout if self._http_options.connect_timeout is not None else CloudSSOCredentialsProvider.DEFAULT_CONNECT_TIMEOUT,
            'readTimeout': self._http_options.read_timeout if self._http_options.read_timeout is not None else CloudSSOCredentialsProvider.DEFAULT_READ_TIMEOUT,
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

        调用 CloudSSO API 获取新的临时凭证。

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        r = urlparse(self._sign_in_url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme
        tea_request.method = 'POST'
        tea_request.pathname = '/cloud-credentials'

        tea_request.body = json.dumps({
            'AccountId': self._account_id,
            'AccessConfigurationId': self._access_config,
        })

        tea_request.headers['Accept'] = 'application/json'
        tea_request.headers['Content-Type'] = 'application/json'
        tea_request.headers['Authorization'] = f'Bearer {self._access_token}'

        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from sso, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'CloudCredential' not in dic:
            raise CredentialException(
                f'error retrieving credentials from sso result: {response.body.decode("utf-8")}')

        cre = dic.get('CloudCredential')
        if 'AccessKeyId' not in cre or 'AccessKeySecret' not in cre or 'SecurityToken' not in cre:
            raise CredentialException(
                f'error retrieving credentials from sso result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(cre.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=cre.get('AccessKeyId'),
            access_key_secret=cre.get('AccessKeySecret'),
            security_token=cre.get('SecurityToken'),
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
        r = urlparse(self._sign_in_url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme
        tea_request.method = 'POST'
        tea_request.pathname = '/cloud-credentials'

        tea_request.body = json.dumps({
            'AccountId': self._account_id,
            'AccessConfigurationId': self._access_config,
        })

        tea_request.headers['Accept'] = 'application/json'
        tea_request.headers['Content-Type'] = 'application/json'
        tea_request.headers['Authorization'] = f'Bearer {self._access_token}'

        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from sso, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'CloudCredential' not in dic:
            raise CredentialException(
                f'error retrieving credentials from sso result: {response.body.decode("utf-8")}')

        cre = dic.get('CloudCredential')
        if 'AccessKeyId' not in cre or 'AccessKeySecret' not in cre or 'SecurityToken' not in cre:
            raise CredentialException(
                f'error retrieving credentials from sso result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(cre.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=cre.get('AccessKeyId'),
            access_key_secret=cre.get('AccessKeySecret'),
            security_token=cre.get('SecurityToken'),
            expiration=expiration,
            provider_name=self.get_provider_name()
        )
        return RefreshResult(value=credentials,
                             stale_time=_get_stale_time(expiration))

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'cloud_sso'
        """
        return 'cloud_sso'

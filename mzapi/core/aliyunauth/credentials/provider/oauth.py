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
_MZAPI_ORIGIN = "mzapi-aliyun-oauth-2026-qxx"


"""
OAuth 凭证提供者模块

提供通过阿里云 OAuth 认证获取临时凭证的功能。
支持自动刷新 OAuth 令牌和凭证刷新回调。

包含的类：
  - OAuthCredentialsProvider：OAuth 凭证提供者，实现 ICredentialsProvider 接口
  - OAuthTokenUpdateCallback：OAuth 令牌更新回调函数类型（同步）
  - OAuthTokenUpdateCallbackAsync：OAuth 令牌更新回调函数类型（异步）

特性：
  - 支持 OAuth 2.0 认证流程
  - 支持自动刷新 OAuth 令牌
  - 支持令牌更新回调函数
  - 支持凭证自动刷新

Type Aliases:
  OAuthTokenUpdateCallback: 同步令牌更新回调函数
  OAuthTokenUpdateCallbackAsync: 异步令牌更新回调函数
"""

import calendar
import json
import logging
import time
from urllib.parse import urlparse, urlencode
from typing import Callable, Optional

from .refreshable import Credentials, RefreshResult, RefreshCachedSupplier
from ..http import HttpOptions
from Tea.core import TeaCore
from .refreshable import ICredentialsProvider
from ... import parameter_helper as ph
from ..exceptions import CredentialException

log = logging.getLogger('credentials')
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
log.addHandler(ch)

# OAuth 令牌更新回调函数类型
OAuthTokenUpdateCallback = Callable[[str, str, str, str, str, int, int], None]
OAuthTokenUpdateCallbackAsync = Callable[[str, str, str, str, str, int, int], None]


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


class OAuthCredentialsProvider(ICredentialsProvider):
    """OAuth 凭证提供者

    通过阿里云 OAuth 2.0 认证获取临时凭证。
    支持自动刷新 OAuth 访问令牌和刷新凭证。

    Class Attributes:
        DEFAULT_CONNECT_TIMEOUT: 默认连接超时（毫秒），默认 5000ms
        DEFAULT_READ_TIMEOUT: 默认读取超时（毫秒），默认 10000ms
    """

    DEFAULT_CONNECT_TIMEOUT = 5000
    DEFAULT_READ_TIMEOUT = 10000

    def __init__(self, *,
                 client_id: str = None,
                 sign_in_url: str = None,
                 access_token: str = None,
                 access_token_expire: int = 0,
                 refresh_token: str = None,
                 http_options: HttpOptions = None,
                 token_update_callback: Optional[OAuthTokenUpdateCallback] = None,
                 token_update_callback_async: Optional[OAuthTokenUpdateCallbackAsync] = None):
        """初始化 OAuth 凭证提供者

        Args:
            client_id: OAuth 客户端 ID
            sign_in_url: OAuth 登录 URL
            access_token: 访问令牌
            access_token_expire: 访问令牌过期时间戳
            refresh_token: 刷新令牌
            http_options: HTTP 请求选项配置
            token_update_callback: 令牌更新回调函数（同步）
            token_update_callback_async: 令牌更新回调函数（异步）

        Raises:
            ValueError: 当 client_id 或 sign_in_url 为空时抛出
        """
        if not client_id:
            raise ValueError('the ClientId is empty')

        if not sign_in_url:
            raise ValueError('the url for sign-in is empty')

        self._client_id = client_id
        self._sign_in_url = sign_in_url
        self._access_token = access_token
        self._access_token_expire = access_token_expire
        self._refresh_token = refresh_token
        self._token_update_callback = token_update_callback
        self._token_update_callback_async = token_update_callback_async

        self._http_options = http_options if http_options is not None else HttpOptions()
        self._runtime_options = {
            'connectTimeout': self._http_options.connect_timeout if self._http_options.connect_timeout is not None else OAuthCredentialsProvider.DEFAULT_CONNECT_TIMEOUT,
            'readTimeout': self._http_options.read_timeout if self._http_options.read_timeout is not None else OAuthCredentialsProvider.DEFAULT_READ_TIMEOUT,
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

    def _try_refresh_oauth_token(self) -> None:
        """刷新 OAuth 访问令牌

        Raises:
            CredentialException: 当刷新令牌失败时抛出
        """
        current_time = int(time.mktime(time.localtime()))
        # 构建刷新令牌请求
        r = urlparse(self._sign_in_url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme
        tea_request.method = 'POST'
        tea_request.pathname = '/v1/token'

        # 设置请求体
        body_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
            'client_id': self._client_id,
            'Timestamp': ph.get_iso_8061_date()
        }
        tea_request.body = urlencode(body_data)
        tea_request.headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(f"failed to refresh OAuth token, status code: {response.status_code}, response: {response.body.decode('utf-8')}")

        # 解析响应
        dic = json.loads(response.body.decode('utf-8'))
        if 'access_token' not in dic or 'refresh_token' not in dic:
            raise CredentialException(f"failed to refresh OAuth token: {response.body.decode('utf-8')}")

        # 更新令牌
        new_access_token = dic.get('access_token')
        new_refresh_token = dic.get('refresh_token')
        expires_in = dic.get('expires_in', 3600)
        new_access_token_expire = current_time + expires_in

        self._access_token = new_access_token
        self._refresh_token = new_refresh_token
        self._access_token_expire = new_access_token_expire

    async def _try_refresh_oauth_token_async(self) -> None:
        """异步刷新 OAuth 访问令牌

        Raises:
            CredentialException: 当刷新令牌失败时抛出
        """
        current_time = int(time.mktime(time.localtime()))
        # 构建刷新令牌请求
        r = urlparse(self._sign_in_url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme
        tea_request.method = 'POST'
        tea_request.pathname = '/v1/token'

        # 设置请求体
        body_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
            'client_id': self._client_id,
            'Timestamp': ph.get_iso_8061_date()
        }
        tea_request.body = urlencode(body_data)
        tea_request.headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(f"failed to refresh OAuth token, status code: {response.status_code}, response: {response.body.decode('utf-8')}")

        # 解析响应
        dic = json.loads(response.body.decode('utf-8'))
        if 'access_token' not in dic or 'refresh_token' not in dic:
            raise CredentialException(f"failed to refresh OAuth token: {response.body.decode('utf-8')}")

        # 更新令牌
        new_access_token = dic.get('access_token')
        new_refresh_token = dic.get('refresh_token')
        expires_in = dic.get('expires_in', 3600)
        new_access_token_expire = current_time + expires_in

        self._access_token = new_access_token
        self._refresh_token = new_refresh_token
        self._access_token_expire = new_access_token_expire

    def _refresh_credentials(self) -> RefreshResult[Credentials]:
        """刷新凭证（同步版本）

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        if self._refresh_token and (
                self._access_token is None or self._access_token_expire <= 0 or self._access_token_expire - int(
                time.mktime(time.localtime())) <= 1200):
            self._try_refresh_oauth_token()

        r = urlparse(self._sign_in_url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme
        tea_request.method = 'POST'
        tea_request.pathname = '/v1/exchange'

        tea_request.headers['Content-Type'] = 'application/json'
        tea_request.headers['Authorization'] = f'Bearer {self._access_token}'

        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f"error refreshing credentials from OAuth, http_code: {response.status_code}, result: {response.body.decode('utf-8')}")

        dic = json.loads(response.body.decode('utf-8'))
        if 'error' in dic:
            raise CredentialException(
                f"error retrieving credentials from OAuth result: {response.body.decode('utf-8')}")

        if 'AccessKeyId' not in dic or 'AccessKeySecret' not in dic or 'SecurityToken' not in dic:
            raise CredentialException(
                f"error retrieving credentials from OAuth result: {response.body.decode('utf-8')}")

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

        # 调用令牌更新回调函数
        if self._token_update_callback:
            try:
                self._token_update_callback(
                    self._refresh_token,
                    self._access_token,
                    credentials.get_access_key_id(),
                    credentials.get_access_key_secret(),
                    credentials.get_security_token(),
                    self._access_token_expire,
                    expiration
                )
            except Exception as e:
                log.warning(f'failed to update OAuth tokens in config file: {e}')

        return RefreshResult(value=credentials,
                             stale_time=_get_stale_time(expiration))

    async def _refresh_credentials_async(self) -> RefreshResult[Credentials]:
        """刷新凭证（异步版本）

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象
        """
        if self._refresh_token and (
                self._access_token is None or self._access_token_expire <= 0 or self._access_token_expire - int(
                time.mktime(time.localtime())) <= 1200):
            await self._try_refresh_oauth_token_async()

        r = urlparse(self._sign_in_url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.protocol = r.scheme
        tea_request.method = 'POST'
        tea_request.pathname = '/v1/exchange'

        tea_request.headers['Content-Type'] = 'application/json'
        tea_request.headers['Authorization'] = f'Bearer {self._access_token}'

        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f"error refreshing credentials from OAuth, http_code: {response.status_code}, result: {response.body.decode('utf-8')}")

        dic = json.loads(response.body.decode('utf-8'))
        if 'error' in dic:
            raise CredentialException(
                f"error retrieving credentials from OAuth result: {response.body.decode('utf-8')}")

        if 'AccessKeyId' not in dic or 'AccessKeySecret' not in dic or 'SecurityToken' not in dic:
            raise CredentialException(
                f"error retrieving credentials from OAuth result: {response.body.decode('utf-8')}")

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

        if self._token_update_callback_async:
            try:
                await self._token_update_callback_async(
                    self._refresh_token,
                    self._access_token,
                    credentials.get_access_key_id(),
                    credentials.get_access_key_secret(),
                    credentials.get_security_token(),
                    self._access_token_expire,
                    expiration
                )
            except Exception as e:
                log.warning(f'failed to update OAuth tokens in config file: {e}')

        return RefreshResult(value=credentials,
                             stale_time=_get_stale_time(expiration))

    def _get_client_id(self) -> str:
        """获取客户端ID"""
        return self._client_id

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'oauth'
        """
        return 'oauth'

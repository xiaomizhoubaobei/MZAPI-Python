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
_MZAPI_ORIGIN = "mzapi-aliyun-rsa-key-pair-2026-qxx"


"""
RSA 密钥对凭证提供者模块

提供通过阿里云 RSA 密钥对获取临时凭证的功能。
使用 GenerateSessionAccessKey API 调用 STS 服务获取临时会话密钥。

包含的类：
  - RsaKeyPairCredentialsProvider：RSA 密钥对凭证提供者，实现 ICredentialsProvider 接口

特性：
  - 支持 RSA 私钥文件认证
  - 支持自定义会话持续时间
  - 支持 VPC 环境和自定义 STS 端点

使用示例：
  provider = RsaKeyPairCredentialsProvider(
      public_key_id='your_public_key_id',
      private_key_file='/path/to/private_key.pem'
  )
  credentials = provider.get_credentials()
"""

import calendar
import json
import time

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


def _get_content(file_path: str) -> str:
    """读取私钥文件内容

    Args:
        file_path: 私钥文件路径

    Returns:
        str: 私钥内容
    """
    with open(file_path, mode='r') as file:
        content = file.read()
    return content


class RsaKeyPairCredentialsProvider(ICredentialsProvider):
    """RSA 密钥对凭证提供者

    通过阿里云 RSA 密钥对调用 GenerateSessionAccessKey API 获取临时会话密钥。
    适用于使用 SSH 密钥对进行认证的场景。

    Class Attributes:
        DEFAULT_DURATION_SECONDS: 默认会话持续时间（秒），默认 3600 秒（1小时）
        DEFAULT_CONNECT_TIMEOUT: 默认连接超时（毫秒），默认 5000ms
        DEFAULT_READ_TIMEOUT: 默认读取超时（毫秒），默认 10000ms
    """

    DEFAULT_DURATION_SECONDS = 3600
    DEFAULT_CONNECT_TIMEOUT = 5000
    DEFAULT_READ_TIMEOUT = 10000

    def __init__(self, *,
                 public_key_id: str = None,
                 private_key_file: str = None,
                 duration_seconds: int = DEFAULT_DURATION_SECONDS,
                 sts_region_id: str = None,
                 sts_endpoint: str = None,
                 enable_vpc: bool = None,
                 http_options: HttpOptions = None):
        """初始化 RSA 密钥对凭证提供者

        Args:
            public_key_id: RSA 公钥 ID
            private_key_file: RSA 私钥文件路径
            duration_seconds: 会话持续时间，默认 3600 秒
            sts_region_id: STS 区域 ID
            sts_endpoint: 自定义 STS 端点
            enable_vpc: 是否启用 VPC 环境
            http_options: HTTP 请求选项配置

        Raises:
            ValueError: 当 public_key_id 或 private_key_file 为空，或 duration_seconds 小于 900 时抛出
        """
        self._public_key_id = public_key_id
        self._private_key_file = private_key_file
        self._duration_seconds = duration_seconds

        if self._duration_seconds is None:
            self._duration_seconds = self.DEFAULT_DURATION_SECONDS
        if self._duration_seconds < 900:
            raise ValueError('session duration should be in the range of 900s - max session duration')
        if self._public_key_id is None or self._public_key_id == '':
            raise ValueError('public_key_id cannot be empty')
        if self._private_key_file is None or self._private_key_file == '':
            raise ValueError('private_key_file cannot be empty')
        self._private_key = _get_content(self._private_key_file)
        if self._private_key is None or self._private_key == '':
            raise ValueError('private_key cannot be empty')

        if sts_endpoint is not None and sts_endpoint != '':
            self._sts_endpoint = sts_endpoint
        else:
            if enable_vpc is not None:
                prefix = 'sts-vpc' if enable_vpc else 'sts'
            else:
                prefix = 'sts-vpc' if au.environment_enable_vpc.lower() == 'true' else 'sts'
            if sts_region_id is not None and sts_region_id != '':
                self._sts_endpoint = f'{prefix}.{sts_region_id}.aliyuncs.com'
            elif au.environment_sts_region is not None and au.environment_sts_region != '':
                self._sts_endpoint = f'{prefix}.{au.environment_sts_region}.aliyuncs.com'
            else:
                self._sts_endpoint = 'sts.ap-northeast-1.aliyuncs.com'

        self._http_options = http_options if http_options is not None else HttpOptions()
        self._runtime_options = {
            'connectTimeout': self._http_options.connect_timeout if self._http_options.connect_timeout is not None else RsaKeyPairCredentialsProvider.DEFAULT_CONNECT_TIMEOUT,
            'readTimeout': self._http_options.read_timeout if self._http_options.read_timeout is not None else RsaKeyPairCredentialsProvider.DEFAULT_READ_TIMEOUT,
            'httpsProxy': self._http_options.proxy
        }
        self._credentials_cache = RefreshCachedSupplier(
            refresh_callable=self._refresh_credentials,
            refresh_callable_async=self._refresh_credentials_async,
        )

    def get_credentials(self) -> Credentials:
        """获取凭证同步方法

        Returns:
            Credentials: 包含临时会话密钥的对象
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

        调用 GenerateSessionAccessKey API 获取新的临时会话密钥。

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'GenerateSessionAccessKey',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self._duration_seconds),
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'Timestamp': ph.get_iso_8061_date(),
            'SignatureNonce': ph.get_uuid(),
            'AccessKeyId': self._public_key_id,
        }

        string_to_sign = ph.compose_string_to_sign('GET', tea_request.query)
        signature = ph.sign_string(string_to_sign, self._private_key + '&')
        tea_request.query['Signature'] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self._sts_endpoint

        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from rsa_key_pair, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'SessionAccessKey' not in dic:
            raise CredentialException(
                f'error retrieving credentials from rsa_key_pair result: {response.body.decode("utf-8")}')

        cre = dic.get('SessionAccessKey')
        if 'SessionAccessKeyId' not in cre or 'SessionAccessKeySecret' not in cre:
            raise CredentialException(
                f'error retrieving credentials from rsa_key_pair result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(cre.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=cre.get('SessionAccessKeyId'),
            access_key_secret=cre.get('SessionAccessKeySecret'),
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
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'GenerateSessionAccessKey',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self._duration_seconds),
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'Timestamp': ph.get_iso_8061_date(),
            'SignatureNonce': ph.get_uuid(),
            'AccessKeyId': self._public_key_id,
        }

        string_to_sign = ph.compose_string_to_sign('GET', tea_request.query)
        signature = ph.sign_string(string_to_sign, self._private_key + '&')
        tea_request.query['Signature'] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self._sts_endpoint

        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from rsa_key_pair, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'SessionAccessKey' not in dic:
            raise CredentialException(
                f'error retrieving credentials from rsa_key_pair result: {response.body.decode("utf-8")}')

        cre = dic.get('SessionAccessKey')
        if 'SessionAccessKeyId' not in cre or 'SessionAccessKeySecret' not in cre:
            raise CredentialException(
                f'error retrieving credentials from rsa_key_pair result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(cre.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=cre.get('SessionAccessKeyId'),
            access_key_secret=cre.get('SessionAccessKeySecret'),
            expiration=expiration,
            provider_name=self.get_provider_name()
        )
        return RefreshResult(value=credentials,
                             stale_time=_get_stale_time(expiration))

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'rsa_key_pair'
        """
        return 'rsa_key_pair'

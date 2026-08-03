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
_MZAPI_ORIGIN = "mzapi-aliyun-ram-role-arn-2026-qxx"


"""
RAM Role ARN 凭证提供者模块

提供通过阿里云 RAM 角色获取临时凭证的功能。
使用 AssumeRole API 调用 RAM 服务获取角色临时凭证。

包含的类：
  - RamRoleArnCredentialsProvider：RAM 角色 ARN 凭证提供者，实现 ICredentialsProvider 接口

特性：
  - 支持通过其他凭证提供者获取原始凭证
  - 支持自定义策略和外部 ID
  - 支持 VPC 环境和自定义 STS 端点

环境变量：
  - ALIBABA_CLOUD_ROLE_ARN：RAM 角色 ARN
  - ALIBABA_CLOUD_ROLE_SESSION_NAME：角色会话名称
  - ALIBABA_CLOUD_ENABLE_VPC：是否启用 VPC 环境
  - ALIBABA_CLOUD_STS_REGION：STS 区域
"""

import calendar
import json
import time

from .refreshable import Credentials, RefreshResult, RefreshCachedSupplier
from . import StaticAKCredentialsProvider, StaticSTSCredentialsProvider
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


class RamRoleArnCredentialsProvider(ICredentialsProvider):
    """RAM Role ARN 凭证提供者

    通过阿里云 RAM 服务的 AssumeRole API 获取临时凭证。
    支持自定义角色会话名称、策略、外部 ID 等参数。

    Class Attributes:
        DEFAULT_DURATION_SECONDS: 默认角色会话持续时间（秒），默认 3600 秒（1小时）
        DEFAULT_CONNECT_TIMEOUT: 默认连接超时（毫秒），默认 5000ms
        DEFAULT_READ_TIMEOUT: 默认读取超时（毫秒），默认 10000ms
    """

    DEFAULT_DURATION_SECONDS = 3600
    DEFAULT_CONNECT_TIMEOUT = 5000
    DEFAULT_READ_TIMEOUT = 10000

    def __init__(self, *,
                 access_key_id: str = None,
                 access_key_secret: str = None,
                 security_token: str = None,
                 credentials_provider: ICredentialsProvider = None,
                 role_arn: str = None,
                 role_session_name: str = None,
                 duration_seconds: int = DEFAULT_DURATION_SECONDS,
                 policy: str = None,
                 external_id: str = None,
                 sts_region_id: str = None,
                 sts_endpoint: str = None,
                 enable_vpc: bool = None,
                 http_options: HttpOptions = None):
        """初始化 RAM Role ARN 凭证提供者

        Args:
            access_key_id: 原始凭证的 AccessKeyId
            access_key_secret: 原始凭证的 AccessKeySecret
            security_token: 原始凭证的 SecurityToken
            credentials_provider: 原始凭证提供者
            role_arn: RAM 角色 ARN，默认从环境变量 ALIBABA_CLOUD_ROLE_ARN 读取
            role_session_name: 角色会话名称，默认自动生成
            duration_seconds: 角色会话持续时间，默认 3600 秒
            policy: 可选的 RAM 策略
            external_id: 可选的外部 ID
            sts_region_id: STS 区域 ID
            sts_endpoint: 自定义 STS 端点
            enable_vpc: 是否启用 VPC 环境
            http_options: HTTP 请求选项配置

        Raises:
            ValueError: 当 role_arn 为空或 duration_seconds 小于 900 时抛出
        """
        if credentials_provider is not None:
            self._credentials_provider = credentials_provider
        elif security_token is not None and security_token != '':
            self._credentials_provider = StaticSTSCredentialsProvider(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
                security_token=security_token
            )
        else:
            self._credentials_provider = StaticAKCredentialsProvider(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
            )

        self._role_arn = role_arn or au.environment_role_arn
        self._role_session_name = role_session_name or au.environment_role_session_name
        self._duration_seconds = duration_seconds
        self._policy = policy
        self._external_id = external_id

        if self._role_session_name is None or self._role_session_name == '':
            self._role_session_name = f'credentials-python-{str(int(time.mktime(time.localtime())))}'
        if self._duration_seconds is None:
            self._duration_seconds = self.DEFAULT_DURATION_SECONDS
        if self._duration_seconds < 900:
            raise ValueError('session duration should be in the range of 900s - max session duration')
        if self._role_arn is None or self._role_arn == '':
            raise ValueError('role_arn or environment variable ALIBABA_CLOUD_ROLE_ARN cannot be empty')

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
                self._sts_endpoint = 'sts.aliyuncs.com'

        self._http_options = http_options if http_options is not None else HttpOptions()
        self._runtime_options = {
            'connectTimeout': self._http_options.connect_timeout if self._http_options.connect_timeout is not None else RamRoleArnCredentialsProvider.DEFAULT_CONNECT_TIMEOUT,
            'readTimeout': self._http_options.read_timeout if self._http_options.read_timeout is not None else RamRoleArnCredentialsProvider.DEFAULT_READ_TIMEOUT,
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

        调用 AssumeRole API 获取新的临时凭证。

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'AssumeRole',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self._duration_seconds),
            'RoleArn': self._role_arn,
            'RoleSessionName': self._role_session_name,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'Timestamp': ph.get_iso_8061_date(),
            'SignatureNonce': ph.get_uuid()
        }

        if self._policy is not None and self._policy != '':
            tea_request.query['Policy'] = self._policy

        if self._external_id is not None and self._external_id != '':
            tea_request.query['ExternalId'] = self._external_id

        pre_credentials = self._credentials_provider.get_credentials()
        if pre_credentials is None:
            raise CredentialException('unable to load original credentials from the provider in RAM role arn')

        tea_request.query['AccessKeyId'] = pre_credentials.get_access_key_id()
        security_token = pre_credentials.get_security_token()
        if security_token is not None and security_token != '':
            tea_request.query['SecurityToken'] = security_token

        string_to_sign = ph.compose_string_to_sign('GET', tea_request.query)
        signature = ph.sign_string(string_to_sign, pre_credentials.get_access_key_secret() + '&')
        tea_request.query['Signature'] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self._sts_endpoint

        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from ram_role_arn, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'Credentials' not in dic:
            raise CredentialException(
                f'error retrieving credentials from ram_role_arn result: {response.body.decode("utf-8")}')

        cre = dic.get('Credentials')
        if 'AccessKeyId' not in cre or 'AccessKeySecret' not in cre or 'SecurityToken' not in cre:
            raise CredentialException(
                f'error retrieving credentials from ram_role_arn result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(cre.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=cre.get('AccessKeyId'),
            access_key_secret=cre.get('AccessKeySecret'),
            security_token=cre.get('SecurityToken'),
            expiration=expiration,
            provider_name=f'{self.get_provider_name()}/{pre_credentials.get_provider_name()}'
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
            'Action': 'AssumeRole',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self._duration_seconds),
            'RoleArn': self._role_arn,
            'RoleSessionName': self._role_session_name,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'Timestamp': ph.get_iso_8061_date(),
            'SignatureNonce': ph.get_uuid()
        }

        if self._policy is not None and self._policy != '':
            tea_request.query['Policy'] = self._policy

        if self._external_id is not None and self._external_id != '':
            tea_request.query['ExternalId'] = self._external_id

        pre_credentials = await self._credentials_provider.get_credentials_async()
        if pre_credentials is None:
            raise CredentialException('unable to load original credentials from the provider in RAM role arn')

        tea_request.query['AccessKeyId'] = pre_credentials.get_access_key_id()
        security_token = pre_credentials.get_security_token()
        if security_token is not None and security_token != '':
            tea_request.query['SecurityToken'] = security_token

        string_to_sign = ph.compose_string_to_sign('GET', tea_request.query)
        signature = ph.sign_string(string_to_sign, pre_credentials.get_access_key_secret() + '&')
        tea_request.query['Signature'] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self._sts_endpoint

        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from ram_role_arn, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'Credentials' not in dic:
            raise CredentialException(
                f'error retrieving credentials from ram_role_arn result: {response.body.decode("utf-8")}')

        cre = dic.get('Credentials')
        if 'AccessKeyId' not in cre or 'AccessKeySecret' not in cre or 'SecurityToken' not in cre:
            raise CredentialException(
                f'error retrieving credentials from ram_role_arn result: {response.body.decode("utf-8")}')

        # 先转换为时间数组
        time_array = time.strptime(cre.get('Expiration'), '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=cre.get('AccessKeyId'),
            access_key_secret=cre.get('AccessKeySecret'),
            security_token=cre.get('SecurityToken'),
            expiration=expiration,
            provider_name=f'{self.get_provider_name()}/{pre_credentials.get_provider_name()}'
        )
        return RefreshResult(value=credentials,
                             stale_time=_get_stale_time(expiration))

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'ram_role_arn'
        """
        return 'ram_role_arn'

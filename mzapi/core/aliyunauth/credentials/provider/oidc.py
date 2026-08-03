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
_MZAPI_ORIGIN = "mzapi-aliyun-oidc-2026-qxx"


"""
OIDC Role ARN 凭证提供者模块

提供通过阿里云 RAM OIDC 角色获取临时凭证的功能。
使用 AssumeRoleWithOIDC API 调用 RAM 服务获取角色临时凭证，适用于支持 OIDC 的身份提供商场景。

包含的类：
  - OIDCRoleArnCredentialsProvider：OIDC Role ARN 凭证提供者，实现 ICredentialsProvider 接口

特性：
  - 支持 OIDC 令牌认证
  - 支持自定义策略
  - 支持 VPC 环境和自定义 STS 端点

环境变量：
  - ALIBABA_CLOUD_ROLE_ARN：RAM 角色 ARN
  - ALIBABA_CLOUD_OIDC_PROVIDER_ARN：OIDC 提供商 ARN
  - ALIBABA_CLOUD_OIDC_TOKEN_FILE：OIDC 令牌文件路径
  - ALIBABA_CLOUD_ROLE_SESSION_NAME：角色会话名称
  - ALIBABA_CLOUD_ENABLE_VPC：是否启用 VPC 环境
  - ALIBABA_CLOUD_STS_REGION：STS 区域
"""

import calendar
import json
import time
import aiofiles

from .refreshable import Credentials, RefreshResult, RefreshCachedSupplier
from ..http import HttpOptions
from Tea.core import TeaCore
from .refreshable import ICredentialsProvider
from ... import auth_util as au
from ... import parameter_helper as ph
from ..exceptions import CredentialException


async def _get_token_async(file_path: str) -> str:
    """异步读取 OIDC 令牌文件

    Args:
        file_path: OIDC 令牌文件路径

    Returns:
        str: OIDC 令牌内容
    """
    async with aiofiles.open(file_path, mode='r') as file:
        token = await file.read()
    return token


def _get_token(file_path: str) -> str:
    """同步读取 OIDC 令牌文件

    Args:
        file_path: OIDC 令牌文件路径

    Returns:
        str: OIDC 令牌内容
    """
    with open(file_path, mode='r') as file:
        token = file.read()
    return token


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


class OIDCRoleArnCredentialsProvider(ICredentialsProvider):
    """OIDC Role ARN 凭证提供者

    通过阿里云 RAM 服务的 AssumeRoleWithOIDC API 获取临时凭证。
    适用于使用支持 OIDC 的身份提供商（如 Kubernetes Service Account）进行认证。

    Class Attributes:
        DEFAULT_DURATION_SECONDS: 默认角色会话持续时间（秒），默认 3600 秒（1小时）
        DEFAULT_CONNECT_TIMEOUT: 默认连接超时（毫秒），默认 5000ms
        DEFAULT_READ_TIMEOUT: 默认读取超时（毫秒），默认 10000ms
    """

    DEFAULT_DURATION_SECONDS = 3600
    DEFAULT_CONNECT_TIMEOUT = 5000
    DEFAULT_READ_TIMEOUT = 10000

    def __init__(self, *,
                 role_arn: str = None,
                 oidc_provider_arn: str = None,
                 oidc_token_file_path: str = None,
                 role_session_name: str = None,
                 duration_seconds: int = DEFAULT_DURATION_SECONDS,
                 policy: str = None,
                 sts_region_id: str = None,
                 sts_endpoint: str = None,
                 enable_vpc: bool = None,
                 http_options: HttpOptions = None):
        """初始化 OIDC Role ARN 凭证提供者

        Args:
            role_arn: RAM 角色 ARN，默认从环境变量 ALIBABA_CLOUD_ROLE_ARN 读取
            oidc_provider_arn: OIDC 提供商 ARN，默认从环境变量 ALIBABA_CLOUD_OIDC_PROVIDER_ARN 读取
            oidc_token_file_path: OIDC 令牌文件路径，默认从环境变量 ALIBABA_CLOUD_OIDC_TOKEN_FILE 读取
            role_session_name: 角色会话名称，默认自动生成
            duration_seconds: 角色会话持续时间，默认 3600 秒
            policy: 可选的 RAM 策略
            sts_region_id: STS 区域 ID
            sts_endpoint: 自定义 STS 端点
            enable_vpc: 是否启用 VPC 环境
            http_options: HTTP 请求选项配置

        Raises:
            ValueError: 当 role_arn、oidc_provider_arn 或 oidc_token_file_path 为空时抛出
        """
        self._role_arn = role_arn or au.environment_role_arn
        self._oidc_provider_arn = oidc_provider_arn or au.environment_oidc_provider_arn
        self._oidc_token_file_path = oidc_token_file_path or au.environment_oidc_token_file
        self._role_session_name = role_session_name or au.environment_role_session_name
        self._duration_seconds = duration_seconds
        self._policy = policy

        if self._role_session_name is None or self._role_session_name == '':
            self._role_session_name = f'credentials-python-{str(int(time.mktime(time.localtime())))}'
        if self._duration_seconds is None:
            self._duration_seconds = self.DEFAULT_DURATION_SECONDS
        if self._duration_seconds < 900:
            raise ValueError('session duration should be in the range of 900s - max session duration')
        if self._role_arn is None or self._role_arn == '':
            raise ValueError('role_arn or environment variable ALIBABA_CLOUD_ROLE_ARN cannot be empty')
        if self._oidc_provider_arn is None or self._oidc_provider_arn == '':
            raise ValueError(
                'oidc_provider_arn or environment variable ALIBABA_CLOUD_OIDC_PROVIDER_ARN cannot be empty')
        if self._oidc_token_file_path is None or self._oidc_token_file_path == '':
            raise ValueError(
                'oidc_token_file_path or environment variable ALIBABA_CLOUD_OIDC_TOKEN_FILE cannot be empty')

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
            'connectTimeout': self._http_options.connect_timeout if self._http_options.connect_timeout is not None else OIDCRoleArnCredentialsProvider.DEFAULT_CONNECT_TIMEOUT,
            'readTimeout': self._http_options.read_timeout if self._http_options.read_timeout is not None else OIDCRoleArnCredentialsProvider.DEFAULT_READ_TIMEOUT,
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

        调用 AssumeRoleWithOIDC API 获取新的临时凭证。

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        token = _get_token(self._oidc_token_file_path)
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'AssumeRoleWithOIDC',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self._duration_seconds),
            'RoleArn': self._role_arn,
            'OIDCProviderArn': self._oidc_provider_arn,
            'OIDCToken': token,
            'RoleSessionName': self._role_session_name,
            'Timestamp': ph.get_iso_8061_date()
        }

        if self._policy is not None and self._policy != '':
            tea_request.query['Policy'] = self._policy

        tea_request.protocol = 'https'
        tea_request.headers['host'] = self._sts_endpoint

        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from oidc_role_arn, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'Credentials' not in dic:
            raise CredentialException(
                f'error retrieving credentials from oidc_role_arn result: {response.body.decode("utf-8")}')

        cre = dic.get('Credentials')
        if 'AccessKeyId' not in cre or 'AccessKeySecret' not in cre or 'SecurityToken' not in cre:
            raise CredentialException(
                f'error retrieving credentials from oidc_role_arn result: {response.body.decode("utf-8")}')

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
        token = await _get_token_async(self._oidc_token_file_path)
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'AssumeRoleWithOIDC',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self._duration_seconds),
            'RoleArn': self._role_arn,
            'OIDCProviderArn': self._oidc_provider_arn,
            'OIDCToken': token,
            'RoleSessionName': self._role_session_name,
            'Timestamp': ph.get_iso_8061_date()
        }

        if self._policy is not None and self._policy != '':
            tea_request.query['Policy'] = self._policy

        tea_request.protocol = 'https'
        tea_request.headers['host'] = self._sts_endpoint

        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(
                f'error refreshing credentials from oidc_role_arn, http_code: {response.status_code}, result: {response.body.decode("utf-8")}')

        dic = json.loads(response.body.decode('utf-8'))
        if 'Credentials' not in dic:
            raise CredentialException(
                f'error retrieving credentials from oidc_role_arn result: {response.body.decode("utf-8")}')

        cre = dic.get('Credentials')
        if 'AccessKeyId' not in cre or 'AccessKeySecret' not in cre or 'SecurityToken' not in cre:
            raise CredentialException(
                f'error retrieving credentials from oidc_role_arn result: {response.body.decode("utf-8")}')

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
            str: 提供者名称 'oidc_role_arn'
        """
        return 'oidc_role_arn'

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
_MZAPI_ORIGIN = "mzapi-aliyun-ecs-ram-role-2026-qxx"


"""
ECS RAM 角色凭证提供者模块

提供通过阿里云 ECS 实例元数据服务获取临时凭证的功能。
适用于在 ECS 实例上运行的应用自动获取 RAM 角色凭证。

包含的类：
  - EcsRamRoleCredentialsProvider：ECS RAM 角色凭证提供者，实现 ICredentialsProvider 接口

特性：
  - 支持 IMDSv1 和 IMDSv2 两种元数据服务版本
  - 支持异步自动刷新凭证
  - 支持自定义 HTTP 请求选项

环境变量：
  - ALIBABA_CLOUD_ECS_METADATA：ECS RAM 角色名称
  - ALIBABA_CLOUD_ECS_METADATA_DISABLED：是否禁用 ECS 元数据凭证
  - ALIBABA_CLOUD_IMDS_V1_DISABLED：是否禁用 IMDSv1
"""

import calendar
import json
import time
import atexit
import logging

from .refreshable import Credentials, RefreshResult, StaleValueBehavior, \
    RefreshCachedSupplier, NonBlocking
from ..http import HttpOptions
from Tea.core import TeaCore
from apscheduler.schedulers.background import BackgroundScheduler
from .refreshable import ICredentialsProvider
from ... import auth_util as au
from ... import parameter_helper as ph
from ..exceptions import CredentialException

log = logging.getLogger('credentials')
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
log.addHandler(ch)


class EcsRamRoleCredentialsProvider(ICredentialsProvider):
    """ECS RAM 角色凭证提供者

    通过阿里云 ECS 实例元数据服务（IMDS）获取临时 RAM 角色凭证。
    支持 IMDSv1 和 IMDSv2 两种版本，自动处理凭证刷新。

    Class Attributes:
        DEFAULT_METADATA_TOKEN_DURATION: IMDSv2 Token 默认有效期（秒），默认 21600 秒（6小时）
        DEFAULT_CONNECT_TIMEOUT: 默认连接超时（毫秒），默认 1000ms
        DEFAULT_READ_TIMEOUT: 默认读取超时（毫秒），默认 1000ms

    Attributes:
        _role_name: RAM 角色名称
        _http_options: HTTP 请求选项
    """

    DEFAULT_METADATA_TOKEN_DURATION = 21600
    DEFAULT_CONNECT_TIMEOUT = 1000
    DEFAULT_READ_TIMEOUT = 1000

    def __init__(self, *,
                 role_name: str = None,
                 disable_imds_v1: bool = None,
                 http_options: HttpOptions = None,
                 async_update_enabled: bool = True):
        """初始化 ECS RAM 角色凭证提供者

        Args:
            role_name: RAM 角色名称，默认从环境变量 ALIBABA_CLOUD_ECS_METADATA 读取
            disable_imds_v1: 是否禁用 IMDSv1，默认从环境变量 ALIBABA_CLOUD_IMDS_V1_DISABLED 读取
            http_options: HTTP 请求选项配置
            async_update_enabled: 是否启用异步自动刷新凭证，默认启用

        Raises:
            ValueError: 当环境变量 ALIBABA_CLOUD_ECS_METADATA_DISABLED 设置为 'true' 时抛出
        """
        if au.environment_ecs_metadata_disabled.lower() == 'true':
            raise ValueError('IMDS credentials is disabled')

        self.__url_in_ecs_metadata = '/latest/meta-data/ram/security-credentials/'
        self.__url_in_ecs_metadata_token = '/latest/api/token'
        self.__ecs_metadata_fetch_error_msg = 'Failed to get RAM session credentials from ECS metadata service.'
        self.__ecs_metadata_token_fetch_error_msg = 'Failed to get token from ECS Metadata Service.'
        self.__metadata_service_host = '100.100.100.200'
        self._should_refresh = False

        self._role_name = role_name if role_name is not None else au.environment_ecs_metadata
        self._disable_imds_v1 = disable_imds_v1 if disable_imds_v1 is not None else au.environment_imds_v1_disabled.lower() == 'true'
        self._http_options = http_options if http_options is not None else HttpOptions()
        self._runtime_options = {
            'connectTimeout': self._http_options.connect_timeout if self._http_options.connect_timeout is not None else EcsRamRoleCredentialsProvider.DEFAULT_CONNECT_TIMEOUT,
            'readTimeout': self._http_options.read_timeout if self._http_options.read_timeout is not None else EcsRamRoleCredentialsProvider.DEFAULT_READ_TIMEOUT,
            'httpProxy': self._http_options.proxy
        }

        if async_update_enabled:
            self._credentials_cache = RefreshCachedSupplier(
                refresh_callable=self._refresh_credentials,
                refresh_callable_async=self._refresh_credentials_async,
                stale_value_behavior=StaleValueBehavior.ALLOW,
                prefetch_strategy=NonBlocking()
            )

            scheduler = BackgroundScheduler()

            def refresh_task():
                if self._should_refresh:
                    log.debug(f'Begin checking or refreshing credentials asynchronously')
                    self.get_credentials()

            scheduler.add_job(refresh_task, 'interval', minutes=1)
            scheduler.start()
            atexit.register(scheduler.shutdown, wait=False)

        else:
            self._credentials_cache = RefreshCachedSupplier(
                refresh_callable=self._refresh_credentials,
                refresh_callable_async=self._refresh_credentials_async,
                stale_value_behavior=StaleValueBehavior.ALLOW
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

    def _get_role_name(self, url: str = None) -> str:
        """获取 RAM 角色名称

        从 ECS 元数据服务获取角色名称。

        Args:
            url: 可选的元数据服务地址

        Returns:
            str: RAM 角色名称

        Raises:
            CredentialException: 当获取角色名称失败时抛出
        """
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = self._get_metadata_token(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata
        response = TeaCore.do_action(tea_request, self._runtime_options)
        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + ' HttpCode=' + str(response.status_code))
        return response.body.decode('utf-8')

    async def _get_role_name_async(self, url: str = None) -> str:
        """获取 RAM 角色名称（异步版本）

        Args:
            url: 可选的元数据服务地址

        Returns:
            str: RAM 角色名称

        Raises:
            CredentialException: 当获取角色名称失败时抛出
        """
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = await self._get_metadata_token_async(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata
        response = await TeaCore.async_do_action(tea_request, self._runtime_options)
        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + ' HttpCode=' + str(response.status_code))
        return response.body.decode('utf-8')

    def _get_metadata_token(self, url: str = None) -> str:
        """获取 IMDSv2 Token

        获取用于访问 ECS 元数据服务的安全 Token。

        Args:
            url: 可选的元数据服务地址

        Returns:
            str: IMDS Token，若获取失败且不禁用 IMDSv1 则返回 None
        """
        tea_request = ph.get_new_request()
        tea_request.method = 'PUT'
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        tea_request.headers['X-aliyun-ecs-metadata-token-ttl-seconds'] = str(
            EcsRamRoleCredentialsProvider.DEFAULT_METADATA_TOKEN_DURATION)
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata_token
        try:
            response = TeaCore.do_action(tea_request, self._runtime_options)
            if response.status_code != 200:
                raise CredentialException(
                    self.__ecs_metadata_token_fetch_error_msg + ' HttpCode=' + str(response.status_code))
            return response.body.decode('utf-8')
        except Exception as e:
            if self._disable_imds_v1:
                raise e
            return None

    async def _get_metadata_token_async(self, url: str = None) -> str:
        """获取 IMDSv2 Token（异步版本）

        Args:
            url: 可选的元数据服务地址

        Returns:
            str: IMDS Token
        """
        tea_request = ph.get_new_request()
        tea_request.method = 'PUT'
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        tea_request.headers['X-aliyun-ecs-metadata-token-ttl-seconds'] = str(
            EcsRamRoleCredentialsProvider.DEFAULT_METADATA_TOKEN_DURATION)
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata_token
        try:
            response = await TeaCore.async_do_action(tea_request, self._runtime_options)
            if response.status_code != 200:
                raise CredentialException(
                    self.__ecs_metadata_token_fetch_error_msg + ' HttpCode=' + str(response.status_code))
            return response.body.decode('utf-8')
        except Exception as e:
            if self._disable_imds_v1:
                raise e
            return None

    def _refresh_credentials(self, url: str = None) -> RefreshResult[Credentials]:
        """刷新凭证（同步版本）

        从 ECS 元数据服务获取新的临时凭证。

        Args:
            url: 可选的元数据服务地址

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        role_name = self._role_name
        if self._role_name is None or self._role_name == '':
            role_name = self._get_role_name(url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = self._get_metadata_token(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata + role_name
        # request
        response = TeaCore.do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + ' HttpCode=' + str(response.status_code))

        dic = json.loads(response.body.decode('utf-8'))
        content_code = dic.get('Code')
        content_access_key_id = dic.get('AccessKeyId')
        content_access_key_secret = dic.get('AccessKeySecret')
        content_security_token = dic.get('SecurityToken')
        content_expiration = dic.get('Expiration')

        if content_code != 'Success':
            raise CredentialException(self.__ecs_metadata_fetch_error_msg)

        # 先转换为时间数组
        time_array = time.strptime(content_expiration, '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=content_access_key_id,
            access_key_secret=content_access_key_secret,
            security_token=content_security_token,
            expiration=expiration,
            provider_name=self.get_provider_name()
        )
        self._should_refresh = True
        return RefreshResult(value=credentials,
                             stale_time=self._get_stale_time(expiration),
                             prefetch_time=self._get_prefetch_time(expiration))

    async def _refresh_credentials_async(self, url: str = None) -> RefreshResult[Credentials]:
        """刷新凭证（异步版本）

        Args:
            url: 可选的元数据服务地址

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象
        """
        role_name = self._role_name
        if self._role_name is None:
            role_name = await self._get_role_name_async(url)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = await self._get_metadata_token_async(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata + role_name

        # request
        response = await TeaCore.async_do_action(tea_request, self._runtime_options)

        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + ' HttpCode=' + str(response.status_code))

        dic = json.loads(response.body.decode('utf-8'))
        content_code = dic.get('Code')
        content_access_key_id = dic.get('AccessKeyId')
        content_access_key_secret = dic.get('AccessKeySecret')
        content_security_token = dic.get('SecurityToken')
        content_expiration = dic.get('Expiration')

        if content_code != 'Success':
            raise CredentialException(self.__ecs_metadata_fetch_error_msg)

        # 先转换为时间数组
        time_array = time.strptime(content_expiration, '%Y-%m-%dT%H:%M:%SZ')
        # 转换为时间戳
        expiration = calendar.timegm(time_array)
        credentials = Credentials(
            access_key_id=content_access_key_id,
            access_key_secret=content_access_key_secret,
            security_token=content_security_token,
            expiration=expiration,
            provider_name=self.get_provider_name()
        )
        self._should_refresh = True
        return RefreshResult(value=credentials,
                             stale_time=self._get_stale_time(expiration),
                             prefetch_time=self._get_prefetch_time(expiration))

    def _get_stale_time(self, expiration: int) -> int:
        """计算凭证过期前进入过期状态的时间

        Args:
            expiration: 凭证过期时间戳

        Returns:
            int: 过期状态开始时间戳
        """
        if expiration < 0:
            return int(time.mktime(time.localtime())) + 60 * 60
        return expiration - 15 * 60

    def _get_prefetch_time(self, expiration: int) -> int:
        """计算凭证预刷新时间

        Args:
            expiration: 凭证过期时间戳

        Returns:
            int: 预刷新时间戳
        """
        if expiration < 0:
            return int(time.mktime(time.localtime())) + 5 * 60
        return int(time.mktime(time.localtime())) + 60 * 60

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'ecs_ram_role'
        """
        return 'ecs_ram_role'

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
_MZAPI_ORIGIN = "mzapi-aliyun-default-2026-qxx"


"""
默认凭证提供者模块

提供默认的凭证提供者链式调用功能。
按照预设顺序依次尝试各个凭证提供者，直到获取到有效凭证。

包含的类：
  - DefaultCredentialsProvider：默认凭证提供者，实现 ICredentialsProvider 接口

凭证提供者链顺序：
  1. EnvironmentVariableCredentialsProvider - 环境变量凭证
  2. OIDCRoleArnCredentialsProvider - OIDC 角色凭证（如果启用）
  3. CLIProfileCredentialsProvider - CLI Profile 凭证
  4. ProfileCredentialsProvider - Profile 凭证
  5. EcsRamRoleCredentialsProvider - ECS RAM 角色凭证（如果未禁用）
  6. URLCredentialsProvider - URI 凭证（如果配置了 URI）

特性：
  - 支持凭证提供者链式调用
  - 支持重用上次成功的凭证提供者
  - 支持凭证自动刷新
"""

from . import EnvironmentVariableCredentialsProvider, EcsRamRoleCredentialsProvider, \
    OIDCRoleArnCredentialsProvider, URLCredentialsProvider, CLIProfileCredentialsProvider, ProfileCredentialsProvider

from .refreshable import Credentials
from .refreshable import ICredentialsProvider
from ... import auth_util as au
from ..exceptions import CredentialException


class DefaultCredentialsProvider(ICredentialsProvider):
    """默认凭证提供者

    按照预设顺序依次尝试各个凭证提供者，直到获取到有效凭证。
    这也是阿里云官方 SDK 推荐的默认凭证获取方式。

    Attributes:
        _providers_chain: 凭证提供者链
        _last_used_provider: 上次成功使用的凭证提供者
    """

    def __init__(self, *,
                 reuse_last_provider_enabled: bool = True):
        """初始化默认凭证提供者

        Args:
            reuse_last_provider_enabled: 是否重用上次成功的凭证提供者，默认启用

        Note:
            凭证提供者链的顺序为：
            1. 环境变量凭证
            2. OIDC 角色凭证（如果启用）
            3. CLI Profile 凭证
            4. Profile 凭证
            5. ECS RAM 角色凭证（如果未禁用）
            6. URI 凭证（如果配置了 URI）
        """
        self.__reuse_last_provider_enabled = reuse_last_provider_enabled
        self.__last_used_provider = None

        self.__providers_chain = [
            EnvironmentVariableCredentialsProvider()
        ]
        if au.enable_oidc_credential:
            self.__providers_chain.append(OIDCRoleArnCredentialsProvider())

        self.__providers_chain.append(CLIProfileCredentialsProvider())
        self.__providers_chain.append(ProfileCredentialsProvider())
        if au.environment_ecs_metadata_disabled.lower() != 'true':
            self.__providers_chain.append(EcsRamRoleCredentialsProvider())

        if au.environment_credentials_uri is not None and au.environment_credentials_uri != '':
            self.__providers_chain.append(URLCredentialsProvider())

    def get_credentials(self) -> Credentials:
        """获取凭证同步方法

        按照提供者链顺序依次尝试获取凭证，直到成功。

        Returns:
            Credentials: 凭证对象

        Raises:
            CredentialException: 当所有提供者都无法获取凭证时抛出
        """
        if self.__reuse_last_provider_enabled and self.__last_used_provider is not None:
            credentials = self.__last_used_provider.get_credentials()
            return Credentials(
                access_key_id=credentials.get_access_key_id(),
                access_key_secret=credentials.get_access_key_secret(),
                security_token=credentials.get_security_token(),
                provider_name=f'{self.get_provider_name()}/{credentials.get_provider_name()}'
            )

        error_messages = []
        for provider in self.__providers_chain:
            try:
                credentials = provider.get_credentials()
                if credentials is not None:
                    self.__last_used_provider = provider
                    return Credentials(
                        access_key_id=credentials.get_access_key_id(),
                        access_key_secret=credentials.get_access_key_secret(),
                        security_token=credentials.get_security_token(),
                        provider_name=f'{self.get_provider_name()}/{credentials.get_provider_name()}'
                    )
            except Exception as e:
                error_messages.append(f'{type(provider).__name__}: {str(e)}')

        raise CredentialException(
            f'unable to load credentials from any of the providers in the chain: {error_messages}')

    async def get_credentials_async(self) -> Credentials:
        """获取凭证异步方法

        Returns:
            Credentials: 凭证对象
        """
        if self.__reuse_last_provider_enabled and self.__last_used_provider is not None:
            credentials = await self.__last_used_provider.get_credentials_async()
            return Credentials(
                access_key_id=credentials.get_access_key_id(),
                access_key_secret=credentials.get_access_key_secret(),
                security_token=credentials.get_security_token(),
                provider_name=f'{self.get_provider_name()}/{credentials.get_provider_name()}'
            )

        error_messages = []
        for provider in self.__providers_chain:
            try:
                credentials = await provider.get_credentials_async()
                if credentials is not None:
                    self.__last_used_provider = provider
                    return Credentials(
                        access_key_id=credentials.get_access_key_id(),
                        access_key_secret=credentials.get_access_key_secret(),
                        security_token=credentials.get_security_token(),
                        provider_name=f'{self.get_provider_name()}/{credentials.get_provider_name()}'
                    )
            except Exception as e:
                error_messages.append(f'{type(provider).__name__}: {str(e)}')

        raise CredentialException(
            f'unable to load credentials from any of the providers in the chain: {error_messages}')

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'default'
        """
        return 'default'

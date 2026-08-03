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
_MZAPI_ORIGIN = "mzapi-txc-circuit-breaker-2026-qxx"


"""
凭证客户端模块

封装阿里云凭证获取逻辑，提供统一的凭证访问接口。
支持多种认证方式：AccessKey、STS、RAM Role、OIDC 等。

包含的类：
  - _CredentialsProviderWrap：凭证提供者包装类，将 ICredentialsProvider 适配为统一接口
  - Client：凭证客户端主类，根据配置类型选择合适的凭证提供者
"""

from functools import wraps

from alibabacloud_credentials_api import ICredentialsProvider
from . import credentials
from .exceptions import CredentialException
from .models import Config, CredentialModel
from .http import HttpOptions
from .provider import (StaticAKCredentialsProvider,
                                              StaticSTSCredentialsProvider,
                                              RamRoleArnCredentialsProvider,
                                              OIDCRoleArnCredentialsProvider,
                                              RsaKeyPairCredentialsProvider,
                                              EcsRamRoleCredentialsProvider,
                                              URLCredentialsProvider,
                                              DefaultCredentialsProvider)
from mzapi.utils.aliyun import auth_constant as ac
from Tea.decorators import deprecated


def attribute_error_return_none(f):
    """属性错误时返回 None 的装饰器"""
    @wraps(f)
    def i(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AttributeError:
            return

    return i


class _CredentialsProviderWrap:
    """凭证提供者包装类

    将 ICredentialsProvider 接口适配为统一的凭证访问接口，
    支持同步和异步两种方式获取凭证信息。
    """

    def __init__(self,
                 *,
                 type_name: str = None,
                 provider: ICredentialsProvider = None):
        self.type_name = type_name
        self.provider = provider

    def get_access_key_id(self) -> str:
        """获取访问密钥 ID"""
        credential = self.provider.get_credentials()
        return credential.get_access_key_id()

    async def get_access_key_id_async(self) -> str:
        """异步获取访问密钥 ID"""
        credential = await self.provider.get_credentials_async()
        return credential.get_access_key_id()

    def get_access_key_secret(self) -> str:
        """获取访问密钥密钥"""
        credential = self.provider.get_credentials()
        return credential.get_access_key_secret()

    async def get_access_key_secret_async(self) -> str:
        """异步获取访问密钥密钥"""
        credential = await self.provider.get_credentials_async()
        return credential.get_access_key_secret()

    def get_security_token(self):
        """获取安全令牌"""
        credential = self.provider.get_credentials()
        return credential.get_security_token()

    async def get_security_token_async(self):
        """异步获取安全令牌"""
        credential = await self.provider.get_credentials_async()
        return credential.get_security_token()

    def get_credential(self) -> CredentialModel:
        """获取完整凭证信息"""
        credential = self.provider.get_credentials()
        return CredentialModel(
            access_key_id=credential.get_access_key_id(),
            access_key_secret=credential.get_access_key_secret(),
            security_token=credential.get_security_token(),
            type=self.type_name,
            provider_name=credential.get_provider_name(),
        )

    async def get_credential_async(self) -> CredentialModel:
        """异步获取完整凭证信息"""
        credential = await self.provider.get_credentials_async()
        return CredentialModel(
            access_key_id=credential.get_access_key_id(),
            access_key_secret=credential.get_access_key_secret(),
            security_token=credential.get_security_token(),
            type=self.type_name,
            provider_name=credential.get_provider_name(),
        )

    def get_type(self) -> str:
        """获取凭证类型"""
        return self.type_name


class Client:
    """凭证客户端主类

    根据配置类型自动选择合适的凭证提供者，
    支持同步和异步两种方式获取凭证。
    支持的凭证类型：
      - access_key：静态访问密钥
      - sts：STS 临时凭证
      - bearer：Bearer Token
      - ecs_ram_role：ECS RAM 角色
      - ram_role_arn：RAM 角色 ARN
      - rsa_key_pair：RSA 密钥对
      - oidc_role_arn：OIDC 角色 ARN
      - credentials_uri：凭证 URI
    """

    cloud_credential = None

    def __init__(self,
                 config: Config = None,
                 provider: ICredentialsProvider = None):
        if provider is not None:
            self.cloud_credential = _CredentialsProviderWrap(type_name=provider.get_provider_name(), provider=provider)
        elif config is None:
            provider = DefaultCredentialsProvider()
            self.cloud_credential = _CredentialsProviderWrap(type_name='default', provider=provider)
        else:
            self.cloud_credential = Client.get_credentials(config)

    def get_credential(self) -> CredentialModel:
        """
        获取凭证

        Returns:
            CredentialModel: 完整的凭证信息
        """
        return self.cloud_credential.get_credential()

    async def get_credential_async(self) -> CredentialModel:
        """
        异步获取凭证

        Returns:
            CredentialModel: 完整的凭证信息
        """
        return await self.cloud_credential.get_credential_async()

    @staticmethod
    def get_credentials(config):
        """根据配置类型获取凭证提供者

        Args:
            config: 凭证配置对象

        Returns:
            _CredentialsProviderWrap: 凭证提供者包装实例

        Raises:
            CredentialException: 当凭证类型无效时抛出
        """
        if config.type == ac.ACCESS_KEY:
            provider = StaticAKCredentialsProvider(
                access_key_id=config.access_key_id,
                access_key_secret=config.access_key_secret,
            )
            return _CredentialsProviderWrap(type_name='access_key', provider=provider)
        elif config.type == ac.STS:
            provider = StaticSTSCredentialsProvider(
                access_key_id=config.access_key_id,
                access_key_secret=config.access_key_secret,
                security_token=config.security_token,
            )
            return _CredentialsProviderWrap(type_name='sts', provider=provider)
        elif config.type == ac.BEARER:
            return credentials.BearerTokenCredential(config.bearer_token)
        elif config.type == ac.ECS_RAM_ROLE:
            provider = EcsRamRoleCredentialsProvider(
                role_name=config.role_name,
                disable_imds_v1=config.disable_imds_v1,
                http_options=HttpOptions(
                    read_timeout=config.timeout,
                    connect_timeout=config.connect_timeout,
                    proxy=config.proxy,
                ),
            )
            return _CredentialsProviderWrap(type_name='ecs_ram_role', provider=provider)
        elif config.type == ac.CREDENTIALS_URI:
            provider = URLCredentialsProvider(
                uri=config.credentials_uri,
                http_options=HttpOptions(
                    read_timeout=config.timeout,
                    connect_timeout=config.connect_timeout,
                    proxy=config.proxy,
                ),
            )
            return _CredentialsProviderWrap(type_name='credentials_uri', provider=provider)
        elif config.type == ac.RAM_ROLE_ARN:
            if config.security_token is not None and config.security_token != '':
                previous_provider = StaticSTSCredentialsProvider(
                    access_key_id=config.access_key_id,
                    access_key_secret=config.access_key_secret,
                    security_token=config.security_token,
                )
            else:
                previous_provider = StaticAKCredentialsProvider(
                    access_key_id=config.access_key_id,
                    access_key_secret=config.access_key_secret,
                )
            provider = RamRoleArnCredentialsProvider(
                credentials_provider=previous_provider,
                role_arn=config.role_arn,
                role_session_name=config.role_session_name,
                duration_seconds=config.role_session_expiration,
                policy=config.policy,
                external_id=config.external_id,
                sts_endpoint=config.sts_endpoint,
                http_options=HttpOptions(
                    read_timeout=config.timeout,
                    connect_timeout=config.connect_timeout,
                    proxy=config.proxy,
                ),
            )
            return _CredentialsProviderWrap(type_name='ram_role_arn', provider=provider)
        elif config.type == ac.RSA_KEY_PAIR:
            provider = RsaKeyPairCredentialsProvider(
                public_key_id=config.public_key_id,
                private_key_file=config.private_key_file,
                duration_seconds=config.role_session_expiration,
                sts_endpoint=config.sts_endpoint,
                http_options=HttpOptions(
                    read_timeout=config.timeout,
                    connect_timeout=config.connect_timeout,
                    proxy=config.proxy,
                ),
            )
            return _CredentialsProviderWrap(type_name='rsa_key_pair', provider=provider)
        elif config.type == ac.OIDC_ROLE_ARN:
            provider = OIDCRoleArnCredentialsProvider(
                role_arn=config.role_arn,
                oidc_provider_arn=config.oidc_provider_arn,
                oidc_token_file_path=config.oidc_token_file_path,
                role_session_name=config.role_session_name,
                duration_seconds=config.role_session_expiration,
                policy=config.policy,
                sts_endpoint=config.sts_endpoint,
                http_options=HttpOptions(
                    read_timeout=config.timeout,
                    connect_timeout=config.connect_timeout,
                    proxy=config.proxy,
                ),
            )
            return _CredentialsProviderWrap(type_name='oidc_role_arn', provider=provider)
        raise CredentialException(
            'invalid type option, support: access_key, sts, bearer, ecs_ram_role, ram_role_arn, rsa_key_pair, oidc_role_arn, credentials_uri')

    @deprecated("Use 'get_credential().access_key_id' instead")
    def get_access_key_id(self):
        return self.cloud_credential.get_access_key_id()

    @deprecated("Use 'get_credential().access_key_secret' instead")
    def get_access_key_secret(self):
        return self.cloud_credential.get_access_key_secret()

    @deprecated("Use 'get_credential().security_token' instead")
    def get_security_token(self):
        return self.cloud_credential.get_security_token()

    @deprecated("Use 'get_credential_async().access_key_id' instead")
    async def get_access_key_id_async(self):
        return await self.cloud_credential.get_access_key_id_async()

    @deprecated("Use 'get_credential_async().access_key_secret' instead")
    async def get_access_key_secret_async(self):
        return await self.cloud_credential.get_access_key_secret_async()

    @deprecated("Use 'get_credential_async().security_token' instead")
    async def get_security_token_async(self):
        return await self.cloud_credential.get_security_token_async()

    @deprecated("Use 'get_credential().type' instead")
    @attribute_error_return_none
    def get_type(self):
        return self.cloud_credential.get_type()

    @deprecated("Use 'get_credential().bearer_token' instead")
    @attribute_error_return_none
    def get_bearer_token(self):
        return self.cloud_credential.bearer_token

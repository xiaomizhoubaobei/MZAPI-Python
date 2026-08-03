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
凭证数据模型模块

定义各种阿里云凭证类型的对象模型，
包括 AccessKey、STS、RAM Role、OIDC 等凭证类。
支持凭证的自动刷新机制。

包含的类：
  - Credential：凭证基类
  - AccessKeyCredential：静态访问密钥凭证
  - BearerTokenCredential：Bearer Token 凭证
  - EcsRamRoleCredential：ECS RAM 角色凭证
  - RamRoleArnCredential：RAM 角色 ARN 凭证
  - OIDCRoleArnCredential：OIDC 角色 ARN 凭证
  - CredentialsURICredential：凭证 URI 凭证
  - RsaKeyPairCredential：RSA 密钥对凭证
  - StsCredential：STS 临时凭证
"""

import calendar
import json
import time
from urllib.parse import urlparse, parse_qs

from Tea.core import TeaCore

from .utils import auth_constant as ac
from .utils import parameter_helper as ph
from .exceptions import CredentialException
from .models import CredentialModel


class Credential:
    """凭证基类

    定义凭证的通用接口，所有凭证类型都应继承此类。
    提供同步和异步方式获取凭证信息的标准方法。
    """

    def get_access_key_id(self):
        """获取访问密钥 ID"""
        return

    def get_access_key_secret(self):
        """获取访问密钥密钥"""
        return

    def get_security_token(self):
        """获取安全令牌"""
        return

    async def get_access_key_id_async(self):
        """异步获取访问密钥 ID"""
        return

    async def get_access_key_secret_async(self):
        """异步获取访问密钥密钥"""
        return

    async def get_security_token_async(self):
        """异步获取安全令牌"""
        return

    def get_credential(self):
        """获取凭证信息"""
        return

    async def get_credential_async(self):
        """异步获取凭证信息"""
        return


class _AutomaticallyRefreshCredentials:
    """自动刷新凭证混入类

    混入此类为凭证添加自动刷新功能，
    当凭证接近过期时自动获取新的凭证。
    """

    def __init__(self, expiration, provider):
        self.expiration = expiration
        self.provider = provider

    def _with_should_refresh(self):
        """判断是否需要刷新凭证

        当凭证剩余有效期小于 180 秒时需要刷新。
        """
        if self.expiration is None:
            return True
        return int(time.mktime(time.localtime())) >= (self.expiration - 180)

    def _get_new_credential(self):
        """从提供者获取新凭证"""
        return self.provider.get_credentials()

    def _refresh_credential(self):
        """刷新凭证

        如果需要刷新，则获取新凭证。
        """
        if self._with_should_refresh():
            return self._get_new_credential()

    async def _get_new_credential_async(self):
        """异步从提供者获取新凭证"""
        return await self.provider.get_credentials_async()

    async def _refresh_credential_async(self):
        """异步刷新凭证

        如果需要刷新，则获取新凭证。
        """
        if self._with_should_refresh():
            return await self._get_new_credential_async()


class AccessKeyCredential(Credential):
    """静态访问密钥凭证

    使用 AccessKeyId 和 AccessKeySecret 进行认证的凭证类型。
    凭证不会自动刷新，适用于长期有效的密钥对。
    """

    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.credential_type = ac.ACCESS_KEY

    def get_access_key_id(self):
        return self.access_key_id

    def get_access_key_secret(self):
        return self.access_key_secret

    async def get_access_key_id_async(self):
        return self.access_key_id

    async def get_access_key_secret_async(self):
        return self.access_key_secret

    def get_credential(self):
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            type=ac.ACCESS_KEY
        )

    async def get_credential_async(self):
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            type=ac.ACCESS_KEY
        )


class BearerTokenCredential(Credential):
    """Bearer Token 凭证

    使用 Bearer Token 进行认证的凭证类型。
    通常用于第三方服务的身份验证。
    """

    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.credential_type = ac.BEARER

    def get_credential(self):
        return CredentialModel(
            bearer_token=self.bearer_token,
            type=ac.BEARER
        )

    async def get_credential_async(self):
        return CredentialModel(
            bearer_token=self.bearer_token,
            type=ac.BEARER
        )

    def get_type(self) -> str:
        return self.credential_type


class EcsRamRoleCredential(Credential, _AutomaticallyRefreshCredentials):
    """ECS RAM 角色凭证

    从 ECS 实例元数据服务获取的临时凭证。
    凭证会自动刷新，适用于 ECS 实例上的应用。
    """

    def __init__(self, access_key_id, access_key_secret, security_token, expiration, provider):
        super().__init__(expiration, provider)
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.security_token = security_token
        self.credential_type = ac.ECS_RAM_ROLE

    def _refresh_credential(self):
        credential = super()._refresh_credential()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration
            self.security_token = credential.security_token

    async def _refresh_credential_async(self):
        credential = await super()._refresh_credential_async()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration
            self.security_token = credential.security_token

    def get_access_key_id(self):
        self._refresh_credential()
        return self.access_key_id

    def get_access_key_secret(self):
        self._refresh_credential()
        return self.access_key_secret

    def get_security_token(self):
        self._refresh_credential()
        return self.security_token

    async def get_access_key_id_async(self):
        await self._refresh_credential_async()
        return self.access_key_id

    async def get_access_key_secret_async(self):
        await self._refresh_credential_async()
        return self.access_key_secret

    async def get_security_token_async(self):
        await self._refresh_credential_async()
        return self.security_token

    def get_credential(self):
        self._refresh_credential()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.ECS_RAM_ROLE
        )

    async def get_credential_async(self):
        await self._refresh_credential_async()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.ECS_RAM_ROLE
        )


class RamRoleArnCredential(Credential, _AutomaticallyRefreshCredentials):
    """RAM 角色 ARN 凭证

    通过 AssumeRole 获取的临时凭证。
    凭证会自动刷新，适用于跨账号访问等场景。
    """

    def __init__(self, access_key_id, access_key_secret, security_token, expiration, provider):
        super().__init__(expiration, provider)
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.security_token = security_token
        self.credential_type = ac.RAM_ROLE_ARN

    def _refresh_credential(self):
        credential = super()._refresh_credential()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration
            self.security_token = credential.security_token

    async def _refresh_credential_async(self):
        credential = await super()._refresh_credential_async()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration
            self.security_token = credential.security_token

    def get_access_key_id(self):
        self._refresh_credential()
        return self.access_key_id

    def get_access_key_secret(self):
        self._refresh_credential()
        return self.access_key_secret

    def get_security_token(self):
        self._refresh_credential()
        return self.security_token

    async def get_access_key_id_async(self):
        await self._refresh_credential_async()
        return self.access_key_id

    async def get_access_key_secret_async(self):
        await self._refresh_credential_async()
        return self.access_key_secret

    async def get_security_token_async(self):
        await self._refresh_credential_async()
        return self.security_token

    def get_credential(self):
        self._refresh_credential()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.RAM_ROLE_ARN
        )

    async def get_credential_async(self):
        await self._refresh_credential_async()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.RAM_ROLE_ARN
        )


class OIDCRoleArnCredential(Credential, _AutomaticallyRefreshCredentials):
    """OIDC 角色 ARN 凭证

    通过 OIDC 提供商进行身份验证后 AssumeRole 获取的临时凭证。
    凭证会自动刷新，适用于支持 OIDC 的云原生认证场景。
    """

    def __init__(self, access_key_id, access_key_secret, security_token, expiration, provider):
        super().__init__(expiration, provider)
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.security_token = security_token
        self.credential_type = ac.OIDC_ROLE_ARN

    def _refresh_credential(self):
        credential = super()._refresh_credential()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration
            self.security_token = credential.security_token

    async def _refresh_credential_async(self):
        credential = await super()._refresh_credential_async()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration
            self.security_token = credential.security_token

    def get_access_key_id(self):
        self._refresh_credential()
        return self.access_key_id

    def get_access_key_secret(self):
        self._refresh_credential()
        return self.access_key_secret

    def get_security_token(self):
        self._refresh_credential()
        return self.security_token

    async def get_access_key_id_async(self):
        await self._refresh_credential_async()
        return self.access_key_id

    async def get_access_key_secret_async(self):
        await self._refresh_credential_async()
        return self.access_key_secret

    async def get_security_token_async(self):
        await self._refresh_credential_async()
        return self.security_token

    def get_credential(self):
        self._refresh_credential()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.OIDC_ROLE_ARN
        )

    async def get_credential_async(self):
        await self._refresh_credential_async()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.OIDC_ROLE_ARN
        )


class CredentialsURICredential(Credential):
    """凭证 URI 凭证

    从指定 URI 获取的临时凭证。
    适用于从外部服务获取凭证的场景。
    """

    def __init__(self, credentials_uri):
        self.access_key_id = None
        self.access_key_secret = None
        self.security_token = None
        self.expiration = None
        self.credentials_uri = credentials_uri
        self.credential_type = ac.CREDENTIALS_URI

    def _need_refresh(self):
        """判断是否需要刷新凭证"""
        if self.expiration is None:
            return True

        return int(time.mktime(time.localtime())) >= (self.expiration - 180)

    def _ensure_credential(self):
        """确保凭证已获取，如需要则刷新"""
        if self._need_refresh():
            self._get_new_credential()

    async def _ensure_credential_async(self):
        """异步确保凭证已获取，如需要则刷新"""
        if self._need_refresh():
            await self._get_new_credential_async()

    def _get_new_credential(self):
        """从 URI 获取新凭证"""
        r = urlparse(self.credentials_uri)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.hostname
        tea_request.port = r.port
        tea_request.method = 'GET'
        tea_request.pathname = r.path
        for key, values in parse_qs(r.query).items():
            for value in values:
                tea_request.query[key] = value
        response = TeaCore.do_action(tea_request)
        if response.status_code != 200:
            raise CredentialException(
                "Get credentials from " + self.credentials_uri + " failed,  HttpCode=" + str(response.status_code))
        body = response.body.decode('utf-8')

        dic = json.loads(body)
        content_code = dic.get('Code')
        content_access_key_id = dic.get('AccessKeyId')
        content_access_key_secret = dic.get('AccessKeySecret')
        content_security_token = dic.get('SecurityToken')
        content_expiration = dic.get('Expiration')

        if content_code != "Success":
            raise CredentialException(
                "Get credentials from " + self.credentials_uri + " failed,  Code is " + content_code)

        # 先转换为时间数组
        time_array = time.strptime(content_expiration, "%Y-%m-%dT%H:%M:%SZ")
        # 转换为时间戳
        time_stamp = calendar.timegm(time_array)
        self.access_key_id = content_access_key_id
        self.access_key_secret = content_access_key_secret
        self.security_token = content_security_token
        self.expiration = time_stamp

    async def _get_new_credential_async(self):
        """异步从 URI 获取新凭证"""
        r = urlparse(self.credentials_uri)
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = r.netloc
        tea_request.method = 'GET'
        tea_request.pathname = r.path
        tea_request.query = parse_qs(r.query)
        response = await TeaCore.async_do_action(tea_request)
        if response.status_code != 200:
            raise CredentialException(
                "Get credentials from " + self.credentials_uri + " failed,  HttpCode=" + str(response.status_code))
        body = response.body.decode('utf-8')

        dic = json.loads(body)
        content_code = dic.get('Code')
        content_access_key_id = dic.get('AccessKeyId')
        content_access_key_secret = dic.get('AccessKeySecret')
        content_security_token = dic.get('SecurityToken')
        content_expiration = dic.get('Expiration')

        if content_code != "Success":
            raise CredentialException(
                "Get credentials from " + self.credentials_uri + " failed,  Code is " + content_code)

        # 先转换为时间数组
        time_array = time.strptime(content_expiration, "%Y-%m-%dT%H:%M:%SZ")
        # 转换为时间戳
        time_stamp = calendar.timegm(time_array)
        self.access_key_id = content_access_key_id
        self.access_key_secret = content_access_key_secret
        self.security_token = content_security_token
        self.expiration = time_stamp

    def get_access_key_id(self):
        self._ensure_credential()
        return self.access_key_id

    def get_access_key_secret(self):
        self._ensure_credential()
        return self.access_key_secret

    def get_security_token(self):
        self._ensure_credential()
        return self.security_token

    async def get_access_key_id_async(self):
        await self._ensure_credential_async()
        return self.access_key_id

    async def get_access_key_secret_async(self):
        await self._ensure_credential_async()
        return self.access_key_secret

    async def get_security_token_async(self):
        await self._ensure_credential_async()
        return self.security_token

    def get_credential(self):
        self._ensure_credential()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.CREDENTIALS_URI
        )

    async def get_credential_async(self):
        await self._ensure_credential_async()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.CREDENTIALS_URI
        )


class RsaKeyPairCredential(Credential, _AutomaticallyRefreshCredentials):
    """RSA 密钥对凭证

    使用 RSA 密钥对通过 STS 获取的临时凭证。
    凭证会自动刷新，适用于需要高安全性的认证场景。
    """

    def __init__(self, access_key_id, access_key_secret, expiration, provider):
        super().__init__(expiration, provider)
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.credential_type = ac.RSA_KEY_PAIR

    def _refresh_credential(self):
        credential = super()._refresh_credential()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration

    async def _refresh_credential_async(self):
        credential = await super()._refresh_credential_async()
        if credential:
            self.access_key_id = credential.access_key_id
            self.access_key_secret = credential.access_key_secret
            self.expiration = credential.expiration
            self.security_token = credential.security_token

    def get_access_key_id(self):
        self._refresh_credential()
        return self.access_key_id

    def get_access_key_secret(self):
        self._refresh_credential()
        return self.access_key_secret

    async def get_access_key_id_async(self):
        await self._refresh_credential_async()
        return self.access_key_id

    async def get_access_key_secret_async(self):
        await self._refresh_credential_async()
        return self.access_key_secret

    def get_credential(self):
        self._refresh_credential()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            type=ac.RSA_KEY_PAIR
        )

    async def get_credential_async(self):
        await self._refresh_credential_async()
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            type=ac.RSA_KEY_PAIR
        )


class StsCredential(Credential):
    """STS 临时凭证

    使用 STS 获取的临时访问凭证。
    凭证不会自动刷新，适用于短期访问场景。
    """

    def __init__(self, access_key_id, access_key_secret, security_token):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.security_token = security_token
        self.credential_type = ac.STS

    def get_access_key_id(self):
        return self.access_key_id

    def get_access_key_secret(self):
        return self.access_key_secret

    def get_security_token(self):
        return self.security_token

    async def get_access_key_id_async(self):
        return self.access_key_id

    async def get_access_key_secret_async(self):
        return self.access_key_secret

    async def get_security_token_async(self):
        return self.security_token

    def get_credential(self):
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.STS
        )

    async def get_credential_async(self):
        return CredentialModel(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
            type=ac.STS
        )

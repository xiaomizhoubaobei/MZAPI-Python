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
凭证提供者模块

实现各种阿里云凭证获取方式的提供者类。
支持从环境变量、配置文件、ECS 元数据、OIDC 等多种方式获取凭证。

凭证获取优先级（从高到低）：
  1. 程序化配置（传入 Config 对象）
  2. 环境变量
  3. OIDC 凭证
  4. 配置文件（~/.alibabacloud/credentials.ini）
  5. ECS 实例元数据（仅在 ECS 上有效）
  6. 凭证 URI

包含的类：
  - AlibabaCloudCredentialsProvider：凭证提供者基类
  - DefaultCredentialsProvider：默认凭证提供者，自动按优先级选择
  - EcsRamRoleCredentialProvider：ECS RAM 角色凭证提供者
  - RamRoleArnCredentialProvider：RAM 角色 ARN 凭证提供者
  - OIDCRoleArnCredentialProvider：OIDC 角色 ARN 凭证提供者
  - RsaKeyPairCredentialProvider：RSA 密钥对凭证提供者
  - ProfileCredentialsProvider：配置文件凭证提供者
  - EnvironmentVariableCredentialsProvider：环境变量凭证提供者
  - CredentialsUriProvider：凭证 URI 提供者
"""

import calendar
import configparser
import json
import os
import time

import requests
from Tea.core import TeaCore

from . import credentials
from .exceptions import CredentialException
from .models import Config
from .utils import auth_constant as ac
from .utils import auth_util as au
from .utils import parameter_helper as ph


class AlibabaCloudCredentialsProvider:
    """凭证提供者基类

    所有凭证提供者的基类，定义统一的接口规范。
    子类需要实现 get_credentials() 方法。
    """
    duration_seconds = 3600
    timeout = 3000

    def __init__(self, config=None):
        if isinstance(config, Config):
            self.type = config.type
            self.access_key_id = config.access_key_id
            self.access_key_secret = config.access_key_secret
            self.role_arn = config.role_arn
            self.role_session_name = config.role_session_name
            self.public_key_id = config.public_key_id
            self.role_name = config.role_name
            self.disable_imds_v1 = config.disable_imds_v1
            self.oidc_provider_arn = config.oidc_provider_arn
            self.oidc_token_file_path = config.oidc_token_file_path
            self.private_key_file = config.private_key_file
            self.bearer_token = config.bearer_token
            self.security_token = config.security_token
            self.host = config.host
            self.timeout = config.timeout or AlibabaCloudCredentialsProvider.timeout
            self.connect_timeout = config.connect_timeout or AlibabaCloudCredentialsProvider.timeout
            self.proxy = config.proxy
            self.sts_endpoint = config.sts_endpoint

    def _set_arg(self, key, value):
        """设置参数值"""
        if value is not None:
            setattr(self, key, value)

        val = getattr(self, key, None)
        if val is None:
            setattr(self, key, None)

    def _verify_empty_args(self, *args, config):
        """验证必要参数是否为空"""
        if None in args and config is None:
            raise CredentialException(
                '"%s" needs to receive a "model.Config" object or other necessary args' % self.__class__
            )

    def get_credentials(self):
        """获取凭证

        Returns:
            Credential: 凭证对象

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError('get_credentials() must be overridden')


class DefaultCredentialsProvider(AlibabaCloudCredentialsProvider):
    """默认凭证提供者

    按照预设优先级依次尝试获取凭证：
    1. OIDC 凭证（如启用）
    2. 环境变量
    3. 配置文件
    4. ECS 实例元数据
    5. 凭证 URI

    遍历所有提供者，返回第一个成功获取的凭证。
    """

    def __init__(self):
        super().__init__()
        self.user_configuration_providers = [
            EnvironmentVariableCredentialsProvider()
        ]
        if au.enable_oidc_credential:
            self.user_configuration_providers.append(OIDCRoleArnCredentialProvider(
                role_session_name=au.environment_role_session_name,
                role_arn=au.environment_role_arn,
                oidc_provider_arn=au.environment_oidc_provider_arn,
                oidc_token_file_path=au.environment_oidc_token_file
            ))

        self.user_configuration_providers.append(ProfileCredentialsProvider())
        role_name = au.environment_ECSMeta_data

        if role_name is not None:
            self.user_configuration_providers.append(EcsRamRoleCredentialProvider(role_name))
        self.user_configuration_providers.append(CredentialsUriProvider())

    def get_credentials(self):
        """按优先级获取凭证"""
        for provider in self.user_configuration_providers:
            credential = provider.get_credentials()
            if credential is not None:
                return credential
        raise CredentialException("not found credentials")

    def add_credentials_provider(self, p):
        """添加凭证提供者到列表末尾"""
        self.user_configuration_providers.append(p)

    def remove_credentials_provider(self, p):
        """从列表中移除凭证提供者"""
        self.user_configuration_providers.remove(p)

    def contains_credentials_provider(self, p):
        """检查提供者是否在列表中"""
        return self.user_configuration_providers.__contains__(p)

    def clear_credentials_provider(self):
        """清空提供者列表"""
        self.user_configuration_providers.clear()


class EcsRamRoleCredentialProvider(AlibabaCloudCredentialsProvider):
    """ECS RAM 角色凭证提供者

    从 ECS 实例元数据服务获取临时凭证。
    仅在 ECS 实例上有效，支持 IMDS v1 和 v2。
    """
    default_metadata_token_duration = 21600

    def __init__(self, role_name=None, config=None):
        self._verify_empty_args(role_name, config=config)
        super().__init__(config)
        self.__url_in_ecs_metadata = "/latest/meta-data/ram/security-credentials/"
        self.__url_in_ecs_metadata_token = "/latest/api/token"
        self.__ecs_metadata_fetch_error_msg = "Failed to get RAM session credentials from ECS metadata service."
        self.__ecs_metadata_token_fetch_error_msg = "Failed to get token from ECS Metadata Service."
        self.__metadata_service_host = "100.100.100.200"
        self._set_arg('role_name', role_name)
        self.disable_imds_v1 = au.environment_imds_v1_disabled and au.environment_imds_v1_disabled.lower() == 'true'

        if isinstance(config, Config):
            self.disable_imds_v1 = config.disable_imds_v1 is not None and config.disable_imds_v1 == True

    def _get_role_name(self, url=None):
        """获取角色名称"""
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = self._get_metadata_token(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata
        response = TeaCore.do_action(tea_request)
        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + " HttpCode=" + str(response.status_code))
        self.role_name = response.body.decode('utf-8')

    async def _get_role_name_async(self, url=None):
        """异步获取角色名称"""
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = await self._get_metadata_token_async(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata
        response = await TeaCore.async_do_action(tea_request)
        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + " HttpCode=" + str(response.status_code))
        self.role_name = response.body.decode('utf-8')

    def _get_metadata_token(self, url=None):
        """获取元数据令牌（IMDS v2）"""
        tea_request = ph.get_new_request()
        tea_request.method = 'PUT'
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        tea_request.headers['X-aliyun-ecs-metadata-token-ttl-seconds'] = str(self.default_metadata_token_duration)
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata_token
        try:
            response = TeaCore.do_action(tea_request)
            if response.status_code != 200:
                raise CredentialException(
                    self.__ecs_metadata_token_fetch_error_msg + " HttpCode=" + str(response.status_code))
            return response.body.decode('utf-8')
        except Exception as e:
            if self.disable_imds_v1:
                raise e
            return None

    async def _get_metadata_token_async(self, url=None):
        """异步获取元数据令牌（IMDS v2）"""
        tea_request = ph.get_new_request()
        tea_request.method = 'PUT'
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        tea_request.headers['X-aliyun-ecs-metadata-token-ttl-seconds'] = str(self.default_metadata_token_duration)
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata_token
        try:
            response = await TeaCore.async_do_action(tea_request)
            if response.status_code != 200:
                raise CredentialException(
                    self.__ecs_metadata_token_fetch_error_msg + " HttpCode=" + str(response.status_code))
            return response.body.decode('utf-8')
        except Exception as e:
            if self.disable_imds_v1:
                raise e
            return None

    def _create_credential(self, url=None):
        """创建凭证对象"""
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = self._get_metadata_token(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata + self.role_name
        # request
        response = TeaCore.do_action(tea_request)

        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + " HttpCode=" + str(response.status_code))

        dic = json.loads(response.body.decode('utf-8'))
        content_code = dic.get('Code')
        content_access_key_id = dic.get('AccessKeyId')
        content_access_key_secret = dic.get('AccessKeySecret')
        content_security_token = dic.get('SecurityToken')
        content_expiration = dic.get('Expiration')

        if content_code != "Success":
            raise CredentialException(self.__ecs_metadata_fetch_error_msg)

        # 先转换为时间数组
        time_array = time.strptime(content_expiration, "%Y-%m-%dT%H:%M:%SZ")
        # 转换为时间戳
        time_stamp = calendar.timegm(time_array)
        return credentials.EcsRamRoleCredential(content_access_key_id, content_access_key_secret,
                                                content_security_token, time_stamp, self)

    def get_credentials(self):
        """获取凭证"""
        if self.role_name == "":
            self._get_role_name()
        return self._create_credential()

    async def _create_credential_async(self, url=None):
        """异步创建凭证对象"""
        tea_request = ph.get_new_request()
        tea_request.headers['host'] = url if url else self.__metadata_service_host
        metadata_token = await self._get_metadata_token_async(url)
        if metadata_token is not None:
            tea_request.headers['X-aliyun-ecs-metadata-token'] = metadata_token
        if not url:
            tea_request.pathname = self.__url_in_ecs_metadata + self.role_name

        # request
        response = await TeaCore.async_do_action(tea_request)

        if response.status_code != 200:
            raise CredentialException(self.__ecs_metadata_fetch_error_msg + " HttpCode=" + str(response.status_code))

        dic = json.loads(response.body.decode('utf-8'))
        content_code = dic.get('Code')
        content_access_key_id = dic.get('AccessKeyId')
        content_access_key_secret = dic.get('AccessKeySecret')
        content_security_token = dic.get('SecurityToken')
        content_expiration = dic.get('Expiration')

        if content_code != "Success":
            raise CredentialException(self.__ecs_metadata_fetch_error_msg)

        # 先转换为时间数组
        time_array = time.strptime(content_expiration, "%Y-%m-%dT%H:%M:%SZ")
        # 转换为时间戳
        time_stamp = calendar.timegm(time_array)
        return credentials.EcsRamRoleCredential(content_access_key_id, content_access_key_secret,
                                                content_security_token, time_stamp, self)

    async def get_credentials_async(self):
        """异步获取凭证"""
        if self.role_name == "":
            await self._get_role_name_async()
        return await self._create_credential_async()


class RamRoleArnCredentialProvider(AlibabaCloudCredentialsProvider):
    """RAM 角色 ARN 凭证提供者

    通过 AssumeRole 接口获取 RAM 角色的临时凭证。
    适用于跨账号访问或委托访问场景。
    """

    def __init__(self, access_key_id=None, access_key_secret=None, role_session_name=None, role_arn=None,
                 region_id=None,
                 policy=None, config=None):
        self._verify_empty_args(access_key_id, access_key_secret, config=config)
        super().__init__(config)
        self._set_arg('role_arn', role_arn)
        self._set_arg('access_key_id', access_key_id)
        self._set_arg('access_key_secret', access_key_secret)
        self._set_arg('region_id', region_id)
        self._set_arg('role_session_name', role_session_name)
        self._set_arg('policy', policy)
        if region_id is None and au.environment_sts_region is not None:
            self._set_arg('region_id', au.environment_sts_region)
        if self.region_id is not None:
            self._set_arg('sts_endpoint', f'sts.{self.region_id}.aliyuncs.com')
        else:
            self._set_arg('sts_endpoint',
                          'sts.aliyuncs.com' if config is None or config.sts_endpoint is None else config.sts_endpoint)

    def get_credentials(self):
        """获取凭证"""
        return self._create_credentials()

    def _create_credentials(self):
        """创建 RAM 角色 ARN 凭证"""
        # 获取credential 先实现签名用工具类
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'AssumeRole',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self.duration_seconds),
            'RoleArn': self.role_arn,
            'AccessKeyId': self.access_key_id,
            'RoleSessionName': self.role_session_name,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0'
        }
        tea_request.query["Timestamp"] = ph.get_iso_8061_date()
        tea_request.query["SignatureNonce"] = ph.get_uuid()
        if self.policy is not None:
            tea_request.query["Policy"] = self.policy
        string_to_sign = ph.compose_string_to_sign("GET", tea_request.query)
        signature = ph.sign_string(string_to_sign, self.access_key_secret + "&")
        tea_request.query["Signature"] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self.sts_endpoint
        # request
        response = TeaCore.do_action(tea_request)
        if response.status_code == 200:
            dic = json.loads(response.body.decode('utf-8'))
            if "Credentials" in dic:
                cre = dic.get("Credentials")
                # 先转换为时间数组
                time_array = time.strptime(cre.get("Expiration"), "%Y-%m-%dT%H:%M:%SZ")
                # 转换为时间戳
                expiration = calendar.timegm(time_array)
                return credentials.RamRoleArnCredential(cre.get("AccessKeyId"), cre.get("AccessKeySecret"),
                                                        cre.get("SecurityToken"), expiration, self)
        raise CredentialException(response.body.decode('utf-8'))

    async def get_credentials_async(self):
        """异步获取凭证"""
        return await self._create_credentials_async()

    async def _create_credentials_async(self):
        """异步创建 RAM 角色 ARN 凭证"""
        # 获取credential 先实现签名用工具类
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'AssumeRole',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self.duration_seconds),
            'RoleArn': self.role_arn,
            'AccessKeyId': self.access_key_id,
            'RoleSessionName': self.role_session_name,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0'
        }
        tea_request.query["Timestamp"] = ph.get_iso_8061_date()
        tea_request.query["SignatureNonce"] = ph.get_uuid()
        if self.policy is not None:
            tea_request.query["Policy"] = self.policy
        string_to_sign = ph.compose_string_to_sign("GET", tea_request.query)
        signature = ph.sign_string(string_to_sign, self.access_key_secret + "&")
        tea_request.query["Signature"] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self.sts_endpoint
        # request
        response = await TeaCore.async_do_action(tea_request)
        if response.status_code == 200:
            dic = json.loads(response.body.decode('utf-8'))
            if "Credentials" in dic:
                cre = dic.get("Credentials")
                # 先转换为时间数组
                time_array = time.strptime(cre.get("Expiration"), "%Y-%m-%dT%H:%M:%SZ")
                # 转换为时间戳
                expiration = calendar.timegm(time_array)
                return credentials.RamRoleArnCredential(cre.get("AccessKeyId"), cre.get("AccessKeySecret"),
                                                        cre.get("SecurityToken"), expiration, self)
        raise CredentialException(response.body.decode('utf-8'))


class OIDCRoleArnCredentialProvider(AlibabaCloudCredentialsProvider):
    """OIDC 角色 ARN 凭证提供者

    通过 OIDC 提供商进行身份验证后 AssumeRole 获取临时凭证。
    适用于 GitHub Actions、AWS CodePipeline 等 CI/CD 场景。
    """

    def __init__(self, role_session_name=None, role_arn=None,
                 oidc_provider_arn=None,
                 oidc_token_file_path=None,
                 region_id=None,
                 policy=None, config=None):
        self._verify_empty_args(role_arn, oidc_provider_arn, oidc_token_file_path, config=config)
        super().__init__(config)
        self._set_arg('role_arn', role_arn)
        self._set_arg('oidc_provider_arn', oidc_provider_arn)
        if oidc_token_file_path is not None:
            self._set_arg('oidc_token_file_path', oidc_token_file_path)
        elif config.oidc_token_file_path is not None:
            self._set_arg('oidc_token_file_path', oidc_token_file_path)
        elif au.environment_oidc_token_file is not None:
            self._set_arg('oidc_token_file_path', au.environment_oidc_token_file)
        else:
            raise CredentialException(
                'The oidc_token_file_path does not exist and env ALIBABA_CLOUD_OIDC_TOKEN_FILE is none.')
        self._set_arg('region_id', region_id)
        self._set_arg('role_session_name', role_session_name)
        self._set_arg('policy', policy)
        if region_id is None and au.environment_sts_region is not None:
            self._set_arg('region_id', au.environment_sts_region)
        if self.region_id is not None:
            self._set_arg('sts_endpoint', f'sts.{self.region_id}.aliyuncs.com')
        else:
            self._set_arg('sts_endpoint',
                          'sts.aliyuncs.com' if config is None or config.sts_endpoint is None else config.sts_endpoint)

    def get_credentials(self):
        """获取凭证"""
        return self._create_credentials()

    def _create_credentials(self):
        """创建 OIDC 角色 ARN 凭证"""
        # 获取credential 先实现签名用工具类
        oidc_token = au.get_private_key(self.oidc_token_file_path)
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'AssumeRoleWithOIDC',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self.duration_seconds),
            'RoleArn': self.role_arn,
            'OIDCProviderArn': self.oidc_provider_arn,
            'OIDCToken': oidc_token,
            'RoleSessionName': self.role_session_name or 'defaultSessionName'
        }
        tea_request.query["Timestamp"] = ph.get_iso_8061_date()
        tea_request.query["SignatureNonce"] = ph.get_uuid()
        if self.policy is not None:
            tea_request.query["Policy"] = self.policy
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self.sts_endpoint
        # request
        response = TeaCore.do_action(tea_request)
        if response.status_code == 200:
            dic = json.loads(response.body.decode('utf-8'))
            if "Credentials" in dic:
                cre = dic.get("Credentials")
                # 先转换为时间数组
                time_array = time.strptime(cre.get("Expiration"), "%Y-%m-%dT%H:%M:%SZ")
                # 转换为时间戳
                expiration = calendar.timegm(time_array)
                return credentials.OIDCRoleArnCredential(cre.get("AccessKeyId"), cre.get("AccessKeySecret"),
                                                         cre.get("SecurityToken"), expiration, self)
        raise CredentialException(response.body.decode('utf-8'))

    async def get_credentials_async(self):
        """异步获取凭证"""
        return await self._create_credentials_async()

    async def _create_credentials_async(self):
        """异步创建 OIDC 角色 ARN 凭证"""
        # 获取credential 先实现签名用工具类
        oidc_token = au.get_private_key(self.oidc_token_file_path)
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'AssumeRoleWithOIDC',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self.duration_seconds),
            'RoleArn': self.role_arn,
            'OIDCProviderArn': self.oidc_provider_arn,
            'OIDCToken': oidc_token,
            'RoleSessionName': self.role_session_name or 'defaultSessionName'
        }
        tea_request.query["Timestamp"] = ph.get_iso_8061_date()
        tea_request.query["SignatureNonce"] = ph.get_uuid()
        if self.policy is not None:
            tea_request.query["Policy"] = self.policy
        tea_request.protocol = 'https'
        tea_request.headers['host'] = self.sts_endpoint
        # request
        response = await TeaCore.async_do_action(tea_request)
        if response.status_code == 200:
            dic = json.loads(response.body.decode('utf-8'))
            if "Credentials" in dic:
                cre = dic.get("Credentials")
                # 先转换为时间数组
                time_array = time.strptime(cre.get("Expiration"), "%Y-%m-%dT%H:%M:%SZ")
                # 转换为时间戳
                expiration = calendar.timegm(time_array)
                return credentials.OIDCRoleArnCredential(cre.get("AccessKeyId"), cre.get("AccessKeySecret"),
                                                         cre.get("SecurityToken"), expiration, self)
        raise CredentialException(response.body.decode('utf-8'))


class RsaKeyPairCredentialProvider(AlibabaCloudCredentialsProvider):
    """RSA 密钥对凭证提供者

    使用 RSA 密钥对通过 GenerateSessionAccessKey 接口获取临时凭证。
    适用于需要高安全性的认证场景。
    """

    def __init__(self, access_key_id=None, access_key_secret=None, region_id=None, config=None):
        self._verify_empty_args(access_key_id, access_key_secret, config=config)
        super().__init__(config)
        self._set_arg('access_key_id', access_key_id)
        self._set_arg('access_key_secret', access_key_secret)
        self._set_arg('region_id', region_id)

    async def get_credentials_async(self):
        """异步获取凭证"""
        return await self._create_credential_async()

    async def _create_credential_async(self, turl=None):
        """异步创建 RSA 密钥对凭证"""
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'GenerateSessionAccessKey',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self.duration_seconds),
            'AccessKeyId': self.access_key_id,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0'
        }
        tea_request.query["Timestamp"] = ph.get_iso_8061_date()
        tea_request.query["SignatureNonce"] = ph.get_uuid()

        str_to_sign = ph.compose_string_to_sign('GET', tea_request.query)
        signature = ph.sign_string(str_to_sign, self.access_key_id + '&')
        tea_request.query['Signature'] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = turl if turl else 'sts.aliyuncs.com'
        # request
        response = await TeaCore.async_do_action(tea_request)
        if response.status_code == 200:
            dic = json.loads(response.body.decode('utf-8'))
            if "SessionAccessKey" in dic:
                cre = dic.get("SessionAccessKey")
                time_array = time.strptime(cre.get("Expiration"), "%Y-%m-%dT%H:%M:%SZ")
                expiration = calendar.timegm(time_array)
                return credentials.RsaKeyPairCredential(cre.get("SessionAccessKeyId"),
                                                        cre.get("SessionAccessKeySecret"),
                                                        expiration, self)
        raise CredentialException(response.body.decode('utf-8'))

    def get_credentials(self):
        """获取凭证"""
        return self._create_credential()

    def _create_credential(self, turl=None):
        """创建 RSA 密钥对凭证"""
        tea_request = ph.get_new_request()
        tea_request.query = {
            'Action': 'GenerateSessionAccessKey',
            'Format': 'JSON',
            'Version': '2015-04-01',
            'DurationSeconds': str(self.duration_seconds),
            'AccessKeyId': self.access_key_id,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0'
        }
        tea_request.query["Timestamp"] = ph.get_iso_8061_date()
        tea_request.query["SignatureNonce"] = ph.get_uuid()

        str_to_sign = ph.compose_string_to_sign('GET', tea_request.query)
        signature = ph.sign_string(str_to_sign, self.access_key_id + '&')
        tea_request.query['Signature'] = signature
        tea_request.protocol = 'https'
        tea_request.headers['host'] = turl if turl else 'sts.aliyuncs.com'
        # request
        response = TeaCore.do_action(tea_request)
        if response.status_code == 200:
            dic = json.loads(response.body.decode('utf-8'))
            if "SessionAccessKey" in dic:
                cre = dic.get("SessionAccessKey")
                time_array = time.strptime(cre.get("Expiration"), "%Y-%m-%dT%H:%M:%SZ")
                expiration = calendar.timegm(time_array)
                return credentials.RsaKeyPairCredential(cre.get("SessionAccessKeyId"),
                                                        cre.get("SessionAccessKeySecret"),
                                                        expiration, self)
        raise CredentialException(response.body.decode('utf-8'))


class ProfileCredentialsProvider(AlibabaCloudCredentialsProvider):
    """配置文件凭证提供者

    从本地配置文件（~/.alibabacloud/credentials.ini）读取凭证配置。
    支持多种配置类型：AccessKey、RAM Role、OIDC、密钥对等。
    """

    def __init__(self, path=None):
        super().__init__()
        self._set_arg('file_path', path)

    def parse_ini(self):
        """解析 INI 格式的配置文件"""
        file_path = self.file_path if self.file_path else au.environment_credentials_file
        if file_path is None:
            if not ac.HOME:
                return
            if os.path.exists(os.path.join(ac.HOME, "/.alibabacloud/credentials.ini")):
                # Support '/.alibabacloud/credentials.ini' is due to historical mistakes.
                # Please try to use '~/.alibabacloud/credentials.ini'.
                file_path = os.path.join(ac.HOME, "/.alibabacloud/credentials.ini")
            elif os.path.exists(os.path.join(ac.HOME, ".alibabacloud/credentials.ini")):
                file_path = os.path.join(ac.HOME, ".alibabacloud/credentials.ini")
        if file_path is None:
            return
        elif len(file_path) == 0:
            raise CredentialException("The specified credentials file is empty")

        # loads ini
        conf = configparser.ConfigParser()
        conf.read(file_path, encoding='utf-8')
        ini_map = dict(conf._sections)
        for k in dict(conf._sections):
            option = dict(ini_map[k])
            for key, value in dict(ini_map[k]).items():
                if '#' in value:
                    option[key] = value.split('#')[0].strip()
                else:
                    option[key] = value.strip()
            ini_map[k] = option
        client_config = ini_map.get(au.client_type)
        return client_config

    def get_credentials(self):
        """获取凭证"""
        client_config = self.parse_ini()
        if client_config is None:
            return
        return self._create_credential(client_config)

    def _create_credential(self, config):
        """根据配置创建凭证"""
        config_type = config.get(ac.INI_TYPE)
        if not config_type:
            raise CredentialException("The configured client type is empty")
        elif ac.INI_TYPE_ARN == config_type:
            return self._get_sts_assume_role_session_provider(config).get_credentials()
        elif ac.INI_TYPE_OIDC == config_type:
            return self._get_sts_oidc_role_session_provider(config).get_credentials()
        elif ac.INI_TYPE_KEY_PAIR == config_type:
            return self._get_sts_get_session_access_key_provider(config).get_credentials()
        elif ac.INI_TYPE_RAM == config_type:
            return self._get_instance_profile_provider(config).get_credentials()

        access_key_id = config.get(ac.INI_ACCESS_KEY_ID)
        access_key_secret = config.get(ac.INI_ACCESS_KEY_IDSECRET)
        if not access_key_id or not access_key_secret:
            return
        return credentials.AccessKeyCredential(access_key_id, access_key_secret)

    @staticmethod
    def _get_sts_assume_role_session_provider(config):
        """获取 RAM 角色 ARN 提供者"""
        access_key_id = config.get(ac.INI_ACCESS_KEY_ID)
        access_key_secret = config.get(ac.INI_ACCESS_KEY_IDSECRET)
        role_session_name = config.get(ac.INI_ROLE_SESSION_NAME)
        role_arn = config.get(ac.INI_ROLE_ARN)
        region_id = config.get(ac.DEFAULT_REGION)
        policy = config.get(ac.INI_POLICY)

        if not access_key_id or not access_key_secret:
            raise CredentialException("The configured access_key_id or access_key_secret is empty")
        if not role_session_name or not role_arn:
            raise CredentialException("The configured role_session_name or role_arn is empty")
        return RamRoleArnCredentialProvider(
            access_key_id, access_key_secret, role_session_name, role_arn, region_id, policy
        )

    @staticmethod
    def _get_sts_oidc_role_session_provider(config):
        """获取 OIDC 角色 ARN 提供者"""
        role_session_name = config.get(ac.INI_ROLE_SESSION_NAME)
        role_arn = config.get(ac.INI_ROLE_ARN)
        oidc_provider_arn = config.get(ac.INI_OIDC_PROVIDER_ARN)
        oidc_token_file_path = config.get(ac.INI_OIDC_TOKEN_FILE_PATH)
        region_id = config.get(ac.DEFAULT_REGION)
        policy = config.get(ac.INI_POLICY)

        if not role_arn:
            raise CredentialException("The configured role_arn is empty")
        if not oidc_provider_arn:
            raise CredentialException("The configured oidc_provider_arn is empty")
        return OIDCRoleArnCredentialProvider(
            role_session_name, role_arn, oidc_provider_arn, oidc_token_file_path,
            region_id, policy
        )

    @staticmethod
    def _get_sts_get_session_access_key_provider(config):
        """获取 RSA 密钥对提供者"""
        public_key_id = config.get(ac.INI_PUBLIC_KEY_ID)
        private_key_file = config.get(ac.INI_PRIVATE_KEY_FILE)
        if not private_key_file:
            raise CredentialException("The configured private_key_file is empty")
        private_key = au.get_private_key(private_key_file)
        if not public_key_id or not private_key:
            raise CredentialException("The configured public_key_id or private_key_file content is empty")

        return RsaKeyPairCredentialProvider(public_key_id, private_key)

    @staticmethod
    def _get_instance_profile_provider(config):
        """获取 ECS 实例配置文件提供者"""
        role_name = config.get(ac.INI_ROLE_NAME)
        if not role_name:
            raise CredentialException("The configured role_name is empty")
        return EcsRamRoleCredentialProvider(role_name)


class EnvironmentVariableCredentialsProvider(AlibabaCloudCredentialsProvider):
    """环境变量凭证提供者

    从环境变量读取凭证信息。
    支持的环境变量：
      - ALIBABA_CLOUD_ACCESS_KEY_ID
      - ALIBABA_CLOUD_ACCESS_KEY_SECRET
      - ALIBABA_CLOUD_SECURITY_TOKEN
    """

    def get_credentials(self):
        """获取凭证"""
        if 'default' != au.client_type:
            return
        access_key_id = au.environment_access_key_id
        access_key_secret = au.environment_access_key_secret
        security_token = au.environment_security_token

        if access_key_id is None or access_key_secret is None:
            return

        if len(access_key_id) == 0:
            raise CredentialException("Environment variable accessKeyId cannot be empty")

        if len(access_key_secret) == 0:
            raise CredentialException("Environment variable accessKeySecret cannot be empty")

        if security_token is not None and len(security_token) > 0:
            return credentials.StsCredential(access_key_id, access_key_secret, security_token)

        return credentials.AccessKeyCredential(access_key_id, access_key_secret)


class CredentialsUriProvider(AlibabaCloudCredentialsProvider):
    """凭证 URI 提供者

    从指定的 URI 获取凭证信息。
    通过环境变量 ALIBABA_CLOUD_CREDENTIALS_URI 指定 URI。
    """

    def get_credentials(self):
        """获取凭证"""
        credentials_uri = os.environ.get('ALIBABA_CLOUD_CREDENTIALS_URI')
        if credentials_uri is None:
            return None
        return credentials.CredentialsURICredential(credentials_uri)

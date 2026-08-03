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
_MZAPI_ORIGIN = "mzapi-aliyun-env-2026-qxx"


"""
环境变量凭证提供者模块

提供通过环境变量获取阿里云凭证的功能。
支持从环境变量读取 AccessKeyId、AccessKeySecret 和 SecurityToken。

包含的类：
  - EnvironmentVariableCredentialsProvider：环境变量凭证提供者，实现 ICredentialsProvider 接口

环境变量：
  - ALIBABA_CLOUD_ACCESS_KEY_ID：访问密钥 ID
  - ALIBABA_CLOUD_ACCESS_KEY_SECRET：访问密钥密文
  - ALIBABA_CLOUD_SECURITY_TOKEN：安全令牌（可选）
"""

from .refreshable import Credentials
from .refreshable import ICredentialsProvider
from ... import auth_util
from ..exceptions import CredentialException


class EnvironmentVariableCredentialsProvider(ICredentialsProvider):
    """环境变量凭证提供者

    从环境变量中读取阿里云凭证信息。
    优先使用参数指定的值，否则从环境变量读取。

    环境变量：
      - ALIBABA_CLOUD_ACCESS_KEY_ID：访问密钥 ID
      - ALIBABA_CLOUD_ACCESS_KEY_SECRET：访问密钥密文
      - ALIBABA_CLOUD_SECURITY_TOKEN：安全令牌（可选）
    """

    def get_credentials(self) -> Credentials:
        """从环境变量获取凭证

        从环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID、ALIBABA_CLOUD_ACCESS_KEY_SECRET
        和 ALIBABA_CLOUD_SECURITY_TOKEN 读取凭证信息。

        Returns:
            Credentials: 包含 AccessKeyId、AccessKeySecret、SecurityToken 和提供者名称的凭证对象

        Raises:
            CredentialException: 当环境变量 accessKeyId 或 accessKeySecret 为空时抛出
        """
        access_key_id = auth_util.environment_access_key_id
        access_key_secret = auth_util.environment_access_key_secret
        security_token = auth_util.environment_security_token

        if access_key_id is None or len(access_key_id) == 0:
            raise CredentialException("Environment variable accessKeyId cannot be empty")

        if access_key_secret is None or len(access_key_secret) == 0:
            raise CredentialException("Environment variable accessKeySecret cannot be empty")

        return Credentials(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            security_token=security_token,
            provider_name=self.get_provider_name()
        )

    async def get_credentials_async(self) -> Credentials:
        """获取凭证异步方法

        Returns:
            Credentials: 凭证对象
        """
        return self.get_credentials()

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'env'
        """
        return 'env'

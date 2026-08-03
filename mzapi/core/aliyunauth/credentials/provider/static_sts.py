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
_MZAPI_ORIGIN = "mzapi-aliyun-static-sts-2026-qxx"


"""
静态 STS 凭证提供者模块

提供通过预配置的 STS 临时凭证（AccessKeyId、AccessKeySecret、SecurityToken）获取阿里云凭证的功能。
适用于已获取临时安全令牌后直接使用的场景。

包含的类：
  - StaticSTSCredentialsProvider：静态 STS 凭证提供者，实现 ICredentialsProvider 接口

使用示例：
  provider = StaticSTSCredentialsProvider(
      access_key_id='your_access_key_id',
      access_key_secret='your_access_key_secret',
      security_token='your_security_token'
  )
  credentials = provider.get_credentials()
"""

from .refreshable import Credentials
from .refreshable import ICredentialsProvider
from ... import auth_util


class StaticSTSCredentialsProvider(ICredentialsProvider):
    """静态 STS 凭证提供者

    使用预配置的 STS 临时凭证创建凭证提供者。
    凭证信息可以通过构造函数参数或环境变量指定。

    Attributes:
        access_key_id: 阿里云 STS 临时访问密钥 ID
        access_key_secret: 阿里云 STS 临时访问密钥密文
        security_token: 阿里云 STS 安全令牌
    """

    def __init__(self, *,
                 access_key_id: str = None,
                 access_key_secret: str = None,
                 security_token: str = None):
        """初始化静态 STS 凭证提供者

        Args:
            access_key_id: 阿里云 STS AccessKeyId，优先使用参数值，其次读取环境变量
            access_key_secret: 阿里云 STS AccessKeySecret，优先使用参数值，其次读取环境变量
            security_token: 阿里云 STS SecurityToken，优先使用参数值，其次读取环境变量

        Raises:
            ValueError: 当 access_key_id、access_key_secret 或 security_token 为空时抛出
        """
        self.access_key_id = access_key_id or auth_util.environment_access_key_id
        self.access_key_secret = access_key_secret or auth_util.environment_access_key_secret
        self.security_token = security_token or auth_util.environment_security_token

        if self.access_key_id is None or self.access_key_id == '':
            raise ValueError('the access key id is empty')
        if self.access_key_secret is None or self.access_key_secret == '':
            raise ValueError('the access key secret is empty')
        if self.security_token is None or self.security_token == '':
            raise ValueError('the security token is empty')

    def get_credentials(self) -> Credentials:
        """获取凭证同步方法

        Returns:
            Credentials: 包含 AccessKeyId、AccessKeySecret、SecurityToken 和提供者名称的凭证对象
        """
        return Credentials(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=self.security_token,
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
            str: 提供者名称 'static_sts'
        """
        return 'static_sts'

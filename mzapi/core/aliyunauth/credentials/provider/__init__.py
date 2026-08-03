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
_MZAPI_ORIGIN = "mzapi-aliyun-credentials-provider-2026-qxx"


"""
阿里云凭证提供者模块

提供多种阿里云凭证获取方式，包括：
- 静态访问密钥（StaticAK/StaticSTS）
- 环境变量凭证
- ECS RAM 角色凭证
- RAM Role ARN 凭证
- OIDC Role ARN 凭证
- RSA 密钥对凭证
- URI 凭证
- CLI Profile 凭证
- Profile 凭证
- 默认凭证提供者（链式调用）
- CloudSSO 凭证
- OAuth 凭证
- 外部程序凭证

导出模块：
  - StaticAKCredentialsProvider：静态访问密钥凭证提供者
  - StaticSTSCredentialsProvider：静态 STS 凭证提供者
  - EnvironmentVariableCredentialsProvider：环境变量凭证提供者
  - EcsRamRoleCredentialsProvider：ECS RAM 角色凭证提供者
  - RamRoleArnCredentialsProvider：RAM Role ARN 凭证提供者
  - OIDCRoleArnCredentialsProvider：OIDC Role ARN 凭证提供者
  - RsaKeyPairCredentialsProvider：RSA 密钥对凭证提供者
  - URLCredentialsProvider：URI 凭证提供者
  - CLIProfileCredentialsProvider：CLI Profile 凭证提供者
  - ProfileCredentialsProvider：Profile 凭证提供者
  - DefaultCredentialsProvider：默认凭证提供者（链式调用）
  - CloudSSOCredentialsProvider：CloudSSO 凭证提供者
  - OAuthCredentialsProvider：OAuth 凭证提供者
  - ExternalCredentialsProvider：外部程序凭证提供者
"""

from .static_ak import StaticAKCredentialsProvider
from .static_sts import StaticSTSCredentialsProvider
from .env import EnvironmentVariableCredentialsProvider
from .ecs_ram_role import EcsRamRoleCredentialsProvider
from .ram_role_arn import RamRoleArnCredentialsProvider
from .oidc import OIDCRoleArnCredentialsProvider
from .rsa_key_pair import RsaKeyPairCredentialsProvider
from .uri import URLCredentialsProvider
from .cli_profile import CLIProfileCredentialsProvider
from .profile import ProfileCredentialsProvider
from .default import DefaultCredentialsProvider
from .cloud_sso import CloudSSOCredentialsProvider
from .oauth import OAuthCredentialsProvider
from .external import ExternalCredentialsProvider

__all__ = [
    'StaticAKCredentialsProvider',
    'StaticSTSCredentialsProvider',
    'EnvironmentVariableCredentialsProvider',
    'EcsRamRoleCredentialsProvider',
    'RamRoleArnCredentialsProvider',
    'OIDCRoleArnCredentialsProvider',
    'RsaKeyPairCredentialsProvider',
    'URLCredentialsProvider',
    'CLIProfileCredentialsProvider',
    'ProfileCredentialsProvider',
    'DefaultCredentialsProvider',
    'CloudSSOCredentialsProvider',
    'OAuthCredentialsProvider',
    'ExternalCredentialsProvider'
]

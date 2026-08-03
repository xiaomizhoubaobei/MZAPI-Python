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
_MZAPI_ORIGIN = "mzapi-aliyun-profile-2026-qxx"


"""
Profile 凭证提供者模块

提供通过阿里云凭证文件（INI 格式）获取凭证的功能。
支持从 ~/.alibabacloud/credentials.ini 读取配置并自动创建对应的凭证提供者。

包含的类：
  - ProfileCredentialsProvider：Profile 凭证提供者，实现 ICredentialsProvider 接口

支持的凭证类型：
  - access_key：静态访问密钥
  - ram_role_arn：RAM 角色 ARN
  - oidc_role_arn：OIDC 角色
  - ecs_ram_role：ECS RAM 角色
  - rsa_key_pair：RSA 密钥对

环境变量：
  - ALIBABA_CLOUD_CREDENTIALS_FILE：凭证文件路径
  - ALIBABA_CLOUD_CLIENT_TYPE：客户端类型（Profile 名称）
"""

import os
import configparser
from typing import Dict

import aiofiles

from . import StaticAKCredentialsProvider, EcsRamRoleCredentialsProvider, \
    RamRoleArnCredentialsProvider, OIDCRoleArnCredentialsProvider, RsaKeyPairCredentialsProvider
from .refreshable import Credentials
from .refreshable import ICredentialsProvider
from ... import auth_constant as ac
from ... import auth_util as au
from ..exceptions import CredentialException


async def _load_ini_async(file_path: str) -> Dict[str, Dict[str, str]]:
    """异步加载 INI 配置文件

    Args:
        file_path: 配置文件路径

    Returns:
        Dict: 配置节字典
    """
    config = configparser.ConfigParser()
    async with aiofiles.open(file_path, mode='r') as f:
        content = await f.read()
    config.read_string(content)
    ini_map = {}
    for section in config.sections():
        option = {}
        for key, value in config.items(section):
            if '#' in value:
                option[key] = value.split('#')[0].strip()
            else:
                option[key] = value.strip()
        ini_map[section] = option
    return ini_map


def _load_ini(file_path: str) -> Dict[str, Dict[str, str]]:
    """同步加载 INI 配置文件

    Args:
        file_path: 配置文件路径

    Returns:
        Dict: 配置节字典
    """
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    ini_map = {}
    for section in config.sections():
        option = {}
        for key, value in config.items(section):
            if '#' in value:
                option[key] = value.split('#')[0].strip()
            else:
                option[key] = value.strip()
        ini_map[section] = option
    return ini_map


def _get_default_file() -> str:
    """获取默认凭证文件路径

    Returns:
        str: 默认凭证文件路径 ~/.alibabacloud/credentials.ini
    """
    return os.path.join(ac.HOME, ".alibabacloud", "credentials.ini")


class ProfileCredentialsProvider(ICredentialsProvider):
    """Profile 凭证提供者

    从阿里云凭证文件（INI 格式）中读取凭证配置，
    并根据配置类型自动创建对应的凭证提供者。

    Attributes:
        _profile_file: 凭证文件路径
        _profile_name: Profile 名称
    """

    def __init__(self, *,
                 profile_file: str = None,
                 profile_name: str = None):
        """初始化 Profile 凭证提供者

        Args:
            profile_file: 凭证文件路径，默认从环境变量读取或使用 ~/.alibabacloud/credentials.ini
            profile_name: Profile 名称，默认从环境变量 ALIBABA_CLOUD_CLIENT_TYPE 读取
        """
        self._profile_file = profile_file or au.environment_credentials_file
        self._profile_name = profile_name or au.client_type
        self.__innerProvider = None

        if self._profile_file is None or self._profile_file == '':
            self._profile_file = _get_default_file()

    def _should_reload_credentials_provider(self) -> bool:
        """检查是否需要重新加载凭证提供者

        Returns:
            bool: 是否需要重新加载
        """
        if self.__innerProvider is None:
            return True
        return False

    def get_credentials(self) -> Credentials:
        """获取凭证同步方法

        Returns:
            Credentials: 凭证对象
        """
        if self._should_reload_credentials_provider():
            ini_map = _load_ini(self._profile_file)
            section = ini_map.get(self._profile_name)
            if section is None:
                raise CredentialException(f'failed to get credential from credentials file: ${self._profile_file}')
            self.__innerProvider = self._get_credentials_provider(section)

        cre = self.__innerProvider.get_credentials()
        credentials = Credentials(
            access_key_id=cre.get_access_key_id(),
            access_key_secret=cre.get_access_key_secret(),
            security_token=cre.get_security_token(),
            provider_name=f'{self.get_provider_name()}/{cre.get_provider_name()}'
        )
        return credentials

    async def get_credentials_async(self) -> Credentials:
        """获取凭证异步方法

        Returns:
            Credentials: 凭证对象
        """
        if self._should_reload_credentials_provider():
            ini_map = await _load_ini_async(self._profile_file)
            section = ini_map.get(self._profile_name)
            if section is None:
                raise CredentialException(f'failed to get credential from credentials file: ${self._profile_file}')
            self.__innerProvider = self._get_credentials_provider(section)

        cre = await self.__innerProvider.get_credentials_async()
        credentials = Credentials(
            access_key_id=cre.get_access_key_id(),
            access_key_secret=cre.get_access_key_secret(),
            security_token=cre.get_security_token(),
            provider_name=f'{self.get_provider_name()}/{cre.get_provider_name()}'
        )
        return credentials

    def _get_credentials_provider(self, section: Dict) -> ICredentialsProvider:
        """根据配置节获取对应的凭证提供者

        Args:
            section: INI 配置节

        Returns:
            ICredentialsProvider: 凭证提供者实例
        """
        config_type = section.get(ac.INI_TYPE)
        if 'access_key' == config_type:
            return StaticAKCredentialsProvider(
                access_key_id=section.get('access_key_id'),
                access_key_secret=section.get('access_key_secret')
            )
        elif 'ram_role_arn' == config_type:
            pre_provider = StaticAKCredentialsProvider(
                access_key_id=section.get('access_key_id'),
                access_key_secret=section.get('access_key_secret')
            )
            return RamRoleArnCredentialsProvider(
                credentials_provider=pre_provider,
                role_arn=section.get('role_arn'),
                role_session_name=section.get('role_session_name'),
                policy=section.get('policy')
            )
        elif 'oidc_role_arn' == config_type:
            return OIDCRoleArnCredentialsProvider(
                role_arn=section.get('role_arn'),
                oidc_provider_arn=section.get('oidc_provider_arn'),
                oidc_token_file_path=section.get('oidc_token_file_path'),
                role_session_name=section.get('role_session_name'),
                policy=section.get('policy')
            )
        elif 'ecs_ram_role' == config_type:
            return EcsRamRoleCredentialsProvider(
                role_name=section.get('role_name')
            )
        elif 'rsa_key_pair' == config_type:
            return RsaKeyPairCredentialsProvider(
                public_key_id=section.get('public_key_id'),
                private_key_file=section.get('private_key_file')
            )
        else:
            raise CredentialException(
                f'unsupported credential type {config_type} from credentials file {self._profile_file}')

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'profile'
        """
        return 'profile'

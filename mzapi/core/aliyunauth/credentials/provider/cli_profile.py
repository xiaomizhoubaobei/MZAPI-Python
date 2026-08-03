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
_MZAPI_ORIGIN = "mzapi-aliyun-cli-profile-2026-qxx"


"""
CLI Profile 凭证提供者模块

提供通过阿里云 CLI 配置文件获取凭证的功能。
支持从 ~/.aliyun/config.json 读取配置并自动创建对应的凭证提供者。

包含的类：
  - CLIProfileCredentialsProvider：CLI Profile 凭证提供者，实现 ICredentialsProvider 接口

支持的凭证模式：
  - AK：静态访问密钥
  - StsToken：STS 临时凭证
  - RamRoleArn：RAM 角色 ARN
  - EcsRamRole：ECS RAM 角色
  - OIDC：OIDC 角色
  - ChainableRamRoleArn：链式 RAM 角色
  - CloudSSO：Cloud SSO
  - OAuth：OAuth 认证
  - External：外部程序获取凭证

环境变量：
  - ALIBABA_CLOUD_PROFILE_NAME：CLI Profile 名称
  - ALIBABA_CLOUD_CLI_PROFILE_DISABLED：是否禁用 CLI Profile 凭证
"""

import os
import json
import threading
import platform
from typing import Any, Dict

import aiofiles

# 跨平台文件锁支持
if platform.system() == 'Windows':
    # Windows平台使用msvcrt
    import msvcrt

    HAS_MSVCRT = True
    HAS_FCNTL = False
else:
    # 其他平台尝试使用fcntl，如果不可用则不设文件锁
    HAS_MSVCRT = False
    try:
        import fcntl

        HAS_FCNTL = True
    except ImportError:
        HAS_FCNTL = False

from .static_ak import StaticAKCredentialsProvider
from .ecs_ram_role import EcsRamRoleCredentialsProvider
from .ram_role_arn import RamRoleArnCredentialsProvider
from .oidc import OIDCRoleArnCredentialsProvider
from .static_sts import StaticSTSCredentialsProvider
from .cloud_sso import CloudSSOCredentialsProvider
from .oauth import OAuthCredentialsProvider, OAuthTokenUpdateCallback, OAuthTokenUpdateCallbackAsync
from .external import (
    ExternalCredentialsProvider,
    ExternalCredentialUpdateCallback,
    ExternalCredentialUpdateCallbackAsync,
)
from .refreshable import Credentials
from .refreshable import ICredentialsProvider
from ... import auth_constant as ac
from ... import auth_util as au
from ..exceptions import CredentialException


async def _load_config_async(file_path: str) -> Any:
    """异步加载 JSON 配置文件

    Args:
        file_path: 配置文件路径

    Returns:
        Any: 解析后的配置对象
    """
    async with aiofiles.open(file_path, mode='r') as f:
        content = await f.read()
    return json.loads(content)


def _load_config(file_path: str) -> Any:
    """同步加载 JSON 配置文件

    Args:
        file_path: 配置文件路径

    Returns:
        Any: 解析后的配置对象
    """
    with open(file_path, mode='r') as f:
        content = f.read()
    return json.loads(content)


class CLIProfileCredentialsProvider(ICredentialsProvider):
    """CLI Profile 凭证提供者

    从阿里云 CLI 配置文件（~/.aliyun/config.json）中读取凭证配置，
    并根据配置模式自动创建对应的凭证提供者。

    支持多种凭证模式，包括 AK、STS、RAM 角色、ECS 角色、OIDC 等。
    支持凭证自动刷新和写回配置文件。

    Attributes:
        _profile_file: CLI 配置文件路径
        _profile_name: Profile 名称
        _file_lock: 文件锁，用于并发安全
    """

    def __init__(self, *,
                 profile_name: str = None,
                 profile_file: str = None,
                 allow_config_force_rewrite: bool = False):
        """初始化 CLI Profile 凭证提供者

        Args:
            profile_name: Profile 名称，默认从环境变量 ALIBABA_CLOUD_PROFILE_NAME 读取
            profile_file: CLI 配置文件路径，默认 ~/.aliyun/config.json
            allow_config_force_rewrite: 是否允许强制重写配置

        Raises:
            CredentialException: 当配置文件禁用时抛出
        """
        self._profile_file = profile_file or os.path.join(ac.HOME, ".aliyun", "config.json")
        self._profile_name = profile_name or au.environment_profile_name
        self._allow_config_force_rewrite = allow_config_force_rewrite
        self.__innerProvider = None
        # 文件锁，用于并发安全
        self._file_lock = threading.RLock()

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

        Raises:
            CredentialException: 当获取凭证失败时抛出
        """
        if au.environment_cli_profile_disabled.lower() == "true":
            raise CredentialException('cli credentials file is disabled')

        if self._should_reload_credentials_provider():
            if not os.path.exists(self._profile_file) or not os.path.isfile(self._profile_file):
                raise CredentialException(f'unable to open credentials file: {self._profile_file}')
            try:
                config = _load_config(self._profile_file)
            except Exception as e:
                raise CredentialException(
                    f'failed to parse credential form cli credentials file: {self._profile_file}')
            if config is None:
                raise CredentialException(
                    f'failed to parse credential form cli credentials file: {self._profile_file}')

            profile_name = self._profile_name
            if self._profile_name is None or self._profile_name == '':
                profile_name = config.get('current')
            self.__innerProvider = self._get_credentials_provider(config, profile_name)

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
        if au.environment_cli_profile_disabled.lower() == "true":
            raise CredentialException('cli credentials file is disabled')

        if self._should_reload_credentials_provider():
            if not os.path.exists(self._profile_file) or not os.path.isfile(self._profile_file):
                raise CredentialException(f'unable to open credentials file: {self._profile_file}')
            try:
                config = await _load_config_async(self._profile_file)
            except Exception as e:
                raise CredentialException(
                    f'failed to parse credential form cli credentials file: {self._profile_file}')
            if config is None:
                raise CredentialException(
                    f'failed to parse credential form cli credentials file: {self._profile_file}')

            profile_name = self._profile_name
            if self._profile_name is None or self._profile_name == '':
                profile_name = config.get('current')
            self.__innerProvider = self._get_credentials_provider(config, profile_name)

        cre = await self.__innerProvider.get_credentials_async()
        credentials = Credentials(
            access_key_id=cre.get_access_key_id(),
            access_key_secret=cre.get_access_key_secret(),
            security_token=cre.get_security_token(),
            provider_name=f'{self.get_provider_name()}/{cre.get_provider_name()}'
        )
        return credentials

    def _get_credentials_provider(self, config: Dict, profile_name: str) -> ICredentialsProvider:
        """根据配置获取对应的凭证提供者

        Args:
            config: CLI 配置文件内容
            profile_name: Profile 名称

        Returns:
            ICredentialsProvider: 凭证提供者实例

        Raises:
            CredentialException: 当配置无效或不支持的模式时抛出
        """
        if profile_name is None or profile_name == '':
            raise CredentialException('invalid profile name')

        profiles = config.get('profiles', [])

        if not profiles:
            raise CredentialException(f"unable to get profile with '{profile_name}' form cli credentials file.")

        for profile in profiles:
            if profile.get('name') is not None and profile['name'] == profile_name:
                mode = profile.get('mode')
                if mode == "AK":
                    return StaticAKCredentialsProvider(
                        access_key_id=profile.get('access_key_id'),
                        access_key_secret=profile.get('access_key_secret')
                    )
                elif mode == "StsToken":
                    return StaticSTSCredentialsProvider(
                        access_key_id=profile.get('access_key_id'),
                        access_key_secret=profile.get('access_key_secret'),
                        security_token=profile.get('sts_token')
                    )
                elif mode == "RamRoleArn":
                    pre_provider = StaticAKCredentialsProvider(
                        access_key_id=profile.get('access_key_id'),
                        access_key_secret=profile.get('access_key_secret')
                    )
                    return RamRoleArnCredentialsProvider(
                        credentials_provider=pre_provider,
                        role_arn=profile.get('ram_role_arn'),
                        role_session_name=profile.get('ram_session_name'),
                        duration_seconds=profile.get('expired_seconds'),
                        policy=profile.get('policy'),
                        external_id=profile.get('external_id'),
                        sts_region_id=profile.get('sts_region'),
                        enable_vpc=profile.get('enable_vpc'),
                    )
                elif mode == "EcsRamRole":
                    return EcsRamRoleCredentialsProvider(
                        role_name=profile.get('ram_role_name')
                    )
                elif mode == "OIDC":
                    return OIDCRoleArnCredentialsProvider(
                        role_arn=profile.get('ram_role_arn'),
                        oidc_provider_arn=profile.get('oidc_provider_arn'),
                        oidc_token_file_path=profile.get('oidc_token_file'),
                        role_session_name=profile.get('role_session_name'),
                        duration_seconds=profile.get('expired_seconds'),
                        policy=profile.get('policy'),
                        sts_region_id=profile.get('sts_region'),
                        enable_vpc=profile.get('enable_vpc'),
                    )
                elif mode == "ChainableRamRoleArn":
                    previous_provider = self._get_credentials_provider(config, profile.get('source_profile'))
                    return RamRoleArnCredentialsProvider(
                        credentials_provider=previous_provider,
                        role_arn=profile.get('ram_role_arn'),
                        role_session_name=profile.get('ram_session_name'),
                        duration_seconds=profile.get('expired_seconds'),
                        policy=profile.get('policy'),
                        external_id=profile.get('external_id'),
                        sts_region_id=profile.get('sts_region'),
                        enable_vpc=profile.get('enable_vpc'),
                    )
                elif mode == "CloudSSO":
                    return CloudSSOCredentialsProvider(
                        sign_in_url=profile.get('cloud_sso_sign_in_url'),
                        account_id=profile.get('cloud_sso_account_id'),
                        access_config=profile.get('cloud_sso_access_config'),
                        access_token=profile.get('access_token'),
                        access_token_expire=profile.get('cloud_sso_access_token_expire'),
                    )
                elif mode == "OAuth":
                    # 获取 OAuth 配置
                    site_type = profile.get('oauth_site_type', 'CN')
                    oauth_base_url_map = {
                        'CN': 'https://oauth.aliyun.com',
                        'INTL': 'https://oauth.alibabacloud.com'
                    }
                    sign_in_url = oauth_base_url_map.get(site_type.upper())
                    if not sign_in_url:
                        raise CredentialException('Invalid OAuth site type, support CN or INTL')

                    oauth_client_map = {
                        'CN': '4038181954557748008',
                        'INTL': '4103531455503354461'
                    }
                    client_id = oauth_client_map.get(site_type.upper())
                    if not client_id:
                        raise CredentialException('Invalid OAuth site type, support CN or INTL')

                    return OAuthCredentialsProvider(
                        client_id=client_id,
                        sign_in_url=sign_in_url,
                        access_token=profile.get('oauth_access_token'),
                        access_token_expire=profile.get('oauth_access_token_expire'),
                        refresh_token=profile.get('oauth_refresh_token'),
                        token_update_callback=self._get_oauth_token_update_callback(),
                        token_update_callback_async=self._get_oauth_token_update_callback_async(),
                    )
                elif mode == "External":
                    return ExternalCredentialsProvider(
                        process_command=profile.get('process_command'),
                        credential_update_callback=self._get_external_credential_update_callback(),
                        credential_update_callback_async=self._get_external_credential_update_callback_async(),
                    )
                else:
                    raise CredentialException(f"unsupported profile mode '{mode}' form cli credentials file.")

        raise CredentialException(f"unable to get profile with '{profile_name}' form cli credentials file.")

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'cli_profile'
        """
        return 'cli_profile'

    def _update_oauth_tokens(self, refresh_token: str, access_token: str, access_key: str, secret: str,
                             security_token: str, access_token_expire: int, sts_expire: int) -> None:
        """更新 OAuth 令牌并写回配置文件"""

        def _find_source_oauth_profile(config: dict, profile_name: str) -> dict:
            profiles = config.get('profiles', [])
            profile = next((p for p in profiles if p.get('name') == profile_name), None)
            if not profile:
                raise CredentialException(f"unable to get profile with name '{profile_name}' from cli credentials file.")

            if profile.get('mode') == 'OAuth':
                return profile
            else:
                source_profile = profile.get('source_profile')
                if source_profile:
                    return _find_source_oauth_profile(config, source_profile)

            raise CredentialException(f"unable to get OAuth profile with name '{profile_name}' from cli credentials file.")


        with self._file_lock:
            try:
                # 读取现有配置
                config = _load_config(self._profile_file)

                # 找到当前 profile 并更新 OAuth 令牌
                profile_name = self._profile_name or config.get('current')
                if not profile_name:
                    raise CredentialException(f"unable to get profile to updated.")

                source_profile = _find_source_oauth_profile(config, profile_name)

                # 更新 OAuth 令牌
                source_profile['oauth_refresh_token'] = refresh_token
                source_profile['oauth_access_token'] = access_token
                source_profile['oauth_access_token_expire'] = access_token_expire
                # 更新 STS 凭据
                source_profile['access_key_id'] = access_key
                source_profile['access_key_secret'] = secret
                source_profile['sts_token'] = security_token
                source_profile['sts_expiration'] = sts_expire

                self._write_configuration_to_file_with_lock(self._profile_file, config)

            except Exception as e:
                raise CredentialException(f"failed to update OAuth tokens in config file: {e}")

    def _write_configuration_to_file(self, config_path: str, config: Dict) -> None:
        """将配置写入文件，使用原子写入确保数据完整性。

        使用 os.replace 而非 os.rename：Windows 上 rename 无法覆盖已存在目标文件
        （WinError 183），而 os.replace 提供跨平台的覆盖语义。
        """
        # 获取原文件权限（如果存在）
        file_mode = 0o644
        if os.path.exists(config_path):
            file_mode = os.stat(config_path).st_mode

        # 创建唯一临时文件
        import time
        temp_file = config_path + '.tmp-' + str(int(time.time() * 1000000))  # 微秒级时间戳

        try:
            # 写入临时文件
            self._write_config_file(temp_file, file_mode, config)
            # 原子替换（Windows 上可覆盖已存在的 config_path）
            os.replace(temp_file, config_path)
        except Exception:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            raise

    def _write_config_file(self, filename: str, file_mode: int, config: Dict) -> None:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            # 设置文件权限
            os.chmod(filename, file_mode)

        except Exception as e:
            raise CredentialException(f"Failed to write config file: {e}")

    def _write_configuration_to_file_with_lock(self, config_path: str, config: Dict) -> None:
        """使用操作系统级别的文件锁写入配置文件。

        Windows 上目标文件被打开锁定时无法 rename/replace，因此在锁内直接原地写入；
        其他平台使用临时文件 + os.replace 原子覆盖。
        """
        # 获取原文件权限（如果存在）
        file_mode = 0o644
        if os.path.exists(config_path):
            file_mode = os.stat(config_path).st_mode

        # 确保文件存在
        if not os.path.exists(config_path):
            # 创建空文件
            with open(config_path, 'w') as f:
                json.dump({}, f)

        # 打开文件用于锁定
        with open(config_path, 'r+') as f:
            # 获取独占锁（阻塞其他进程）
            if HAS_MSVCRT:
                # Windows使用msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            elif HAS_FCNTL:
                # Unix/Linux使用fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            # 如果都不支持，则跳过文件锁（仅进程内保护）

            try:
                if platform.system() == 'Windows':
                    # Windows 下目标文件处于打开锁定状态时无法 replace，改为原地写入
                    f.seek(0)
                    f.truncate()  # 清空文件内容
                    json.dump(config, f, indent=4, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                else:
                    # 其他环境使用临时文件 + os.replace（在文件锁内部进行原子操作）
                    import time
                    temp_file = config_path + '.tmp-' + str(int(time.time() * 1000000))
                    self._write_config_file(temp_file, file_mode, config)
                    os.replace(temp_file, config_path)

            finally:
                # 释放锁
                try:
                    if HAS_MSVCRT:
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    elif HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (OSError, PermissionError):
                    # 在Windows下，如果文件被重命名，文件句柄可能已经无效
                    # 这种情况下锁会自动释放，所以忽略错误
                    pass

    def _get_oauth_token_update_callback(self) -> OAuthTokenUpdateCallback:
        """获取 OAuth 令牌更新回调函数"""
        return lambda refresh_token, access_token, access_key, secret, security_token, access_token_expire, sts_expire: self._update_oauth_tokens(
            refresh_token, access_token, access_key, secret, security_token, access_token_expire, sts_expire
        )

    def _update_external_credentials(self, access_key: str, secret: str,
                                     security_token: str, expiration: int) -> None:
        """更新 External 凭证并写回配置文件"""

        def _find_source_external_profile(config: dict, profile_name: str) -> dict:
            profiles = config.get('profiles', [])
            profile = next((p for p in profiles if p.get('name') == profile_name), None)
            if not profile:
                raise CredentialException(f"unable to get profile with name '{profile_name}' from cli credentials file.")

            if profile.get('mode') == 'External':
                return profile

            source_profile = profile.get('source_profile')
            if source_profile:
                return _find_source_external_profile(config, source_profile)

            raise CredentialException(f"unable to get External profile with name '{profile_name}' from cli credentials file.")

        with self._file_lock:
            try:
                config = _load_config(self._profile_file)
                profile_name = self._profile_name or config.get('current')
                if not profile_name:
                    raise CredentialException(f"unable to get profile to updated.")

                source_profile = _find_source_external_profile(config, profile_name)
                source_profile['access_key_id'] = access_key
                source_profile['access_key_secret'] = secret
                source_profile['sts_token'] = security_token
                source_profile['sts_expiration'] = expiration

                self._write_configuration_to_file_with_lock(self._profile_file, config)
            except Exception as e:
                raise CredentialException(f"failed to update External credentials in config file: {e}")

    def _get_external_credential_update_callback(self) -> ExternalCredentialUpdateCallback:
        """获取 External 凭证更新回调函数"""
        return lambda access_key, secret, security_token, expiration: self._update_external_credentials(
            access_key, secret, security_token, expiration
        )

    async def _write_configuration_to_file_async(self, config_path: str, config: Dict) -> None:
        """异步将配置写入文件，使用原子写入确保数据完整性。

        使用 os.replace 而非 os.rename，确保 Windows 上可覆盖已存在文件。
        """
        # 获取原文件权限（如果存在）
        file_mode = 0o644
        if os.path.exists(config_path):
            file_mode = os.stat(config_path).st_mode

        # 创建唯一临时文件
        import time
        temp_file = config_path + '.tmp-' + str(int(time.time() * 1000000))  # 微秒级时间戳

        try:
            # 异步写入临时文件
            await self._write_config_file_async(temp_file, file_mode, config)
            # 原子替换（Windows 上可覆盖已存在的 config_path）
            os.replace(temp_file, config_path)
        except Exception:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            raise

    async def _write_config_file_async(self, filename: str, file_mode: int, config: Dict) -> None:
        try:
            async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(config, indent=4, ensure_ascii=False))

            # 设置文件权限
            os.chmod(filename, file_mode)

        except Exception as e:
            raise CredentialException(f"Failed to write config file: {e}")

    async def _write_configuration_to_file_with_lock_async(self, config_path: str, config: Dict) -> None:
        """异步使用操作系统级别的文件锁写入配置文件。

        Windows 上目标文件被打开锁定时无法 rename/replace，因此在锁内直接原地写入；
        其他平台使用临时文件 + os.replace 原子覆盖。
        """
        # 获取原文件权限（如果存��）
        file_mode = 0o644
        if os.path.exists(config_path):
            file_mode = os.stat(config_path).st_mode

        # 确保文件存在
        if not os.path.exists(config_path):
            # 创建空文件
            with open(config_path, 'w') as f:
                json.dump({}, f)

        # 打开文件用于锁定
        with open(config_path, 'r+') as f:
            # 获取独占锁（阻塞其他进程）
            if HAS_MSVCRT:
                # Windows使用msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            elif HAS_FCNTL:
                # Unix/Linux使用fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            # 如果都不支持，则跳过文件锁（仅进程内保护）

            try:
                if platform.system() == 'Windows':
                    # Windows 下目标文件处于打开锁定状态时无法 replace，改为原地写入
                    f.seek(0)
                    f.truncate()  # 清空文件内容
                    json.dump(config, f, indent=4, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                else:
                    # 其他环境使用临时文件 + os.replace（在文件锁内部进行原子操作）
                    import time
                    temp_file = config_path + '.tmp-' + str(int(time.time() * 1000000))
                    await self._write_config_file_async(temp_file, file_mode, config)
                    os.replace(temp_file, config_path)

            finally:
                # 释放锁
                try:
                    if HAS_MSVCRT:
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    elif HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (OSError, PermissionError):
                    # 在Windows下，如果文件被重命名，文件句柄可能已经无效
                    # 这种情况下锁会自动释放，所以忽略错误
                    pass

    async def _update_oauth_tokens_async(self, refresh_token: str, access_token: str, access_key: str, secret: str,
                                         security_token: str, access_token_expire: int, sts_expire: int) -> None:
        """异步更新 OAuth 令牌并写回配置文件"""

        def _find_source_oauth_profile(config: dict, profile_name: str) -> dict:
            profiles = config.get('profiles', [])
            profile = next((p for p in profiles if p.get('name') == profile_name), None)
            if not profile:
                raise CredentialException(f"unable to get profile with name '{profile_name}' from cli credentials file.")

            if profile.get('mode') == 'OAuth':
                return profile
            else:
                source_profile = profile.get('source_profile')
                if source_profile:
                    return _find_source_oauth_profile(config, source_profile)

            raise CredentialException(f"unable to get OAuth profile with name '{profile_name}' from cli credentials file.")

        with self._file_lock:
            try:
                # 读取现有配置
                config = await _load_config_async(self._profile_file)

                # 找到当前 profile 并更新 OAuth 令牌
                profile_name = self._profile_name or config.get('current')
                if not profile_name:
                    raise CredentialException(f"unable to get profile to updated.")

                source_profile = _find_source_oauth_profile(config, profile_name)

                # 更新 OAuth 令牌
                source_profile['oauth_refresh_token'] = refresh_token
                source_profile['oauth_access_token'] = access_token
                source_profile['oauth_access_token_expire'] = access_token_expire
                # 更新 STS 凭据
                source_profile['access_key_id'] = access_key
                source_profile['access_key_secret'] = secret
                source_profile['sts_token'] = security_token
                source_profile['sts_expiration'] = sts_expire

                await self._write_configuration_to_file_with_lock_async(self._profile_file, config)

            except Exception as e:
                raise CredentialException(f"failed to update OAuth tokens in config file: {e}")

    def _get_oauth_token_update_callback_async(self) -> OAuthTokenUpdateCallbackAsync:
        """获取异步 OAuth 令牌更新回调函数"""
        return lambda refresh_token, access_token, access_key, secret, security_token, access_token_expire, sts_expire: self._update_oauth_tokens_async(
            refresh_token, access_token, access_key, secret, security_token, access_token_expire, sts_expire
        )

    async def _update_external_credentials_async(self, access_key: str, secret: str,
                                                 security_token: str, expiration: int) -> None:
        """异步更新 External 凭证并写回配置文件"""

        def _find_source_external_profile(config: dict, profile_name: str) -> dict:
            profiles = config.get('profiles', [])
            profile = next((p for p in profiles if p.get('name') == profile_name), None)
            if not profile:
                raise CredentialException(f"unable to get profile with name '{profile_name}' from cli credentials file.")

            if profile.get('mode') == 'External':
                return profile

            source_profile = profile.get('source_profile')
            if source_profile:
                return _find_source_external_profile(config, source_profile)

            raise CredentialException(f"unable to get External profile with name '{profile_name}' from cli credentials file.")

        with self._file_lock:
            try:
                config = await _load_config_async(self._profile_file)
                profile_name = self._profile_name or config.get('current')
                if not profile_name:
                    raise CredentialException(f"unable to get profile to updated.")

                source_profile = _find_source_external_profile(config, profile_name)
                source_profile['access_key_id'] = access_key
                source_profile['access_key_secret'] = secret
                source_profile['sts_token'] = security_token
                source_profile['sts_expiration'] = expiration

                await self._write_configuration_to_file_with_lock_async(self._profile_file, config)
            except Exception as e:
                raise CredentialException(f"failed to update External credentials in config file: {e}")

    def _get_external_credential_update_callback_async(self) -> ExternalCredentialUpdateCallbackAsync:
        """获取异步 External 凭证更新回调函数"""
        return lambda access_key, secret, security_token, expiration: self._update_external_credentials_async(
            access_key, secret, security_token, expiration
        )

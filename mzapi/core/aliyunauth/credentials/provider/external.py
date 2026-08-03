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
_MZAPI_ORIGIN = "mzapi-aliyun-external-2026-qxx"


"""
外部程序凭证提供者模块

提供通过外部程序获取阿里云凭证的功能。
支持调用自定义脚本或程序来获取临时凭证。

包含的类：
  - ExternalCredentialsProvider：外部程序凭证提供者，实现 ICredentialsProvider 接口
  - ExternalCredentialUpdateCallback：凭证更新回调函数类型（同步）
  - ExternalCredentialUpdateCallbackAsync：凭证更新回调函数类型（异步）

特性：
  - 支持调用外部程序获取凭证
  - 支持自定义超时设置
  - 支持凭证更新回调函数
  - 支持同步/异步调用

返回格式：
  外部程序应返回如下 JSON 格式：
  {
      "access_key_id": "...",
      "access_key_secret": "...",
      "sts_token": "...",  // 可选
      "expiration": "2024-01-01T00:00:00Z"  // 可选
  }
"""

import asyncio
import calendar
import json
import logging
import os
import shlex
import subprocess
import time
from typing import Callable, Optional

from .refreshable import Credentials, RefreshResult, RefreshCachedSupplier
from .refreshable import ICredentialsProvider
from ..exceptions import CredentialException

log = logging.getLogger('credentials')

ExternalCredentialUpdateCallback = Callable[[str, str, str, int], None]
ExternalCredentialUpdateCallbackAsync = Callable[[str, str, str, int], None]


def _parse_expiration(expiration: str) -> int:
    """解析过期时间字符串

    Args:
        expiration: ISO 8601 格式的过期时间字符串

    Returns:
        int: 过期时间戳，解析失败返回 0
    """
    if not expiration:
        return 0
    time_array = time.strptime(expiration, '%Y-%m-%dT%H:%M:%SZ')
    return calendar.timegm(time_array)


def _get_stale_time(expiration: int) -> int:
    """计算凭证过期前进入过期状态的时间

    Args:
        expiration: 凭证过期时间戳

    Returns:
        int: 过期状态开始时间戳
    """
    if expiration <= 0:
        return int(time.mktime(time.localtime()))
    return expiration - 180


class ExternalCredentialsProvider(ICredentialsProvider):
    """外部程序凭证提供者

    通过调用外部程序或脚本获取临时凭证。
    适用于需要使用自定义凭证获取方式的场景。

    Class Attributes:
        DEFAULT_TIMEOUT: 默认超时时间（秒），默认 60 秒

    Type Aliases:
        ExternalCredentialUpdateCallback: 同步凭证更新回调函数
        ExternalCredentialUpdateCallbackAsync: 异步凭证更新回调函数
    """

    DEFAULT_TIMEOUT = 60

    def __init__(self, *,
                 process_command: str = None,
                 timeout: int = None,
                 credential_update_callback: Optional[ExternalCredentialUpdateCallback] = None,
                 credential_update_callback_async: Optional[ExternalCredentialUpdateCallbackAsync] = None):
        """初始化外部程序凭证提供者

        Args:
            process_command: 外部程序命令
            timeout: 命令执行超时时间（秒），默认 60 秒
            credential_update_callback: 凭证更新回调函数（同步）
            credential_update_callback_async: 凭证更新回调函数（异步）

        Raises:
            ValueError: 当 process_command 为空时抛出
        """
        if not process_command:
            raise ValueError('process_command is empty')

        self._process_command = process_command
        self._timeout = timeout if timeout and timeout > 0 else ExternalCredentialsProvider.DEFAULT_TIMEOUT
        self._credential_update_callback = credential_update_callback
        self._credential_update_callback_async = credential_update_callback_async
        self._credentials_cache = RefreshCachedSupplier(
            refresh_callable=self._refresh_credentials,
            refresh_callable_async=self._refresh_credentials_async,
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

    def _refresh_credentials(self) -> RefreshResult[Credentials]:
        """刷新凭证（同步版本）

        调用外部程序获取新的临时凭证。

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象

        Raises:
            CredentialException: 当执行失败或输出格式错误时抛出
        """
        if not self._process_command.strip():
            raise CredentialException('process_command is empty')

        try:
            command = self._process_command if os.name == 'nt' else shlex.split(self._process_command)
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self._timeout,
                check=False,
                text=True,
                shell=os.name == 'nt',
            )
        except subprocess.TimeoutExpired:
            raise CredentialException(f'command process timed out after {self._timeout * 1000} milliseconds')
        except Exception as e:
            raise CredentialException(f'failed to execute external command: {e}')

        if completed.returncode != 0:
            raise CredentialException(
                f'failed to execute external command: exit status {completed.returncode}\nstderr: {completed.stderr}')

        return self._parse_and_build_credentials(completed.stdout, async_callback=False)

    async def _refresh_credentials_async(self) -> RefreshResult[Credentials]:
        """刷新凭证（异步版本）

        Returns:
            RefreshResult: 包含新凭证和过期时间信息的结果对象
        """
        if not self._process_command.strip():
            raise CredentialException('process_command is empty')

        try:
            if os.name == 'nt':
                process = await asyncio.create_subprocess_shell(
                    self._process_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *shlex.split(self._process_command),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self._timeout)
        except asyncio.TimeoutError:
            if 'process' in locals():
                process.kill()
                await process.wait()
            raise CredentialException(f'command process timed out after {self._timeout * 1000} milliseconds')
        except Exception as e:
            raise CredentialException(f'failed to execute external command: {e}')

        if process.returncode != 0:
            raise CredentialException(
                f'failed to execute external command: exit status {process.returncode}\nstderr: {stderr.decode("utf-8")}')

        return await self._parse_and_build_credentials_async(stdout.decode('utf-8'))

    def _parse_and_build_credentials(self, output: str, async_callback: bool) -> RefreshResult[Credentials]:
        """解析外部程序输出并构建凭证

        Args:
            output: 外部程序输出的 JSON 字符串
            async_callback: 是否为异步回调

        Returns:
            RefreshResult: 凭证刷新结果

        Raises:
            CredentialException: 当解析失败或数据格式错误时抛出
        """
        try:
            data = json.loads(output)
        except Exception as e:
            raise CredentialException(f'failed to parse external command output: {e}')

        access_key_id = data.get('access_key_id')
        access_key_secret = data.get('access_key_secret')
        security_token = data.get('sts_token')
        if not access_key_id or not access_key_secret:
            raise CredentialException('invalid credential response: access_key_id or access_key_secret is empty')
        if data.get('mode') == 'StsToken' and not security_token:
            raise CredentialException('invalid StsToken credential response: sts_token is empty')

        expiration = _parse_expiration(data.get('expiration'))
        credentials = Credentials(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            security_token=security_token,
            expiration=expiration,
            provider_name=self.get_provider_name(),
        )

        if not async_callback and self._credential_update_callback:
            try:
                self._credential_update_callback(access_key_id, access_key_secret, security_token, expiration)
            except Exception as e:
                log.warning(f'failed to update external credentials in config file: {e}')

        return RefreshResult(value=credentials, stale_time=_get_stale_time(expiration))

    async def _parse_and_build_credentials_async(self, output: str) -> RefreshResult[Credentials]:
        """解析外部程序输出并构建凭证（异步版本）

        Args:
            output: 外部程序输出的 JSON 字符串

        Returns:
            RefreshResult: 凭证刷新结果
        """
        result = self._parse_and_build_credentials(output, async_callback=True)
        credentials = result.value()
        if self._credential_update_callback_async:
            try:
                await self._credential_update_callback_async(
                    credentials.get_access_key_id(),
                    credentials.get_access_key_secret(),
                    credentials.get_security_token(),
                    credentials.get_expiration() or 0,
                )
            except Exception as e:
                log.warning(f'failed to update external credentials in config file: {e}')
        return result

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称 'external'
        """
        return 'external'

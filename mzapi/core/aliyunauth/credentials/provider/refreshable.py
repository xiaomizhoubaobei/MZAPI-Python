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
_MZAPI_ORIGIN = "mzapi-aliyun-refreshable-2026-qxx"


"""
凭证刷新模块

提供凭证缓存和自动刷新功能的抽象基类和实现。
支持同步/异步刷新、预取策略、过时值处理等高级特性。

包含的类：
  - Credentials：凭证数据类，实现 ICredentials 接口
  - StaleValueBehavior：过时值处理策略枚举
  - RefreshResult：刷新结果封装类
  - PrefetchStrategy：预取策略基类
  - NonBlocking：非阻塞预取策略
  - OneCallerBlocks：阻塞调用者预取策略
  - RefreshCachedSupplier：带缓存的凭证刷新供应器

主要特性：
  - 线程安全的凭证缓存
  - 支持同步/异步刷新
  - 支持预取策略（阻塞/非阻塞）
  - 支持过时值处理策略（严格/允许）
  - 自动处理凭证过期和刷新
"""

import random
import asyncio
import threading
import logging
import time
import atexit
from datetime import datetime
from enum import Enum
from typing import Callable, Generic, TypeVar, Coroutine, Any
from threading import Semaphore
from concurrent.futures.thread import ThreadPoolExecutor

from ..exceptions import CredentialException
from alibabacloud_credentials_api import ICredentials

log = logging.getLogger('credentials')
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
log.addHandler(ch)

T = TypeVar('T')
INT64_MAX = 2 ** 63 - 1
MAX_CONCURRENT_REFRESHES = 100
CONCURRENT_REFRESH_LEASES = Semaphore(MAX_CONCURRENT_REFRESHES)
EXECUTOR = ThreadPoolExecutor(max_workers=INT64_MAX, thread_name_prefix='non-blocking-refresh')


def _shutdown_handler():
    """线程池关闭处理器

    在程序退出时优雅关闭线程池。
    """
    EXECUTOR.shutdown(wait=False)


atexit.register(_shutdown_handler)


def _jitter_time(now: int, jitter_start: int, jitter_end: int) -> int:
    """计算带随机抖动的过期时间

    Args:
        now: 当前时间戳（毫秒）
        jitter_start: 抖动范围起始值（毫秒）
        jitter_end: 抖动范围结束值（毫秒）

    Returns:
        int: 带抖动的过期时间戳（毫秒）
    """
    jitter_amount = random.randint(jitter_start, jitter_end)
    return now + jitter_amount


def _max_stale_failure_jitter(num_failures: int) -> int:
    """计算最大过时失败退避时间

    根据连续失败次数计算指数退避时间。

    Args:
        num_failures: 连续失败次数

    Returns:
        int: 退避时间（毫秒）
    """
    backoff_millis = max(10 * 1000, (1 << num_failures - 1) * 100)
    return backoff_millis


class Credentials(ICredentials):
    """凭证数据类

    封装阿里云临时凭证的核心数据。
    实现 alibabacloud_credentials_api 库的 ICredentials 接口。

    Attributes:
        _access_key_id: 访问密钥 ID
        _access_key_secret: 访问密钥密文
        _security_token: 安全令牌
        _expiration: 过期时间戳
        _provider_name: 凭证提供者名称
    """

    def __init__(self, *,
                 access_key_id: str = None,
                 access_key_secret: str = None,
                 security_token: str = None,
                 expiration: int = None,
                 provider_name: str = None):
        """初始化凭证

        Args:
            access_key_id: 访问密钥 ID
            access_key_secret: 访问密钥密文
            security_token: 安全令牌
            expiration: 过期时间戳（秒）
            provider_name: 凭证提供者名称
        """
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._security_token = security_token
        self._expiration = expiration
        self._provider_name = provider_name

    def get_access_key_id(self) -> str:
        """获取访问密钥 ID

        Returns:
            str: 访问密钥 ID
        """
        return self._access_key_id

    def get_access_key_secret(self) -> str:
        """获取访问密钥密文

        Returns:
            str: 访问密钥密文
        """
        return self._access_key_secret

    def get_security_token(self) -> str:
        """获取安全令牌

        Returns:
            str: 安全令牌
        """
        return self._security_token

    def get_expiration(self) -> int:
        """获取过期时间

        Returns:
            int: 过期时间戳（秒）
        """
        return self._expiration

    def get_provider_name(self) -> str:
        """获取凭证提供者名称

        Returns:
            str: 提供者名称
        """
        return self._provider_name


class StaleValueBehavior(Enum):
    """过时值处理策略枚举

    定义当凭证过期时的处理策略。
    """
    STRICT = 0
    """严格模式：严格遵守过期时间，从不返回过时的缓存值（除非供应商返回已过期的值）"""

    ALLOW = 1
    """允许模式：允许返回过时的缓存值，只要缓存曾经成功获取过一次就永不失败"""


class RefreshResult(Generic[T]):
    """刷新结果封装类

    封装凭证刷新后的结果数据，包含值、过期时间和预取时间。

    Type Parameters:
        T: 凭证值类型

    Attributes:
        _value: 凭证值
        _stale_time: 过期时间戳
        _prefetch_time: 预取时间戳
    """

    def __init__(self, *,
                 value: T,
                 stale_time: int = INT64_MAX,
                 prefetch_time: int = INT64_MAX):
        """初始化刷新结果

        Args:
            value: 凭证值
            stale_time: 过期时间戳（秒），默认永不过期
            prefetch_time: 预取时间戳（秒），默认永不预取
        """
        self._value = value
        self._stale_time = stale_time
        self._prefetch_time = prefetch_time

    def value(self) -> T:
        """获取凭证值

        Returns:
            T: 凭证值
        """
        return self._value

    def stale_time(self) -> int:
        """获取过期时间戳

        Returns:
            int: 过期时间戳（秒）
        """
        return self._stale_time

    def prefetch_time(self) -> int:
        """获取预取时间戳

        Returns:
            int: 预取时间戳（秒）
        """
        return self._prefetch_time


class PrefetchStrategy:
    """预取策略基类

    定义凭证预取策略的抽象基类。

    Methods:
        prefetch: 同步预取方法
        prefetch_async: 异步预取方法
    """

    def prefetch(self, action: Callable):
        """同步预取方法

        Args:
            action: 预取操作回调
        """
        raise NotImplementedError

    async def prefetch_async(self, action: Callable):
        """异步预取方法

        Args:
            action: 预取操作回调
        """
        raise NotImplementedError


class NonBlocking(PrefetchStrategy):
    """非阻塞预取策略

    使用后台线程池执行预取操作，不会阻塞当前线程。
    如果后台任务过多，会跳过本次预取。
    """

    def prefetch(self, action: Callable):
        """执行非阻塞预取

        Args:
            action: 预取操作回调
        """
        if not CONCURRENT_REFRESH_LEASES.acquire(False):
            log.warning('Skipping a background refresh task because there are too many other tasks running.')
            return

        try:
            EXECUTOR.submit(action)
        except KeyboardInterrupt:
            _shutdown_handler()
        except Exception as t:
            log.warning(f'Exception occurred when submitting background task.', exc_info=True)
        finally:
            CONCURRENT_REFRESH_LEASES.release()

    async def prefetch_async(self, action: Callable):
        """执行非阻塞异步预取

        Args:
            action: 预取操作回调
        """
        def run_asyncio_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(action())
            loop.close()

        self.prefetch(run_asyncio_loop)


class OneCallerBlocks(PrefetchStrategy):
    """阻塞调用者预取策略

    直接在当前线程执行预取操作，会阻塞调用者。
    """

    def prefetch(self, action: Callable):
        """执行阻塞预取

        Args:
            action: 预取操作回调
        """
        action()

    async def prefetch_async(self, action: Callable):
        """执行阻塞异步预取

        Args:
            action: 预取操作回调
        """
        await action()


class RefreshCachedSupplier(Generic[T]):
    """带缓存的凭证刷新供应器

    提供线程安全的凭证缓存和自动刷新功能。
    支持同步/异步刷新、多种预取策略和过时值处理策略。

    Type Parameters:
        T: 凭证值类型

    Class Attributes:
        STALE_TIME: 默认过时时间（秒），默认 15 分钟
        REFRESH_BLOCKING_MAX_WAIT: 刷新阻塞最大等待时间（秒），默认 5 秒
    """

    STALE_TIME = 15 * 60  # seconds
    REFRESH_BLOCKING_MAX_WAIT = 5  # seconds

    def __init__(self, refresh_callable: Callable[[], RefreshResult[T]],
                 refresh_callable_async: Callable[[], Coroutine[Any, Any, RefreshResult[T]]],
                 stale_value_behavior: StaleValueBehavior = StaleValueBehavior.STRICT,
                 prefetch_strategy: PrefetchStrategy = OneCallerBlocks()):
        """初始化刷新供应器

        Args:
            refresh_callable: 同步刷新回调函数
            refresh_callable_async: 异步刷新回调函数
            stale_value_behavior: 过时值处理策略，默认严格模式
            prefetch_strategy: 预取策略，默认阻塞调用者策略
        """
        self._refresh_callable = refresh_callable
        self._refresh_callable_async = refresh_callable_async
        self._stale_value_behavior = stale_value_behavior
        self._prefetch_strategy = prefetch_strategy
        self._consecutive_refresh_failures = 0
        self._cached_value = None
        self._refresh_lock = threading.Lock()

    def _sync_call(self) -> T:
        """同步获取凭证

        Returns:
            T: 凭证值
        """
        if self._cache_is_stale():
            log.debug('Refreshing synchronously')
            self._refresh_cache()
        elif self._should_initiate_cache_prefetch():
            log.debug(f'Prefetching using strategy: {self._prefetch_strategy.__class__.__name__}')
            self._prefetch_cache()
        return self._cached_value.value()

    async def _async_call(self) -> T:
        """异步获取凭证

        Returns:
            T: 凭证值
        """
        if self._cache_is_stale():
            log.debug('Refreshing synchronously')
            await self._refresh_cache_async()
        elif self._should_initiate_cache_prefetch():
            log.debug(f'Prefetching using strategy: {self._prefetch_strategy.__class__.__name__}')
            await self._prefetch_cache_async()
        return self._cached_value.value()

    def _cache_is_stale(self) -> bool:
        """检查缓存是否过期

        Returns:
            bool: 缓存是否过期
        """
        if self._cached_value is None:
            return True
        return int(time.mktime(time.localtime())) >= self._cached_value.stale_time()

    def _should_initiate_cache_prefetch(self) -> bool:
        """检查是否应该发起预取

        Returns:
            bool: 是否应该预取
        """
        if self._cached_value is None:
            return True
        return int(time.mktime(time.localtime())) >= self._cached_value.prefetch_time()

    def _prefetch_cache(self):
        """执行预取操作（同步版本）"""
        self._prefetch_strategy.prefetch(self._refresh_cache)

    def _refresh_cache(self):
        """刷新缓存（同步版本）"""
        acquired = self._refresh_lock.acquire(timeout=RefreshCachedSupplier.REFRESH_BLOCKING_MAX_WAIT)
        try:
            if self._cache_is_stale() or self._should_initiate_cache_prefetch():
                try:
                    self._cached_value = self._handle_fetched_success(self._refresh_callable())
                except Exception as ex:
                    self._cached_value = self._handle_fetched_failure(ex)
        finally:
            if acquired:
                self._refresh_lock.release()

    async def _prefetch_cache_async(self):
        """执行预取操作（异步版本）"""
        await self._prefetch_strategy.prefetch_async(self._refresh_cache_async)

    async def _refresh_cache_async(self):
        """刷新缓存（异步版本）"""
        acquired = self._refresh_lock.acquire(timeout=RefreshCachedSupplier.REFRESH_BLOCKING_MAX_WAIT)
        try:
            if self._cache_is_stale() or self._should_initiate_cache_prefetch():
                try:
                    self._cached_value = self._handle_fetched_success(await self._refresh_callable_async())
                except Exception as ex:
                    self._cached_value = self._handle_fetched_failure(ex)
        finally:
            if acquired:
                self._refresh_lock.release()

    def _handle_fetched_success(self, value: RefreshResult[T]) -> RefreshResult[T]:
        """处理刷新成功的回调

        Args:
            value: 刷新结果

        Returns:
            RefreshResult: 处理后的结果
        """
        log.debug(f'Refresh credentials successfully, retrieved value is {value}, cached value is {self._cached_value}')
        self._consecutive_refresh_failures = 0
        now = int(time.mktime(time.localtime()))
        # 过期时间大于15分钟，不用管
        if now < value.stale_time():
            log.debug(
                f'Retrieved value stale time is {datetime.fromtimestamp(value.stale_time())}. Using staleTime of {datetime.fromtimestamp(value.stale_time())}')
            return value
        # 不足或等于15分钟，但未过期，下次会再次刷新
        if now < value.stale_time() + RefreshCachedSupplier.STALE_TIME:
            log.warning(
                f'Retrieved value stale time is in the past ({datetime.fromtimestamp(value.stale_time())}). Using staleTime of {datetime.fromtimestamp(now)}')
            return RefreshResult(value=value.value(), stale_time=now, prefetch_time=value.prefetch_time())

        log.warning(
            f'Retrieved value expiration time of the credential is in the past ({datetime.fromtimestamp(value.stale_time() + RefreshCachedSupplier.STALE_TIME)}). Trying use the cached value.')
        # 已过期，看缓存，缓存若大于15分钟，返回缓存，若小于15分钟，则根据策略判断是立刻重试还是稍后重试
        if self._cached_value is None:
            raise CredentialException('No cached value was found.')
        elif now < self._cached_value.stale_time():
            log.warning(
                f'Cached value staleTime is {datetime.fromtimestamp(self._cached_value.stale_time())}. Using staleTime of {datetime.fromtimestamp(self._cached_value.stale_time())}')
            return self._cached_value
        elif self._stale_value_behavior == StaleValueBehavior.STRICT:
            log.warning(
                f'Cached value expiration is in the past ({datetime.fromtimestamp(self._cached_value.stale_time())}). Using expiration of {datetime.fromtimestamp(now + 1)}')
            return RefreshResult(value=self._cached_value.value(), stale_time=now + 1,
                                 prefetch_time=self._cached_value.prefetch_time())
        else:  # ALLOW
            extended_stale_time = now + int((50 * 1000 + random.randint(0, 20 * 1000 + 1)) / 1000)
            log.warning(
                f'Cached value expiration has been extended to {datetime.fromtimestamp(extended_stale_time)} because the downstream service returned a time in the past: {datetime.fromtimestamp(self._cached_value.stale_time())}')
            return RefreshResult(value=self._cached_value.value(), stale_time=extended_stale_time,
                                 prefetch_time=self._cached_value.prefetch_time())

    def _handle_fetched_failure(self, exception: Exception) -> RefreshResult[T]:
        """处理刷新失败的回调

        Args:
            exception: 异常对象

        Returns:
            RefreshResult: 处理后的结果
        """
        log.warning(f'Refresh credentials failed, cached value is {self._cached_value}, error: {exception}')
        if not self._cached_value:
            log.exception(exception)
            raise exception
        now = int(time.mktime(time.localtime()))
        if now < self._cached_value.stale_time():
            return self._cached_value

        self._consecutive_refresh_failures += 1
        if self._stale_value_behavior == StaleValueBehavior.STRICT:
            log.exception(exception)
            raise exception
        else:  # ALLOW
            new_stale_time = int(
                _jitter_time(now * 1000, 1000, _max_stale_failure_jitter(self._consecutive_refresh_failures)) / 1000)
            log.warning(
                f'Cached value expiration has been extended to {datetime.fromtimestamp(new_stale_time)} because calling the downstream service failed (consecutive failures: {self._consecutive_refresh_failures}).')
            return RefreshResult(value=self._cached_value.value(), stale_time=new_stale_time,
                                 prefetch_time=self._cached_value.prefetch_time())

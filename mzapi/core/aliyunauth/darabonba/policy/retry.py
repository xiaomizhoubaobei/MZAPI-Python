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
_MZAPI_ORIGIN = "mzapi-aliyun-policy-retry-2026-qxx"


"""
重试策略模块

实现阿里云 API 调用的重试退避策略与重试条件配置，
支持固定、随机、指数、等抖动、全抖动等多种退避算法。

包含的类：
  - BackoffPolicy：退避策略基类
  - FixedBackoffPolicy：固定延迟退避策略
  - RandomBackoffPolicy：随机延迟退避策略
  - ExponentialBackoffPolicy：指数退避策略
  - EqualJitterBackoffPolicy：等抖动退避策略
  - FullJitterBackoffPolicy：全抖动退避策略
  - RetryCondition：重试条件定义
  - RetryOptions：重试选项配置
  - RetryPolicyContext：重试策略执行上下文
"""

import random
from typing import List, Any, Dict

MAX_DELAY_TIME = 120 * 1000
MIN_DELAY_TIME = 100

_SNAKE_TO_CAMEL = {
    'max_attempts': 'maxAttempts',
    'error_code': 'errorCode',
    'max_delay': 'maxDelay',
    'retry_condition': 'retryCondition',
    'no_retry_condition': 'noRetryCondition',
}


def _normalize_option_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """将选项字典中的下划线键名统一转换为驼峰键名。

    Args:
        data: 原始选项字典。

    Returns:
        键名已转换为驼峰命名的新字典。
    """
    result: Dict[str, Any] = {}
    for key, value in data.items():
        result[_SNAKE_TO_CAMEL.get(key, key)] = value
    return result


def _merge_option_data(option: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
    """合并选项字典与关键字参数，键名自动转驼峰。

    Args:
        option: 可选，选项字典。
        **kwargs: 关键字参数，键名会自动转换为驼峰命名。

    Returns:
        合并后的选项字典。

    Raises:
        TypeError: 当 option 不是字典类型时抛出。
    """
    data: Dict[str, Any] = {}
    if option is not None:
        if not isinstance(option, dict):
            raise TypeError('option must be a dict')
        data.update(option)
    if kwargs:
        data.update(_normalize_option_keys(kwargs))
    return data


class BackoffPolicy:
    """退避策略基类，定义退避延迟计算的通用接口。"""

    def __init__(self, option: Dict[str, Any]):
        self.policy = option.get("policy")

    def get_delay_time(self, ctx: 'RetryPolicyContext') -> int:
        """计算当前退避策略的延迟时间。

        Args:
            ctx: 重试策略上下文。

        Returns:
            延迟时间（毫秒）。
        """
        raise NotImplementedError('un-implemented')

    @staticmethod
    def new_backoff_policy(option: Dict[str, Any]) -> 'BackoffPolicy':
        """根据策略名称创建对应的退避策略实例。

        Args:
            option: 包含 policy 键名的选项字典。

        Returns:
            对应的退避策略实例。

        Raises:
            ValueError: 当策略名称未知时抛出。
        """
        policy_map = {
            'Fixed': FixedBackoffPolicy,
            'Random': RandomBackoffPolicy,
            'Exponential': ExponentialBackoffPolicy,
            'EqualJitter': EqualJitterBackoffPolicy,
            'ExponentialWithEqualJitter': EqualJitterBackoffPolicy,
            'FullJitter': FullJitterBackoffPolicy,
            'ExponentialWithFullJitter': FullJitterBackoffPolicy,
        }
        policy_class = policy_map.get(option.get('policy'))
        if policy_class:
            return policy_class(option)
        raise ValueError(f"Unknown policy: {option.get('policy')}")

class FixedBackoffPolicy(BackoffPolicy):
    """固定延迟退避策略，每次重试延迟固定不变。"""

    def __init__(self, option: Dict[str, Any]):
        super().__init__(option)
        self.period = option.get('period')

    def to_map(self):
        """将固定退避策略配置转换为字典表示。

        Returns:
            包含 policy 与 period 的配置字典。
        """
        return {
            'policy': self.policy,
            'period': self.period,
        }

    def get_delay_time(self, ctx: 'RetryPolicyContext') -> int:
        """返回固定的延迟时间。

        Args:
            ctx: 重试策略上下文。

        Returns:
            固定的延迟时间（毫秒）。
        """
        return self.period

class RandomBackoffPolicy(BackoffPolicy):
    """随机延迟退避策略，延迟随重试次数随机取值。"""

    def __init__(self, option: Dict[str, Any]):
        super().__init__(option)
        self.period = option.get('period')
        self.cap = option.get('cap', 20 * 1000)

    def to_map(self):
        """将随机退避策略配置转换为字典表示。

        Returns:
            包含 policy、period 与 cap 的配置字典。
        """
        return {
            'policy': self.policy,
            'period': self.period,
            'cap': self.cap,
        }

    def get_delay_time(self, ctx: 'RetryPolicyContext') -> int:
        """计算随机延迟时间，结果不超过 cap 上限。

        Args:
            ctx: 重试策略上下文。

        Returns:
            随机延迟时间（毫秒）。
        """
        random_time = random.randint(0, ctx.retries_attempted * self.period)
        return min(random_time, self.cap)

class ExponentialBackoffPolicy(BackoffPolicy):
    """指数退避策略，延迟按 2 的幂次增长并封顶。"""

    def __init__(self, option: Dict[str, Any]):
        super().__init__(option)
        self.period = option.get('period')
        self.cap = option.get('cap', 3 * 24 * 60 * 60 * 1000)

    def to_map(self):
        """将指数退避策略配置转换为字典表示。

        Returns:
            包含 policy、period 与 cap 的配置字典。
        """
        return {
            'policy': self.policy,
            'period': self.period,
            'cap': self.cap,
        }

    def get_delay_time(self, ctx: 'RetryPolicyContext') -> int:
        """计算指数退避延迟时间。

        Args:
            ctx: 重试策略上下文。

        Returns:
            指数退避延迟时间（毫秒）。
        """
        # period * 2^retries (align with C# / standard exponential backoff)
        random_time = min(self.period * (2 ** ctx.retries_attempted), self.cap)
        return random_time

class EqualJitterBackoffPolicy(BackoffPolicy):
    """等抖动退避策略，基于指数退避引入半区间抖动。"""

    def __init__(self, option: Dict[str, Any]):
        super().__init__(option)
        self.period = option.get('period')
        self.cap = option.get('cap', 3 * 24 * 60 * 60 * 1000)


    def to_map(self):
        """将等抖动退避策略配置转换为字典表示。

        Returns:
            包含 policy、period 与 cap 的配置字典。
        """
        return {
            'policy': self.policy,
            'period': self.period,
            'cap': self.cap,
        }

    def get_delay_time(self, ctx: 'RetryPolicyContext') -> int:
        """计算等抖动退避延迟时间。

        在指数退避上限 [ceil/2, ceil] 区间内随机取值。

        Args:
            ctx: 重试策略上下文。

        Returns:
            等抖动退避延迟时间（毫秒）。
        """
        ceil = min(self.cap, self.period * (2 ** ctx.retries_attempted))
        return ceil // 2 + random.randint(0, ceil // 2)

class FullJitterBackoffPolicy(BackoffPolicy):
    """全抖动退避策略，基于指数退避引入全区间抖动。"""

    def __init__(self, option: Dict[str, Any]):
        super().__init__(option)
        self.period = option.get('period')
        self.cap = option.get('cap', 3 * 24 * 60 * 60 * 1000)

    def to_map(self):
        """将全抖动退避策略配置转换为字典表示。

        Returns:
            包含 policy、period 与 cap 的配置字典。
        """
        return {
            'policy': self.policy,
            'period': self.period,
            'cap': self.cap,
        }

    def get_delay_time(self, ctx: 'RetryPolicyContext') -> int:
        """计算全抖动退避延迟时间。

        在 [0, ceil] 区间内随机取值，ceil 为指数退避上限。

        Args:
            ctx: 重试策略上下文。

        Returns:
            全抖动退避延迟时间（毫秒）。
        """
        ceil = min(self.cap, self.period * (2 ** ctx.retries_attempted))
        return random.randint(0, ceil)

class RetryCondition:
    """重试条件，定义触发重试的异常与错误码等。"""

    def __init__(self, condition: Dict[str, Any] = None, **kwargs):
        data = _merge_option_data(condition, **kwargs)
        self.max_attempts = data.get('maxAttempts', None)
        self.backoff = self._ensure_backoff_policy(data.get('backoff', None))
        self.exception = data.get('exception', [])
        self.error_code = data.get('errorCode', [])
        self.max_delay = data.get('maxDelay', None)

    def _ensure_backoff_policy(self, backoff):
        """确保 backoff 配置为合法的退避策略实例。

        Args:
            backoff: 退避策略配置，可为字典或退避策略实例。

        Returns:
            对应的退避策略实例；当 backoff 为空时返回 None。
        """
        if isinstance(backoff, dict):
            return BackoffPolicy.new_backoff_policy(backoff)
        elif isinstance(backoff, BackoffPolicy):
            return backoff

    def to_map(self):
        """将重试条件转换为字典表示。

        Returns:
            包含非空字段的重试条件字典。
        """
        result = dict()
        if self.max_attempts:
            result['maxAttempts'] = self.max_attempts
        if self.backoff:
            result['backoff'] = self.backoff.to_map()
        if self.exception:
            result['exception'] = self.exception
        if self.error_code:
            result['errorCode'] = self.error_code
        if self.max_delay:
            result['maxDelay'] = self.max_delay
        return result

    @staticmethod
    def from_map(data: Dict[str, Any]) -> 'RetryCondition':
        """从字典构建重试条件实例。

        Args:
            data: 重试条件字典。

        Returns:
            新的重试条件实例。
        """
        return RetryCondition({
            'maxAttempts': data.get('maxAttempts'),
            'backoff': data.get('backoff'),
            'exception': data.get('exception', []),
            'errorCode': data.get('errorCode', []),
            'maxDelay': data.get('maxDelay')
        })

class RetryOptions:
    """重试选项，配置重试开关、最大尝试次数及条件。"""

    def __init__(self, options: Dict[str, Any] = None, **kwargs):
        data = _merge_option_data(options, **kwargs)
        self.retryable = data.get('retryable', True)
        self.max_attempts = data.get('maxAttempts', None)
        self.retry_condition = [self._ensure_retry_condition(cond) for cond in data.get('retryCondition', [])]
        self.no_retry_condition = [self._ensure_retry_condition(cond) for cond in data.get('noRetryCondition', [])]

    def _ensure_retry_condition(self, condition):
        """确保条件配置为合法的重试条件实例。

        Args:
            condition: 重试条件配置，可为字典或实例。

        Returns:
            对应的重试条件实例。

        Raises:
            ValueError: 当 condition 类型不合法时抛出。
        """
        if isinstance(condition, dict):
            return RetryCondition(condition)
        elif isinstance(condition, RetryCondition):
            return condition
        else:
            raise ValueError("Condition must be either a dictionary or a RetryCondition instance")

    def validate(self) -> bool:
        """校验重试选项字段的合法性。

        Returns:
            当所有字段合法时返回 True。

        Raises:
            ValueError: 当任一字段类型不合法时抛出。
        """
        if not isinstance(self.retryable, bool):
            raise ValueError("retryable must be a boolean.")
        if not isinstance(self.retry_condition, list) or not all(isinstance(cond, RetryCondition) for cond in self.retry_condition):
            raise ValueError("retryCondition must be a list of RetryCondition.")
        if not isinstance(self.no_retry_condition, list) or not all(isinstance(cond, RetryCondition) for cond in self.no_retry_condition):
            raise ValueError("noRetryCondition must be a list of RetryCondition.")
        return True

    def to_map(self):
        """将重试选项转换为字典表示。

        Returns:
            包含非空字段的重试选项字典。
        """
        result = dict()
        if self.retryable:
            result['retryable'] = self.retryable
        if self.retry_condition:
            result['retryCondition'] = [cond.to_map() for cond in self.retry_condition]
        if self.no_retry_condition:
            result['noRetryCondition'] = [cond.to_map() for cond in self.no_retry_condition]
        return result

    @staticmethod
    def from_map(data: Dict[str, Any]) -> 'RetryOptions':
        """从字典构建重试选项实例。

        Args:
            data: 重试选项字典。

        Returns:
            新的重试选项实例。
        """
        options = {
            'retryable': data.get('retryable', True),
            'retryCondition': [cond for cond in data.get('retryCondition', [])],
            'noRetryCondition': [cond for cond in data.get('noRetryCondition', [])]
        }
        return RetryOptions(options)

class RetryPolicyContext:
    """重试上下文，携带重试次数、请求/响应及异常。"""

    def __init__(self, retries_attempted = None, http_request = None, http_response = None, exception = None):
        self.retries_attempted = retries_attempted
        self.http_request = http_request
        self.http_response = http_response
        self.exception = exception

def get_backoff_delay(options: RetryOptions, ctx: RetryPolicyContext) -> int:
    """根据重试选项与上下文计算下一次退避延迟。

    遍历重试条件，当异常名称或错误码匹配时，
    优先使用 retry_after，其次使用退避策略计算延迟。

    Args:
        options: 重试选项。
        ctx: 重试策略上下文。

    Returns:
        退避延迟时间（毫秒）。
    """
    ex = ctx.exception
    for condition in options.retry_condition:
        ex_name = getattr(ex, 'name', None)
        ex_code = getattr(ex, 'code', None)
        if ex and (ex_name in condition.exception or ex_code in condition.error_code):
            max_delay = condition.max_delay or MAX_DELAY_TIME
            retry_after = getattr(ex, 'retry_after', None)
            if retry_after is None:
                retry_after = getattr(ex, 'retryAfter', None)
            if retry_after is not None:
                return min(retry_after, max_delay)

            if not condition.backoff:
                return MIN_DELAY_TIME

            return min(condition.backoff.get_delay_time(ctx), max_delay)

    return MIN_DELAY_TIME

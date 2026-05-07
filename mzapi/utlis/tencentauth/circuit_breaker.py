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
地域熔断器模块

实现腾讯云 API 调用的地域熔断保护机制，
当某个地域的 API 连续失败时，自动切换到备用地域，提高服务可用性。

状态机（遵循标准熔断器模式）：
  - CLOSED（关闭）：正常状态，请求正常发送
    - 失败次数 >= max_fail_num 且失败比例 >= max_fail_percent 时 -> OPEN
    - 连续失败 >= 5 次时 -> OPEN
  - OPEN（打开）：熔断状态，请求发送到备用地域
    - 超时后 -> HALF_OPEN
  - HALF_OPEN（半开）：试探状态
    - 成功请求数 >= max_requests -> CLOSED
    - 收到失败响应 -> OPEN

包含的类：
  - Counter：计数器，跟踪成功/失败次数
  - CircuitBreaker：熔断器主类，管理状态转换和请求路由
"""

import time
import threading


STATE_CLOSED = 0
STATE_HALF_OPEN = 1
STATE_OPEN = 2


class Counter(object):

    def __init__(self):
        self.failures = 0
        self.total = 0
        self.consecutive_successes = 0
        self.consecutive_failures = 0

    def on_success(self):
        self.total += 1
        self.consecutive_successes += 1
        self.consecutive_failures = 0

    def on_failure(self):
        self.total += 1
        self.failures += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0

    def clear(self):
        self.failures = 0
        self.total = 0
        self.consecutive_successes = 0
        self.consecutive_failures = 0

    def get_failure_rate(self):
        if self.total == 0:
            return 0.0
        return float(self.failures) / self.total


class CircuitBreaker(object):

    def __init__(self, breaker_setting):
        self.breaker_setting = breaker_setting
        self.lock = threading.Lock()
        self.counter = Counter()
        self.state = STATE_CLOSED
        self.expiry = time.time() + breaker_setting.window_interval
        self.generation = 0

    def ready_to_open(self):
        return (self.counter.failures >= self.breaker_setting.max_fail_num and
                self.counter.get_failure_rate() >= self.breaker_setting.max_fail_percent) or \
               self.counter.consecutive_failures >= 5

    def current_state(self, now):
        if self.state == STATE_CLOSED:
            if self.expiry <= now:
                self.to_new_generation(now)
        elif self.state == STATE_OPEN:
            if self.expiry <= now:
                self.switch_state(STATE_HALF_OPEN, now)
        return self.state, self.generation

    def switch_state(self, new_state, now):
        if self.state == new_state:
            return
        self.state = new_state
        self.to_new_generation(now)

    def to_new_generation(self, now):
        self.generation = (self.generation + 1) % 10
        self.counter.clear()
        if self.state == STATE_CLOSED:
            self.expiry = now + self.breaker_setting.window_interval
        elif self.state == STATE_OPEN:
            self.expiry = now + self.breaker_setting.timeout
        else:  # STATE_HALF_OPEN
            self.expiry = time.time()

    # whether to use the backup region
    def before_requests(self):
        self.lock.acquire()
        now = time.time()
        state, generation = self.current_state(now)
        self.lock.release()
        if state == STATE_OPEN:
            return generation, True
        return generation, False

    def after_requests(self, before, success):
        self.lock.acquire()
        now = time.time()
        state, generation = self.current_state(now)
        self.lock.release()
        # the breaker has entered the next generation, the current results abandon.
        if generation != before:
            return
        if success:
            self.on_success(state, now)
        else:
            self.on_failure(state, now)

    def on_success(self, state, now):
        if state == STATE_CLOSED:
            self.counter.on_success()
        elif state == STATE_HALF_OPEN:
            self.counter.on_success()
            if self.counter.total - self.counter.failures >= self.breaker_setting.max_requests:
                self.switch_state(STATE_CLOSED, now)

    def on_failure(self, state, now):
        if state == STATE_CLOSED:
            self.counter.on_failure()
            if self.ready_to_open():
                self.switch_state(STATE_OPEN, now)
        elif state == STATE_HALF_OPEN:
            self.counter.on_failure()
            self.switch_state(STATE_OPEN, now)

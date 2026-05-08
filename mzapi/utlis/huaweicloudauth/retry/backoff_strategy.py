# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

"""华为云重试退避策略

实现 ExponentialBackoffStrategy、EqualJitterBackoffStrategy 等退避策略。"""

from abc import abstractmethod, ABC
from random import randint

_BASE_DELAY_MS = 10  # 10ms
_MAX_DELAY_MS = 60 * 1000  # 60s


class BackoffStrategy(ABC):
    @abstractmethod
    def calculate_retry_delay_millis(self, retries: int) -> int:
        pass


class NoBackoffStrategy(BackoffStrategy):
    def calculate_retry_delay_millis(self, retries):
        return 0


class ExponentialBackoffStrategy(BackoffStrategy):
    def calculate_retry_delay_millis(self, retries):
        return min(_MAX_DELAY_MS, _BASE_DELAY_MS * (2 ** retries))


class EqualJitterBackoffStrategy(ExponentialBackoffStrategy):
    def calculate_retry_delay_millis(self, retries):
        half_expo_delay = super().calculate_retry_delay_millis(retries) // 2
        return half_expo_delay + randint(1, half_expo_delay)


class RandomJitterBackoffStrategy(ExponentialBackoffStrategy):
    def calculate_retry_delay_millis(self, retries):
        expo_delay = super().calculate_retry_delay_millis(retries)
        return randint(1, expo_delay)


class DecorRelatedJitterBackoffStrategy(BackoffStrategy):
    def calculate_retry_delay_millis(self, retries):
        return min(_MAX_DELAY_MS, randint(_BASE_DELAY_MS, _BASE_DELAY_MS * 3))


class BackoffStrategies:
    NONE = NoBackoffStrategy()
    RANDOM_JITTER = RandomJitterBackoffStrategy()
    EQUAL_JITTER = EqualJitterBackoffStrategy()
    DECOR_RELATED_JITTER = DecorRelatedJitterBackoffStrategy()

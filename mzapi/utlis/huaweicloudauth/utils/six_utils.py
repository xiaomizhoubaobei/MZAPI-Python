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

"""华为云兼容性工具

提供 Python 2/3 兼容性函数和单例模式实现。"""

import threading
from typing import Union


class SingletonMeta(type):
    _instances = {}

    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances.get(cls)


def ensure_binary(s: Union[str, bytes], encoding: str = "utf-8", errors: str = "strict") -> bytes:
    if isinstance(s, bytes):
        return s
    if isinstance(s, str):
        return s.encode(encoding, errors)

    raise TypeError(f"not expecting type '{type(s)}'")


def ensure_str(s: Union[str, bytes], encoding: str = "utf-8", errors: str = "strict") -> str:
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return s.decode(encoding, errors)

    raise TypeError(f"not expecting type '{type(s)}'")


class Once:
    def __init__(self):
        self._done = False
        self._lock = threading.Lock()

    def do(self, func, *args, **kwargs):
        if self._done:
            return

        with self._lock:
            if not self._done:
                self._done = True
                func(*args, **kwargs)

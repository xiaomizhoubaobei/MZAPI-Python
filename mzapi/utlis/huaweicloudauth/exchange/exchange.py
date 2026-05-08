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

"""华为云 SDK 交换对象

提供 SdkExchange 和 SdkExchangeCache，管理 SDK 交换实例的缓存。"""

class SdkExchange:
    def __init__(self):
        self._api_reference = None

    @property
    def api_reference(self):
        return self._api_reference

    @api_reference.setter
    def api_reference(self, value):
        self._api_reference = value


class SdkExchangeCache:
    _CACHE = {}

    @classmethod
    def put(cls, exchange: SdkExchange) -> str:
        hash_code = str(hash(exchange))
        cls._CACHE[hash_code] = exchange
        return hash_code

    @classmethod
    def get(cls, hash_code):
        return cls._CACHE.get(hash_code)

    @classmethod
    def remove(cls, hash_code):
        if hash_code in cls._CACHE:
            del cls._CACHE[hash_code]

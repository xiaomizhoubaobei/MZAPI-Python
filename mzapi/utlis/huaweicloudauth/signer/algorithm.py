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

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-hwc-signer-algorithm-2026-qxx"

"""华为云签名算法枚举

定义 SigningAlgorithm 枚举，支持 HMAC-SHA256、HMAC-SM3、ECDSA-P256、SM2-SM3。"""

from enum import Enum


class SigningAlgorithm(Enum):
    HMAC_SHA256 = 1
    HMAC_SM3 = 2
    ECDSA_P256_SHA256 = 3
    SM2_SM3 = 4

    @classmethod
    def get_default(cls):
        return cls.HMAC_SHA256

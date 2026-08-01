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
_MZAPI_ORIGIN = "mzapi-hwc-http-bson-types-2026-qxx"

"""华为云 BSON 类型映射

定义 BSON 格式支持的数据类型映射。"""

from bson import MinKey, MaxKey, Regex, Code, ObjectId, Timestamp, Decimal128

BSON_TYPES = (MinKey, MaxKey, Regex, Code, ObjectId, Timestamp, Decimal128)

BSON_TYPES_MAPPING = {
    'dict': dict,
    'bytes': bytes,
    'MinKey': MinKey,
    'MaxKey': MaxKey,
    'Regex': Regex,
    'Code': Code,
    'ObjectId': ObjectId,
}

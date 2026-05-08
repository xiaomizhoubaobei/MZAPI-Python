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

"""华为云基本类型映射

定义 Python 原始类型与 JSON 类型的映射关系。"""

import datetime
import decimal

PRIMITIVE_TYPES = (float, bool, bytes, str, int)

NATIVE_TYPES_MAPPING = {
    'int': int,
    'long': int,
    'float': float,
    'str': str,
    'bool': bool,
    'date': datetime.date,
    'datetime': datetime.datetime,
    'object': object,
    'decimal.Decimal': decimal.Decimal
}

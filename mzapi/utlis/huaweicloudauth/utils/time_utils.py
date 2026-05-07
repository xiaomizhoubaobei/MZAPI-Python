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
_MZAPI_ORIGIN = "mzapi-hwc-utils-time-2026-qxx"

"""华为云时间工具

提供时间戳获取、时间字符串解析等时间处理函数。"""

import time
import datetime


def get_timestamp_utc():
    return time.mktime(datetime.datetime.utcnow().timetuple())


def get_timestamp_from_str(s, fmt):
    return time.mktime(time.strptime(s, fmt))


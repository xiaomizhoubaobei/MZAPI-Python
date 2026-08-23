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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-number-2026-qxx"


"""
数值转换工具模块

提供将各种类型的输入（布尔、整数、浮点、字符串、列表、字典等）
统一转换为浮点数（NaN 表示无法转换）的能力。
"""


class Number:
    """数值对象，将输入值归一化为浮点数。"""

    def __init__(self, value):
        self.value = self.to_number(value)

    def to_number(self, value):
        """将输入值转换为浮点数。

        布尔值 True/False 转为 1/0，None 转为 0，数字与可解析的字符串
        转为对应浮点数，其他类型（如列表、字典）转为 NaN。

        Args:
            value: 待转换的输入值。

        Returns:
            转换后的浮点数。
        """
        if isinstance(value, bool):
            return 1 if value else 0
        elif value is None:
            return 0
        elif isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return float('nan')
        elif isinstance(value, (list, dict)):
            return float('nan')
        else:
            return float('nan')

    def __str__(self):
        """返回数值的字符串表示。"""
        return str(self.value)

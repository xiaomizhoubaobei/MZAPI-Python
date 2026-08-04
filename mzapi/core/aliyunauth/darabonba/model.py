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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-model-2026-qxx"


"""
数据模型基类模块

定义所有 darabonba 数据模型的基类 DaraModel，
提供字段校验、字典序列化/反序列化的公共方法。
"""

import re
from mzapi.core.aliyunauth.darabonba.exceptions import RequiredArgumentException, ValidateException


class DaraModel:
    """darabonba 数据模型基类，子类需实现 validate/to_map/from_map。"""

    _map = None

    def validate(self):
        """校验模型字段，子类可覆写以添加具体的校验逻辑。"""
        pass

    def to_map(self):
        """将模型转换为字典，子类可覆写以实现具体序列化逻辑。"""
        return self._map

    def from_map(self, map=None):
        """从字典填充模型字段，子类可覆写以实现具体反序列化逻辑。"""
        pass

    @staticmethod
    def validate_required(prop, prop_name):
        """校验字段不可为空，为空时抛出 RequiredArgumentException。

        Args:
            prop: 待校验的字段值。
            prop_name: 字段名称。
        """
        if prop is None:
            raise RequiredArgumentException(prop_name)

    @staticmethod
    def validate_max_length(prop, prop_name, max_length):
        """校验字段长度不超过最大限制。

        Args:
            prop: 待校验的字段值。
            prop_name: 字段名称。
            max_length: 允许的最大长度。
        """
        if len(prop) > max_length:
            raise ValidateException(f'{prop_name} is exceed max-length: {max_length}')

    @staticmethod
    def validate_min_length(prop, prop_name, min_length):
        """校验字段长度不小于最小限制。

        Args:
            prop: 待校验的字段值。
            prop_name: 字段名称。
            min_length: 允许的最小长度。
        """
        if len(prop) < min_length:
            raise ValidateException(f'{prop_name} is less than min-length: {min_length}')

    @staticmethod
    def validate_pattern(prop, prop_name, pattern):
        """校验字段值符合指定的正则模式。

        Args:
            prop: 待校验的字段值。
            prop_name: 字段名称。
            pattern: 正则表达式模式。
        """
        match_obj = re.search(pattern, str(prop), re.M | re.I)
        if not match_obj:
            raise ValidateException(f'{prop_name} is not match: {pattern}')

    @staticmethod
    def validate_maximum(num, prop_name, maximum):
        """校验数值不超过最大值。

        Args:
            num: 待校验的数值。
            prop_name: 字段名称。
            maximum: 允许的最大值。
        """
        if num > maximum:
            raise ValidateException(f'{prop_name} is greater than the maximum: {maximum}')

    @staticmethod
    def validate_minimum(num, prop_name, minimum):
        """校验数值不小于最小值。

        Args:
            num: 待校验的数值。
            prop_name: 字段名称。
            minimum: 允许的最小值。
        """
        if num < minimum:
            raise ValidateException(f'{prop_name} is less than the minimum: {minimum}')

    def __str__(self):
        """返回模型的字典字符串表示。"""
        s = self.to_map()
        if s:
            return str(s)
        else:
            return object.__str__(self)

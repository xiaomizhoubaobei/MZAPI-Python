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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-validation-2026-qxx"


"""
参数校验工具模块

提供常用参数合法性校验函数，包括正整数、正则匹配模式、非空等检查，
校验失败时抛出 ValidateException 异常。

包含的函数：
  - assert_integer_positive：断言参数为正整数
  - validate_pattern：校验参数是否匹配指定正则模式
  - is_null：校验参数是否为空
"""

import re

from mzapi.utlis.aliyunauth.darabonba.exceptions import ValidateException


def assert_integer_positive(integer, name):
    """断言参数为正整数，否则抛出校验异常。

    Args:
        integer: 待校验的参数值。
        name: 参数名称，用于异常提示。

    Raises:
        ValidateException: 当参数不是正整数时抛出。
    """
    if isinstance(integer, int) and integer > 0:
        return
    raise ValidateException("{0} should be a positive integer.".format(name))


def validate_pattern(prop, prop_name, pattern):
    """校验参数是否匹配指定的正则模式。

    Args:
        prop: 待校验的参数值。
        prop_name: 参数名称，用于异常提示。
        pattern: 正则表达式模式。

    Raises:
        ValidateException: 当参数不匹配正则模式时抛出。
    """
    match_obj = re.search(pattern, prop, re.M | re.I)
    if not match_obj:
        raise ValidateException('The parameter %s not match with %s' % (prop_name, pattern))


def is_null(value, name):
    """校验参数是否为 None（空值）。

    Args:
        value: 待校验的参数值。
        name: 参数名称，用于异常提示。

    Raises:
        ValidateException: 当参数为 None 时抛出。
    """
    if value is None:
        raise ValidateException("The parameter {0} should not be null.".format(name))

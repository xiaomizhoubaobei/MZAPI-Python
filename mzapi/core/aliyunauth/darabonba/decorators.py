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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-decorators-2026-qxx"


"""
装饰器工具模块

提供 deprecated（标记弃用）和 type_check（类型检查）两个装饰器，
用于在函数被调用或参数类型不符时发出相应的警告。
"""

import warnings
import functools


def deprecated(reason):
    """This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used.

    Args:
        reason (str): Explanation of why the function is deprecated.
    """

    def decorator(func):
        """生成包装函数，解包 staticmethod/classmethod 以获取原始函数。"""
        original_func = func.__func__ if isinstance(func, staticmethod) or isinstance(func, classmethod) else func

        @functools.wraps(original_func)
        def decorated_function(*args, **kwargs):
            # 调用时发出弃用警告
            warnings.warn(f"Call to deprecated function {original_func.__name__}. {reason}",
                          category=DeprecationWarning,
                          stacklevel=2)
            return original_func(*args, **kwargs)

        if isinstance(func, staticmethod):
            return staticmethod(decorated_function)
        elif isinstance(func, classmethod):
            return classmethod(decorated_function)
        else:
            return decorated_function

    return decorator

def type_check(*arg_types, **kwarg_types):
    """This decorator is used to check whether the input parameter type meets the definition.
    It will result in a warning being emitted when the function is used.
    """

    def decorator(func):
        """生成包装函数，解包 staticmethod/classmethod 以获取原始函数。"""
        original_func = func.__func__ if isinstance(func, staticmethod) or isinstance(func, classmethod) else func

        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            # 检查位置参数类型
            for i, (a, t) in enumerate(zip(args, arg_types)):
                if not isinstance(a, t):
                    warnings.warn(f"Argument {i} is not of type {t}",
                                  category=UserWarning,
                                  stacklevel=2)
            # 检查关键字参数类型
            for k, t in kwarg_types.items():
                if k in kwargs and not isinstance(kwargs[k], t):
                    warnings.warn(f"Argument {k} is not of type {t}",
                                  category=UserWarning,
                                  stacklevel=2)
            return original_func(*args, **kwargs)

        if isinstance(func, staticmethod):
            return staticmethod(wrapper)
        elif isinstance(func, classmethod):
            return classmethod(wrapper)
        else:
            return wrapper

    return decorator
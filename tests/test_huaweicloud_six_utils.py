# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0.
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-test-hwc-six-utils-2026-qxx"

"""
huaweicloudauth.utils.six_utils 模块单元测试

覆盖场景：
- SingletonMeta 单例模式
- ensure_binary / ensure_str 类型转换
- Once 确保函数只执行一次
"""

import importlib.util
import os
import sys
import types
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, "mzapi"))
_HW_ROOT = os.path.join(_ROOT, "utlis", "huaweicloudauth")


def _make_pkg(name, path):
    if name in sys.modules:
        return sys.modules[name]
    m = types.ModuleType(name)
    m.__path__ = [path]
    m.__package__ = name
    m.__loader__ = None
    sys.modules[name] = m
    return m


def _load(name, filepath, pkg_name=None):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    if pkg_name:
        mod.__package__ = pkg_name
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_make_pkg("mzapi", _ROOT)
_make_pkg("mzapi.utlis", os.path.join(_ROOT, "utlis"))
_make_pkg("mzapi.utlis.huaweicloudauth", _HW_ROOT)
_make_pkg("mzapi.utlis.huaweicloudauth.utils", os.path.join(_HW_ROOT, "utils"))

_six_mod = _load(
    "mzapi.utlis.huaweicloudauth.utils.six_utils",
    os.path.join(_HW_ROOT, "utils", "six_utils.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.utils",
)

SingletonMeta = _six_mod.SingletonMeta
ensure_binary = _six_mod.ensure_binary
ensure_str = _six_mod.ensure_str
Once = _six_mod.Once


class TestEnsureBinary(unittest.TestCase):
    """测试 ensure_binary"""

    def test_str_to_bytes(self):
        result = ensure_binary("hello")
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"hello")

    def test_bytes_passthrough(self):
        result = ensure_binary(b"hello")
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"hello")

    def test_custom_encoding(self):
        result = ensure_binary("你好", encoding="utf-8")
        self.assertEqual(result, "你好".encode("utf-8"))

    def test_non_string_raises(self):
        with self.assertRaises(TypeError):
            ensure_binary(123)


class TestEnsureStr(unittest.TestCase):
    """测试 ensure_str"""

    def test_str_passthrough(self):
        result = ensure_str("hello")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "hello")

    def test_bytes_to_str(self):
        result = ensure_str(b"hello")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "hello")

    def test_custom_encoding(self):
        result = ensure_str("你好".encode("utf-8"), encoding="utf-8")
        self.assertEqual(result, "你好")

    def test_non_bytes_raises(self):
        with self.assertRaises(TypeError):
            ensure_str(123)


class TestOnce(unittest.TestCase):
    """测试 Once"""

    def test_executes_once(self):
        once = Once()
        counter = [0]

        def increment():
            counter[0] += 1

        once.do(increment)
        once.do(increment)
        once.do(increment)
        self.assertEqual(counter[0], 1)

    def test_with_args_kwargs(self):
        once = Once()
        results = []

        def append(*args, **kwargs):
            results.append((args, kwargs))

        once.do(append, 1, 2, key="value")
        self.assertEqual(results, [((1, 2), {"key": "value"})])

    def test_second_call_with_different_args_ignored(self):
        once = Once()
        results = []

        def append(val):
            results.append(val)

        once.do(append, "first")
        once.do(append, "second")
        self.assertEqual(results, ["first"])


class TestSingletonMeta(unittest.TestCase):
    """测试 SingletonMeta 单例模式"""

    def test_singleton(self):
        # SingletonMeta 使用类本身作为 key，需要在测试中创建唯一的子类
        class MyClass(metaclass=SingletonMeta):
            def __init__(self, val=0):
                self.val = val

        a = MyClass(1)
        b = MyClass(2)
        self.assertIs(a, b)
        # 第二次调用不会重新 __init__
        self.assertEqual(a.val, 1)

    def test_different_classes_are_different_singletons(self):
        class ClassA(metaclass=SingletonMeta):
            pass

        class ClassB(metaclass=SingletonMeta):
            pass

        a = ClassA()
        b = ClassB()
        self.assertIsNot(a, b)


if __name__ == "__main__":
    unittest.main()

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
_MZAPI_ORIGIN = "mzapi-test-hwc-string-utils-2026-qxx"

"""
huaweicloudauth.utils.string_utils 模块单元测试

覆盖场景：
- camel_to_underline：驼峰转下划线
- underline_to_camel：下划线转驼峰
- replace_invalid_character：非法字符替换
- mask：字符串脱敏
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

_str_mod = _load(
    "mzapi.utlis.huaweicloudauth.utils.string_utils",
    os.path.join(_HW_ROOT, "utils", "string_utils.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.utils",
)

camel_to_underline = _str_mod.camel_to_underline
underline_to_camel = _str_mod.underline_to_camel
replace_invalid_character = _str_mod.replace_invalid_character
mask = _str_mod.mask


class TestCamelToUnderline(unittest.TestCase):
    """测试 camel_to_underline"""

    def test_simple_camel(self):
        self.assertEqual(camel_to_underline("CamelCase"), "camel_case")

    def test_already_lowercase(self):
        self.assertEqual(camel_to_underline("lowercase"), "lowercase")

    def test_empty_string(self):
        self.assertEqual(camel_to_underline(""), "")

    def test_non_string_returns_empty(self):
        self.assertEqual(camel_to_underline(123), "")

    def test_consecutive_uppercase(self):
        self.assertEqual(camel_to_underline("XMLParser"), "x_m_l_parser")

    def test_mixed_with_digits(self):
        self.assertEqual(camel_to_underline("get2ndValue"), "get2nd_value")


class TestUnderlineToCamel(unittest.TestCase):
    """测试 underline_to_camel"""

    def test_simple_underline(self):
        self.assertEqual(underline_to_camel("hello_world"), "HelloWorld")

    def test_single_word(self):
        self.assertEqual(underline_to_camel("hello"), "Hello")

    def test_empty_string(self):
        self.assertEqual(underline_to_camel(""), "")

    def test_non_string_returns_empty(self):
        self.assertEqual(underline_to_camel(123), "")


class TestReplaceInvalidCharacter(unittest.TestCase):
    """测试 replace_invalid_character"""

    def test_ascii_printable(self):
        self.assertEqual(replace_invalid_character("hello"), "hello")

    def test_spaces_replaced(self):
        self.assertEqual(replace_invalid_character("hello world"), "hello_world")

    def test_control_chars_replaced(self):
        # Each char is checked individually: ord(c) > 32 and <= 126
        # \x00 (0) -> '_', \x1f (31) -> '_'
        self.assertEqual(replace_invalid_character("a\x00b\x1fc"), "a_b_c")

    def test_non_ascii_replaced(self):
        # '你' and '好' are each 1 char with ord > 126 -> '_'
        self.assertEqual(replace_invalid_character("你好"), "__")


class TestMask(unittest.TestCase):
    """测试 mask"""

    def test_default_ratio(self):
        result = mask("1234567890")
        self.assertEqual(len(result), 10)
        # 默认 ratio=0.7, 中间 7 个字符被替换
        self.assertTrue(result.startswith("1"))
        self.assertTrue(result.endswith("0"))

    def test_full_mask(self):
        result = mask("secret", ratio=1.0)
        self.assertEqual(result, "******")

    def test_no_mask(self):
        result = mask("secret", ratio=0.0)
        self.assertEqual(result, "secret")

    def test_empty_text(self):
        self.assertEqual(mask(""), "")

    def test_none_text(self):
        self.assertIsNone(mask(None))

    def test_custom_char(self):
        result = mask("abcdef", ratio=1.0, char="#")
        self.assertEqual(result, "######")

    def test_short_text(self):
        result = mask("ab", ratio=0.5)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()

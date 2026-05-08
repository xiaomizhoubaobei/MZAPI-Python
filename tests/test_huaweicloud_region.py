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
_MZAPI_ORIGIN = "mzapi-test-hwc-region-2026-qxx"

"""
huaweicloudauth.region.region 模块单元测试

覆盖场景：
- 两种初始化方式（kwargs / args）
- id 和 endpoints 属性
- with_endpoint_override / with_endpoints_override
- endpoint 属性的 DeprecationWarning
- 缺少必要参数时的 ValueError
"""

import importlib.util
import os
import sys
import types
import unittest
import warnings

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
_make_pkg("mzapi.utlis.huaweicloudauth.region", os.path.join(_HW_ROOT, "region"))

_region_mod = _load(
    "mzapi.utlis.huaweicloudauth.region.region",
    os.path.join(_HW_ROOT, "region", "region.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.region",
)

Region = _region_mod.Region


class TestRegionInit(unittest.TestCase):
    """测试 Region 初始化"""

    def test_kwargs_init(self):
        r = Region(id="cn-north-1", endpoint="https://cn-north-1.myhuaweicloud.com")
        self.assertEqual(r.id, "cn-north-1")
        self.assertEqual(r.endpoints, ["https://cn-north-1.myhuaweicloud.com"])

    def test_args_init(self):
        r = Region("cn-north-1", "ep1", "ep2")
        self.assertEqual(r.id, "cn-north-1")
        self.assertEqual(r.endpoints, ["ep1", "ep2"])

    def test_kwargs_priority_over_args(self):
        """kwargs 优先于 args"""
        r = Region("id-from-args", "ep-from-args",
                    id="id-from-kwargs", endpoint="ep-from-kwargs")
        self.assertEqual(r.id, "id-from-kwargs")
        self.assertEqual(r.endpoints, ["ep-from-kwargs"])

    def test_missing_id_raises(self):
        with self.assertRaises(ValueError) as ctx:
            Region(endpoint="https://ep.com")
        self.assertIn("id is required", str(ctx.exception))

    def test_missing_endpoints_raises(self):
        with self.assertRaises(ValueError) as ctx:
            Region(id="cn-north-1")
        self.assertIn("at lease one endpoint is required", str(ctx.exception))


class TestRegionProperties(unittest.TestCase):
    """测试 Region 属性和方法"""

    def setUp(self):
        self.r = Region(id="cn-north-1", endpoint="https://cn-north-1.myhuaweicloud.com")

    def test_id_setter(self):
        self.r.id = "cn-north-2"
        self.assertEqual(self.r.id, "cn-north-2")

    def test_endpoints_setter(self):
        self.r.endpoints = ["ep1", "ep2", "ep3"]
        self.assertEqual(self.r.endpoints, ["ep1", "ep2", "ep3"])

    def test_endpoint_deprecation_warning_getter(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            val = self.r.endpoint
            self.assertEqual(val, "https://cn-north-1.myhuaweicloud.com")
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("endpoints", str(w[0].message))

    def test_endpoint_deprecation_warning_setter(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.r.endpoint = "https://new-endpoint.com"
            self.assertEqual(self.r.endpoints, ["https://new-endpoint.com"])
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))


class TestRegionOverride(unittest.TestCase):
    """测试端点覆盖方法"""

    def test_with_endpoint_override(self):
        r = Region(id="cn-north-1", endpoint="ep1")
        r2 = r.with_endpoint_override("ep2", "ep3")
        self.assertIs(r2, r)
        self.assertEqual(r.endpoints, ["ep2", "ep3"])

    def test_with_endpoints_override(self):
        r = Region(id="cn-north-1", endpoint="ep1")
        r.with_endpoints_override(["a", "b", "c"])
        self.assertEqual(r.endpoints, ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()

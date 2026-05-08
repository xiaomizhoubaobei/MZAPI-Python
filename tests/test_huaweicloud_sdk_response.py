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
_MZAPI_ORIGIN = "mzapi-test-hwc-sdk-response-2026-qxx"

"""
huaweicloudauth.sdk_response 模块单元测试

覆盖场景：
- SdkResponse 默认值
- SdkResponse status_code/raw_content setter（仅首次写入生效）
- SdkResponse to_json_object
- FutureSdkResponse 基础结构
"""

import importlib.util
import json
import os
import sys
import types
import unittest
from unittest.mock import MagicMock

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
_make_pkg("mzapi.utlis.huaweicloudauth.exceptions", os.path.join(_HW_ROOT, "exceptions"))

_load(
    "mzapi.utlis.huaweicloudauth.utils.six_utils",
    os.path.join(_HW_ROOT, "utils", "six_utils.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.utils",
)
_load(
    "mzapi.utlis.huaweicloudauth.exceptions.exceptions",
    os.path.join(_HW_ROOT, "exceptions", "exceptions.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.exceptions",
)

# 需要 mock process_connection_error，因为它依赖 requests 等外部库
import types as _types
_exc_handler_mod = types.ModuleType("mzapi.utlis.huaweicloudauth.exceptions.exception_handler")
_exc_handler_mod.process_connection_error = lambda conn_err, logger: None
sys.modules["mzapi.utlis.huaweicloudauth.exceptions.exception_handler"] = _exc_handler_mod

_resp_mod = _load(
    "mzapi.utlis.huaweicloudauth.sdk_response",
    os.path.join(_HW_ROOT, "sdk_response.py"),
    pkg_name="mzapi.utlis.huaweicloudauth",
)

SdkResponse = _resp_mod.SdkResponse
FutureSdkResponse = _resp_mod.FutureSdkResponse


class TestSdkResponse(unittest.TestCase):
    """测试 SdkResponse"""

    def test_default_values(self):
        resp = SdkResponse()
        self.assertIsNone(resp.status_code)
        self.assertIsNone(resp.raw_content)

    def test_status_code_setter_first_write(self):
        resp = SdkResponse()
        resp.status_code = 200
        self.assertEqual(resp.status_code, 200)

    def test_status_code_setter_second_write_ignored(self):
        resp = SdkResponse()
        resp.status_code = 200
        resp.status_code = 404
        self.assertEqual(resp.status_code, 200)

    def test_raw_content_setter_first_write(self):
        resp = SdkResponse()
        resp.raw_content = b"hello"
        self.assertEqual(resp.raw_content, b"hello")

    def test_raw_content_setter_second_write_ignored(self):
        resp = SdkResponse()
        resp.raw_content = b"first"
        resp.raw_content = b"second"
        self.assertEqual(resp.raw_content, b"first")

    def test_to_json_object(self):
        resp = SdkResponse()
        data = {"key": "value", "count": 42}
        resp.raw_content = json.dumps(data).encode("utf-8")
        result = resp.to_json_object()
        self.assertEqual(result, data)

    def test_to_json_object_none_content(self):
        resp = SdkResponse()
        result = resp.to_json_object()
        self.assertIsNone(result)

    def test_to_json_object_with_kwargs(self):
        resp = SdkResponse()
        resp.raw_content = b'{"a": 1}'
        result = resp.to_json_object(parse_float=lambda x: round(float(x), 1))
        self.assertEqual(result, {"a": 1})


class TestFutureSdkResponse(unittest.TestCase):
    """测试 FutureSdkResponse"""

    def test_result_with_data_attribute(self):
        # FutureSdkResponse.result() calls self._future.result().result()
        # then checks hasattr(future_response, "data") and data is not None
        inner_response = MagicMock()
        inner_response.data = {"result": "ok"}
        middle_future = MagicMock()
        middle_future.result.return_value = inner_response

        outer_future = MagicMock()
        outer_future.result.return_value = middle_future

        logger = MagicMock()
        fsr = FutureSdkResponse(outer_future, logger)
        result = fsr.result()
        self.assertEqual(result, {"result": "ok"})

    def test_result_without_data_attribute(self):
        inner_response = MagicMock(spec=[])  # no 'data' attribute
        middle_future = MagicMock()
        middle_future.result.return_value = inner_response

        outer_future = MagicMock()
        outer_future.result.return_value = middle_future

        logger = MagicMock()
        fsr = FutureSdkResponse(outer_future, logger)
        result = fsr.result()
        self.assertEqual(result, inner_response)

    def test_result_with_data_none(self):
        inner_response = MagicMock()
        inner_response.data = None
        middle_future = MagicMock()
        middle_future.result.return_value = inner_response

        outer_future = MagicMock()
        outer_future.result.return_value = middle_future

        logger = MagicMock()
        fsr = FutureSdkResponse(outer_future, logger)
        result = fsr.result()
        self.assertEqual(result, inner_response)


if __name__ == "__main__":
    unittest.main()

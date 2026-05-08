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
_MZAPI_ORIGIN = "mzapi-test-hwc-sdk-stream-2026-qxx"

"""
huaweicloudauth.sdk_stream_request / sdk_stream_response 模块单元测试

覆盖场景：
- SdkStreamRequest 初始化与 get_file_stream
- SdkStreamResponse 初始化与 consume_download_stream
- SdkStreamResponse IOError 传播
"""

import importlib.util
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

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

# Mock process_connection_error
_exc_handler_mod = types.ModuleType("mzapi.utlis.huaweicloudauth.exceptions.exception_handler")
_exc_handler_mod.process_connection_error = lambda conn_err, logger: None
sys.modules["mzapi.utlis.huaweicloudauth.exceptions.exception_handler"] = _exc_handler_mod

_load(
    "mzapi.utlis.huaweicloudauth.sdk_response",
    os.path.join(_HW_ROOT, "sdk_response.py"),
    pkg_name="mzapi.utlis.huaweicloudauth",
)

_stream_req_mod = _load(
    "mzapi.utlis.huaweicloudauth.sdk_stream_request",
    os.path.join(_HW_ROOT, "sdk_stream_request.py"),
    pkg_name="mzapi.utlis.huaweicloudauth",
)

_stream_resp_mod = _load(
    "mzapi.utlis.huaweicloudauth.sdk_stream_response",
    os.path.join(_HW_ROOT, "sdk_stream_response.py"),
    pkg_name="mzapi.utlis.huaweicloudauth",
)

SdkStreamRequest = _stream_req_mod.SdkStreamRequest
SdkStreamResponse = _stream_resp_mod.SdkStreamResponse


class TestSdkStreamRequest(unittest.TestCase):
    """测试 SdkStreamRequest"""

    def test_init(self):
        stream = MagicMock()
        req = SdkStreamRequest(stream)
        self.assertEqual(req._stream, stream)

    def test_get_file_stream(self):
        stream = MagicMock()
        req = SdkStreamRequest(stream)
        self.assertIs(req.get_file_stream(), stream)


class TestSdkStreamResponse(unittest.TestCase):
    """测试 SdkStreamResponse"""

    def test_init(self):
        stream = MagicMock()
        resp = SdkStreamResponse(stream)
        self.assertEqual(resp._stream, stream)

    def test_inherits_sdk_response(self):
        from mzapi.utlis.huaweicloudauth.sdk_response import SdkResponse
        resp = SdkStreamResponse(MagicMock())
        self.assertIsInstance(resp, SdkResponse)

    def test_consume_download_stream(self):
        stream = MagicMock()
        resp = SdkStreamResponse(stream)
        fn = MagicMock()
        resp.consume_download_stream(fn)
        fn.assert_called_once_with(stream)

    def test_consume_download_stream_io_error(self):
        stream = MagicMock()
        resp = SdkStreamResponse(stream)

        def failing_fn(s):
            raise IOError("read error")

        with self.assertRaises(IOError):
            resp.consume_download_stream(failing_fn)


if __name__ == "__main__":
    unittest.main()

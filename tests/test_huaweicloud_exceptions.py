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
_MZAPI_ORIGIN = "mzapi-test-hwc-exceptions-2026-qxx"

"""
huaweicloudauth.exceptions 模块单元测试

覆盖场景：
- SdkException 基础异常：初始化、error_msg 属性、__str__ 格式
- ConnectionException / HostUnreachableException / SslHandShakeException 层次
- ServiceResponseException：status_code、error_code、request_id 等属性
- ClientRequestException / ServerResponseException 区分
- RequestTimeoutException / CallTimeoutException / RetryOutageException 层次
- SdkError 数据对象
- ApiTypeError / ApiValueError / ApiKeyError
- render_path 工具函数
"""

import importlib.util
import os
import sys
import types
import unittest

# =====================================================================
# 模块加载：避免触发 mzapi/__init__.py 中缺失的模块
# =====================================================================

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


# 注册包层次
_make_pkg("mzapi", _ROOT)
_make_pkg("mzapi.utlis", os.path.join(_ROOT, "utlis"))
_make_pkg("mzapi.utlis.huaweicloudauth", _HW_ROOT)
_make_pkg("mzapi.utlis.huaweicloudauth.exceptions", os.path.join(_HW_ROOT, "exceptions"))

# 先加载 six_utils（被 exception_handler 依赖）
_make_pkg("mzapi.utlis.huaweicloudauth.utils", os.path.join(_HW_ROOT, "utils"))
_load(
    "mzapi.utlis.huaweicloudauth.utils.six_utils",
    os.path.join(_HW_ROOT, "utils", "six_utils.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.utils",
)

_exc_mod = _load(
    "mzapi.utlis.huaweicloudauth.exceptions.exceptions",
    os.path.join(_HW_ROOT, "exceptions", "exceptions.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.exceptions",
)

SdkException = _exc_mod.SdkException
ConnectionException = _exc_mod.ConnectionException
HostUnreachableException = _exc_mod.HostUnreachableException
SslHandShakeException = _exc_mod.SslHandShakeException
ServiceResponseException = _exc_mod.ServiceResponseException
ClientRequestException = _exc_mod.ClientRequestException
ServerResponseException = _exc_mod.ServerResponseException
RequestTimeoutException = _exc_mod.RequestTimeoutException
CallTimeoutException = _exc_mod.CallTimeoutException
RetryOutageException = _exc_mod.RetryOutageException
SdkError = _exc_mod.SdkError
ApiTypeError = _exc_mod.ApiTypeError
ApiValueError = _exc_mod.ApiValueError
ApiKeyError = _exc_mod.ApiKeyError
render_path = _exc_mod.render_path


# =========================================================================
#  SdkException 测试
# =========================================================================
class TestSdkException(unittest.TestCase):
    """测试 SdkException 基础异常类"""

    def test_basic_init(self):
        exc = SdkException("something went wrong")
        self.assertEqual(exc.error_msg, "something went wrong")

    def test_str_representation(self):
        exc = SdkException("test error")
        s = str(exc)
        self.assertIn("SdkException", s)
        self.assertIn("test error", s)

    def test_error_msg_setter(self):
        exc = SdkException("old msg")
        exc.error_msg = "new msg"
        self.assertEqual(exc.error_msg, "new msg")

    def test_inherits_exception(self):
        self.assertIsInstance(SdkException("x"), Exception)


# =========================================================================
#  连接异常层次测试
# =========================================================================
class TestConnectionExceptions(unittest.TestCase):
    """测试 ConnectionException 及其子类"""

    def test_connection_exception(self):
        exc = ConnectionException("conn err")
        self.assertIsInstance(exc, SdkException)
        self.assertEqual(exc.error_msg, "conn err")

    def test_host_unreachable(self):
        exc = HostUnreachableException("host unreachable")
        self.assertIsInstance(exc, ConnectionException)
        self.assertIsInstance(exc, SdkException)

    def test_ssl_handshake(self):
        exc = SslHandShakeException("ssl handshake failed")
        self.assertIsInstance(exc, ConnectionException)
        self.assertIsInstance(exc, SdkException)


# =========================================================================
#  ServiceResponseException 测试
# =========================================================================
class TestServiceResponseException(unittest.TestCase):
    """测试 ServiceResponseException 及其子类"""

    def _make_error(self, error_code="ERR001", error_msg="bad request",
                    request_id="req-123", encoded_auth_msg="auth_msg"):
        return SdkError(
            request_id=request_id,
            error_code=error_code,
            error_msg=error_msg,
            encoded_auth_msg=encoded_auth_msg,
        )

    def test_basic_init(self):
        err = self._make_error()
        exc = ServiceResponseException(400, err)
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.error_code, "ERR001")
        self.assertEqual(exc.request_id, "req-123")
        self.assertEqual(exc.encoded_auth_msg, "auth_msg")
        self.assertEqual(exc.error_msg, "bad request")

    def test_str_representation(self):
        err = self._make_error()
        exc = ServiceResponseException(500, err)
        s = str(exc)
        self.assertIn("ServiceResponseException", s)
        self.assertIn("500", s)
        self.assertIn("req-123", s)
        self.assertIn("ERR001", s)

    def test_status_code_setter(self):
        err = self._make_error()
        exc = ServiceResponseException(400, err)
        exc.status_code = 503
        self.assertEqual(exc.status_code, 503)

    def test_client_request_exception(self):
        err = self._make_error()
        exc = ClientRequestException(400, err)
        self.assertIsInstance(exc, ServiceResponseException)
        self.assertEqual(exc.status_code, 400)

    def test_server_response_exception(self):
        err = self._make_error()
        exc = ServerResponseException(500, err)
        self.assertIsInstance(exc, ServiceResponseException)
        self.assertEqual(exc.status_code, 500)


# =========================================================================
#  超时异常层次测试
# =========================================================================
class TestTimeoutExceptions(unittest.TestCase):
    """测试 RequestTimeoutException 及其子类"""

    def test_request_timeout(self):
        exc = RequestTimeoutException("timeout")
        self.assertIsInstance(exc, SdkException)

    def test_call_timeout(self):
        exc = CallTimeoutException("call timeout")
        self.assertIsInstance(exc, RequestTimeoutException)
        self.assertIsInstance(exc, SdkException)

    def test_retry_outage(self):
        exc = RetryOutageException("retry exhausted")
        self.assertIsInstance(exc, RequestTimeoutException)
        self.assertIsInstance(exc, SdkException)


# =========================================================================
#  SdkError 数据对象测试
# =========================================================================
class TestSdkError(unittest.TestCase):
    """测试 SdkError 数据对象"""

    def test_defaults(self):
        err = SdkError()
        self.assertIsNone(err.request_id)
        self.assertIsNone(err.error_code)
        self.assertIsNone(err.error_msg)
        self.assertIsNone(err.encoded_auth_msg)

    def test_with_values(self):
        err = SdkError(
            request_id="r1", error_code="C1", error_msg="m1", encoded_auth_msg="a1"
        )
        self.assertEqual(err.request_id, "r1")
        self.assertEqual(err.error_code, "C1")
        self.assertEqual(err.error_msg, "m1")
        self.assertEqual(err.encoded_auth_msg, "a1")

    def test_setters(self):
        err = SdkError()
        err.request_id = "new_rid"
        err.error_code = "new_code"
        err.error_msg = "new_msg"
        err.encoded_auth_msg = "new_auth"
        self.assertEqual(err.request_id, "new_rid")
        self.assertEqual(err.error_code, "new_code")
        self.assertEqual(err.error_msg, "new_msg")
        self.assertEqual(err.encoded_auth_msg, "new_auth")


# =========================================================================
#  render_path 工具函数测试
# =========================================================================
class TestRenderPath(unittest.TestCase):
    """测试 render_path"""

    def test_empty_path(self):
        self.assertEqual(render_path([]), "")

    def test_string_keys(self):
        self.assertEqual(render_path(["a", "b", "c"]), "['a']['b']['c']")

    def test_int_indices(self):
        self.assertEqual(render_path(["items", 0, "name"]), "['items'][0]['name']")

    def test_mixed(self):
        self.assertEqual(render_path(["a", 1, "b"]), "['a'][1]['b']")


# =========================================================================
#  ApiTypeError / ApiValueError / ApiKeyError 测试
# =========================================================================
class TestApiTypeValueKeyError(unittest.TestCase):
    """测试 API 异常类"""

    def test_api_type_error(self):
        exc = ApiTypeError("type mismatch")
        self.assertIsInstance(exc, TypeError)
        self.assertIn("type mismatch", str(exc))

    def test_api_type_error_with_path(self):
        exc = ApiTypeError("wrong type", path_to_item=["a", 0])
        self.assertIn("['a'][0]", str(exc))
        self.assertEqual(exc.path_to_item, ["a", 0])

    def test_api_value_error(self):
        exc = ApiValueError("bad value")
        self.assertIsInstance(exc, ValueError)
        self.assertIn("bad value", str(exc))

    def test_api_value_error_with_path(self):
        exc = ApiValueError("bad value", path_to_item=["x", "y"])
        self.assertIn("['x']['y']", str(exc))

    def test_api_key_error(self):
        exc = ApiKeyError("missing key")
        self.assertIsInstance(exc, KeyError)
        self.assertIn("missing key", str(exc))

    def test_api_key_error_with_path(self):
        exc = ApiKeyError("missing", path_to_item=[0, "z"])
        self.assertIn("[0]['z']", str(exc))


if __name__ == "__main__":
    unittest.main()

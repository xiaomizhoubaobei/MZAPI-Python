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
_MZAPI_ORIGIN = "mzapi-test-txc-common-2026-qxx"

"""
tencentauth 模块单元测试

覆盖场景：
- Credential 凭证类（初始化校验、属性、get_credential_info）
- Sign 签名类（HmacSHA1/SHA256、TC3-HMAC-SHA256）
- TencentCloudSDKException 异常类
- ClientProfile 配置（签名方法、语言校验）
- HttpProfile 配置（默认值、自定义值）
- EnvironmentVariableCredential 环境变量凭证
"""

import binascii
import hashlib
import hmac
import importlib.util
import os
import sys
import types
import unittest
import warnings

# =====================================================================
# 模块加载：避免触发 mzapi/__init__.py 中缺失的 tencent 模块
# =====================================================================

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, "mzapi"))
_TC_ROOT = os.path.join(_ROOT, "utlis", "tencentauth")


def _make_pkg(name, path):
    """在 sys.modules 中注册一个包模块"""
    m = types.ModuleType(name)
    m.__path__ = [path]
    m.__package__ = name
    m.__loader__ = None
    sys.modules[name] = m
    return m


def _load(name, filepath, pkg_name=None):
    """加载单个 .py 文件为模块，设置 __package__ 以支持相对导入"""
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
_make_pkg("mzapi.utlis.tencentauth", _TC_ROOT)
_make_pkg("mzapi.utlis.tencentauth.exception", os.path.join(_TC_ROOT, "exception"))
_make_pkg("mzapi.utlis.tencentauth.profile", os.path.join(_TC_ROOT, "profile"))

# 加载各模块
_exc_mod = _load(
    "mzapi.utlis.tencentauth.exception.tencent_cloud_sdk_exception",
    os.path.join(_TC_ROOT, "exception", "tencent_cloud_sdk_exception.py"),
    pkg_name="mzapi.utlis.tencentauth.exception",
)
_sign_mod = _load(
    "mzapi.utlis.tencentauth.sign",
    os.path.join(_TC_ROOT, "sign.py"),
    pkg_name="mzapi.utlis.tencentauth",
)
_cred_mod = _load(
    "mzapi.utlis.tencentauth.credential",
    os.path.join(_TC_ROOT, "credential.py"),
    pkg_name="mzapi.utlis.tencentauth",
)
_http_mod = _load(
    "mzapi.utlis.tencentauth.profile.http_profile",
    os.path.join(_TC_ROOT, "profile", "http_profile.py"),
    pkg_name="mzapi.utlis.tencentauth.profile",
)
_cp_mod = _load(
    "mzapi.utlis.tencentauth.profile.client_profile",
    os.path.join(_TC_ROOT, "profile", "client_profile.py"),
    pkg_name="mzapi.utlis.tencentauth.profile",
)

TencentCloudSDKException = _exc_mod.TencentCloudSDKException
Sign = _sign_mod.Sign
Credential = _cred_mod.Credential
EnvironmentVariableCredential = _cred_mod.EnvironmentVariableCredential
HttpProfile = _http_mod.HttpProfile
ClientProfile = _cp_mod.ClientProfile

NL = chr(10)  # newline，用于构建多行字符串


# =========================================================================
#  Credential 测试
# =========================================================================
class TestCredential(unittest.TestCase):
    """测试 Credential 凭证类"""

    def test_valid_init(self):
        cred = Credential("test_id", "test_key")
        self.assertEqual(cred.secret_id, "test_id")
        self.assertEqual(cred.secret_key, "test_key")
        self.assertIsNone(cred.token)

    def test_valid_init_with_token(self):
        cred = Credential("test_id", "test_key", "test_token")
        self.assertEqual(cred.token, "test_token")

    def test_secret_id_property(self):
        cred = Credential("id123", "key456")
        self.assertEqual(cred.secretId, "id123")

    def test_secret_key_property(self):
        cred = Credential("id123", "key456")
        self.assertEqual(cred.secretKey, "key456")

    def test_get_credential_info(self):
        cred = Credential("id", "key", "tok")
        sid, sk, token = cred.get_credential_info()
        self.assertEqual(sid, "id")
        self.assertEqual(sk, "key")
        self.assertEqual(token, "tok")

    def test_none_secret_id_raises(self):
        with self.assertRaises(TencentCloudSDKException) as ctx:
            Credential(None, "key")
        self.assertIn("secret id", str(ctx.exception))

    def test_empty_secret_id_raises(self):
        with self.assertRaises(TencentCloudSDKException):
            Credential("", "key")

    def test_secret_id_with_spaces_raises(self):
        with self.assertRaises(TencentCloudSDKException):
            Credential(" id ", "key")

    def test_none_secret_key_raises(self):
        with self.assertRaises(TencentCloudSDKException) as ctx:
            Credential("id", None)
        self.assertIn("secret key", str(ctx.exception))

    def test_empty_secret_key_raises(self):
        with self.assertRaises(TencentCloudSDKException):
            Credential("id", "")

    def test_secret_key_with_spaces_raises(self):
        with self.assertRaises(TencentCloudSDKException):
            Credential("id", " key ")


# =========================================================================
#  Sign 测试
# =========================================================================
class TestSignHmac(unittest.TestCase):
    """测试 Sign 旧版签名方法"""

    def test_hmac_sha256(self):
        result = Sign.sign("secret", "message", "HmacSHA256")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_hmac_sha1(self):
        result = Sign.sign("secret", "message", "HmacSHA1")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_hmac_sha256_deterministic(self):
        r1 = Sign.sign("key", "data", "HmacSHA256")
        r2 = Sign.sign("key", "data", "HmacSHA256")
        self.assertEqual(r1, r2)

    def test_invalid_sign_method_raises(self):
        with self.assertRaises(TencentCloudSDKException) as ctx:
            Sign.sign("key", "data", "HmacMD5")
        self.assertIn("signMethod invalid", str(ctx.exception))

    def test_hmac_sha256_is_base64(self):
        """HmacSHA256 结果应为合法的 base64 字符串"""
        result = Sign.sign("secret", "test", "HmacSHA256")
        decoded = binascii.a2b_base64(result)
        self.assertTrue(len(decoded) > 0)


class TestSignTC3(unittest.TestCase):
    """测试 Sign TC3-HMAC-SHA256 签名方法"""

    def test_sign_tc3_returns_hex(self):
        result = Sign.sign_tc3(
            "secret_key", "2026-01-01", "service", "string_to_sign"
        )
        self.assertIsInstance(result, str)
        self.assertTrue(all(c in "0123456789abcdef" for c in result))

    def test_sign_tc3_deterministic(self):
        args = ("key", "2026-05-06", "ocr", "test_data")
        self.assertEqual(Sign.sign_tc3(*args), Sign.sign_tc3(*args))

    def test_sign_tc3_different_keys_differ(self):
        r1 = Sign.sign_tc3("key1", "2026-01-01", "svc", "data")
        r2 = Sign.sign_tc3("key2", "2026-01-01", "svc", "data")
        self.assertNotEqual(r1, r2)

    def test_sign_tc3_different_dates_differ(self):
        r1 = Sign.sign_tc3("key", "2026-01-01", "svc", "data")
        r2 = Sign.sign_tc3("key", "2026-01-02", "svc", "data")
        self.assertNotEqual(r1, r2)

    def test_sign_tc3_matches_manual(self):
        """验证与手动 HMAC-SHA256 计算结果一致"""
        sk = "my_secret"
        date = "2026-05-06"
        svc = "ocr"
        s2s = "TC3-HMAC-SHA256" + NL + "1234567890" + NL + "2026-05-06/ocr/tc3_request" + NL + "abc123"

        k_date = hmac.new(("TC3" + sk).encode("utf-8"), date.encode("utf-8"), hashlib.sha256).digest()
        k_svc = hmac.new(k_date, svc.encode("utf-8"), hashlib.sha256).digest()
        k_sign = hmac.new(k_svc, b"tc3_request", hashlib.sha256).digest()
        expected = hmac.new(k_sign, s2s.encode("utf-8"), hashlib.sha256).hexdigest()

        self.assertEqual(Sign.sign_tc3(sk, date, svc, s2s), expected)


# =========================================================================
#  TencentCloudSDKException 测试
# =========================================================================
class TestTencentCloudSDKException(unittest.TestCase):
    """测试 TencentCloudSDKException 异常类"""

    def test_basic_exception(self):
        exc = TencentCloudSDKException("InvalidCredential", "test msg", "req-123")
        self.assertEqual(exc.code, "InvalidCredential")
        self.assertEqual(exc.message, "test msg")
        self.assertEqual(exc.requestId, "req-123")

    def test_str_representation(self):
        exc = TencentCloudSDKException("Err", "msg", "id")
        s = str(exc)
        self.assertIn("Err", s)
        self.assertIn("msg", s)
        self.assertIn("id", s)

    def test_getters(self):
        exc = TencentCloudSDKException("C", "M", "R")
        self.assertEqual(exc.get_code(), "C")
        self.assertEqual(exc.get_message(), "M")
        self.assertEqual(exc.get_request_id(), "R")

    def test_inherits_exception(self):
        self.assertIsInstance(TencentCloudSDKException(), Exception)


# =========================================================================
#  HttpProfile 测试
# =========================================================================
class TestHttpProfile(unittest.TestCase):
    """测试 HttpProfile 配置"""

    def test_defaults(self):
        hp = HttpProfile()
        self.assertEqual(hp.reqMethod, "POST")
        self.assertEqual(hp.reqTimeout, 60)
        self.assertFalse(hp.keepAlive)
        self.assertIsNone(hp.proxy)
        self.assertEqual(hp.rootDomain, "tencentcloudapi.com")
        self.assertEqual(hp.protocol, "https")
        self.assertEqual(hp.scheme, "https")
        self.assertIsNone(hp.endpoint)
        self.assertIsNone(hp.certification)

    def test_custom(self):
        hp = HttpProfile(
            protocol="http", endpoint="test.api.com", reqMethod="GET",
            reqTimeout=120, keepAlive=True, proxy="http://p:8080",
            rootDomain="api.com",
        )
        self.assertEqual(hp.protocol, "http")
        self.assertEqual(hp.endpoint, "test.api.com")
        self.assertEqual(hp.reqMethod, "GET")
        self.assertEqual(hp.reqTimeout, 120)
        self.assertTrue(hp.keepAlive)
        self.assertEqual(hp.proxy, "http://p:8080")
        self.assertEqual(hp.rootDomain, "api.com")

    def test_none_req_method_defaults_post(self):
        self.assertEqual(HttpProfile(reqMethod=None).reqMethod, "POST")

    def test_none_req_timeout_defaults_60(self):
        self.assertEqual(HttpProfile(reqTimeout=None).reqTimeout, 60)


# =========================================================================
#  ClientProfile 测试
# =========================================================================
class TestClientProfile(unittest.TestCase):
    """测试 ClientProfile 配置"""

    def test_defaults(self):
        cp = ClientProfile()
        self.assertEqual(cp.signMethod, "TC3-HMAC-SHA256")
        self.assertEqual(cp.language, "zh-CN")
        self.assertTrue(cp.disable_region_breaker)
        self.assertIsInstance(cp.httpProfile, HttpProfile)
        self.assertIsNone(cp.request_client)

    def test_custom_sign_method(self):
        self.assertEqual(ClientProfile(signMethod="HmacSHA256").signMethod, "HmacSHA256")

    def test_custom_language(self):
        self.assertEqual(ClientProfile(language="en-US").language, "en-US")

    def test_invalid_language_raises(self):
        with self.assertRaises(TencentCloudSDKException):
            ClientProfile(language="ja-JP")

    def test_valid_request_client(self):
        cp = ClientProfile(request_client="test-client-1.0")
        self.assertEqual(cp.request_client, "test-client-1.0")

    def test_long_request_client_truncated(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            cp = ClientProfile(request_client="a" * 200)
            self.assertEqual(len(cp.request_client), 128)

    def test_invalid_request_client_ignored(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.assertIsNone(ClientProfile(request_client="has spaces!").request_client)


# =========================================================================
#  EnvironmentVariableCredential 测试
# =========================================================================
class TestEnvironmentVariableCredential(unittest.TestCase):
    """测试 EnvironmentVariableCredential"""

    def test_get_credential_from_env(self):
        os.environ["TENCENTCLOUD_SECRET_ID"] = "env_id"
        os.environ["TENCENTCLOUD_SECRET_KEY"] = "env_key"
        try:
            cred = EnvironmentVariableCredential().get_credential()
            self.assertIsNotNone(cred)
            self.assertEqual(cred.secret_id, "env_id")
            self.assertEqual(cred.secret_key, "env_key")
        finally:
            del os.environ["TENCENTCLOUD_SECRET_ID"]
            del os.environ["TENCENTCLOUD_SECRET_KEY"]

    def test_missing_env_returns_none(self):
        os.environ.pop("TENCENTCLOUD_SECRET_ID", None)
        os.environ.pop("TENCENTCLOUD_SECRET_KEY", None)
        self.assertIsNone(EnvironmentVariableCredential().get_credential())

    def test_empty_env_returns_none(self):
        os.environ["TENCENTCLOUD_SECRET_ID"] = ""
        os.environ["TENCENTCLOUD_SECRET_KEY"] = ""
        try:
            self.assertIsNone(EnvironmentVariableCredential().get_credential())
        finally:
            del os.environ["TENCENTCLOUD_SECRET_ID"]
            del os.environ["TENCENTCLOUD_SECRET_KEY"]



if __name__ == "__main__":
    unittest.main()

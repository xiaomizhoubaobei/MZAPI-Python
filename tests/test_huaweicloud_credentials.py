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
_MZAPI_ORIGIN = "mzapi-test-hwc-credentials-2026-qxx"

"""
huaweicloudauth.auth.credentials 模块单元测试

覆盖场景：
- BasicCredentials 初始化与属性
- GlobalCredentials 初始化与属性
- with_* 链式调用
- get_update_path_params
- sign_request 流程（mock signer 依赖）
- ak/setter 校验
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

# 注册所有需要的包
_make_pkg("mzapi.utlis.huaweicloudauth.signer", os.path.join(_HW_ROOT, "signer"))
_make_pkg("mzapi.utlis.huaweicloudauth.utils", os.path.join(_HW_ROOT, "utils"))
_make_pkg("mzapi.utlis.huaweicloudauth.exceptions", os.path.join(_HW_ROOT, "exceptions"))
_make_pkg("mzapi.utlis.huaweicloudauth.http", os.path.join(_HW_ROOT, "http"))
_make_pkg("mzapi.utlis.huaweicloudauth.auth", os.path.join(_HW_ROOT, "auth"))

# 加载基础模块
_load(
    "mzapi.utlis.huaweicloudauth.signer.algorithm",
    os.path.join(_HW_ROOT, "signer", "algorithm.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.signer",
)

# Mock signer.signer 和 signer.hkdf 以避免复杂的依赖
_signer_mod = types.ModuleType("mzapi.utlis.huaweicloudauth.signer.signer")


class _MockSigner:
    def __init__(self, credentials):
        self.credentials = credentials

    def sign(self, request):
        return request


_signer_mod.Signer = _MockSigner
_signer_mod.SM3Signer = _MockSigner
_signer_mod.DerivationAKSKSigner = lambda c: _MockSigner(c)
_signer_mod.P256SHA256Signer = _MockSigner
_signer_mod.SM2SM3Signer = _MockSigner
sys.modules["mzapi.utlis.huaweicloudauth.signer.signer"] = _signer_mod

_load(
    "mzapi.utlis.huaweicloudauth.utils.six_utils",
    os.path.join(_HW_ROOT, "utils", "six_utils.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.utils",
)
_load(
    "mzapi.utlis.huaweicloudauth.utils.string_utils",
    os.path.join(_HW_ROOT, "utils", "string_utils.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.utils",
)
_load(
    "mzapi.utlis.huaweicloudauth.utils.time_utils",
    os.path.join(_HW_ROOT, "utils", "time_utils.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.utils",
)
_load(
    "mzapi.utlis.huaweicloudauth.exceptions.exceptions",
    os.path.join(_HW_ROOT, "exceptions", "exceptions.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.exceptions",
)
_load(
    "mzapi.utlis.huaweicloudauth.sdk_request",
    os.path.join(_HW_ROOT, "sdk_request.py"),
    pkg_name="mzapi.utlis.huaweicloudauth",
)

# Mock http 相关模块
_http_client_mod = types.ModuleType("mzapi.utlis.huaweicloudauth.http.http_client")
_http_client_mod.HttpClient = MagicMock
sys.modules["mzapi.utlis.huaweicloudauth.http.http_client"] = _http_client_mod

_http_config_mod = types.ModuleType("mzapi.utlis.huaweicloudauth.http.http_config")
sys.modules["mzapi.utlis.huaweicloudauth.http.http_config"] = _http_config_mod

# Mock auth.internal 和 auth.endpoint
_auth_internal_mod = types.ModuleType("mzapi.utlis.huaweicloudauth.auth.internal")
_auth_internal_mod.IamHelper = MagicMock()
_auth_internal_mod.MetadataAccessor = MagicMock()
_auth_internal_mod.StsHelper = MagicMock()
_auth_internal_mod.StsAccessor = MagicMock()
_auth_internal_mod.FederalAccessor = MagicMock()
sys.modules["mzapi.utlis.huaweicloudauth.auth.internal"] = _auth_internal_mod

_auth_endpoint_mod = types.ModuleType("mzapi.utlis.huaweicloudauth.auth.endpoint")
sys.modules["mzapi.utlis.huaweicloudauth.auth.endpoint"] = _auth_endpoint_mod

# 加载 credentials 模块
_cred_mod = _load(
    "mzapi.utlis.huaweicloudauth.auth.credentials",
    os.path.join(_HW_ROOT, "auth", "credentials.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.auth",
)

BasicCredentials = _cred_mod.BasicCredentials
GlobalCredentials = _cred_mod.GlobalCredentials
Credentials = _cred_mod.Credentials

SigningAlgorithm = sys.modules["mzapi.utlis.huaweicloudauth.signer.algorithm"].SigningAlgorithm
SdkRequest = sys.modules["mzapi.utlis.huaweicloudauth.sdk_request"].SdkRequest


class TestBasicCredentials(unittest.TestCase):
    """测试 BasicCredentials"""

    def test_init(self):
        cred = BasicCredentials(ak="my_ak", sk="my_sk", project_id="proj_1")
        self.assertEqual(cred.ak, "my_ak")
        self.assertEqual(cred.sk, "my_sk")
        self.assertEqual(cred.project_id, "proj_1")

    def test_init_defaults(self):
        cred = BasicCredentials()
        self.assertIsNone(cred.ak)
        self.assertIsNone(cred.sk)
        self.assertIsNone(cred.project_id)

    def test_project_id_setter(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        cred.project_id = "new_proj"
        self.assertEqual(cred.project_id, "new_proj")

    def test_with_project_id(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        result = cred.with_project_id("p1")
        self.assertIs(result, cred)
        self.assertEqual(cred.project_id, "p1")

    def test_get_update_path_params_with_project(self):
        cred = BasicCredentials(ak="ak", sk="sk", project_id="proj1")
        params = cred.get_update_path_params()
        self.assertEqual(params, {"project_id": "proj1"})

    def test_get_update_path_params_without_project(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        params = cred.get_update_path_params()
        self.assertEqual(params, {})

    def test_sign_request_sets_project_header(self):
        cred = BasicCredentials(ak="ak", sk="sk", project_id="proj1")
        req = SdkRequest(
            method="GET", schema="https", host="api.example.com", uri="/test",
            header_params={},
        )
        result = cred.sign_request(req)
        self.assertEqual(result.header_params["X-Project-Id"], "proj1")

    def test_sign_request_no_project_no_header(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        req = SdkRequest(
            method="GET", schema="https", host="api.example.com", uri="/test",
            header_params={},
        )
        result = cred.sign_request(req)
        self.assertNotIn("X-Project-Id", result.header_params)

    def test_with_ak(self):
        cred = BasicCredentials()
        cred.with_ak("new_ak")
        self.assertEqual(cred.ak, "new_ak")

    def test_with_sk(self):
        cred = BasicCredentials()
        cred.with_sk("new_sk")
        self.assertEqual(cred.sk, "new_sk")

    def test_ak_setter_empty_raises(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        with self.assertRaises(ValueError):
            cred.ak = ""

    def test_ak_setter_none_raises(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        with self.assertRaises(ValueError):
            cred.ak = None

    def test_sk_setter_empty_raises(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        with self.assertRaises(ValueError):
            cred.sk = ""

    def test_sk_setter_none_raises(self):
        cred = BasicCredentials(ak="ak", sk="sk")
        with self.assertRaises(ValueError):
            cred.sk = None


class TestGlobalCredentials(unittest.TestCase):
    """测试 GlobalCredentials"""

    def test_init(self):
        cred = GlobalCredentials(ak="ak", sk="sk", domain_id="dom1")
        self.assertEqual(cred.ak, "ak")
        self.assertEqual(cred.sk, "sk")
        self.assertEqual(cred.domain_id, "dom1")

    def test_init_defaults(self):
        cred = GlobalCredentials()
        self.assertIsNone(cred.ak)
        self.assertIsNone(cred.sk)
        self.assertIsNone(cred.domain_id)

    def test_domain_id_setter(self):
        cred = GlobalCredentials(ak="ak", sk="sk")
        cred.domain_id = "new_dom"
        self.assertEqual(cred.domain_id, "new_dom")

    def test_with_domain_id(self):
        cred = GlobalCredentials(ak="ak", sk="sk")
        result = cred.with_domain_id("d1")
        self.assertIs(result, cred)
        self.assertEqual(cred.domain_id, "d1")

    def test_get_update_path_params_with_domain(self):
        cred = GlobalCredentials(ak="ak", sk="sk", domain_id="dom1")
        params = cred.get_update_path_params()
        self.assertEqual(params, {"domain_id": "dom1"})

    def test_get_update_path_params_without_domain(self):
        cred = GlobalCredentials(ak="ak", sk="sk")
        params = cred.get_update_path_params()
        self.assertEqual(params, {})

    def test_sign_request_sets_domain_header(self):
        cred = GlobalCredentials(ak="ak", sk="sk", domain_id="dom1")
        req = SdkRequest(
            method="GET", schema="https", host="api.example.com", uri="/test",
            header_params={},
        )
        result = cred.sign_request(req)
        self.assertEqual(result.header_params["X-Domain-Id"], "dom1")

    def test_sign_request_no_domain_no_header(self):
        cred = GlobalCredentials(ak="ak", sk="sk")
        req = SdkRequest(
            method="GET", schema="https", host="api.example.com", uri="/test",
            header_params={},
        )
        result = cred.sign_request(req)
        self.assertNotIn("X-Domain-Id", result.header_params)

    def test_with_ak(self):
        cred = GlobalCredentials()
        cred.with_ak("ak2")
        self.assertEqual(cred.ak, "ak2")

    def test_with_sk(self):
        cred = GlobalCredentials()
        cred.with_sk("sk2")
        self.assertEqual(cred.sk, "sk2")


class TestCredentialsBase(unittest.TestCase):
    """测试 Credentials 基类"""

    def test_with_security_token(self):
        cred = Credentials(ak="ak", sk="sk")
        result = cred.with_security_token("token1")
        self.assertIs(result, cred)
        self.assertEqual(cred.security_token, "token1")

    def test_sign_request_sets_security_token_header(self):
        cred = Credentials(ak="ak", sk="sk")
        cred.security_token = "token123"
        req = SdkRequest(
            method="GET", schema="https", host="api.example.com", uri="/",
            header_params={},
        )
        result = cred.sign_request(req)
        self.assertEqual(result.header_params["X-Security-Token"], "token123")

    def test_with_derived_predicate(self):
        cred = Credentials(ak="ak", sk="sk")
        pred = lambda req: True
        result = cred.with_derived_predicate(pred)
        self.assertIs(result, cred)

    def test_with_iam_endpoint(self):
        cred = Credentials(ak="ak", sk="sk")
        cred.with_iam_endpoint("https://iam.example.com")
        self.assertEqual(cred.iam_endpoint, "https://iam.example.com")

    def test_with_idp_id(self):
        cred = Credentials(ak="ak", sk="sk")
        cred.with_idp_id("idp-1")
        self.assertEqual(cred.idp_id, "idp-1")

    def test_with_id_token_file(self):
        cred = Credentials(ak="ak", sk="sk")
        cred.with_id_token_file("/path/to/token")
        self.assertEqual(cred.id_token_file, "/path/to/token")


if __name__ == "__main__":
    unittest.main()

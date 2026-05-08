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
_MZAPI_ORIGIN = "mzapi-test-hwc-sdk-request-2026-qxx"

"""
huaweicloudauth.sdk_request 模块单元测试

覆盖场景：
- 默认参数初始化
- 自定义参数初始化
- 所有属性的 getter/setter
- url 属性拼接
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
_make_pkg("mzapi.utlis.huaweicloudauth.signer", os.path.join(_HW_ROOT, "signer"))

_load(
    "mzapi.utlis.huaweicloudauth.signer.algorithm",
    os.path.join(_HW_ROOT, "signer", "algorithm.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.signer",
)

_req_mod = _load(
    "mzapi.utlis.huaweicloudauth.sdk_request",
    os.path.join(_HW_ROOT, "sdk_request.py"),
    pkg_name="mzapi.utlis.huaweicloudauth",
)

SdkRequest = _req_mod.SdkRequest
SigningAlgorithm = sys.modules["mzapi.utlis.huaweicloudauth.signer.algorithm"].SigningAlgorithm


class TestSdkRequestInit(unittest.TestCase):
    """测试 SdkRequest 初始化"""

    def test_default_init(self):
        req = SdkRequest()
        self.assertEqual(req.method, "GET")
        self.assertIsNone(req.schema)
        self.assertIsNone(req.host)
        self.assertIsNone(req.resource_path)
        self.assertIsNone(req.uri)
        self.assertIsNone(req.query_params)
        self.assertIsNone(req.header_params)
        self.assertIsNone(req.body)
        self.assertFalse(req.stream)
        self.assertEqual(req.signing_algorithm, SigningAlgorithm.HMAC_SHA256)

    def test_custom_init(self):
        req = SdkRequest(
            method="POST",
            schema="https",
            host="api.example.com",
            resource_path="/v1/test",
            uri="/v1/test",
            query_params=[("key", "value")],
            header_params={"Content-Type": "application/json"},
            body='{"data": 1}',
            stream=True,
            signing_algorithm=SigningAlgorithm.HMAC_SM3,
        )
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.schema, "https")
        self.assertEqual(req.host, "api.example.com")
        self.assertEqual(req.resource_path, "/v1/test")
        self.assertEqual(req.uri, "/v1/test")
        self.assertEqual(req.query_params, [("key", "value")])
        self.assertEqual(req.header_params, {"Content-Type": "application/json"})
        self.assertEqual(req.body, '{"data": 1}')
        self.assertTrue(req.stream)
        self.assertEqual(req.signing_algorithm, SigningAlgorithm.HMAC_SM3)


class TestSdkRequestSetters(unittest.TestCase):
    """测试 SdkRequest setter 方法"""

    def setUp(self):
        self.req = SdkRequest()

    def test_method_setter(self):
        self.req.method = "PUT"
        self.assertEqual(self.req.method, "PUT")

    def test_schema_setter(self):
        self.req.schema = "http"
        self.assertEqual(self.req.schema, "http")

    def test_host_setter(self):
        self.req.host = "new-host.com"
        self.assertEqual(self.req.host, "new-host.com")

    def test_uri_setter(self):
        self.req.uri = "/new/uri"
        self.assertEqual(self.req.uri, "/new/uri")

    def test_query_params_setter(self):
        self.req.query_params = [("a", 1), ("b", 2)]
        self.assertEqual(self.req.query_params, [("a", 1), ("b", 2)])

    def test_header_params_setter(self):
        self.req.header_params = {"X-Custom": "value"}
        self.assertEqual(self.req.header_params, {"X-Custom": "value"})

    def test_body_setter(self):
        self.req.body = "new body"
        self.assertEqual(self.req.body, "new body")

    def test_stream_setter(self):
        self.req.stream = True
        self.assertTrue(self.req.stream)

    def test_signing_algorithm_setter(self):
        self.req.signing_algorithm = SigningAlgorithm.SM2_SM3
        self.assertEqual(self.req.signing_algorithm, SigningAlgorithm.SM2_SM3)

    def test_resource_path_setter(self):
        self.req.resource_path = "/new/path"
        self.assertEqual(self.req.resource_path, "/new/path")


class TestSdkRequestUrl(unittest.TestCase):
    """测试 SdkRequest.url 属性"""

    def test_url_concatenation(self):
        req = SdkRequest(schema="https", host="api.example.com", uri="/v1/test")
        self.assertEqual(req.url, "https://api.example.com/v1/test")

    def test_url_with_none_values(self):
        req = SdkRequest()
        # url 使用 %s 格式化，None 会显示为 "None"
        self.assertIn("None", req.url)


if __name__ == "__main__":
    unittest.main()

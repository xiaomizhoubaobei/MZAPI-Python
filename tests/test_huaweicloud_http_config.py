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
_MZAPI_ORIGIN = "mzapi-test-hwc-http-config-2026-qxx"

"""
huaweicloudauth.http.http_config 模块单元测试

覆盖场景：
- 默认配置值
- 自定义配置值
- proxy 构建逻辑
- get_default_config 工厂方法
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
_make_pkg("mzapi.utlis.huaweicloudauth.http", os.path.join(_HW_ROOT, "http"))

_load(
    "mzapi.utlis.huaweicloudauth.signer.algorithm",
    os.path.join(_HW_ROOT, "signer", "algorithm.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.signer",
)

_http_mod = _load(
    "mzapi.utlis.huaweicloudauth.http.http_config",
    os.path.join(_HW_ROOT, "http", "http_config.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.http",
)

HttpConfig = _http_mod.HttpConfig
SigningAlgorithm = sys.modules["mzapi.utlis.huaweicloudauth.signer.algorithm"].SigningAlgorithm


class TestHttpConfigDefaults(unittest.TestCase):
    """测试 HttpConfig 默认值"""

    def test_default_timeout(self):
        cfg = HttpConfig()
        self.assertEqual(cfg.timeout, (60, 120))

    def test_default_retry_times(self):
        cfg = HttpConfig()
        self.assertEqual(cfg.retry_times, 0)

    def test_default_pool_connections(self):
        cfg = HttpConfig()
        self.assertEqual(cfg.pool_connections, 10)

    def test_default_pool_maxsize(self):
        cfg = HttpConfig()
        self.assertEqual(cfg.pool_maxsize, 10)

    def test_default_allow_redirects(self):
        cfg = HttpConfig()
        self.assertFalse(cfg.allow_redirects)

    def test_default_ignore_ssl_verification(self):
        cfg = HttpConfig()
        self.assertFalse(cfg.ignore_ssl_verification)

    def test_default_signing_algorithm(self):
        cfg = HttpConfig()
        self.assertEqual(cfg.signing_algorithm, SigningAlgorithm.HMAC_SHA256)

    def test_default_proxy_fields(self):
        cfg = HttpConfig()
        self.assertIsNone(cfg.proxy_protocol)
        self.assertIsNone(cfg.proxy_host)
        self.assertIsNone(cfg.proxy_port)
        self.assertIsNone(cfg.proxy_user)
        self.assertIsNone(cfg.proxy_password)

    def test_default_ssl_fields(self):
        cfg = HttpConfig()
        self.assertIsNone(cfg.ssl_ca_cert)
        self.assertIsNone(cfg.cert_file)
        self.assertIsNone(cfg.key_file)

    def test_default_user_agent(self):
        cfg = HttpConfig()
        self.assertIsNone(cfg.user_agent)

    def test_get_default_config(self):
        cfg = HttpConfig.get_default_config()
        self.assertIsInstance(cfg, HttpConfig)
        self.assertEqual(cfg.timeout, (60, 120))


class TestHttpConfigCustom(unittest.TestCase):
    """测试 HttpConfig 自定义值"""

    def test_custom_values(self):
        cfg = HttpConfig(
            proxy_protocol="https",
            proxy_host="proxy.example.com",
            proxy_port=8080,
            proxy_user="user",
            proxy_password="pass",
            ignore_ssl_verification=True,
            ssl_ca_cert="/path/to/ca",
            cert_file="/path/to/cert",
            key_file="/path/to/key",
            timeout=30,
            retry_times=3,
            pool_connections=20,
            pool_maxsize=20,
            allow_redirects=True,
            ignore_content_type_for_get_request=True,
            signing_algorithm=SigningAlgorithm.HMAC_SM3,
            user_agent="CustomAgent/1.0",
        )
        self.assertEqual(cfg.proxy_protocol, "https")
        self.assertEqual(cfg.proxy_host, "proxy.example.com")
        self.assertEqual(cfg.proxy_port, 8080)
        self.assertEqual(cfg.proxy_user, "user")
        self.assertEqual(cfg.proxy_password, "pass")
        self.assertTrue(cfg.ignore_ssl_verification)
        self.assertEqual(cfg.ssl_ca_cert, "/path/to/ca")
        self.assertEqual(cfg.cert_file, "/path/to/cert")
        self.assertEqual(cfg.key_file, "/path/to/key")
        self.assertEqual(cfg.timeout, 30)
        self.assertEqual(cfg.retry_times, 3)
        self.assertEqual(cfg.pool_connections, 20)
        self.assertEqual(cfg.pool_maxsize, 20)
        self.assertTrue(cfg.allow_redirects)
        self.assertTrue(cfg.ignore_content_type_for_get_request)
        self.assertEqual(cfg.signing_algorithm, SigningAlgorithm.HMAC_SM3)
        self.assertEqual(cfg.user_agent, "CustomAgent/1.0")

    def test_setters(self):
        cfg = HttpConfig()
        cfg.proxy_host = "new-host"
        cfg.timeout = 5
        cfg.retry_times = 5
        self.assertEqual(cfg.proxy_host, "new-host")
        self.assertEqual(cfg.timeout, 5)
        self.assertEqual(cfg.retry_times, 5)


class TestHttpConfigProxy(unittest.TestCase):
    """测试 HttpConfig.proxy 构建"""

    def test_no_proxy_host_returns_empty(self):
        cfg = HttpConfig()
        self.assertEqual(cfg.proxy, {})

    def test_simple_proxy(self):
        cfg = HttpConfig(proxy_protocol="https", proxy_host="proxy.example.com", proxy_port=8080)
        self.assertEqual(cfg.proxy, {"https": "https://proxy.example.com:8080"})

    def test_proxy_with_auth(self):
        cfg = HttpConfig(
            proxy_protocol="http",
            proxy_host="proxy.com",
            proxy_port=3128,
            proxy_user="admin",
            proxy_password="p@ss",
        )
        proxy_url = cfg.proxy["https"]
        self.assertIn("http://", proxy_url)
        self.assertIn("admin:", proxy_url)
        self.assertIn("@proxy.com:3128", proxy_url)

    def test_proxy_no_port(self):
        cfg = HttpConfig(proxy_protocol="https", proxy_host="proxy.example.com")
        self.assertEqual(cfg.proxy, {"https": "https://proxy.example.com"})


if __name__ == "__main__":
    unittest.main()

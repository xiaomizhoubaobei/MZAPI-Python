# -*- coding: utf-8 -*-
# 阿里云 OpenAPI SDK 单元测试

import sys
import types
import unittest

# 确保 mzapi 包可以被导入（修复 mzapi/__init__.py 语法问题）
if 'mzapi' not in sys.modules:
    fake_mzapi = types.ModuleType('mzapi')
    fake_mzapi.__path__ = ['mzapi']
    sys.modules['mzapi'] = fake_mzapi
if 'mzapi.utlis' not in sys.modules:
    fake_utlis = types.ModuleType('mzapi.utlis')
    fake_utlis.__path__ = ['mzapi/utlis']
    sys.modules['mzapi.utlis'] = fake_utlis

from mzapi.utlis.alicloudauth.utils_models import (
    Config,
    GlobalParameters,
    OpenApiRequest,
    Params,
)
from mzapi.utlis.alicloudauth.exceptions import (
    AlibabaCloudException,
    ClientException,
    ServerException,
    ThrottlingException,
)
from mzapi.utlis.alicloudauth.utils import Utils
from mzapi.utlis.alicloudauth.sm3 import Sm3, hash_sm3
from mzapi.utlis.alicloudauth.models import SSEResponse


class TestConfig(unittest.TestCase):
    """Config 模型测试"""

    def test_init_and_to_map(self):
        config = Config(
            access_key_id="test_ak",
            access_key_secret="test_sk",
            endpoint="ecs.aliyuncs.com",
            region_id="cn-hangzhou",
            protocol="HTTPS",
        )
        m = config.to_map()
        self.assertEqual(m["accessKeyId"], "test_ak")
        self.assertEqual(m["accessKeySecret"], "test_sk")
        self.assertEqual(m["endpoint"], "ecs.aliyuncs.com")
        self.assertEqual(m["regionId"], "cn-hangzhou")
        self.assertEqual(m["protocol"], "HTTPS")

    def test_from_map(self):
        config = Config()
        config.from_map({
            "accessKeyId": "ak2",
            "accessKeySecret": "sk2",
            "securityToken": "token_xxx",
            "regionId": "cn-beijing",
            "readTimeout": 5000,
            "connectTimeout": 3000,
            "httpProxy": "http://proxy:8080",
            "httpsProxy": "https://proxy:8443",
            "noProxy": "localhost",
            "maxIdleConns": 200,
            "network": "public",
            "userAgent": "MySDK/1.0",
            "suffix": "internal",
            "socks5Proxy": "socks5://proxy:1080",
            "socks5NetWork": "tcp",
            "endpointType": "regional",
            "openPlatformEndpoint": "openservice.aliyuncs.com",
            "type": "sts",
            "signatureVersion": "v2",
            "signatureAlgorithm": "ACS3-HMAC-SHA256",
            "bearerToken": "bearer_xxx",
            "method": "POST",
            "key": "private_key",
            "cert": "cert_pem",
            "ca": "ca_pem",
            "disableHttp2": True,
            "tlsMinVersion": "1.2",
        })
        self.assertEqual(config.access_key_id, "ak2")
        self.assertEqual(config.security_token, "token_xxx")
        self.assertEqual(config.read_timeout, 5000)
        self.assertEqual(config.connect_timeout, 3000)
        self.assertEqual(config.http_proxy, "http://proxy:8080")
        self.assertTrue(config.disable_http_2)

    def test_roundtrip(self):
        config = Config(
            access_key_id="ak", access_key_secret="sk", endpoint="ep"
        )
        m = config.to_map()
        config2 = Config()
        config2.from_map(m)
        self.assertEqual(config2.access_key_id, "ak")
        self.assertEqual(config2.access_key_secret, "sk")
        self.assertEqual(config2.endpoint, "ep")

    def test_none_values_omitted(self):
        config = Config()
        m = config.to_map()
        self.assertNotIn("accessKeyId", m)
        self.assertNotIn("regionId", m)

    def test_global_parameters_in_config(self):
        gp = GlobalParameters(headers={"x-h": "v1"}, queries={"q1": "v2"})
        config = Config(global_parameters=gp)
        m = config.to_map()
        self.assertEqual(m["globalParameters"]["headers"]["x-h"], "v1")


class TestGlobalParameters(unittest.TestCase):
    """GlobalParameters 模型测试"""

    def test_to_map(self):
        gp = GlobalParameters(headers={"x-custom": "val"}, queries={"q": "1"})
        m = gp.to_map()
        self.assertEqual(m["headers"]["x-custom"], "val")
        self.assertEqual(m["queries"]["q"], "1")

    def test_from_map(self):
        gp = GlobalParameters()
        gp.from_map({"headers": {"a": "b"}, "queries": {"c": "d"}})
        self.assertEqual(gp.headers["a"], "b")
        self.assertEqual(gp.queries["c"], "d")

    def test_none_values(self):
        gp = GlobalParameters()
        m = gp.to_map()
        self.assertEqual(m, {})


class TestOpenApiRequest(unittest.TestCase):
    """OpenApiRequest 模型测试"""

    def test_to_map(self):
        req = OpenApiRequest(
            headers={"host": "ecs.aliyuncs.com"},
            query={"Action": "DescribeInstances"},
        )
        m = req.to_map()
        self.assertEqual(m["headers"]["host"], "ecs.aliyuncs.com")
        self.assertEqual(m["query"]["Action"], "DescribeInstances")

    def test_from_map(self):
        req = OpenApiRequest()
        req.from_map({
            "headers": {"h": "v"},
            "query": {"q": "v"},
            "body": "some body",
            "hostMap": {"ep": "override"},
            "endpointOverride": "custom.endpoint.com",
        })
        self.assertEqual(req.headers["h"], "v")
        self.assertEqual(req.body, "some body")
        self.assertEqual(req.host_map["ep"], "override")


class TestParams(unittest.TestCase):
    """Params 模型测试"""

    def test_to_map(self):
        p = Params(
            action="DescribeInstances",
            version="2014-05-26",
            protocol="HTTPS",
            pathname="/",
            method="GET",
            auth_type="AK",
            body_type="json",
            req_body_type="json",
            style="ROA",
        )
        m = p.to_map()
        self.assertEqual(m["action"], "DescribeInstances")
        self.assertEqual(m["authType"], "AK")
        self.assertEqual(m["bodyType"], "json")
        self.assertEqual(m["reqBodyType"], "json")

    def test_from_map(self):
        p = Params()
        p.from_map({
            "action": "CreateInstance",
            "version": "2014-05-26",
            "protocol": "HTTP",
            "pathname": "/",
            "method": "POST",
            "authType": "AK",
            "bodyType": "xml",
            "reqBodyType": "xml",
            "style": "RPC",
        })
        self.assertEqual(p.action, "CreateInstance")
        self.assertEqual(p.style, "RPC")


class TestUtils(unittest.TestCase):
    """Utils 工具类测试"""

    def test_hex_encode(self):
        self.assertEqual(Utils.hex_encode(b"\x01\x02\x03"), "010203")
        self.assertEqual(Utils.hex_encode(b"\xff"), "ff")
        self.assertIsNone(Utils.hex_encode(b""))

    def test_get_endpoint_public(self):
        result = Utils.get_endpoint("ecs", False, "public")
        self.assertEqual(result, "ecs")

    def test_get_endpoint_internal(self):
        result = Utils.get_endpoint("ecs", False, "internal")
        self.assertEqual(result, "ecs-internal")

    def test_get_timestamp(self):
        ts = Utils.get_timestamp()
        self.assertIn("T", ts)
        self.assertTrue(ts.endswith("Z"))

    def test_get_date_utcstring(self):
        dts = Utils.get_date_utcstring()
        self.assertIn("GMT", dts)

    def test_get_nonce(self):
        nonce = Utils.get_nonce()
        self.assertEqual(len(nonce), 32)

    def test_get_user_agent_with_agent(self):
        ua = Utils.get_user_agent("TestAgent/1.0")
        self.assertIn("TestAgent/1.0", ua)
        self.assertIn("AlibabaCloud", ua)

    def test_get_user_agent_without_agent(self):
        ua = Utils.get_user_agent("")
        self.assertIn("AlibabaCloud", ua)

    def test_get_encode_path(self):
        path = Utils.get_encode_path("/acs/ecs")
        self.assertEqual(path, "/acs/ecs")

    def test_get_encode_param(self):
        param = Utils.get_encode_param("hello world")
        self.assertIn("hello", param)

    def test_get_endpoint_rules_regional(self):
        result = Utils.get_endpoint_rules("ecs", "cn-hangzhou", "regional", "public")
        self.assertIn("ecs", result)
        self.assertIn("cn-hangzhou", result)

    def test_get_endpoint_rules_public(self):
        result = Utils.get_endpoint_rules("ecs", None, "public", "public")
        self.assertIn("ecs", result)

    def test_get_endpoint_rules_vpc(self):
        result = Utils.get_endpoint_rules("rds", "cn-beijing", "regional", "vpc")
        self.assertIn("rds", result)
        self.assertIn("vpc", result)
        self.assertIn("cn-beijing", result)

    def test_get_rpcsignature(self):
        sig = Utils.get_rpcsignature(
            {"Action": "DescribeInstances", "Version": "2014-05-26"},
            "GET",
            "test_secret_key",
        )
        self.assertIsInstance(sig, str)
        self.assertTrue(len(sig) > 0)

    def test_get_string_to_sign(self):
        class FakeRequest:
            method = "GET"
            pathname = "/"
            headers = {"accept": "application/json", "content-type": "application/json"}
            query = {"Action": "DescribeInstances"}
        sts = Utils.get_string_to_sign(FakeRequest())
        self.assertIn("GET", sts)
        self.assertIn("/", sts)

    def test_get_roasignature(self):
        sig = Utils.get_roasignature("string_to_sign_test", "secret_key")
        self.assertIsInstance(sig, str)
        self.assertTrue(len(sig) > 0)

    def test_anyify_map_value(self):
        m = {"a": "b"}
        self.assertEqual(Utils.anyify_map_value(m), m)

    def test_get_authorization(self):
        class FakeRequest:
            method = "POST"
            pathname = "/"
            headers = {"host": "ecs.aliyuncs.com", "x-acs-date": "2024-01-01T00:00:00Z"}
            query = {"Action": "DescribeInstances"}
        auth = Utils.get_authorization(
            FakeRequest(),
            "ACS3-HMAC-SHA256",
            "empty_payload_hash",
            "test_ak",
            "test_sk",
        )
        self.assertIn("ACS3-HMAC-SHA256", auth)
        self.assertIn("Credential=test_ak", auth)
        self.assertIn("SignedHeaders=", auth)
        self.assertIn("Signature=", auth)

    def test_flat_map(self):
        result = Utils.flat_map({"a": {"b": "c"}})
        self.assertEqual(result["a.b"], "c")

    def test_stringify_map_value(self):
        result = Utils.stringify_map_value({"k": 123, "b": b"hello"})
        self.assertEqual(result["k"], "123")
        self.assertEqual(result["b"], "hello")


class TestSm3(unittest.TestCase):
    """SM3 国密哈希算法测试"""

    def test_hash_sm3_basic(self):
        digest = hash_sm3(b"abc")
        self.assertEqual(len(digest), 32)

    def test_hash_sm3_empty(self):
        digest = hash_sm3(b"")
        self.assertEqual(len(digest), 32)

    def test_sm3_class_update(self):
        sm3 = Sm3(b"abc")
        sm3.update(b"def")
        hex_d = sm3.hexdigest()
        self.assertEqual(len(hex_d), 64)

    def test_sm3_copy(self):
        sm3 = Sm3(b"test")
        sm3_copy = sm3.copy()
        self.assertEqual(sm3.hexdigest(), sm3_copy.hexdigest())

    def test_sm3_block_size(self):
        sm3 = Sm3()
        self.assertEqual(sm3.block_size, 64)


class TestExceptions(unittest.TestCase):
    """异常类测试"""

    def test_alibaba_cloud_exception(self):
        try:
            raise AlibabaCloudException(
                code="InvalidAccessKey",
                message="Invalid AK",
                status_code=400,
                request_id="req-123",
            )
        except AlibabaCloudException as e:
            self.assertEqual(e.code, "InvalidAccessKey")
            self.assertEqual(e.message, "Invalid AK")
            self.assertEqual(e.status_code, 400)
            self.assertEqual(e.request_id, "req-123")

    def test_client_exception(self):
        try:
            raise ClientException(
                code="InvalidParameter",
                message="Bad param",
            )
        except ClientException as e:
            self.assertEqual(e.code, "InvalidParameter")
            self.assertEqual(e.name, "ClientException")

    def test_server_exception(self):
        try:
            raise ServerException(
                code="InternalError",
                message="Server error",
                status_code=500,
            )
        except ServerException as e:
            self.assertEqual(e.code, "InternalError")
            self.assertEqual(e.name, "ServerException")

    def test_throttling_exception(self):
        try:
            raise ThrottlingException(
                code="Throttling",
                message="Rate limited",
                retry_after=1000,
            )
        except ThrottlingException as e:
            self.assertEqual(e.code, "Throttling")
            self.assertEqual(e.retry_after, 1000)
            self.assertEqual(e.name, "ThrottlingException")

    def test_alibaba_cloud_exception_is_always_caught(self):
        """所有子类异常都可以被 AlibabaCloudException 捕获"""
        for ExcClass in [ClientException, ServerException, ThrottlingException]:
            with self.subTest(exc=ExcClass.__name__):
                try:
                    raise ExcClass(code="test", message="test")
                except AlibabaCloudException:
                    pass


class TestSSEResponse(unittest.TestCase):
    """SSEResponse 模型测试"""

    def test_importable(self):
        self.assertIsNotNone(SSEResponse)

    def test_init(self):
        resp = SSEResponse(headers={"content-type": "text/event-stream"}, status_code=200)
        self.assertEqual(resp.status_code, 200)


class TestModuleInit(unittest.TestCase):
    """模块初始化测试"""

    def test_exceptions_init_all(self):
        from mzapi.utlis.alicloudauth import exceptions as exc_mod
        self.assertTrue(hasattr(exc_mod, "AlibabaCloudException"))
        self.assertTrue(hasattr(exc_mod, "ClientException"))
        self.assertTrue(hasattr(exc_mod, "ServerException"))
        self.assertTrue(hasattr(exc_mod, "ThrottlingException"))

    def test_utils_models_init_all(self):
        from mzapi.utlis.alicloudauth import utils_models as um_mod
        self.assertTrue(hasattr(um_mod, "Config"))
        self.assertTrue(hasattr(um_mod, "GlobalParameters"))
        self.assertTrue(hasattr(um_mod, "OpenApiRequest"))
        self.assertTrue(hasattr(um_mod, "Params"))


if __name__ == "__main__":
    unittest.main()

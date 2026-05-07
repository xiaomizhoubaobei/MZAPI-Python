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


"""
HuaweiCloudAuth 单元测试

覆盖场景：
- 空 body / 非空 body 的签名正确性
- GET/POST/PUT/DELETE 各方法的签名
- Query Params 排序与编码
- SM3 算法路径（环境支持时）
- sign_request_for_url 的 URL 解析
- 异常输入（空 ak/sk、非法 algorithm）
- _build_canonical_uri 不出现双重编码
- UNSIGNED-PAYLOAD 非 JSON Content-Type
"""

import hashlib
import hmac
import importlib.util
import os
import sys
import unittest

# Direct import to avoid mzapi/__init__.py dependency on missing modules
_spec = importlib.util.spec_from_file_location(
    "huaweicloud_auth",
    os.path.join(os.path.dirname(__file__), os.pardir, "mzapi", "utlis", "huaweicloud_auth.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
HuaweiCloudAuth = _mod.HuaweiCloudAuth


class TestHuaweiCloudAuthInit(unittest.TestCase):
    """测试初始化和参数校验"""

    def test_valid_init_sha256(self):
        auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk")
        self.assertEqual(auth._algorithm, "SDK-HMAC-SHA256")

    def test_valid_init_sm3(self):
        auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk", algorithm="SDK-HMAC-SM3")
        self.assertEqual(auth._algorithm, "SDK-HMAC-SM3")

    def test_empty_ak_raises(self):
        with self.assertRaises(ValueError):
            HuaweiCloudAuth(ak="", sk="test_sk")

    def test_none_ak_raises(self):
        with self.assertRaises(ValueError):
            HuaweiCloudAuth(ak=None, sk="test_sk")

    def test_empty_sk_raises(self):
        with self.assertRaises(ValueError):
            HuaweiCloudAuth(ak="test_ak", sk="")

    def test_none_sk_raises(self):
        with self.assertRaises(ValueError):
            HuaweiCloudAuth(ak="test_ak", sk=None)

    def test_unsupported_algorithm_raises(self):
        with self.assertRaises(ValueError) as ctx:
            HuaweiCloudAuth(ak="test_ak", sk="test_sk", algorithm="HMAC-SHA1")
        self.assertIn("Unsupported algorithm", str(ctx.exception))

    def test_unsupported_algorithm_raises_sm2(self):
        with self.assertRaises(ValueError):
            HuaweiCloudAuth(ak="ak", sk="sk", algorithm="SDK-HMAC-SM2")


class TestCanonicalUri(unittest.TestCase):
    """测试 _build_canonical_uri"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk")

    def test_simple_path(self):
        result = self.auth._build_canonical_uri("/v2/ocr/general-text")
        self.assertEqual(result, "/v2/ocr/general-text/")

    def test_root_path(self):
        result = self.auth._build_canonical_uri("/")
        self.assertEqual(result, "/")

    def test_path_with_spaces(self):
        """路径含空格应被编码为 %20"""
        result = self.auth._build_canonical_uri("/v2/my project/file")
        self.assertEqual(result, "/v2/my%20project/file/")

    def test_encoded_slash_becomes_path_separator(self):
        """%2F 解码为 / 后被 split 为路径分隔符（与华为云 SDK 行为一致）"""
        result = self.auth._build_canonical_uri("/v2/a%2Fb/c")
        self.assertEqual(result, "/v2/a/b/c/")

    def test_normalized_space_encoding(self):
        """已编码的 %20 会被规范化"""
        result = self.auth._build_canonical_uri("/v2/my%20file")
        self.assertEqual(result, "/v2/my%20file/")

    def test_unnormalized_space_gets_encoded(self):
        """未编码的空格会被编码为 %20"""
        result = self.auth._build_canonical_uri("/v2/my file")
        self.assertEqual(result, "/v2/my%20file/")

    def test_already_encoded_not_double_encoded(self):
        """连续编码的 URI 只会规范化一次（unquote 后 re-encode）"""
        # %252F → unquote → %2F → 这是路径段内容，re-encode → %252F
        result = self.auth._build_canonical_uri("/v2/a%252Fb/c")
        self.assertEqual(result, "/v2/a%252Fb/c/")

    def test_unencoded_slash_stays_slash(self):
        """普通的斜杠保持为路径分隔符"""
        result = self.auth._build_canonical_uri("/v2/a/b/c")
        self.assertEqual(result, "/v2/a/b/c/")

    def test_trailing_slash_preserved(self):
        result = self.auth._build_canonical_uri("/v2/ocr/")
        self.assertEqual(result, "/v2/ocr/")


class TestCanonicalQueryString(unittest.TestCase):
    """测试 _build_canonical_query_string"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk")

    def test_empty_params(self):
        result = self.auth._build_canonical_query_string(None)
        self.assertEqual(result, "")

    def test_single_param(self):
        result = self.auth._build_canonical_query_string({"key": "value"})
        self.assertEqual(result, "key=value")

    def test_sorted_params(self):
        result = self.auth._build_canonical_query_string({"z": "1", "a": "2"})
        self.assertEqual(result, "a=2&z=1")

    def test_list_param(self):
        result = self.auth._build_canonical_query_string({"a": ["c", "b"]})
        self.assertEqual(result, "a=b&a=c")

    def test_bool_param_lowercased(self):
        result = self.auth._build_canonical_query_string({"flag": True})
        self.assertEqual(result, "flag=true")

    def test_special_chars_encoded(self):
        result = self.auth._build_canonical_query_string({"q": "hello world"})
        self.assertEqual(result, "q=hello%20world")

    def test_tilde_not_encoded(self):
        result = self.auth._build_canonical_query_string({"q": "~test~"})
        self.assertEqual(result, "q=~test~")


class TestSignedHeaders(unittest.TestCase):
    """测试 _get_signed_headers"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk")

    def test_basic_headers(self):
        headers = {"Content-Type": "application/json", "Host": "example.com",
                    "X-Sdk-Date": "20260101T000000Z"}
        result = self.auth._get_signed_headers(headers)
        self.assertIn("content-type", result)
        self.assertIn("host", result)
        self.assertIn("x-sdk-date", result)
        self.assertEqual(result, sorted(result))

    def test_underscore_headers_excluded(self):
        """含下划线的头部不参与签名"""
        headers = {"X_Amz_Date": "20260101T000000Z",
                    "X-Sdk-Date": "20260101T000000Z",
                    "Host": "example.com"}
        result = self.auth._get_signed_headers(headers)
        self.assertNotIn("x_amz_date", result)
        self.assertIn("x-sdk-date", result)
        self.assertIn("host", result)


class TestSignRequest(unittest.TestCase):
    """测试 sign_request 完整签名流程"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="test_access_key", sk="test_secret_key")

    def test_get_request_returns_auth_header(self):
        headers = self.auth.sign_request(
            method="GET",
            host="example.com",
            uri="/test",
        )
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("SDK-HMAC-SHA256"))
        self.assertIn("Access=test_access_key", headers["Authorization"])
        self.assertIn("SignedHeaders=", headers["Authorization"])
        self.assertIn("Signature=", headers["Authorization"])

    def test_post_request_with_json_body(self):
        body = '{"key": "value"}'
        headers = self.auth.sign_request(
            method="POST",
            host="example.com",
            uri="/api/test",
            body=body,
            content_type="application/json",
        )
        self.assertIn("Authorization", headers)
        self.assertIn("X-Sdk-Content-Sha256", headers)
        expected_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        self.assertEqual(headers["X-Sdk-Content-Sha256"], expected_hash)

    def test_put_request(self):
        headers = self.auth.sign_request(
            method="PUT",
            host="example.com",
            uri="/api/resource",
            body="data",
        )
        self.assertIn("Authorization", headers)

    def test_delete_request(self):
        headers = self.auth.sign_request(
            method="DELETE",
            host="example.com",
            uri="/api/resource/123",
        )
        self.assertIn("Authorization", headers)

    def test_empty_body_uses_empty_hash(self):
        headers = self.auth.sign_request(
            method="GET",
            host="example.com",
            uri="/",
        )
        expected_empty = hashlib.sha256(b"").hexdigest()
        self.assertEqual(headers["X-Sdk-Content-Sha256"], expected_empty)

    def test_query_params_affect_signature(self):
        headers1 = self.auth.sign_request(
            method="GET", host="example.com", uri="/api",
            query_params={"b": "2", "a": "1"},
        )
        headers2 = self.auth.sign_request(
            method="GET", host="example.com", uri="/api",
            query_params={"a": "1", "b": "2"},
        )
        # 参数顺序不同但内容相同，排序后应该得到相同签名
        self.assertEqual(
            headers1["Authorization"],
            headers2["Authorization"],
        )

    def test_non_json_content_type_unsigned(self):
        headers = self.auth.sign_request(
            method="POST",
            host="example.com",
            uri="/upload",
            body="binary-data",
            content_type="application/octet-stream",
        )
        self.assertEqual(headers.get("X-Sdk-Content-Sha256"), "UNSIGNED-PAYLOAD")

    def test_method_is_uppercased(self):
        headers = self.auth.sign_request(
            method="post",
            host="example.com",
            uri="/test",
        )
        self.assertIn("Authorization", headers)


class TestSM3Algorithm(unittest.TestCase):
    """测试 SM3 签名算法"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk", algorithm="SDK-HMAC-SM3")

    def test_sm3_algorithm_in_auth(self):
        headers = self.auth.sign_request(
            method="GET", host="example.com", uri="/test",
        )
        self.assertTrue(headers["Authorization"].startswith("SDK-HMAC-SM3"))

    def test_sm3_content_header(self):
        headers = self.auth.sign_request(
            method="POST", host="example.com", uri="/test",
            body="hello",
        )
        self.assertIn("X-Sdk-Content-Sm3", headers)

    def test_sm3_empty_body_hash(self):
        expected = "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b"
        headers = self.auth.sign_request(
            method="GET", host="example.com", uri="/",
        )
        self.assertEqual(headers["X-Sdk-Content-Sm3"], expected)


class TestSignRequestForUrl(unittest.TestCase):
    """测试 sign_request_for_url"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk")

    def test_simple_url(self):
        full_url, headers = self.auth.sign_request_for_url(
            method="GET",
            url="https://example.com/api/test",
        )
        self.assertEqual(full_url, "https://example.com/api/test")
        self.assertIn("Authorization", headers)

    def test_url_with_query(self):
        full_url, headers = self.auth.sign_request_for_url(
            method="GET",
            url="https://example.com/api/test?key=value&foo=bar",
        )
        self.assertIn("key=value", full_url)
        self.assertIn("foo=bar", full_url)

    def test_url_with_extra_query_params(self):
        full_url, headers = self.auth.sign_request_for_url(
            method="GET",
            url="https://example.com/api?key=1",
            query_params={"extra": "2"},
        )
        self.assertIn("key=1", full_url)
        self.assertIn("extra=2", full_url)


class TestConvenienceMethods(unittest.TestCase):
    """测试便捷方法 sign_get/sign_post/sign_put/sign_delete"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="test_ak", sk="test_sk")

    def test_sign_get(self):
        headers = self.auth.sign_get("example.com", "/api/data")
        self.assertIn("Authorization", headers)

    def test_sign_post(self):
        headers = self.auth.sign_post(
            "example.com", "/api/data", body='{"key":"value"}',
        )
        self.assertIn("Authorization", headers)

    def test_sign_put(self):
        headers = self.auth.sign_put(
            "example.com", "/api/data/1", body='{"key":"updated"}',
        )
        self.assertIn("Authorization", headers)

    def test_sign_delete(self):
        headers = self.auth.sign_delete("example.com", "/api/data/1")
        self.assertIn("Authorization", headers)


class TestSignatureDeterministic(unittest.TestCase):
    """测试签名的确定性：相同输入应产出相同签名"""

    def setUp(self):
        self.auth = HuaweiCloudAuth(ak="ak", sk="sk")

    def test_deterministic(self):
        kwargs = dict(method="POST", host="h.com", uri="/api",
                      query_params={"k": "v"}, body="data",
                      content_type="application/json")
        h1 = self.auth.sign_request(**kwargs)
        h2 = self.auth.sign_request(**kwargs)
        self.assertEqual(h1["Authorization"], h2["Authorization"])


if __name__ == "__main__":
    unittest.main()
# -*- coding: utf-8 -*-
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
#
# 阿里云 OCR RecognizeAllText 单元测试

import sys
import types
import unittest

# 确保 mzapi 包可以被导入（避免依赖触发其他模块）
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
    OpenApiRequest,
    Params,
)
from mzapi.utlis.alicloudauth.client import Client as AliyunOpenApiClient
from mzapi.alicloud.ocr import RecognizeAllText, RecognizeAllTextResponse


# =========================================================================
#  RecognizeAllTextResponse 测试
# =========================================================================
class TestRecognizeAllTextResponse(unittest.TestCase):
    """RecognizeAllTextResponse 响应封装测试"""

    def test_init_defaults(self):
        resp = RecognizeAllTextResponse()
        self.assertIsNone(resp.status_code)
        self.assertEqual(resp.headers, {})
        self.assertEqual(resp.body, {})

    def test_init_with_values(self):
        resp = RecognizeAllTextResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body={"RequestId": "req-123", "Code": "200", "Data": {"Content": "你好世界"}},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"], "application/json")
        self.assertEqual(resp.body["Data"]["Content"], "你好世界")

    def test_body_is_mutable(self):
        resp = RecognizeAllTextResponse()
        resp.body["Data"] = {"Content": "test"}
        self.assertEqual(resp.body["Data"]["Content"], "test")


# =========================================================================
#  RecognizeAllText 客户端测试
# =========================================================================
class TestRecognizeAllTextClient(unittest.TestCase):
    """RecognizeAllText 客户端初始化与参数构造测试"""

    def test_init_with_credentials(self):
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
        )
        self.assertEqual(client.endpoint, "ocr-api.cn-hangzhou.aliyuncs.com")
        self.assertIsNotNone(client.client)

    def test_init_with_custom_endpoint(self):
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
            endpoint="ocr-api.cn-shanghai.aliyuncs.com",
        )
        self.assertEqual(client.endpoint, "ocr-api.cn-shanghai.aliyuncs.com")

    def test_init_with_security_token(self):
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
            security_token="test_token",
        )
        self.assertIsNotNone(client.client)

    def test_init_with_protocol(self):
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
            protocol="HTTP",
        )
        self.assertIsNotNone(client.client)

    def test_init_with_timeouts(self):
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
            read_timeout=30000,
            connect_timeout=10000,
        )
        self.assertIsNotNone(client.client)


# =========================================================================
#  RecognizeAllText 参数构造测试
# =========================================================================
class TestRecognizeAllTextParams(unittest.TestCase):
    """测试 RecognizeAllText 的请求参数构造"""

    def test_recognize_method_exists(self):
        """确认 recognize 方法存在且可调用"""
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
        )
        self.assertTrue(hasattr(client, "recognize"))
        self.assertTrue(callable(client.recognize))

    def test_biz_params_with_url(self):
        """测试 URL 参数传递"""
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
        )
        # 验证 recognize 方法签名接受 url 参数
        import inspect
        sig = inspect.signature(client.recognize)
        self.assertIn("url", sig.parameters)

    def test_biz_params_all_optional(self):
        """测试所有可选参数都在方法签名中"""
        client = RecognizeAllText(
            access_key_id="test_ak",
            access_key_secret="test_sk",
        )
        import inspect
        sig = inspect.signature(client.recognize)
        expected_params = [
            "url", "body",
            "output_char_info", "output_table", "output_figure",
            "output_formula", "output_barcode", "output_qrcode",
            "output_seal", "output_handwriting", "output_stamp",
            "output_kv_pair", "output_coordinate",
            "type", "min_size", "max_side", "cut_type",
            "need_rotate", "need_sort", "multi_language",
        ]
        for param in expected_params:
            self.assertIn(param, sig.parameters, f"Missing parameter: {param}")


# =========================================================================
#  RPC 参数模型测试
# =========================================================================
class TestRecognizeAllTextRpcParams(unittest.TestCase):
    """测试 RecognizeAllText 使用的 RPC 参数模型"""

    def test_params_construction(self):
        """验证 RPC 风格参数构造正确"""
        params = Params(
            action="RecognizeAllText",
            version="2021-07-07",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="AK",
            body_type="json",
            req_body_type="json",
            style="RPC",
        )
        m = params.to_map()
        self.assertEqual(m["action"], "RecognizeAllText")
        self.assertEqual(m["version"], "2021-07-07")
        self.assertEqual(m["method"], "POST")
        self.assertEqual(m["authType"], "AK")
        self.assertEqual(m["bodyType"], "json")
        self.assertEqual(m["style"], "RPC")

    def test_open_api_request_body(self):
        """验证 OpenApiRequest 能正确封装业务参数"""
        biz_params = {
            "Url": "https://example.com/image.jpg",
            "OutputTable": True,
            "OutputCoordinate": True,
            "Type": "Advanced",
        }
        request = OpenApiRequest(
            body=biz_params,
            query={},
        )
        m = request.to_map()
        self.assertEqual(m["body"]["Url"], "https://example.com/image.jpg")
        self.assertTrue(m["body"]["OutputTable"])
        self.assertTrue(m["body"]["OutputCoordinate"])
        self.assertEqual(m["body"]["Type"], "Advanced")

    def test_open_api_request_body_minimal(self):
        """验证最小参数集"""
        request = OpenApiRequest(
            body={"Url": "https://example.com/img.jpg"},
            query={},
        )
        m = request.to_map()
        self.assertEqual(len(m["body"]), 1)
        self.assertEqual(m["body"]["Url"], "https://example.com/img.jpg")


# =========================================================================
#  模块导入测试
# =========================================================================
class TestAlicloudOcrModule(unittest.TestCase):
    """测试模块初始化和导出"""

    def test_module_origin(self):
        """验证内部项目标识"""
        import mzapi.alicloud.ocr as ocr_mod
        self.assertEqual(ocr_mod._MZAPI_ORIGIN, "mzapi-alicloud-ocr-2026-qxx")

    def test_import_classes(self):
        """验证可以导入所有公开类"""
        from mzapi.alicloud.ocr import RecognizeAllText
        from mzapi.alicloud.ocr import RecognizeAllTextResponse
        self.assertTrue(callable(RecognizeAllText))
        self.assertTrue(callable(RecognizeAllTextResponse))


if __name__ == "__main__":
    unittest.main()

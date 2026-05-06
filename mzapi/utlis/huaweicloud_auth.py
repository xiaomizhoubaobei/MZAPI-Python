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
_MZAPI_ORIGIN = "mzapi-xxx-xxx-2026-qxx"

"""
华为云 API 签名工具类

基于华为云官方 SDK (huaweicloud-sdk-python-v3) 签名算法的独立实现，
支持以下签名算法：
  - SDK-HMAC-SHA256（默认，最常用）
  - SDK-HMAC-SM3（国密 SM3 哈希）

签名流程（参照 Huawei Cloud SDK V4）：
  1. 构建规范请求串 (Canonical Request)
  2. 构建待签名字符串 (String to Sign)
  3. 计算签名 (Signature)
  4. 拼接 Authorization 头

参考文档：
  - https://support.huaweicloud.com/devg-apisign/api-sign-sign-0004.html
  - https://github.com/huaweicloud/huaweicloud-sdk-python-v3
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from urllib.parse import quote, unquote

NL = chr(10)


class HuaweiCloudAuth:
    """
    华为云 API 签名工具类

    用法示例：
        auth = HuaweiCloudAuth(ak="your_access_key", sk="your_secret_key")

        # 方式一：直接发送请求
        response = auth.send_request(
            method="POST",
            host="ocr.cn-east-3.myhuaweicloud.com",
            uri="/v2/{project_id}/ocr/general-text",
            json_body={"image": "base64_string"},
        )

        # 方式二：仅生成签名 headers
        headers = auth.sign_request(
            method="POST",
            host="ocr.cn-east-3.myhuaweicloud.com",
            uri="/v2/{project_id}/ocr/general-text",
            body='{"image":"base64_string"}',
            content_type="application/json",
        )
    """

    # 签名算法常量
    _ALGORITHM_HMAC_SHA256 = "SDK-HMAC-SHA256"
    _ALGORITHM_HMAC_SM3 = "SDK-HMAC-SM3"

    # HTTP 日期格式: 20260101T120000Z
    _DATE_FORMAT = "%Y%m%dT%H%M%SZ"

    # 请求头常量
    _HEADER_X_DATE = "X-Sdk-Date"
    _HEADER_HOST = "Host"
    _HEADER_AUTHORIZATION = "Authorization"
    _HEADER_CONTENT_SHA256 = "X-Sdk-Content-Sha256"
    _HEADER_CONTENT_SM3 = "X-Sdk-Content-Sm3"

    # SHA-256 对空字符串的哈希值
    _EMPTY_HASH_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    # SM3 对空字符串的哈希值
    _EMPTY_HASH_SM3 = "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b"

    def __init__(self, ak, sk, algorithm="SDK-HMAC-SHA256"):
        """
        初始化华为云 API 签名工具类。

        :param ak: 华为云 Access Key ID
        :param sk: 华为云 Secret Access Key
        :param algorithm: 签名算法，可选值：
            - "SDK-HMAC-SHA256"（默认）
            - "SDK-HMAC-SM3"
        """
        if not ak:
            raise ValueError("ak is required")
        if not sk:
            raise ValueError("sk is required")
        if algorithm not in (self._ALGORITHM_HMAC_SHA256, self._ALGORITHM_HMAC_SM3):
            raise ValueError(
                "Unsupported algorithm: {0}. "
                "Use 'SDK-HMAC-SHA256' or 'SDK-HMAC-SM3'.".format(algorithm)
            )
        self._ak = ak
        self._sk = sk
        self._algorithm = algorithm

        # 根据算法选择哈希函数和相关常量
        if algorithm == self._ALGORITHM_HMAC_SM3:
            self._hash_func = self._sm3_hash
            self._empty_hash = self._EMPTY_HASH_SM3
            self._content_header = self._HEADER_CONTENT_SM3
        else:
            self._hash_func = hashlib.sha256
            self._empty_hash = self._EMPTY_HASH_SHA256
            self._content_header = self._HEADER_CONTENT_SHA256

    # ===================================================================
    #  公共方法
    # ===================================================================

    def sign_request(self, method, host, uri, query_params=None,
                     headers=None, body=None, content_type=None):
        """
        对请求进行签名，返回包含 Authorization 的完整请求头字典。

        :param method: HTTP 方法（大写），如 "GET", "POST", "PUT", "DELETE"
        :param host: 请求域名，如 "ocr.cn-east-3.myhuaweicloud.com"
        :param uri: 请求路径，如 "/v2/{project_id}/ocr/general-text"
        :param query_params: 查询参数字典（可选）
        :param headers: 自定义请求头（可选），内部头（含下划线）不参与签名
        :param body: 请求体字符串（可选）
        :param content_type: Content-Type（可选）
        :return: 包含签名信息的完整请求头字典
        """
        method = method.upper()

        # 初始化请求头
        request_headers = {}
        if headers:
            request_headers.update(headers)

        # 自动添加 Host
        self._ensure_header(request_headers, self._HEADER_HOST, host)

        # 自动添加 X-Sdk-Date
        now = datetime.now(timezone.utc)
        date_str = now.strftime(self._DATE_FORMAT)
        self._ensure_header(request_headers, self._HEADER_X_DATE, date_str)

        # 设置 Content-Type
        if content_type:
            request_headers["Content-Type"] = content_type
        elif "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/json"

        # 处理非 JSON/BSON 的 Content-Type -> UNSIGNED-PAYLOAD
        self._process_content_header(request_headers)

        # 处理 body 的哈希头
        self._process_content_hash_header(request_headers, body)

        # 构建签名
        signed_headers = self._get_signed_headers(request_headers)
        canonical_request = self._build_canonical_request(
            method, uri, query_params, request_headers, signed_headers, body
        )
        string_to_sign = self._build_string_to_sign(date_str, canonical_request)
        signature = self._compute_signature(string_to_sign)
        auth_value = self._build_authorization(signature, signed_headers)
        request_headers[self._HEADER_AUTHORIZATION] = auth_value

        return request_headers

    def sign_request_for_url(self, method, url, query_params=None,
                             headers=None, body=None, content_type=None):
        """
        根据完整 URL 进行签名，返回 (完整URL, 签名后的headers)。

        :param method: HTTP 方法（大写）
        :param url: 完整 URL
        :param query_params: 查询参数字典（可选）
        :param headers: 自定义请求头（可选）
        :param body: 请求体字符串（可选）
        :param content_type: Content-Type（可选）
        :return: (完整URL, 签名后的headers字典)
        """
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(url)
        host = parsed.netloc
        uri = parsed.path

        if parsed.query:
            url_params = {
                k: v[0] if len(v) == 1 else v
                for k, v in parse_qs(parsed.query).items()
            }
            if query_params:
                url_params.update(query_params)
            query_params = url_params

        signed_headers = self.sign_request(
            method, host, uri, query_params, headers, body, content_type
        )

        canonical_qs = self._build_canonical_query_string(query_params)
        full_url = "https://{0}{1}".format(host, uri)
        if canonical_qs:
            full_url = "{0}?{1}".format(full_url, canonical_qs)

        return full_url, signed_headers

    def send_request(self, method, host, uri, query_params=None, headers=None,
                     body=None, json_body=None, content_type=None, timeout=30,
                     **kwargs):
        """
        签名并发送 HTTP 请求到华为云 API。

        :param method: HTTP 方法（大写）
        :param host: 请求域名
        :param uri: 请求路径
        :param query_params: 查询参数字典（可选）
        :param headers: 自定义请求头（可选）
        :param body: 请求体字符串（可选）
        :param json_body: 请求体字典（可选，会被 json.dumps 序列化）
        :param content_type: Content-Type（可选）
        :param timeout: 超时时间（秒），默认 30
        :param kwargs: 传递给 requests.request 的额外参数
        :return: requests.Response 对象
        """
        if json_body is not None:
            body = json.dumps(json_body, ensure_ascii=False)
            if content_type is None:
                content_type = "application/json"

        if headers is None:
            headers = {}
        headers.setdefault("User-Agent", "MZAPI/python HuaweiCloudAuth/1.0")

        signed_headers = self.sign_request(
            method, host, uri, query_params, headers, body, content_type
        )

        url = "https://{0}{1}".format(host, uri)
        canonical_qs = self._build_canonical_query_string(query_params)
        if canonical_qs:
            url = "{0}?{1}".format(url, canonical_qs)

        import requests
        response = requests.request(
            method=method,
            url=url,
            headers=signed_headers,
            data=body,
            timeout=timeout,
            **kwargs,
        )
        return response

    # ===================================================================
    #  签名核心方法（参照 Huawei Cloud SDK V4）
    # ===================================================================

    def _process_content_header(self, headers):
        """非 JSON/BSON Content-Type -> UNSIGNED-PAYLOAD"""
        content_type = headers.get("Content-Type", "")
        is_json_or_bson = (
            content_type.startswith("application/json")
            or content_type.startswith("application/bson")
        )
        if content_type and not is_json_or_bson:
            headers[self._content_header] = "UNSIGNED-PAYLOAD"

    def _process_content_hash_header(self, headers, body):
        """设置请求体哈希到 X-Sdk-Content-Sha256 头"""
        if body is None:
            if self._content_header not in headers:
                headers[self._content_header] = self._empty_hash
        elif self._content_header not in headers:
            headers[self._content_header] = self._hash_hex(body.encode("utf-8"))

    def _get_signed_headers(self, headers):
        """
        获取参与签名的头部列表。

        规则：按 key 小写排序，排除含下划线的自定义头部
        （如代理添加的 X-Amz-*/X-Cdn-* 等，华为云签名规范要求这些不参与签名）。
        """
        signed = []
        for key in headers:
            if "_" in key:
                continue
            signed.append(key.lower())
        signed.sort()
        return signed

    def _build_canonical_request(self, method, uri, query_params, headers,
                                 signed_headers, body):
        """构建规范请求串（Canonical Request）"""
        http_method = method.upper()
        canonical_uri = self._build_canonical_uri(uri)
        canonical_qs = self._build_canonical_query_string(query_params)
        canonical_headers = self._build_canonical_headers(headers, signed_headers)
        payload_hash = self._get_payload_hash(headers, body)
        signed_headers_str = ";".join(signed_headers)

        parts = [
            http_method,
            canonical_uri,
            canonical_qs,
            canonical_headers,
            signed_headers_str,
            payload_hash,
        ]
        return NL.join(parts)

    def _build_canonical_uri(self, uri):
        """
        构建规范 URI：先解码再逐段统一编码，尾部追加 "/"

        注意：按照华为云官方 SDK 的实现，先 unquote 再逐段 re-encode
        是规范化 URI 的标准做法，确保不同编码方式的等价路径
        （如 %2F 和 /）产生一致的签名结果。
        """
        patterns = unquote(uri).split("/")
        encoded_parts = [self._url_encode(p) for p in patterns]
        url_path = "/".join(encoded_parts)
        if not url_path.endswith("/"):
            url_path = url_path + "/"
        return url_path

    def _build_canonical_query_string(self, query_params):
        """
        构建规范查询字符串：参数按 key 排序，URL 编码 key/value。
        """
        if not query_params:
            return ""

        sorted_params = sorted(query_params.items())
        canonical_parts = []

        for key, value in sorted_params:
            encoded_key = self._url_encode(str(key))
            if isinstance(value, list):
                for v in sorted(value, key=str):
                    kv = "{0}={1}".format(encoded_key, self._url_encode(str(v)))
                    canonical_parts.append(kv)
            elif isinstance(value, bool):
                kv = "{0}={1}".format(encoded_key, self._url_encode(str(value).lower()))
                canonical_parts.append(kv)
            else:
                kv = "{0}={1}".format(encoded_key, self._url_encode(str(value)))
                canonical_parts.append(kv)

        return "&".join(canonical_parts)

    def _build_canonical_headers(self, headers, signed_headers):
        """构建规范请求头：按 SignedHeaders 顺序拼接 key:value"""
        normalized = {}
        for key, value in headers.items():
            normalized[key.lower()] = str(value).strip()

        lines = []
        for key in signed_headers:
            lines.append("{0}:{1}".format(key, normalized.get(key, "")))

        return NL.join(lines) + NL

    def _get_payload_hash(self, headers, body):
        """获取请求体哈希值"""
        content_hash = headers.get(self._content_header)
        if content_hash:
            return content_hash
        if body is None:
            return self._empty_hash
        return self._hash_hex(body.encode("utf-8"))

    def _build_string_to_sign(self, date_str, canonical_request):
        """构建待签名字符串（String to Sign）"""
        return NL.join([
            self._algorithm,
            date_str,
            self._hash_hex(canonical_request.encode("utf-8")),
        ])

    def _compute_signature(self, string_to_sign):
        """计算 HMAC 签名并返回十六进制字符串"""
        signature = hmac.new(
            self._sk.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            self._hash_func,
        ).digest()
        return signature.hex()

    def _build_authorization(self, signature, signed_headers):
        """拼接 Authorization 头值"""
        signed_headers_str = ";".join(signed_headers)
        return "{0} Access={1}, SignedHeaders={2}, Signature={3}".format(
            self._algorithm, self._ak, signed_headers_str, signature
        )

    # ===================================================================
    #  工具方法
    # ===================================================================

    @staticmethod
    def _url_encode(s):
        """URL 编码，保留 ~（与华为云 SDK 保持一致）"""
        return quote(str(s), safe="~")

    @staticmethod
    def _ensure_header(headers, key, value):
        """仅在 header 不存在时设置（大小写不敏感检查）"""
        for k in headers:
            if k.lower() == key.lower():
                return
        headers[key] = value

    @staticmethod
    def _sm3_hash(data=None):
        """
        SM3 哈希封装。
        优先使用 hashlib.new('sm3') (Python 3.7+ / OpenSSL 1.1.1+)。

        支持两种调用方式：
        - 作为哈希函数：_sm3_hash(data) → hash object with data
        - 作为 HMAC digestmod：hmac.new(..., _sm3_hash) → hmac.new calls _sm3_hash()
        """
        try:
            h = hashlib.new("sm3")
            if data is not None:
                h.update(data)
            return h
        except (ValueError, AttributeError):
            raise ImportError(
                "SM3 requires Python >= 3.7 and OpenSSL >= 1.1.1. "
                "Please upgrade your environment or use SDK-HMAC-SHA256."
            )

    def _hash_hex(self, data):
        """计算哈希并返回十六进制字符串"""
        return self._hash_func(data).hexdigest()

    # ===================================================================
    #  便捷签名方法（常用 API 快捷调用）
    # ===================================================================

    def sign_get(self, host, uri, query_params=None, headers=None):
        """快捷方法：签名 GET 请求"""
        return self.sign_request("GET", host, uri, query_params, headers)

    def sign_post(self, host, uri, body=None, query_params=None,
                  headers=None, content_type="application/json"):
        """快捷方法：签名 POST 请求"""
        return self.sign_request("POST", host, uri, query_params, headers,
                                 body, content_type)

    def sign_put(self, host, uri, body=None, query_params=None,
                 headers=None, content_type="application/json"):
        """快捷方法：签名 PUT 请求"""
        return self.sign_request("PUT", host, uri, query_params, headers,
                                 body, content_type)

    def sign_delete(self, host, uri, query_params=None, headers=None):
        """快捷方法：签名 DELETE 请求"""
        return self.sign_request("DELETE", host, uri, query_params, headers)
# coding: utf-8
#
# Copyright 2026 祁筱欣
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import hashlib
import hmac
import math
import binascii
import json
import requests
from datetime import datetime, timezone
from typing import Dict, Optional, List, Any, Union
from urllib.parse import quote, unquote


class HuaweiCloudAuth:
    """
    华为云API鉴权类

    支持两种鉴权方式:
    1. SDK-HMAC-SHA256: 标准鉴权，适用于华为云域名
    2. V11-HMAC-SHA256: 派生认证，适用于非华为云域名/跨云场景
    """

    _EMPTY_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def __init__(self, access_key: str, secret_key: str):
        """
        初始化鉴权类

        :param access_key: 华为云 Access Key ID
        :param secret_key: 华为云 Secret Access Key
        """
        if not access_key or not secret_key:
            raise ValueError("access_key 和 secret_key 不能为空")
        self._ak = access_key
        self._sk = secret_key

    @property
    def access_key(self) -> str:
        """
        获取 Access Key ID

        :return: Access Key ID
        """
        return self._ak

    @property
    def secret_key(self) -> str:
        """
        获取 Secret Access Key

        :return: Secret Access Key
        """
        return self._sk

    @staticmethod
    def _prepare_request_headers(
        headers: Optional[Dict[str, str]],
        host: Optional[str]
    ) -> tuple:
        """
        准备请求头

        :param headers: 请求头字典
        :param host: 主机名
        :return: (headers, timestamp) 元组
        """
        if not headers:
            headers = {}

        # 添加时间戳头
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        headers["X-Sdk-Date"] = timestamp

        # 添加 Host 头
        if host and "host" not in {k.lower() for k in headers.keys()}:
            headers["Host"] = host

        # 处理内容类型头
        content_type = headers.get("Content-Type", "")
        if content_type and not content_type.startswith("application/json") \
                and not content_type.startswith("application/bson"):
            headers["X-Sdk-Content-Sha256"] = "UNSIGNED-PAYLOAD"

        return headers, timestamp

    def create_standard_signature(
        self,
        method: str,
        uri: str,
        query_params: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        host: Optional[str] = None
    ) -> Dict[str, str]:
        """
        创建 SDK-HMAC-SHA256 标准鉴权签名

        :param method: HTTP 请求方法 (GET, POST, PUT, DELETE 等)
        :param uri: 请求路径
        :param query_params: 查询参数字典
        :param headers: 请求头字典
        :param body: 请求体 (JSON 字符串)
        :param host: 主机名 (用于添加 Host 头)
        :return: 包含签名和必要请求头的字典
        """
        # 准备请求头
        headers, timestamp = HuaweiCloudAuth._prepare_request_headers(headers, host)

        # 处理请求体
        if body is None:
            body = ""

        # 构建规范请求串
        canonical_request = HuaweiCloudAuth._build_canonical_request(
            method, uri, query_params, headers, body
        )

        # 构建待签名字符串
        string_to_sign = HuaweiCloudAuth._build_string_to_sign(canonical_request, timestamp)

        # 计算签名
        signature = HuaweiCloudAuth._calculate_signature(string_to_sign, self._sk)

        # 构建授权头
        signed_headers = HuaweiCloudAuth._get_signed_headers(headers)
        signed_headers_str = ";".join(signed_headers)
        authorization = f"SDK-HMAC-SHA256 Access={self._ak}, SignedHeaders={signed_headers_str}, Signature={signature}"

        # 返回完整的请求头
        headers["Authorization"] = authorization

        return headers

    def create_derived_signature(
        self,
        method: str,
        uri: str,
        query_params: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        host: Optional[str] = None,
        region_id: Optional[str] = None,
        service_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        创建 V11-HMAC-SHA256 派生认证签名

        :param method: HTTP 请求方法
        :param uri: 请求路径
        :param query_params: 查询参数字典
        :param headers: 请求头字典
        :param body: 请求体
        :param host: 主机名
        :param region_id: 区域ID (例如: cn-north-4)
        :param service_name: 服务名称 (例如: ocr)
        :return: 包含签名和必要请求头的字典
        """
        if not region_id or not service_name:
            raise ValueError("region_id 和 service_name 不能为空")

        # 准备请求头
        headers, timestamp = HuaweiCloudAuth._prepare_request_headers(headers, host)

        # 处理请求体
        if body is None:
            body = ""

        # 构建规范请求串
        canonical_request = HuaweiCloudAuth._build_canonical_request(
            method, uri, query_params, headers, body
        )

        # 构建派生信息字符串
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        info_str = f"{date_str}/{region_id}/{service_name}"

        # 构建待签名字符串 (V11 格式)
        string_to_sign = HuaweiCloudAuth._build_derived_string_to_sign(
            canonical_request, timestamp, info_str
        )

        # 派生密钥
        derivation_key = HuaweiCloudAuth._hkdf_sha256_derive_key(self._ak, self._sk, info_str)

        # 计算签名
        signature = HuaweiCloudAuth._calculate_signature(string_to_sign, derivation_key)

        # 构建授权头
        signed_headers = HuaweiCloudAuth._get_signed_headers(headers)
        signed_headers_str = ";".join(signed_headers)
        authorization = (
            f"V11-HMAC-SHA256 Credential={self._ak}/{info_str}, "
            f"SignedHeaders={signed_headers_str}, Signature={signature}"
        )

        # 返回完整的请求头
        headers["Authorization"] = authorization

        return headers

    @staticmethod
    def _build_canonical_request(
        method: str,
        uri: str,
        query_params: Optional[Dict[str, any]],
        headers: Dict[str, str],
        body: str
    ) -> str:
        """
        构建规范请求串

        格式:
        HTTPRequestMethod
        CanonicalURI
        CanonicalQueryString
        CanonicalHeaders
        SignedHeaders
        HexEncode(Hash(RequestPayload))
        """
        # 1. HTTP 请求方法 (大写)
        http_method = method.upper()

        # 2. 规范 URI
        canonical_uri = HuaweiCloudAuth._build_canonical_uri(uri)

        # 3. 规范查询字符串
        canonical_query = HuaweiCloudAuth._build_canonical_query_string(query_params)

        # 4. 规范请求头
        signed_headers = HuaweiCloudAuth._get_signed_headers(headers)
        canonical_headers = HuaweiCloudAuth._build_canonical_headers(headers, signed_headers)

        # 5. 签名头列表
        signed_headers_str = ";".join(signed_headers)

        # 6. 请求体哈希
        body_hash = HuaweiCloudAuth._hash_hex_string(body.encode("utf-8"))

        # 拼接
        canonical_request = "\n".join([
            http_method,
            canonical_uri,
            canonical_query,
            canonical_headers,
            signed_headers_str,
            body_hash
        ])

        return canonical_request

    @staticmethod
    def _build_string_to_sign(canonical_request: str, timestamp: str) -> str:
        """
        构建待签名字符串 (标准格式)

        格式:
        SDK-HMAC-SHA256
        X-Sdk-Date
        HexEncode(Hash(CanonicalRequest))
        """
        canonical_request_hash = HuaweiCloudAuth._hash_hex_string(canonical_request.encode("utf-8"))

        string_to_sign = "\n".join([
            "SDK-HMAC-SHA256",
            timestamp,
            canonical_request_hash
        ])

        return string_to_sign

    @staticmethod
    def _build_derived_string_to_sign(
        canonical_request: str,
        timestamp: str,
        info: str
    ) -> str:
        """
        构建待签名字符串 (派生格式)

        格式:
        V11-HMAC-SHA256
        X-Sdk-Date
        Info
        HexEncode(Hash(CanonicalRequest))
        """
        canonical_request_hash = HuaweiCloudAuth._hash_hex_string(canonical_request.encode("utf-8"))

        string_to_sign = "\n".join([
            "V11-HMAC-SHA256",
            timestamp,
            info,
            canonical_request_hash
        ])

        return string_to_sign

    @staticmethod
    def _calculate_signature(string_to_sign: str, key: str) -> str:
        """
        计算签名 (HMAC-SHA256)
        """
        return hmac.new(
            key.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _hkdf_sha256_derive_key(
        access_key: str,
        secret_key: str,
        info: str
    ) -> str:
        """
        HKDF-SHA256 密钥派生

        :param access_key: 访问密钥 (作为 salt)
        :param secret_key: 密钥 (作为 IKM)
        :param info: 上下文信息
        :return: 派生密钥 (十六进制字符串)
        """
        # HKDF Extract
        prk = HuaweiCloudAuth._hmac_sha256_extract(secret_key, access_key)

        # HKDF Expand
        okm = HuaweiCloudAuth._hmac_sha256_expand(prk, info.encode("utf-8"), 32)

        # 返回十六进制字符串
        return binascii.hexlify(okm).decode("utf-8")

    @staticmethod
    def _hmac_sha256_extract(ikm: str, salt: str) -> bytes:
        """
        HKDF Extract 阶段
        """
        if not salt:
            salt = bytes(32).decode("utf-8")

        return hmac.new(
            salt.encode("utf-8"),
            ikm.encode("utf-8"),
            hashlib.sha256
        ).digest()

    @staticmethod
    def _hmac_sha256_expand(prk: bytes, info: bytes, okm_len: int) -> bytes:
        """
        HKDF Expand 阶段
        """
        hash_len = 32  # SHA-256 输出长度
        ceil = math.ceil(float(okm_len) / float(hash_len))

        if ceil == 1:
            # 单次展开
            result = info + bytearray((1,))
            return hmac.new(prk, result, hashlib.sha256).digest()
        else:
            # 多次展开
            raw_result = bytes()
            tmp = bytes()
            for i in range(1, ceil + 1):
                tmp = hmac.new(prk, tmp + info + bytearray((i,)), hashlib.sha256).digest()
                raw_result += tmp

            return raw_result[:okm_len]

    @staticmethod
    def _build_canonical_uri(uri: str) -> str:
        """
        构建规范 URI

        注意：华为云 SDK 要求 URI 必须以 / 结尾
        """
        pattens = unquote(uri).split('/')
        uri_parts = []
        for v in pattens:
            uri_parts.append(HuaweiCloudAuth._url_encode(v))
        url_path = "/".join(uri_parts)

        # 如果 URI 不是以 / 开头，添加 /
        if not url_path.startswith('/'):
            url_path = '/' + url_path

        # 强制在 URI 末尾添加 /（华为云 SDK 要求）
        if not url_path.endswith('/'):
            url_path = url_path + "/"

        return url_path

    @staticmethod
    def _build_canonical_query_string(query_params: Optional[Dict[str, any]]) -> str:
        """
        构建规范查询字符串
        """
        if not query_params:
            return ""

        params = []
        for key, value in query_params.items():
            params.append((key, value))

        params.sort()

        query_parts = []
        for key, value in params:
            k = HuaweiCloudAuth._url_encode(key)
            if isinstance(value, list):
                value.sort()
                for v in value:
                    kv = f"{k}={HuaweiCloudAuth._url_encode(str(v))}"
                    query_parts.append(kv)
            elif isinstance(value, bool):
                kv = f"{k}={HuaweiCloudAuth._url_encode(str(value).lower())}"
                query_parts.append(kv)
            else:
                kv = f"{k}={HuaweiCloudAuth._url_encode(str(value))}"
                query_parts.append(kv)

        return '&'.join(query_parts)

    @staticmethod
    def _build_canonical_headers(
        headers: Dict[str, str],
        signed_headers: List[str]
    ) -> str:
        """
        构建规范请求头
        """
        canonical_headers = []
        normalized_headers = {}

        for key, value in headers.items():
            key_lower = key.lower()
            value_str = str(value).strip()
            normalized_headers[key_lower] = value_str

        for key in signed_headers:
            canonical_headers.append(f"{key}:{normalized_headers.get(key)}")

        return '\n'.join(canonical_headers) + "\n"

    @staticmethod
    def _get_signed_headers(headers: Dict[str, str]) -> List[str]:
        """
        获取待签名头列表

        排除:
        1. 包含下划线的头
        2. Authorization 头（因为这是签名本身）
        """
        signed_headers = []
        for key in headers.keys():
            key_lower = key.lower()
            # 排除包含下划线的头和 authorization 头
            if "_" in key or key_lower == "authorization":
                continue
            signed_headers.append(key_lower)

        signed_headers.sort()
        return signed_headers

    @staticmethod
    def _hash_hex_string(data: bytes) -> str:
        """
        计算哈希并返回十六进制字符串
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _url_encode(s: str) -> str:
        """
        URL 编码 (使用 ~ 作为安全字符)
        """
        return quote(s, safe='~')

    def send_request(
        self,
        method: str,
        uri: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        host: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
        region_id: Optional[str] = None,
        service_name: Optional[str] = None,
        enterprise_project_id: Optional[str] = None,
        use_derived_auth: bool = True
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        :param method: HTTP 请求方法
        :param uri: 请求路径
        :param headers: 请求头字典
        :param body: 请求体 (字典，会自动转为 JSON)
        :param host: 主机名
        :param query_params: 查询参数字典
        :param region_id: 区域ID (用于派生认证)
        :param service_name: 服务名称 (用于派生认证)
        :param enterprise_project_id: 企业项目ID
        :param use_derived_auth: 是否使用派生认证 (V11)，否则使用标准认证 (SDK)
        :return: API 返回的 JSON 数据
        """
        if not headers:
            headers = {}

        # 添加企业项目ID
        if enterprise_project_id:
            headers["Enterprise-Project-Id"] = enterprise_project_id

        # 准备请求体
        body_str = json.dumps(body) if body else ""

        # 生成签名
        if use_derived_auth and region_id and service_name:
            signed_headers = self.create_derived_signature(
                method=method,
                uri=uri,
                query_params=query_params,
                headers=headers,
                body=body_str,
                host=host,
                region_id=region_id,
                service_name=service_name
            )
        else:
            signed_headers = self.create_standard_signature(
                method=method,
                uri=uri,
                query_params=query_params,
                headers=headers,
                body=body_str,
                host=host
            )

        # 构建 URL
        if use_derived_auth and region_id and service_name:
            signed_headers = self.create_derived_signature(
                method=method,
                uri=uri,
                query_params=query_params,
                headers=headers,
                body=body_str,
                host=host,
                region_id=region_id,
                service_name=service_name
            )
        else:
            signed_headers = self.create_standard_signature(
                method=method,
                uri=uri,
                query_params=query_params,
                headers=headers,
                body=body_str,
                host=host
            )

        # 构建 URL
        if query_params:
            canonical_query = self._build_canonical_query_string(query_params)
            url = f"https://{host}{uri}?{canonical_query}"
        else:
            url = f"https://{host}{uri}"

        # 发送请求
        if method.upper() == "GET":
            response = requests.get(
                url,
                headers=signed_headers,
                timeout=30
            )
        else:
            response = requests.post(
                url,
                headers=signed_headers,
                data=body_str if body else None,
                timeout=30
            )

        # 检查状态码
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('error_msg', response.text)
                error_code = error_data.get('error_code', str(response.status_code))
                raise Exception(f"华为云API请求失败 (状态码: {response.status_code}): 错误码={error_code}, 错误信息={error_msg}")
            except:
                raise Exception(f"华为云API请求失败 (状态码: {response.status_code}): {response.text}")

        # 提取响应数据，包括响应头中的 X-Request-Id
        response_data = response.json()
        x_request_id = response.headers.get('X-Request-Id')
        
        # 将 X-Request-Id 添加到响应数据中（如果存在）
        if x_request_id and 'X-Request-Id' not in response_data:
            response_data['X-Request-Id'] = x_request_id

        return response_data

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

"""
腾讯云 API 鉴权工具类

基于腾讯云官方 SDK (tencentcloud-sdk-python) 的 common 模块实现，
使用 Credential 管理凭证，Sign 类进行签名。

签名算法：TC3-HMAC-SHA256（推荐）

参考文档：
  - https://cloud.tencent.com/document/product/598/12555
  - https://github.com/TencentCloud/tencentcloud-sdk-python/tree/master/tencentcloud/common
"""

import hashlib
import json
import time
import uuid

import requests

from ..tencentcloud.common.credential import Credential
from ..tencentcloud.common.sign import Sign
from ..tencentcloud.common.profile.http_profile import HttpProfile
from ..tencentcloud.common.profile.client_profile import ClientProfile


class TencentCloudAuth:
    """腾讯云 API 鉴权工具类

    提供基于 TC3-HMAC-SHA256 签名算法的腾讯云 API 鉴权和请求发送功能。

    用法示例：
        auth = TencentCloudAuth(secret_id="your_secret_id", secret_key="your_secret_key")

        # 方式一：直接发送请求
        result = auth.send_request(
            service="ocr",
            action="RecognizeGeneralText",
            version="2018-11-19",
            region="ap-guangzhou",
            payload={"ImageBase64": "base64_string"},
        )

        # 方式二：仅生成签名 headers
        headers = auth.sign_request(
            endpoint="ocr.tencentcloudapi.com",
            payload={"ImageBase64": "base64_string"},
        )

    :param secret_id: 腾讯云 SecretId
    :type secret_id: str
    :param secret_key: 腾讯云 SecretKey
    :type secret_key: str
    :param token: 联合身份凭证 Token（临时凭证，可选）
    :type token: str
    """

    _SDK_VERSION = "MZAPI_PYTHON_1.0"

    def __init__(self, secret_id, secret_key, token=None):
        """初始化 TencentCloudAuth 类实例

        :param secret_id: 腾讯云 SecretId
        :type secret_id: str
        :param secret_key: 腾讯云 SecretKey
        :type secret_key: str
        :param token: 联合身份凭证 Token（临时凭证，可选）
        :type token: str
        """
        self.credential = Credential(secret_id, secret_key, token)

    @property
    def secret_id(self):
        """获取 SecretId"""
        return self.credential.secret_id

    @property
    def secret_key(self):
        """获取 SecretKey"""
        return self.credential.secret_key

    @property
    def token(self):
        """获取 Token"""
        return self.credential.token

    def _build_tc3_signature_headers(
        self, endpoint, payload, content_type="application/json"
    ):
        """构建 TC3-HMAC-SHA256 签名请求头

        基于腾讯云官方 SDK 的签名流程：
          1. 构建规范请求串 (Canonical Request)
          2. 构建待签名字符串 (String to Sign)
          3. 通过 Sign.sign_tc3 计算签名
          4. 拼接 Authorization 头

        :param endpoint: API 域名
        :type endpoint: str
        :param payload: 请求体字符串
        :type payload: str
        :param content_type: Content-Type，默认 application/json
        :type content_type: str
        :return: (签名后的 headers 字典, 时间戳)
        :rtype: tuple
        """
        cred_secret_id, cred_secret_key, cred_token = (
            self.credential.get_credential_info()
        )
        timestamp = int(time.time())
        trace_id = str(uuid.uuid4())

        # 构建请求头
        headers = {
            "Content-Type": content_type,
            "Host": endpoint,
            "X-TC-Action": "",
            "X-TC-RequestClient": self._SDK_VERSION,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": "",
            "X-TC-TraceId": trace_id,
        }
        if cred_token:
            headers["X-TC-Token"] = cred_token

        # 构建规范请求串
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        canonical_headers = "content-type:%s\nhost:%s\n" % (
            content_type,
            endpoint,
        )
        signed_headers = "content-type;host"

        # 占位符，实际签名时由调用方设置
        return headers, timestamp, payload_hash, canonical_headers, signed_headers

    def sign_request(
        self,
        endpoint,
        payload,
        service,
        action,
        version,
        region="",
        content_type="application/json",
    ):
        """对请求进行签名，返回包含 Authorization 的完整请求头字典

        :param endpoint: API 域名，如 ocr.tencentcloudapi.com
        :type endpoint: str
        :param payload: 请求体字典（会被 json.dumps 序列化）
        :type payload: dict
        :param service: 服务名称，如 ocr
        :type service: str
        :param action: 操作名称，如 RecognizeGeneralText
        :type action: str
        :param version: API 版本，如 2018-11-19
        :type version: str
        :param region: 地域，默认空字符串
        :type region: str
        :param content_type: Content-Type，默认 application/json
        :type content_type: str
        :return: 包含签名信息的完整请求头字典
        :rtype: dict
        """
        cred_secret_id, cred_secret_key, cred_token = (
            self.credential.get_credential_info()
        )
        timestamp = int(time.time())

        # 序列化 payload
        if isinstance(payload, dict):
            payload_str = json.dumps(payload)
        else:
            payload_str = payload
        payload_bytes = (
            payload_str.encode("utf-8")
            if isinstance(payload_str, str)
            else payload_str
        )
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        # 构建规范请求串
        canonical_headers = "content-type:%s\nhost:%s\n" % (content_type, endpoint)
        signed_headers = "content-type;host"
        canonical_request = "%s\n%s\n%s\n%s\n%s\n%s" % (
            "POST",
            "/",
            "",
            canonical_headers,
            signed_headers,
            payload_hash,
        )

        # 构建待签名字符串
        algorithm = "TC3-HMAC-SHA256"
        date = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
        credential_scope = "%s/%s/tc3_request" % (date, service)
        digest = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = "%s\n%s\n%s\n%s" % (
            algorithm,
            str(timestamp),
            credential_scope,
            digest,
        )

        # 计算签名
        signature = Sign.sign_tc3(cred_secret_key, date, service, string_to_sign)

        # 拼接 Authorization
        authorization = (
            "%s Credential=%s/%s, SignedHeaders=%s, Signature=%s"
            % (algorithm, cred_secret_id, credential_scope, signed_headers, signature)
        )

        # 构建完整请求头
        headers = {
            "Content-Type": content_type,
            "Authorization": authorization,
            "Host": endpoint,
            "X-TC-Action": action[0].upper() + action[1:],
            "X-TC-Version": version,
            "X-TC-Timestamp": str(timestamp),
            "User-Agent": "MZAPI/python",
        }
        if region:
            headers["X-TC-Region"] = region
        if cred_token:
            headers["X-TC-Token"] = cred_token

        return headers

    def send_request(
        self,
        service,
        action,
        version,
        region,
        payload,
        endpoint,
        timeout=30,
        **kwargs,
    ):
        """签名并发送 POST 请求到腾讯云 API

        :param service: 服务名称，如 ocr
        :type service: str
        :param action: 操作名称，如 RecognizeGeneralText
        :type action: str
        :param version: API 版本，如 2018-11-19
        :type version: str
        :param region: 地域，如 ap-guangzhou
        :type region: str
        :param payload: 请求体字典
        :type payload: dict
        :param endpoint: 服务域名，如 ocr.tencentcloudapi.com
        :type endpoint: str
        :param timeout: 请求超时时间（秒），默认 30
        :type timeout: int
        :param kwargs: 传递给 requests.post 的额外参数
        :return: 响应 JSON 字典
        :rtype: dict
        """
        headers = self.sign_request(
            endpoint=endpoint,
            payload=payload,
            service=service,
            action=action,
            version=version,
            region=region,
        )
        url = "https://%s" % endpoint
        response = requests.post(
            url, headers=headers, json=payload, timeout=timeout, **kwargs
        )
        return response.json()
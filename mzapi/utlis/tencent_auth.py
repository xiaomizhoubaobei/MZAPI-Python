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

import requests
import hmac
import hashlib
import json
from datetime import datetime
import pytz


class TencentCloudAuth:
    """
    腾讯云API鉴权类
    """
    def __init__(self, secret_id, secret_key):
        """
        初始化 TencentCloudAuth 类实例。

        :param secret_id: 腾讯云 SecretId
        :param secret_key: 腾讯云 SecretKey
        """
        self.secret_id = secret_id
        self.secret_key = secret_key

    @staticmethod
    def _sign(key, msg):
        """
        使用 HMAC-SHA256 算法对消息进行签名。

        :param key: 密钥 (str 或 bytes)
        :param msg: 消息 (str 或 bytes)
        :return: 签名结果 (bytes)
        """
        key = key.encode('utf-8') if isinstance(key, str) else key
        msg = msg.encode('utf-8') if isinstance(msg, str) else msg
        return hmac.new(key, msg, hashlib.sha256).digest()

    def _create_signature(self, service, payload, endpoint):
        """
        创建签名。

        :param service: 服务名称
        :param payload: 请求体
        :param endpoint: 服务的域名
        :return: 签名
        """
        # 1. 拼接规范请求串 CanonicalRequest
        http_request_method = 'POST'
        canonical_uri = '/'
        canonical_querystring = ''
        canonical_headers = f'content-type:application/json\nhost:{endpoint}\n'
        signed_headers = 'content-type;host'
        hashed_request_payload = hashlib.sha256(json.dumps(payload).encode('utf-8')).hexdigest()
        canonical_request = (
            f'{http_request_method}\n'
            f'{canonical_uri}\n'
            f'{canonical_querystring}\n'
            f'{canonical_headers}\n'
            f'{signed_headers}\n'
            f'{hashed_request_payload}'
        )

        # 2. 拼接待签名字符串 StringToSign
        algorithm = 'TC3-HMAC-SHA256'
        request_timestamp = int(datetime.now().timestamp())
        date = datetime.fromtimestamp(request_timestamp, pytz.UTC).strftime('%Y-%m-%d')
        credential_scope = f'{date}/{service}/tc3_request'
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = (
            f'{algorithm}\n'
            f'{request_timestamp}\n'
            f'{credential_scope}\n'
            f'{hashed_canonical_request}'
        )

        # 3. 计算签名 Signature
        secret_date = self._sign('TC3' + self.secret_key, date)
        secret_service = self._sign(secret_date, service)
        secret_signing = self._sign(secret_service, 'tc3_request')
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # 4. 拼接签名 Authorization
        authorization = (
            f'{algorithm} '
            f'Credential={self.secret_id}/{credential_scope}, '
            f'SignedHeaders={signed_headers}, '
            f'Signature={signature}'
        )

        return authorization, request_timestamp

    def send_request(self, service, action, version, region, payload, endpoint):
        """
        发送请求。

        :param service: 服务名称
        :param action: 操作名称
        :param version: API 版本
        :param region: 地域
        :param payload: 请求体
        :param endpoint: 服务的域名
        :return: 请求结果
        """
        authorization, request_timestamp = self._create_signature(service, payload, endpoint)

        # 5. 发送 POST 请求
        headers = {
            'Content-Type': 'application/json',
            'Authorization': authorization,
            'Host': endpoint,
            'X-TC-Action': action,
            'X-TC-Version': version,
            'X-TC-Timestamp': str(request_timestamp),
            'X-TC-Region': region,
            'User-Agent': 'MZAPI/python'
        }
        url = f'https://{endpoint}'
        response = requests.post(url, headers=headers, json=payload,timeout=30)

        return response.json()

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
_MZAPI_ORIGIN = "mzapi-tc-credential-2026-qxx"

"""
腾讯云凭证管理

基于腾讯云官方 SDK (tencentcloud-sdk-python) 的凭证管理实现。
支持以下凭证类型：
  - Credential：标准凭证（SecretId + SecretKey + 可选 Token）
  - EnvironmentVariableCredential：从环境变量获取凭证

参考文档：
  - https://cloud.tencent.com/document/product/598/34228
  - https://console.cloud.tencent.com/cam/capi
"""

import os

from .exception.tencent_cloud_sdk_exception import TencentCloudSDKException


class Credential(object):
    """腾讯云标准凭证类

    管理腾讯云 API 认证所需的 SecretId 和 SecretKey。

    :param secret_id: 密钥 ID，从 https://console.cloud.tencent.com/cam/capi 获取
    :type secret_id: str
    :param secret_key: 密钥值
    :type secret_key: str
    :param token: 联合身份凭证 Token（临时凭证），指定时 secret_id 和 secret_key
                  应为临时密钥，参见：https://cloud.tencent.com/document/product/598/13896
    :type token: str
    """

    def __init__(self, secret_id, secret_key, token=None):
        if secret_id is None or secret_id.strip() == "":
            raise TencentCloudSDKException(
                "InvalidCredential", "secret id should not be none or empty"
            )
        if secret_id.strip() != secret_id:
            raise TencentCloudSDKException(
                "InvalidCredential", "secret id should not contain spaces"
            )
        self.secret_id = secret_id

        if secret_key is None or secret_key.strip() == "":
            raise TencentCloudSDKException(
                "InvalidCredential", "secret key should not be none or empty"
            )
        if secret_key.strip() != secret_key:
            raise TencentCloudSDKException(
                "InvalidCredential", "secret key should not contain spaces"
            )
        self.secret_key = secret_key

        self.token = token

    @property
    def secretId(self):
        """获取 SecretId（驼峰命名兼容）"""
        return self.secret_id

    @property
    def secretKey(self):
        """获取 SecretKey（驼峰命名兼容）"""
        return self.secret_key

    def get_credential_info(self):
        """获取凭证三元组

        :return: (secret_id, secret_key, token)
        :rtype: tuple
        """
        return self.secret_id, self.secret_key, self.token


class EnvironmentVariableCredential(object):
    """腾讯云环境变量凭证类

    从环境变量获取凭证信息。

    环境变量：
      - TENCENTCLOUD_SECRET_ID：SecretId
      - TENCENTCLOUD_SECRET_KEY：SecretKey

    参考：https://console.cloud.tencent.com/cam/capi
    """

    def get_credential(self):
        """从环境变量获取凭证

        :return: Credential 实例，环境变量未设置时返回 None
        :rtype: Credential or None
        """
        self.secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID")
        self.secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY")

        if self.secret_id is None or self.secret_key is None:
            return None
        if len(self.secret_id) == 0 or len(self.secret_key) == 0:
            return None
        return Credential(self.secret_id, self.secret_key)
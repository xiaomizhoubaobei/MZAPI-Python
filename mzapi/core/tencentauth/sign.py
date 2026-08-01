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
_MZAPI_ORIGIN = "mzapi-txc-sign-2026-qxx"

"""
腾讯云 API 签名算法

基于腾讯云官方 SDK (tencentcloud-sdk-python) 的签名实现。
支持以下签名方法：
  - TC3-HMAC-SHA256（推荐，v3 签名）
  - HmacSHA256（旧版 v1 签名）
  - HmacSHA1（旧版 v1 签名）

参考文档：
  - https://cloud.tencent.com/document/product/598/12555
"""

import binascii
import hashlib
import hmac
import sys

from .exception.tencent_cloud_sdk_exception import TencentCloudSDKException


class Sign(object):
    """腾讯云 API 签名工具类

    提供静态方法实现腾讯云 API 的签名计算。

    签名流程（TC3-HMAC-SHA256）：
      1. 构建规范请求串 (Canonical Request)
      2. 构建待签名字符串 (String to Sign)
      3. 通过 HMAC-SHA256 计算签名 (Signature)
      4. 拼接 Authorization 头

    签名流程（HmacSHA1/SHA256）：
      1. 构建签名参数串（按键名排序）
      2. 通过 HMAC 算法计算签名
      3. Base64 编码签名结果
    """

    @staticmethod
    def sign(secret_key, sign_str, sign_method):
        """旧版签名方法（HmacSHA1 / HmacSHA256）

        适用于腾讯云 v1 版本 API 签名。

        :param secret_key: 密钥（SecretKey）
        :type secret_key: str
        :param sign_str: 待签名字符串
        :type sign_str: str
        :param sign_method: 签名方法，可选值：HmacSHA1, HmacSHA256
        :type sign_method: str
        :return: Base64 编码的签名结果
        :rtype: str
        :raises TencentCloudSDKException: 签名方法不支持时抛出异常
        """
        if sys.version_info[0] > 2:
            sign_str = bytes(sign_str, "utf-8")
            secret_key = bytes(secret_key, "utf-8")

        digestmod = None
        if sign_method == "HmacSHA256":
            digestmod = hashlib.sha256
        elif sign_method == "HmacSHA1":
            digestmod = hashlib.sha1
        else:
            raise TencentCloudSDKException(
                "signMethod invalid",
                "signMethod only support (HmacSHA1, HmacSHA256)",
            )

        hashed = hmac.new(secret_key, sign_str, digestmod)
        base64 = binascii.b2a_base64(hashed.digest())[:-1]

        if sys.version_info[0] > 2:
            base64 = base64.decode()

        return base64

    @staticmethod
    def sign_tc3(secret_key, date, service, str2sign):
        """TC3-HMAC-SHA256 签名方法（推荐）

        适用于腾讯云 v3 版本 API 签名。

        签名密钥推导流程：
          secret_key -> ('TC3' + secret_key) + date -> service -> 'tc3_request'

        :param secret_key: 密钥（SecretKey）
        :type secret_key: str
        :param date: 日期字符串，格式 YYYY-MM-DD
        :type date: str
        :param service: 服务名称，如 cvc、ocr 等
        :type service: str
        :param str2sign: 待签名字符串
        :type str2sign: str
        :return: 十六进制签名字符串
        :rtype: str
        """

        def _hmac_sha256(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256)

        def _get_signature_key(key, date, service):
            k_date = _hmac_sha256(("TC3" + key).encode("utf-8"), date)
            k_service = _hmac_sha256(k_date.digest(), service)
            k_signing = _hmac_sha256(k_service.digest(), "tc3_request")
            return k_signing.digest()

        signing_key = _get_signature_key(secret_key, date, service)
        signature = _hmac_sha256(signing_key, str2sign).hexdigest()
        return signature
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
腾讯云 Client Profile 配置

基于腾讯云官方 SDK (tencentcloud-sdk-python) 的 ClientProfile 实现。
"""

import re
import warnings

from ..exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from .http_profile import HttpProfile


class ClientProfile(object):
    """SDK 客户端配置

    :param signMethod: 签名方法，可选值：HmacSHA1, HmacSHA256, TC3-HMAC-SHA256
    :type signMethod: str
    :param httpProfile: HTTP 配置
    :type httpProfile: :class:`HttpProfile`
    :param language: 语言，可选值：en-US, zh-CN
    :type language: str
    :param disable_region_breaker: 地域熔断开关
    :type disable_region_breaker: bool
    :param request_client: 自定义请求客户端标识
    :type request_client: str
    """

    unsignedPayload = False

    def __init__(
        self,
        signMethod=None,
        httpProfile=None,
        language="zh-CN",
        disable_region_breaker=True,
        region_breaker_profile=None,
        request_client=None,
        retryer=None,
    ):
        self.httpProfile = HttpProfile() if httpProfile is None else httpProfile
        self.signMethod = "TC3-HMAC-SHA256" if signMethod is None else signMethod
        valid_language = ["zh-CN", "en-US"]
        if language not in valid_language:
            raise TencentCloudSDKException(
                "ClientError",
                "Language invalid, choices: %s" % valid_language,
            )
        self.language = language
        self.disable_region_breaker = disable_region_breaker
        self.region_breaker_profile = region_breaker_profile
        if not self.disable_region_breaker and self.region_breaker_profile is None:
            self.region_breaker_profile = RegionBreakerProfile()
        self.request_client = None
        if isinstance(request_client, str) and re.match(
            "^[0-9a-zA-Z-_,;.]+$", request_client
        ):
            if len(request_client) > 128:
                warnings.warn(
                    "the length of RequestClient should be with in 128 characters, "
                    "it will be truncated"
                )
            self.request_client = request_client[:128]
        elif request_client is not None:
            warnings.warn(
                "RequestClient not match the regexp: "
                "^[0-9a-zA-Z-_,;.]+$, ignored"
            )
        self.retryer = retryer


class RegionBreakerProfile(object):
    """地域熔断配置

    :param backup_endpoint: 备用地域域名，默认 ap-guangzhou.tencentcloudapi.com
    :type backup_endpoint: str
    :param max_fail_num: 触发熔断的最大失败次数，默认 5
    :type max_fail_num: int
    :param max_fail_percent: 触发熔断的最大失败比例，默认 0.75
    :type max_fail_percent: float
    :param window_interval: 熔断状态重置窗口间隔（秒），默认 300（5 分钟）
    :type window_interval: int
    :param timeout: 熔断器超时时间（秒），默认 60
    :type timeout: int
    :param max_requests: 半开状态下最大请求数，默认 5
    :type max_requests: int
    """

    def __init__(
        self,
        backup_endpoint="ap-guangzhou.tencentcloudapi.com",
        max_fail_num=5,
        max_fail_percent=0.75,
        window_interval=60 * 5,
        timeout=60,
        max_requests=5,
    ):
        self.backup_endpoint = backup_endpoint
        if not self.check_endpoint():
            raise TencentCloudSDKException(
                "ClientError",
                "the format of `backup_endpoint` must be tencentcloudapi.com "
                "or ${region}.tencentcloudapi.com",
            )
        self.max_fail_num = max_fail_num
        self.max_fail_percent = max_fail_percent
        if self.max_fail_percent < 0 or self.max_fail_percent > 1:
            raise TencentCloudSDKException(
                "ClientError",
                "max fail percent must be set between 0 and 1",
            )
        self.window_interval = window_interval
        self.timeout = timeout
        self.max_requests = max_requests

    def check_endpoint(self):
        """校验 backup_endpoint 格式"""
        endpoint_split = self.backup_endpoint.split(".")
        if len(endpoint_split) != 3 and len(endpoint_split) != 2:
            return False
        if endpoint_split[-2] != "tencentcloudapi" or endpoint_split[-1] != "com":
            return False
        if len(endpoint_split) == 3:
            region = endpoint_split[0]
            if len(region.split("-")) != 2:
                return False
        return True
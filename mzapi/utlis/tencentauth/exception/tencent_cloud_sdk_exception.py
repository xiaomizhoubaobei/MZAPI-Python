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
腾讯云 SDK 异常类

基于腾讯云官方 SDK (tencentcloud-sdk-python) 的异常定义。
"""

import sys


class TencentCloudSDKException(Exception):
    """腾讯云 SDK 异常基类

    所有腾讯云 API 调用产生的异常都继承自此类。

    :param code: 错误码，如 "InvalidCredential"、"InternalError" 等
    :type code: str
    :param message: 错误描述信息
    :type message: str
    :param requestId: 请求唯一标识，用于问题排查
    :type requestId: str
    """

    def __init__(self, code=None, message=None, requestId=None):
        self.code = code
        self.message = message
        self.requestId = requestId

    def __str__(self):
        s = (
            "[TencentCloudSDKException] code:%s message:%s requestId:%s"
            % (self.code, self.message, self.requestId)
        )
        if sys.version_info[0] < 3 and isinstance(s, unicode):
            return s.encode("utf8")
        return s

    def get_code(self):
        """获取错误码"""
        return self.code

    def get_message(self):
        """获取错误描述"""
        return self.message

    def get_request_id(self):
        """获取请求 ID"""
        return self.requestId

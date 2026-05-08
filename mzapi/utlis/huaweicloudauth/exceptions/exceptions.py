# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-hwc-exceptions-2026-qxx"

"""华为云 SDK 异常定义

定义 SdkException、ConnectionException、ServiceResponseException 等异常类型。"""

class SdkException(Exception):
    def __init__(self, error_msg):
        """
        基础异常类。
        """
        super().__init__()
        self._error_msg = error_msg

    @property
    def error_msg(self):
        return self._error_msg

    @error_msg.setter
    def error_msg(self, value):
        self._error_msg = value

    def __str__(self):
        return "%s - %s" % (self.__class__.__name__, self.error_msg)


class ConnectionException(SdkException):
    def __init__(self, error_msg):
        """
        连接异常基类。
        """
        super().__init__(error_msg)


class HostUnreachableException(ConnectionException):
    def __init__(self, error_msg):
        """
        主机不可达异常。
        """
        super().__init__(error_msg)


class SslHandShakeException(ConnectionException):
    def __init__(self, error_msg):
        """
        SSL 握手异常。
        """
        super().__init__(error_msg)


class ServiceResponseException(SdkException):
    def __init__(self, status_code, sdk_error):
        """
        服务响应异常基类。
        """
        super().__init__(sdk_error.error_msg)
        self._status_code = status_code
        self._error_code = sdk_error.error_code
        self._request_id = sdk_error.request_id
        self._encoded_auth_msg = sdk_error.encoded_auth_msg

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def error_code(self):
        return self._error_code

    @error_code.setter
    def error_code(self, value):
        self._error_code = value

    @property
    def request_id(self):
        return self._request_id

    @request_id.setter
    def request_id(self, value):
        self._request_id = value

    @property
    def encoded_auth_msg(self):
        return self._encoded_auth_msg

    @encoded_auth_msg.setter
    def encoded_auth_msg(self, value):
        self._encoded_auth_msg = value

    def __str__(self):
        return "%s - {status_code:%s,request_id:%s,error_code:%s,error_msg:%s,encoded_authorization_message:%s }" % (
            self.__class__.__name__, self.status_code, self.request_id, self.error_code, self.error_msg,
            self.encoded_auth_msg)


class ClientRequestException(ServiceResponseException):
    def __init__(self, status_code, sdk_error):
        """
        客户端请求异常。
        """
        super().__init__(status_code, sdk_error)


class ServerResponseException(ServiceResponseException):
    def __init__(self, status_code, sdk_error):
        """
        服务端响应异常。
        """
        super().__init__(status_code, sdk_error)


class RequestTimeoutException(SdkException):
    def __init__(self, error_msg):
        """
        请求超时异常基类。
        """
        super().__init__(error_msg)


class CallTimeoutException(RequestTimeoutException):
    def __init__(self, error_msg):
        """
        调用超时异常。
        """
        super().__init__(error_msg)


class RetryOutageException(RequestTimeoutException):
    def __init__(self, error_msg):
        """
        重试耗尽异常。
        """
        super().__init__(error_msg)


class SdkError:
    def __init__(self, request_id=None, error_code=None, error_msg=None, encoded_auth_msg=None):
        self._error_msg = error_msg
        self._error_code = error_code
        self._request_id = request_id
        self._encoded_auth_msg = encoded_auth_msg

    @property
    def error_msg(self):
        return self._error_msg

    @error_msg.setter
    def error_msg(self, value):
        self._error_msg = value

    @property
    def error_code(self):
        return self._error_code

    @error_code.setter
    def error_code(self, value):
        self._error_code = value

    @property
    def request_id(self):
        return self._request_id

    @request_id.setter
    def request_id(self, value):
        self._request_id = value

    @property
    def encoded_auth_msg(self):
        return self._encoded_auth_msg

    @encoded_auth_msg.setter
    def encoded_auth_msg(self, value):
        self._encoded_auth_msg = value


def render_path(path_to_item):
    """返回路径的字符串表示"""
    result = ""
    for pth in path_to_item:
        if isinstance(pth, int):
            result += "[{0}]".format(pth)
        else:
            result += "['{0}']".format(pth)
    return result


class ApiTypeError(TypeError):
    def __init__(self, msg, path_to_item=None, valid_classes=None,
                 key_type=None):
        """类型错误异常

        参数:
            msg (str): 异常消息

        可选参数:
            path_to_item (list): 定位到当前元素的键和索引列表，未设置时为 None
            valid_classes (tuple): 当前元素应为实例的原始类型，未设置时为 None
            key_type (bool): 值是否为字典中的值(False)、字典中的键(True)或列表中的元素(False)，未设置时为 None
        """
        self.path_to_item = path_to_item
        self.valid_classes = valid_classes
        self.key_type = key_type
        full_msg = msg
        if path_to_item:
            full_msg = "%s at %s" % (msg, render_path(path_to_item))
        super().__init__(full_msg)


class ApiValueError(ValueError):
    def __init__(self, msg, path_to_item=None):
        """
        参数:
            msg (str): 异常消息

        可选参数:
            path_to_item (list): 在接收数据字典中定位异常的路径，未设置时为 None
        """

        self.path_to_item = path_to_item
        full_msg = msg
        if path_to_item:
            full_msg = "%s at %s" % (msg, render_path(path_to_item))
        super().__init__(full_msg)


class ApiKeyError(KeyError):
    def __init__(self, msg, path_to_item=None):
        """
        参数:
            msg (str): 异常消息

        可选参数:
            path_to_item (list): 在接收数据字典中定位异常的路径，未设置时为 None
        """
        self.path_to_item = path_to_item
        full_msg = msg
        if path_to_item:
            full_msg = "%s at %s" % (msg, render_path(path_to_item))
        super().__init__(full_msg)

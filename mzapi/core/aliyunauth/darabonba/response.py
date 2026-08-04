# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION - DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0.
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-response-2026-qxx"


"""
HTTP 响应模型模块

定义 darabonba 风格的 HTTP 响应对象 DaraResponse，
保存状态码、状态消息、响应头、原始响应对象及响应体。
"""

from typing import Any, Dict, Optional, Union
from aiohttp import ClientResponse


class DaraResponse:
    """darabonba HTTP 响应对象，承载一次请求的完整响应信息。"""

    def __init__(self):
        # status
        self.status_code: Optional[int] = None
        # reason
        self.status_message: Optional[str] = None
        self.headers: Optional[Dict[str, str]] = None
        self.response: Optional[Union[ClientResponse, Any]] = None
        self.body: Optional[Union[bytes, Any]] = None
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

"""华为云异步会话

提供 FutureSession 类，封装异步 HTTP 请求的 Future 机制。"""

from requests import Session


class FutureSession(Session):
    def __init__(self, session, executor):
        super().__init__()
        self._session = session
        self._executor = executor

    def request(self, *args, **kwargs):
        return self._executor.submit(self._session.request, *args, **kwargs)

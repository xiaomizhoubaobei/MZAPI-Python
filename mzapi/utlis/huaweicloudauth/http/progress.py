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

"""华为云上传/下载进度

提供 ProgressNotifier 和 ProgressRequestBody，实现文件传输进度回调。"""

import threading
import time

from urllib3.response import HTTPResponse
from queue import Queue

_CHUNK_SIZE = 65536
_INTERVAL = 102400


class ProgressNotifier:

    def __init__(self, callback=None, total_amount=-1, interval=_INTERVAL):
        self.callback = callback
        if self.callback is None or not callable(self.callback):
            raise TypeError('Invalid callback')
        self._total_amount = total_amount
        self._interval = interval
        self._transferred_amount = 0
        self._newly_transferred_amount = 0
        self._queue = Queue()
        self._start_checkpoint = None

    def _run(self):
        while True:
            data = self._queue.get()
            if data is None:
                self.callback(*self._calculate())
                self.callback = None
                self._queue = None
                break

            self._transferred_amount += data
            self._newly_transferred_amount += data
            if self._newly_transferred_amount >= self._interval and (
                    self._transferred_amount < self._total_amount or self._total_amount <= 0):
                self._newly_transferred_amount = 0
                self.callback(*self._calculate())

    def start(self):
        now = time.time()
        self._start_checkpoint = now
        t = threading.Thread(target=self._run)
        t.daemon = True
        t.start()

    def _calculate(self):
        total_seconds = time.time() - self._start_checkpoint
        return self._transferred_amount, self._total_amount, total_seconds if total_seconds > 0 else 0.001

    def send(self, data):
        if isinstance(data, int):
            self._queue.put(data)

    def end(self):
        self._queue.put(None)


class ProgressRequestBody:
    def __init__(self, _file, notifier):
        self._file = _file
        self._notifier = notifier

    def __iter__(self):
        self._notifier.start()
        with self._file as f:
            while True:
                chunk = f.read(_CHUNK_SIZE)
                if not chunk:
                    self._notifier.end()
                    break
                self._notifier.send(len(chunk))
                yield chunk


class ProgressHTTPResponse(HTTPResponse):
    def __init__(self, notifier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._notifier = notifier

    def read(self, amt=_CHUNK_SIZE, decode_content=None, cache_content=False):
        chunk = super().read(amt, decode_content, cache_content)
        if chunk:
            self._notifier.send(len(chunk))
        else:
            self._notifier.end()
        return chunk

    @classmethod
    def convert(cls, http_response: HTTPResponse, notifier: ProgressNotifier):
        if not isinstance(http_response, cls.__base__):
            raise TypeError("can not convert non-HTTPResponse to ProgressHTTPResponse")
        http_response.__class__ = cls
        setattr(http_response, "_notifier", notifier)
        notifier.start()

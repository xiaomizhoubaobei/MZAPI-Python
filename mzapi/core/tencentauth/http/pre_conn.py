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
_MZAPI_ORIGIN = "mzapi-txc-pre-conn-2026-qxx"



"""
HTTP 预连接池优化模块

实现基于 urllib3 的预连接池机制，
在请求发起之前预先建立 TCP/TLS 连接，减少首次请求的延迟。

包含的类：
  - HTTPSPreConnPool：HTTPS 预连接池
  - HTTPPreConnPool：HTTP 预连接池
  - PreConnPoolManager：预连接池管理器
  - PreConnAdapter：预连接适配器

工作原理：
  1. 创建连接池时，清空默认连接
  2. 启动后台守护线程，持续创建新连接并放入池中
  3. 请求时直接从池中获取已建立的连接
"""

import logging
import threading

from requests.adapters import HTTPAdapter
from urllib3 import HTTPSConnectionPool, PoolManager, HTTPConnectionPool

logger = logging.getLogger("tencentcloud_sdk_common")


class HTTPSPreConnPool(HTTPSConnectionPool):
    _close_signal = {}

    def __init__(self, *args, **kwargs):
        super(HTTPSPreConnPool, self).__init__(*args, **kwargs)
        # clear the pool
        for _ in range(self.pool.maxsize):
            self.pool.get()
        self._conn_producer = threading.Thread(target=self._conn_producer_loop)
        self._conn_producer.setDaemon(True)
        self._conn_producer.start()

    def _conn_producer_loop(self):
        while True:
            conn = super(HTTPSPreConnPool, self)._new_conn()
            conn.connect()
            logger.debug("HTTPSPreConnPool: created a new conn")
            self.pool.put(conn)


class HTTPPreConnPool(HTTPConnectionPool):
    _close_signal = {}

    def __init__(self, *args, **kwargs):
        super(HTTPPreConnPool, self).__init__(*args, **kwargs)
        # clear the pool
        for _ in range(self.pool.maxsize):
            self.pool.get()
        self._conn_producer = threading.Thread(target=self._conn_producer_loop)
        self._conn_producer.setDaemon(True)
        self._conn_producer.start()

    def _conn_producer_loop(self):
        while True:
            conn = super(HTTPPreConnPool, self)._new_conn()
            conn.connect()
            logger.debug("HTTPSPreConnPool: created a new conn")
            self.pool.put(conn)


class PreConnPoolManager(PoolManager):
    def __init__(self, pool_size, *args, **kwargs):
        self._pool_size = pool_size
        super(PreConnPoolManager, self).__init__(*args, **kwargs)

    def _new_pool(self, scheme, host, port, request_context):
        if scheme == 'https':
            return HTTPSPreConnPool(host, port, maxsize=self._pool_size - 1)
        if scheme == 'http':
            return HTTPPreConnPool(host, port, maxsize=self._pool_size - 1)
        return super(PreConnPoolManager, self)._new_pool(scheme, host, port, request_context)


class PreConnAdapter(HTTPAdapter):
    def __init__(self, conn_pool_size, *args, **kwargs):
        self._conn_pool_size = conn_pool_size
        super(PreConnAdapter, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        self.poolmanager = PreConnPoolManager(self._conn_pool_size, *args, **kwargs)

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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-core-2026-qxx"


"""
darabonba 核心运行时模块

提供 HTTP 请求的同步/异步执行、SSE 流式响应、TLS 适配、重试判断、
退避计算、数据模型序列化等核心能力。

包含的类：
  - DaraCore：核心运行时类，提供静态工具方法完成请求发送与数据处理。
  - TLSVersion：TLS 版本枚举。
  - _ModelEncoder：支持 DaraModel 与 bytes 的 JSON 编码器。
  - _TLSAdapter：自定义 TLS 版本的 requests HTTPAdapter。
"""

import asyncio
import aiohttp
import logging
import io
import os
import ssl
import time
import re
import certifi
import json
from requests import status_codes, adapters, PreparedRequest
from typing import Any, Dict, Optional, Union
from enum import Enum
from urllib.parse import urlencode, urlparse
from requests import status_codes, adapters, PreparedRequest, Session
from mzapi.core.aliyunauth.darabonba.exceptions import RequiredArgumentException, RetryError
from mzapi.core.aliyunauth.darabonba.model import DaraModel
from mzapi.core.aliyunauth.darabonba.request import DaraRequest
from mzapi.core.aliyunauth.darabonba.response import DaraResponse
from mzapi.core.aliyunauth.darabonba.utils.stream import BaseStream, SSEResponseWrapper, SyncSSEResponseWrapper
from mzapi.core.aliyunauth.darabonba.policy.retry import RetryOptions, RetryPolicyContext


DEFAULT_CONNECT_TIMEOUT = 5000
DEFAULT_READ_TIMEOUT = 10000
DEFAULT_POOL_SIZE = 10
DEFAULT_POOL_MAXSIZE = DEFAULT_POOL_SIZE * 4
MAX_DELAY_TIME = 120 * 1000
MIN_DELAY_TIME = 100

logger = logging.getLogger('darabonba-core')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

class _ModelEncoder(json.JSONEncoder):
    """JSON 编码器，将 DaraModel 序列化为字典、bytes 解码为字符串。"""

    def default(self, o: Any) -> Any:
        if isinstance(o, DaraModel):
            return o.to_map()
        elif isinstance(o, bytes):
            return o.decode('utf-8')
        super().default(o)


class TLSVersion(Enum):
    """TLS 版本枚举。"""
    TLSv1 = 'TLSv1'
    TLSv1_1 = 'TLSv1.1'
    TLSv1_2 = 'TLSv1.2'
    TLSv1_3 = 'TLSv1.3'

class _TLSAdapter(adapters.HTTPAdapter):
    """使用指定 TLS 版本的 requests HTTPAdapter。"""

    def __init__(self, ssl_context=None, **kwargs):
        """初始化 TLS 适配器。

        Args:
            ssl_context: 用于连接的 SSL 上下文。
            **kwargs: 传递给 HTTPAdapter 的其余参数。
        """
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        """覆写 init_poolmanager 方法，将自定义 SSL 上下文注入连接池。"""
        kwargs['ssl_context'] = self.ssl_context
        super().init_poolmanager(*args, **kwargs)


class DaraCore:
    """darabonba 核心运行时类。

    提供请求 URL 组装、同步/异步 HTTP 请求执行、SSE 流式响应、
    TLS 适配、重试判断与退避计算、数据模型序列化等静态工具方法。
    """

    _sessions = {}
    http_adapter = adapters.HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_MAXSIZE)
    https_adapter = adapters.HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_MAXSIZE)

    @staticmethod
    def to_json_string(
        val: Any,
    ) -> str:
        """将值序列化为 JSON 格式字符串。

        Args:
            val: 待序列化的值，字符串原样返回，其他类型走 JSON 编码。

        Returns:
            JSON 格式字符串。
        """
        if isinstance(val, str):
            return str(val)
        return json.dumps(
            val, cls=_ModelEncoder, ensure_ascii=False, separators=(",", ":")
        )

    @staticmethod
    def _resolve_pool_maxsize(runtime_option=None) -> int:
        """从运行时配置 maxIdleConns 解析连接池大小。

        与 Go tea 的 MaxIdleConns / MaxIdleConnsPerHost 语义对齐。

        Args:
            runtime_option: 运行时配置（字典）。

        Returns:
            连接池最大连接数。
        """
        runtime_option = runtime_option or {}
        max_idle = runtime_option.get('maxIdleConns')
        if max_idle is None:
            return DEFAULT_POOL_MAXSIZE
        try:
            max_idle = int(max_idle)
        except (TypeError, ValueError):
            return DEFAULT_POOL_MAXSIZE
        if max_idle > 0:
            return max_idle
        return DEFAULT_POOL_MAXSIZE

    @staticmethod
    def _set_tls_minimum_version(sls_context, tls_min_version):
        """为 SSL 上下文设置最低 TLS 版本。

        Args:
            sls_context: SSL 上下文。
            tls_min_version: TLS 版本名称（TLSv1、TLSv1.1 等）。

        Returns:
            设置后的 SSL 上下文。
        """
        context = sls_context
        if tls_min_version is not None:
            if tls_min_version == 'TLSv1':
                context.minimum_version = ssl.TLSVersion.TLSv1
            elif tls_min_version == 'TLSv1.1':
                context.minimum_version = ssl.TLSVersion.TLSv1_1
            elif tls_min_version == 'TLSv1.2':
                context.minimum_version = ssl.TLSVersion.TLSv1_2
            elif tls_min_version == 'TLSv1.3':
                context.minimum_version = ssl.TLSVersion.TLSv1_3
        return context

    @staticmethod
    def get_adapter(prefix, tls_min_version: str = None, pool_size: int = None):
        """根据协议前缀创建 HTTP/HTTPS 适配器，并加载 CA 证书。

        Args:
            prefix: 协议前缀（http / https）。
            tls_min_version: 最低 TLS 版本。
            pool_size: 连接池大小。

        Returns:
            配置好的 HTTPAdapter。
        """
        pool_maxsize = pool_size if pool_size is not None and pool_size > 0 else DEFAULT_POOL_MAXSIZE
        ca_cert = certifi.where()
        context = ssl.create_default_context()
        if ca_cert and prefix.upper() == 'HTTPS':
            context = DaraCore._set_tls_minimum_version(context, tls_min_version)
            context.load_verify_locations(ca_cert)
        adapter = _TLSAdapter(
            ssl_context=context,
            pool_connections=DEFAULT_POOL_SIZE,
            pool_maxsize=pool_maxsize,
        )
        return adapter

    @staticmethod
    def _prepare_http_debug(request, symbol):
        """拼接请求/响应的调试头信息。

        Args:
            request: 请求或响应对象。
            symbol: 行前缀符号（> 表示请求，< 表示响应）。

        Returns:
            格式化的头信息字符串。
        """
        base = ''
        for key, value in request.headers.items():
            base += f'\n{symbol} {key} : {value}'
        return base

    @staticmethod
    def _do_http_debug(request, response):
        """输出请求与响应的 HTTP 调试日志。

        Args:
            request: 请求对象。
            response: 响应对象。
        """
        # logger the request
        url = urlparse(request.url)
        request_base = f'\n> {request.method.upper()} {url.path + url.query} HTTP/1.1'
        logger.debug(request_base + DaraCore._prepare_http_debug(request, '>'))

        # logger the response
        response_base = f'\n< HTTP/1.1 {response.status_code}' \
                        f' {status_codes._codes.get(response.status_code)[0].upper()}'
        logger.debug(response_base + DaraCore._prepare_http_debug(response, '<'))

    @staticmethod
    def compose_url(request):
        """根据请求对象组装完整的请求 URL。

        Args:
            request: DaraRequest 请求对象。

        Returns:
            组装后的完整 URL 字符串。

        Raises:
            RequiredArgumentException: 当缺少 host 请求头时抛出。
        """
        host = request.headers.get('host')
        if not host:
            raise RequiredArgumentException('endpoint')
        else:
            host = host.rstrip('/')
        protocol = f'{request.protocol.lower()}://'
        pathname = request.pathname

        if host.startswith(('http://', 'https://')):
            protocol = ''

        if request.port == 80:
            port = ''
        else:
            port = f':{request.port}'

        url = protocol + host + port + pathname

        if request.query:
            if "?" in url:
                if not url.endswith("&"):
                    url += "&"
            else:
                url += "?"

            encode_query = {}
            for key in request.query:
                value = request.query[key]
                if value is not None:
                    encode_query[key] = str(value)
            url += urlencode(encode_query)
        return url.rstrip("?&")

    @staticmethod
    async def async_do_action(
            request: DaraRequest,
            runtime_option=None
    ) -> DaraResponse:
        """异步执行 HTTP 请求并返回响应。

        支持 TLS 校验、客户端证书、代理、连接池与超时等运行时配置。

        Args:
            request: DaraRequest 请求对象。
            runtime_option: 运行时配置（字典）。

        Returns:
            DaraResponse 响应对象。

        Raises:
            RetryError: 当请求发生 I/O 错误时抛出，交由上层重试。
        """
        runtime_option = runtime_option or {}

        url = DaraCore.compose_url(request)
        ignore_ssl = runtime_option.get('ignoreSSL', False)
        verify: Union[bool, str] = not ignore_ssl
        tls_min_version = runtime_option.get('tlsMinVersion')
        if isinstance(tls_min_version, Enum):
            tls_min_version = tls_min_version.value

        if verify:
            ca = runtime_option.get('ca')
            if ca is not None:
                verify = ca

        cert = runtime_option.get('cert', None)

        timeout = runtime_option.get('timeout')
        connect_timeout = runtime_option.get('connectTimeout') or timeout or DEFAULT_CONNECT_TIMEOUT
        read_timeout = runtime_option.get('readTimeout') or timeout or DEFAULT_READ_TIMEOUT

        connect_timeout, read_timeout = (int(connect_timeout) / 1000, int(read_timeout) / 1000)

        proxy = None
        if request.protocol.upper() == 'HTTP':
            proxy = runtime_option.get('httpProxy')
            if not proxy:
                proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        elif request.protocol.upper() == 'HTTPS':
            proxy = runtime_option.get('httpsProxy')
            if not proxy:
                proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        pool_maxsize = DaraCore._resolve_pool_maxsize(runtime_option)
        connector = None
        ca_cert = certifi.where()
        ssl_context = None
        if isinstance(verify, str) and request.protocol.upper() == 'HTTPS':
            ssl_context = ssl.create_default_context()
            ssl_context = DaraCore._set_tls_minimum_version(ssl_context, tls_min_version)
            ssl_context.load_verify_locations(verify)
            # Handle cert if provided
            if cert is not None:
                if isinstance(cert, (list, tuple)):
                    ssl_context.load_cert_chain(certfile=cert[0], keyfile=cert[1] if len(cert) > 1 else None)
                else:
                    ssl_context.load_cert_chain(certfile=cert, keyfile=None)
            connector = aiohttp.TCPConnector(
                ssl=ssl_context, limit=pool_maxsize, limit_per_host=pool_maxsize
            )
        elif ca_cert and request.protocol.upper() == 'HTTPS' and verify:
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context = DaraCore._set_tls_minimum_version(ssl_context, tls_min_version)
            ssl_context.load_verify_locations(ca_cert)
            # Handle cert if provided
            if cert is not None:
                if isinstance(cert, (list, tuple)):
                    ssl_context.load_cert_chain(certfile=cert[0], keyfile=cert[1] if len(cert) > 1 else None)
                else:
                    ssl_context.load_cert_chain(certfile=cert, keyfile=None)
            connector = aiohttp.TCPConnector(
                ssl=ssl_context, limit=pool_maxsize, limit_per_host=pool_maxsize
            )
        else:
            verify = False
            connector = aiohttp.TCPConnector(limit=pool_maxsize, limit_per_host=pool_maxsize)

        timeout = aiohttp.ClientTimeout(
            sock_read=read_timeout,
            sock_connect=connect_timeout
        )
        async with aiohttp.ClientSession(
                connector=connector
        ) as s:
            body = b''
            if isinstance(request.body, BaseStream):
                for content in request.body:
                    body += content
            elif isinstance(request.body, str):
                body = request.body.encode('utf-8')
            else:
                body = request.body or b''
            try:
                ssl_param: Union[bool, ssl.SSLContext] = ssl_context if ssl_context is not None else bool(verify)
                async with s.request(request.method, url,
                                     data=body,
                                     headers=request.headers,
                                     ssl=ssl_param,
                                     proxy=proxy,
                                     timeout=timeout) as response:
                    tea_resp: DaraResponse = DaraResponse()
                    tea_resp.body = await response.read()
                    tea_resp.headers = dict({k.lower(): v for k, v in response.headers.items()})
                    tea_resp.status_code = response.status
                    tea_resp.status_message = response.reason
                    tea_resp.response = response
            except IOError as e:
                raise RetryError(str(e))
        return tea_resp

    @staticmethod
    def do_action(
            request: DaraRequest,
            runtime_option=None
    ) -> DaraResponse:
        """同步执行 HTTP 请求并返回响应。

        使用 requests.Session 发送请求，支持代理、TLS、调试日志等配置。

        Args:
            request: DaraRequest 请求对象。
            runtime_option: 运行时配置（字典）。

        Returns:
            DaraResponse 响应对象。

        Raises:
            RetryError: 当请求发生 I/O 错误时抛出，交由上层重试。
        """
        url = DaraCore.compose_url(request)

        runtime_option = runtime_option or {}

        verify = not runtime_option.get('ignoreSSL', False)
        tls_min_version = runtime_option.get('tlsMinVersion')
        if isinstance(tls_min_version, Enum):
            tls_min_version = tls_min_version.value

        if verify:
            verify = runtime_option.get('ca', True) if runtime_option.get('ca', True) is not None else True
        cert = runtime_option.get('cert', None)

        timeout = runtime_option.get('timeout')
        connect_timeout = runtime_option.get('connectTimeout') or timeout or DEFAULT_CONNECT_TIMEOUT
        read_timeout = runtime_option.get('readTimeout') or timeout or DEFAULT_READ_TIMEOUT

        timeout = (int(connect_timeout) / 1000, int(read_timeout) / 1000)

        if isinstance(request.body, str):
            request.body = request.body.encode('utf-8')

        p = PreparedRequest()
        p.prepare(
            method=request.method.upper(),
            url=url,
            data=request.body,
            headers=request.headers,
        )

        proxies = {}
        http_proxy = runtime_option.get('httpProxy')
        https_proxy = runtime_option.get('httpsProxy')
        no_proxy = runtime_option.get('noProxy')

        if not http_proxy:
            http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        if not https_proxy:
            https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        if no_proxy:
            proxies['no_proxy'] = no_proxy

        host = request.headers.get('host')
        host = host.rstrip('/')

        pool_maxsize = DaraCore._resolve_pool_maxsize(runtime_option)
        session_key = f'{request.protocol.lower()}://{host}:{request.port}:pool={pool_maxsize}'
        session = DaraCore._get_session(session_key=session_key, protocol=request.protocol,
                                       tls_min_version=tls_min_version, verify=verify,
                                       pool_size=pool_maxsize)
        try:
            resp = session.send(
                p,
                proxies=proxies,
                timeout=timeout,
                verify=verify,
                cert=cert,
            )
        except IOError as e:
            raise RetryError(str(e))

        debug = runtime_option.get('debug') or os.getenv('DEBUG')
        if debug and debug.lower() == 'sdk':
            DaraCore._do_http_debug(p, resp)

        response = DaraResponse()
        response.status_message = resp.reason
        response.status_code = resp.status_code
        response.headers = {k.lower(): v for k, v in resp.headers.items()}
        response.body = resp.content
        response.response = resp
        return response


    @staticmethod
    async def async_do_sse_action(
            request: DaraRequest,
            runtime_option=None
    ) -> DaraResponse:
        """异步执行 SSE 流式请求并返回流式响应。

        返回的响应体为 SSEResponseWrapper，可逐块读取事件流。

        Args:
            request: DaraRequest 请求对象。
            runtime_option: 运行时配置（字典）。

        Returns:
            DaraResponse 响应对象，body 为 SSE 流包装器。

        Raises:
            RetryError: 当请求发生 I/O 错误时抛出。
        """
        runtime_option = runtime_option or {}

        url = DaraCore.compose_url(request)
        ignore_ssl = runtime_option.get('ignoreSSL', False)
        verify: Union[bool, str] = not ignore_ssl
        tls_min_version = runtime_option.get('tlsMinVersion')
        if isinstance(tls_min_version, Enum):
            tls_min_version = tls_min_version.value

        if verify:
            ca = runtime_option.get('ca')
            if ca is not None:
                verify = ca

        cert = runtime_option.get('cert', None)

        timeout = runtime_option.get('timeout')
        connect_timeout = runtime_option.get('connectTimeout') or timeout or DEFAULT_CONNECT_TIMEOUT
        read_timeout = runtime_option.get('readTimeout') or timeout or DEFAULT_READ_TIMEOUT

        connect_timeout, read_timeout = (int(connect_timeout) / 1000, int(read_timeout) / 1000)

        proxy = None
        if request.protocol.upper() == 'HTTP':
            proxy = runtime_option.get('httpProxy')
            if not proxy:
                proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        elif request.protocol.upper() == 'HTTPS':
            proxy = runtime_option.get('httpsProxy')
            if not proxy:
                proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        pool_maxsize = DaraCore._resolve_pool_maxsize(runtime_option)
        connector = None
        ca_cert = certifi.where()
        ssl_context = None
        if isinstance(verify, str) and request.protocol.upper() == 'HTTPS':
            ssl_context = ssl.create_default_context()
            ssl_context = DaraCore._set_tls_minimum_version(ssl_context, tls_min_version)
            ssl_context.load_verify_locations(verify)
            # Handle cert if provided
            if cert is not None:
                if isinstance(cert, (list, tuple)):
                    ssl_context.load_cert_chain(certfile=cert[0], keyfile=cert[1] if len(cert) > 1 else None)
                else:
                    ssl_context.load_cert_chain(certfile=cert, keyfile=None)
            connector = aiohttp.TCPConnector(
                ssl=ssl_context, limit=pool_maxsize, limit_per_host=pool_maxsize
            )
        elif ca_cert and request.protocol.upper() == 'HTTPS' and verify:
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context = DaraCore._set_tls_minimum_version(ssl_context, tls_min_version)
            ssl_context.load_verify_locations(ca_cert)
            # Handle cert if provided
            if cert is not None:
                if isinstance(cert, (list, tuple)):
                    ssl_context.load_cert_chain(certfile=cert[0], keyfile=cert[1] if len(cert) > 1 else None)
                else:
                    ssl_context.load_cert_chain(certfile=cert, keyfile=None)
            connector = aiohttp.TCPConnector(
                ssl=ssl_context, limit=pool_maxsize, limit_per_host=pool_maxsize
            )
        else:
            verify = False
            connector = aiohttp.TCPConnector(limit=pool_maxsize, limit_per_host=pool_maxsize)

        timeout = aiohttp.ClientTimeout(
            sock_read=read_timeout,
            sock_connect=connect_timeout
        )

        session = aiohttp.ClientSession(connector=connector)

        body = b''
        if isinstance(request.body, BaseStream):
            for content in request.body:
                body += content
        elif isinstance(request.body, str):
            body = request.body.encode('utf-8')
        else:
            body = request.body or b''

        try:
            headers = request.headers.copy()
            ssl_param: Union[bool, ssl.SSLContext] = ssl_context if ssl_context is not None else bool(verify)
            response = await session.request(
                request.method,
                url,
                data=body,
                headers=headers,
                ssl=ssl_param,
                proxy=proxy,
                timeout=timeout
            )
            tea_resp: DaraResponse = DaraResponse()
            tea_resp.status_code = response.status
            tea_resp.status_message = response.reason
            tea_resp.headers = dict({k.lower(): v for k, v in response.headers.items()})
            tea_resp.body = SSEResponseWrapper(session, response)
            return tea_resp

        except IOError as e:
            await session.close()
            raise RetryError(str(e))

    @staticmethod
    def do_sse_action(
            request: DaraRequest,
            runtime_option=None
    ) -> DaraResponse:
        """同步执行 SSE 流式请求并返回流式响应。

        返回的响应体为 SyncSSEResponseWrapper，可同步逐块读取事件流。

        Args:
            request: DaraRequest 请求对象。
            runtime_option: 运行时配置（字典）。

        Returns:
            DaraResponse 响应对象，body 为 SSE 流包装器。

        Raises:
            RetryError: 当请求发生 I/O 错误时抛出。
        """
        url = DaraCore.compose_url(request)

        runtime_option = runtime_option or {}

        verify = not runtime_option.get('ignoreSSL', False)
        tls_min_version = runtime_option.get('tlsMinVersion')
        if isinstance(tls_min_version, Enum):
            tls_min_version = tls_min_version.value

        if verify:
            verify = runtime_option.get('ca', True) if runtime_option.get('ca', True) is not None else True
        cert = runtime_option.get('cert', None)

        timeout = runtime_option.get('timeout')
        connect_timeout = runtime_option.get('connectTimeout') or timeout or DEFAULT_CONNECT_TIMEOUT
        read_timeout = runtime_option.get('readTimeout') or timeout or DEFAULT_READ_TIMEOUT

        timeout = (int(connect_timeout) / 1000, int(read_timeout) / 1000)

        if isinstance(request.body, str):
            request.body = request.body.encode('utf-8')

        p = PreparedRequest()
        p.prepare(
            method=request.method.upper(),
            url=url,
            data=request.body,
            headers=request.headers,
        )

        proxies = {}
        http_proxy = runtime_option.get('httpProxy')
        https_proxy = runtime_option.get('httpsProxy')
        no_proxy = runtime_option.get('noProxy')

        if not http_proxy:
            http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        if not https_proxy:
            https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        if no_proxy:
            proxies['no_proxy'] = no_proxy

        host = request.headers.get('host')
        host = host.rstrip('/') if host else ''

        pool_maxsize = DaraCore._resolve_pool_maxsize(runtime_option)
        session_key = f'{request.protocol.lower()}://{host}:{request.port}:pool={pool_maxsize}'
        session = DaraCore._get_session(session_key=session_key, protocol=request.protocol,
                                    tls_min_version=tls_min_version, verify=verify,
                                    pool_size=pool_maxsize)
        try:
            resp = session.send(
                p,
                proxies=proxies,
                timeout=timeout,
                verify=verify,
                cert=cert,
                stream=True
            )
        except IOError as e:
            raise RetryError(str(e))

        debug = runtime_option.get('debug') or os.getenv('DEBUG')
        if debug and debug.lower() == 'sdk':
            DaraCore._do_http_debug(p, resp)

        response = DaraResponse()
        response.status_message = resp.reason
        response.status_code = resp.status_code
        response.headers = {k.lower(): v for k, v in resp.headers.items()}
        response.body = SyncSSEResponseWrapper(session, resp)

        return response
    @staticmethod
    def get_response_body(resp) -> str:
        """返回响应的文本内容（UTF-8 解码）。

        Args:
            resp: 响应对象。

        Returns:
            响应体字符串。
        """
        return resp.content.decode("utf-8")

    @staticmethod
    def allow_retry(dic, retry_times, now=None) -> bool:
        """判断当前是否允许继续重试。

        Args:
            dic: 重试配置字典（含 maxAttempts、retryable 字段）。
            retry_times: 已重试次数。
            now: 当前时间（预留）。

        Returns:
            允许重试返回 True。
        """
        if retry_times == 0:
            return True
        if dic is None or not dic.__contains__("maxAttempts") or \
                dic.get('retryable') is not True and retry_times >= 1:
            return False
        else:
            retry = 0 if dic.get("maxAttempts") is None else int(
                dic.get("maxAttempts"))
        return retry >= retry_times

    @staticmethod
    def should_retry(options: RetryOptions, ctx: RetryPolicyContext) -> bool:
        """根据重试策略判断当前请求是否应当重试。

        Args:
            options: 重试配置。
            ctx: 重试策略上下文。

        Returns:
            应当重试返回 True。
        """
        if ctx.retries_attempted == 0:
            return True

        if not options or not options.retryable:
            return False

        retries_attempted = ctx.retries_attempted
        ex = ctx.exception

        for condition in options.no_retry_condition:
            if getattr(ex, 'name', None) in condition.exception or getattr(ex, 'code', None) in condition.error_code:
                return False

        for condition in options.retry_condition:
            if getattr(ex, 'name', None) not in condition.exception and getattr(ex, 'code', None) not in condition.error_code:
                continue

            if retries_attempted >= condition.max_attempts:
                return False
            return True

        return False

    @staticmethod
    def get_backoff_time(options: RetryOptions, ctx: RetryPolicyContext) -> int:
        """计算下一次重试的退避等待时间（毫秒）。

        优先使用响应中的 retry_after，其次按策略的退避算法计算。

        Args:
            options: 重试配置。
            ctx: 重试策略上下文。

        Returns:
            退避等待毫秒数。
        """
        ex = ctx.exception
        conditions = options.retry_condition
        for condition in conditions:
            if getattr(ex, 'name', None) not in condition.exception and getattr(ex, 'code', None) not in condition.error_code:
                continue
            max_delay = condition.max_delay or MAX_DELAY_TIME
            retry_after = getattr(ctx.exception, "retry_after", None)
            if retry_after is not None:
                return min(retry_after, max_delay)
            if not condition.backoff:
                return MIN_DELAY_TIME
            return min(condition.backoff.get_delay_time(ctx), max_delay)
        return MIN_DELAY_TIME

    @staticmethod
    async def sleep_async(millisecond: int):
        """异步休眠指定毫秒数。"""
        await asyncio.sleep(millisecond / 1000)

    @staticmethod
    def sleep(millisecond: int):
        """同步休眠指定毫秒数。"""
        time.sleep(millisecond / 1000)

    @staticmethod
    def is_retryable(ex) -> bool:
        """判断异常是否为可重试错误（RetryError）。

        Args:
            ex: 异常对象。

        Returns:
            可重试返回 True。
        """
        return isinstance(ex, RetryError)

    @staticmethod
    def bytes_readable(body):
        """返回可读的字节数据（原样返回）。"""
        return body

    @staticmethod
    def merge(*dic_list) -> dict:
        """合并多个字典或 DaraModel 为一个字典。

        Args:
            *dic_list: 待合并的字典或 DaraModel 对象。

        Returns:
            合并后的字典。
        """
        dic_result = {}
        for item in dic_list:
            if isinstance(item, dict):
                dic_result.update(item)
            elif isinstance(item, DaraModel):
                dic_result.update(item.to_map())
        return dic_result

    @staticmethod
    def is_null(value) -> bool:
        """判断值是否为 None。

        Args:
            value: 待判断的值。

        Returns:
            为 None 返回 True。
        """
        return value is None

    @staticmethod
    def to_readable_stream(data):
        """将字符串或字节数据转换为可读的 IO 流。

        Args:
            data: 字符串或字节数据。

        Returns:
            StringIO 或 BytesIO 对象。

        Raises:
            TypeError: 当输入类型不是 str 或 bytes 时抛出。
        """
        if isinstance(data, str):
            return io.StringIO(data)
        elif isinstance(data, bytes):
            return io.BytesIO(data)
        else:
            raise TypeError("Input data must be of type str or bytes")

    @staticmethod
    def to_map(model: Optional[DaraModel]) -> Dict[str, Any]:
        """将 DaraModel 模型转换为字典。

        Args:
            model: 数据模型对象。

        Returns:
            转换后的字典；非 DaraModel 返回空字典。
        """
        if isinstance(model, DaraModel):
            return model.to_map()
        else:
            return dict()

    @staticmethod
    def to_number(model) -> int:
        """将各种类型值转换为整数。

        Args:
            model: 待转换的值（int、str、float 等）。

        Returns:
            转换后的整数；无法转换时返回 0。
        """
        if isinstance(model, int):
            return model
        if isinstance(model, str):
            if model == "":
                return 0
            return int(model)
        if isinstance(model, float):
            return int(model)
        return 0

    @staticmethod
    def from_map(
            model: DaraModel,
            dic: Dict[str, Any]
    ) -> DaraModel:
        """从字典填充 DaraModel 模型。

        反序列化失败时，将字典直接写入模型的 _map 属性。

        Args:
            model: 数据模型对象。
            dic: 待填充的字典。

        Returns:
            填充后的模型对象。
        """
        if isinstance(model, DaraModel):
            try:
                return model.from_map(dic)
            except Exception:
                model._map = dic
                return model
        else:
            return model

    @staticmethod
    def _get_session(session_key: str, protocol: str, tls_min_version: str = None,
                     verify: bool = True, pool_size: int = None):
        """按会话键获取（或创建）请求 Session，并挂载对应的 TLS 适配器。

        Args:
            session_key: 会话缓存键。
            protocol: 协议（http / https）。
            tls_min_version: 最低 TLS 版本。
            verify: 是否校验 SSL。
            pool_size: 连接池大小。

        Returns:
            请求 Session 对象。
        """
        if session_key not in DaraCore._sessions:
            session = Session()
            adapter = DaraCore.get_adapter(protocol, tls_min_version, pool_size=pool_size)
            if protocol.upper() == 'HTTPS':
                if verify:
                    session.mount('https://', adapter)
                else:
                    # Honor configured pool size even when SSL verify is disabled.
                    insecure_adapter = adapters.HTTPAdapter(
                        pool_connections=DEFAULT_POOL_SIZE,
                        pool_maxsize=pool_size if pool_size is not None and pool_size > 0 else DEFAULT_POOL_MAXSIZE,
                    )
                    session.mount('https://', insecure_adapter)
            else:
                session.mount('http://', adapter)
            DaraCore._sessions[session_key] = session
        return DaraCore._sessions[session_key]

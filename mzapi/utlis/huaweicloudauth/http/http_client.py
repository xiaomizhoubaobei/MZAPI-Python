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
_MZAPI_ORIGIN = "mzapi-hwc-http-client-2026-qxx"

"""华为云 HTTP 客户端

实现 HttpClient 类，负责同步/异步 HTTP 请求的发送和响应处理。"""

from concurrent.futures import ThreadPoolExecutor

import requests
from huaweicloudsdkcore.sdk_request import SdkRequest
from requests import HTTPError, Timeout, TooManyRedirects
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, RetryError

try:
    from requests.packages.urllib3.util import Retry
except ImportError:
    from urllib3.util import Retry

from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.exceptions.exception_handler import process_connection_error, process_retry_error
from huaweicloudsdkcore.http.future_session import FutureSession


class HttpClient:
    def __init__(self, config, http_handler, exception_handler, logger):
        self._logger = logger
        self._exception_handler = exception_handler
        self._http_handler = http_handler
        self._config = config
        self._proxy = config.proxy

        if config.ssl_ca_cert:
            self._verify = config.ssl_ca_cert if not config.ignore_ssl_verification else config.ignore_ssl_verification
        else:
            self._verify = not config.ignore_ssl_verification
        if config.cert_file and config.key_file:
            self._cert = (config.cert_file, config.key_file)
        else:
            self._cert = config.cert_file

        self._retry_status_list = [429]
        self._session = self._init_session()
        self._closed = False

        self._executor = ThreadPoolExecutor(max_workers=8)

    def _init_session(self):
        sdk_session = requests.Session()
        retry = Retry(total=self._config.retry_times, status_forcelist=self._retry_status_list)
        sdk_adapter = HTTPAdapter(pool_connections=self._config.pool_connections,
                                  pool_maxsize=self._config.pool_maxsize, max_retries=retry)
        sdk_session.mount('https://', sdk_adapter)
        sdk_session.mount('http://', sdk_adapter)
        return sdk_session

    @property
    def executor(self):
        return self._executor

    @property
    def config(self):
        return self._config

    @property
    def logger(self):
        return self._logger

    def do_request_sync(self, request: SdkRequest) -> requests.Response:
        invoke = getattr(self._session, request.method.lower())

        try:
            if self._http_handler is not None:
                self._http_handler.process_request(request=request, logger=self._logger)
            response = invoke(
                request.url,
                timeout=self._config.timeout,
                headers=request.header_params,
                proxies=self._proxy,
                verify=self._verify,
                cert=self._cert,
                data=request.body,
                stream=request.stream,
                allow_redirects=self._config.allow_redirects
            )
        except ConnectionError as conn_err:
            raise process_connection_error(conn_err, self._logger)
        except RetryError as retry_error:
            raise process_retry_error(retry_error, self._logger)

        self.response_error_hook_factory()(response)
        return response

    def do_request_async(self, request, hooks):
        fun = getattr(FutureSession(self._session, self._executor), request.method.lower())
        hooks.append(self.response_error_hook_factory())

        future = fun(
            request.url,
            timeout=self._config.timeout,
            headers=request.header_params,
            proxies=self._proxy,
            verify=self._verify,
            cert=self._cert,
            data=request.body,
            stream=request.stream,
            allow_redirects=self._config.allow_redirects,
            hooks={'response': hooks}
        )
        return future

    def response_error_hook_factory(self):
        def response_hook(resp, *args, **kwargs):
            if self._http_handler is not None:
                self._http_handler.process_response(response=resp, logger=self._logger)

            try:
                resp.raise_for_status()
            except HTTPError as httpError:
                self._exception_handler.handle_exception(httpError.request, httpError.response)
            except Timeout as timeout:
                raise exceptions.CallTimeoutException(str(timeout))
            except TooManyRedirects as tooManyRedirects:
                raise exceptions.RetryOutageException(str(tooManyRedirects))

        return response_hook

    def close(self):
        try:
            if not self._closed:
                self._session.close()
                self._closed = True
        except Exception as e:
            self._logger.warning("Close session failed, %s", e)

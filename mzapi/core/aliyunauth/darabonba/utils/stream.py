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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-stream-2026-qxx"


"""
流式处理工具模块

提供可读 / 可写流抽象、响应包装与 SSE（Server-Sent Events）事件流解析能力，
同时支持同步与异步（aiohttp）两种模式，用于处理流式数据读取与逐事件解析。

包含的类：
  - BaseStream：流基类，定义 read / __len__ / __next__ / __iter__ 抽象接口
  - _ReadableMc：可读性判断的元类
  - READABLE：可读流标记类，用于 isinstance 判断
  - SyncSSEResponseWrapper：同步 SSE 响应包装器
  - SSEResponseWrapper：异步 SSE 响应包装器（基于 aiohttp）
  - _WriteableMc：可写性判断的元类
  - WRITABLE：可写流标记类，用于 isinstance 判断
  - Stream：流工具类，提供字节 / 字符串 / JSON / SSE 的读取与解析
"""

import json
import re
import aiohttp
import codecs
from mzapi.utlis.aliyunauth.darabonba.event import Event

from io import BytesIO, StringIO
from typing import Any, BinaryIO, Generator, AsyncGenerator, Dict

# define WRITEABLE
sse_line_pattern = re.compile('(?P<name>[^:]*):?( ?(?P<value>.*))?')

class BaseStream:
    """流基类，定义可读流需要实现的抽象接口。"""

    def __init__(self, size=1024):
        """初始化流基类。

        Args:
            size: 默认读取缓冲区大小。
        """
        self.size = size

    def read(self, size=1024):
        """读取指定大小的数据（需子类实现）。

        Args:
            size: 读取的字节数。

        Raises:
            NotImplementedError: 子类未实现时抛出。
        """
        raise NotImplementedError('read method must be overridden')

    def __len__(self):
        """返回流的长度（需子类实现）。

        Raises:
            NotImplementedError: 子类未实现时抛出。
        """
        raise NotImplementedError('__len__ method must be overridden')

    def __next__(self):
        """返回下一个数据分片（需子类实现）。

        Raises:
            NotImplementedError: 子类未实现时抛出。
        """
        raise NotImplementedError('__next__ method must be overridden')

    def __iter__(self):
        """返回迭代器自身，支持迭代读取。"""
        return self


class _ReadableMc(type):
    """可读流判断元类，通过实例属性判断是否可读。"""

    def __instancecheck__(self, instance):
        """判断实例是否为可读流（具备 read 与 __iter__ 方法）。"""
        if hasattr(instance, 'read') and hasattr(instance, '__iter__'):
            return True


class READABLE(metaclass=_ReadableMc):
    """可读流标记类，用于 isinstance 判断。"""


class SyncSSEResponseWrapper:
    """同步 SSE 响应包装器，封装 requests 会话与响应，支持分块迭代读取。"""

    def __init__(self, session, response):
        """初始化同步响应包装器。

        Args:
            session: requests 会话对象。
            response: requests 响应对象。
        """
        self.session = session
        self.response = response
        self._closed = False

    def close(self):
        """关闭响应与会话，释放资源。"""
        if not self._closed:
            self.response.close()
            self.session.close()
            self._closed = True

    def __iter__(self):
        """返回分块迭代器，按块读取响应内容。"""
        return self._read_chunks()

    def _read_chunks(self):
        """按 8192 字节分块读取响应内容，并在结束后关闭。"""
        try:
            for chunk in self.response.iter_content(chunk_size=8192):
                yield chunk
        finally:
            self.close()

    def read(self) -> bytes:
        """一次性读取完整响应内容，并在读取后关闭。"""
        try:
            return self.response.content
        finally:
            self.close()

class SSEResponseWrapper:
    """异步 SSE 响应包装器，封装 aiohttp 会话与响应，支持异步分块迭代读取。"""

    def __init__(self, session: aiohttp.ClientSession, response: aiohttp.ClientResponse):
        """初始化异步响应包装器。

        Args:
            session: aiohttp 客户端会话对象。
            response: aiohttp 客户端响应对象。
        """
        self.session = session
        self.response = response
        self._closed = False
        self._content_cache = None

    async def close(self):
        """异步关闭响应与会话，释放资源。"""
        if not self._closed:
            self.response.close()
            await self.session.close()
            self._closed = True

    def __aiter__(self):
        """返回异步分块迭代器，支持 async for 读取。"""
        return self._read_chunks()

    async def _read_chunks(self):
        """按 8192 字节异步分块读取响应内容，并在结束后关闭。"""
        try:
            async for chunk in self.response.content.iter_chunked(8192):
                yield chunk
        finally:
            await self.close()

    async def read(self) -> bytes:
        """异步一次性读取完整响应内容（带缓存），并在读取后关闭。

        Returns:
            响应内容的字节数据。
        """
        if self._content_cache is not None:
            return self._content_cache

        try:
            content = await self.response.read()
            self._content_cache = content
            return content
        finally:
            await self.close()

class _WriteableMc(type):
    """可写流判断元类，通过实例属性判断是否可写。"""

    def __instancecheck__(self, instance):
        """判断实例是否为可写流（具备 write 方法）。"""
        if hasattr(instance, 'write'):
            return True


class WRITABLE(metaclass=_WriteableMc):
    """可写流标记类，用于 isinstance 判断。"""


STREAM_CLASS = (READABLE, WRITABLE)


class Stream:
    """流工具类，提供字节 / 字符串 / JSON / SSE 的读取与解析能力。

    支持可读流、可写流的转换，以及同步 / 异步两种模式下的数据读取。
    """

    def __init__(self, data=None):
        """初始化 Stream 实例。

        Args:
            data: 初始数据，可为字节或字符串，默认为空字节。
        """
        self.data = data if data is not None else b''
        self.position = 0

    @staticmethod
    def __read_part(f, size=1024):
        """按分片读取可读流，直到读取完毕。

        Args:
            f: 可读流对象。
            size: 每次读取的字节数。

        Yields:
            每次读取到的字节分片。
        """
        while True:
            part = f.read(size)
            if part:
                yield part
            else:
                return

    @staticmethod
    def __to_string(
        val: bytes,
    ) -> str:
        """
        Convert a bytes to string(utf8)
        @return: the return string
        """
        if isinstance(val, str):
            return val
        elif isinstance(val, bytes):
            return val.decode('utf-8')
        else:
            return str(val)

    @staticmethod
    def __parse_json(
        val: str,
    ) -> Any:
        """
        Parse it by JSON format
        @return: the parsed result
        """
        try:
            return json.loads(val)
        except ValueError:
            raise RuntimeError(f'Failed to parse the value as json format, Value: "{val}".')

    @staticmethod
    def read_as_bytes(stream) -> bytes:
        """
        Read data from a readable stream, and compose it to a bytes
        @param stream: the readable stream
        @return: the bytes result
        """
        if isinstance(stream, SyncSSEResponseWrapper):
            return stream.read()
        elif isinstance(stream, READABLE):
            b = b''
            for part in Stream.__read_part(stream, 1024):
                b += part
            return b
        elif isinstance(stream, bytes):
            return stream
        else:
            return bytes(stream, encoding='utf-8')
    
    @staticmethod
    async def read_as_bytes_async(stream) -> bytes:
        """
        Read data from a readable stream, and compose it to a bytes
        @param stream: the readable stream
        @return: the bytes result
        """
        if isinstance(stream, bytes):
            return stream
        elif isinstance(stream, str):
            return bytes(stream, encoding='utf-8')
        else:
            return await stream.read()
    
    @staticmethod
    def read_as_json(stream) -> Any:
        """
        Read data from a readable stream, and parse it by JSON format
        @param stream: the readable stream
        @return: the parsed result
        """
        return Stream.__parse_json(Stream.read_as_string(stream))

    @staticmethod
    async def read_as_json_async(stream) -> Any:
        """
        Read data from a readable stream, and parse it by JSON format
        @param stream: the readable stream
        @return: the parsed result
        """
        return Stream.__parse_json(
            await Stream.read_as_string_async(stream)
        )


    @staticmethod
    def read_as_string(stream) -> str:
        """
        Read data from a readable stream, and compose it to a string
        @param stream: the readable stream
        @return: the string result
        """
        buff = Stream.read_as_bytes(stream)
        return Stream.__to_string(buff)
    
    @staticmethod
    async def read_as_string_async(stream) -> str:
        """
        Read data from a readable stream, and compose it to a string
        @param stream: the readable stream
        @return: the string result
        """
        buff = await Stream.read_as_bytes_async(stream)
        return Stream.__to_string(buff)
    
    @staticmethod
    def read_as_sse(stream) -> Generator[Event, None, None]:
        """
        Read events from SSE stream (synchronous version)
        """
        if isinstance(stream, SyncSSEResponseWrapper):
            for event in Stream._parse_sse_stream_sync(stream):
                yield Event(
                    id=event.get('id'),
                    data=event.get('data'),
                    event=event.get('event'),
                    retry=event.get('retry'))
        elif hasattr(stream, 'iter_content'):
            # Read directly from the content stream of requests response object
            for event in Stream._parse_sse_stream_from_response_sync(stream):
                yield Event(
                    id=event.get('id'),
                    data=event.get('data'),
                    event=event.get('event'),
                    retry=event.get('retry'))
        else:
            for event in Stream._parse_sse_stream_sync(stream):
                yield Event(
                    id=event.get('id'),
                    data=event.get('data'),
                    event=event.get('event'),
                    retry=event.get('retry'))

    @staticmethod
    async def read_as_sse_async(stream) -> AsyncGenerator[Event, None]:
        """
        Read events from SSE stream
        """
        if isinstance(stream, SSEResponseWrapper):
            async for event in Stream._parse_sse_stream(stream):
                yield Event(
                    id = event.get('id'),
                    data = event.get('data'),
                    event= event.get('event'),
                    retry = event.get('retry'))
        elif hasattr(stream, 'content'):
            # Read directly from the content stream of aiohttp response object
            async for event in Stream._parse_sse_stream_from_response(stream):
                yield Event(
                    id = event.get('id'),
                    data = event.get('data'),
                    event= event.get('event'),
                    retry = event.get('retry'))
        else:
            async for event in Stream._parse_sse_stream(stream):
                yield Event(
                    id = event.get('id'),
                    data = event.get('data'),
                    event= event.get('event'),
                    retry = event.get('retry'))

    def read(self, size=None):
        """从当前流中读取数据，支持指定大小读取。

        Args:
            size: 读取的字节数，None 表示读取全部剩余数据。

        Returns:
            读取到的字节数据。
        """
        if size is None:
            return self.data[self.position:]

        start = self.position
        end = min(start + size, len(self.data))
        self.position = end
        return self.data[start:end]

    def write(self, data):
        """将数据写入当前流，覆盖原有内容。

        Args:
            data: 待写入的数据，须为字节或字符串。

        Raises:
            TypeError: 当数据类型不受支持时抛出。
        """
        if isinstance(data, (bytes, str)):
            self.data = data
        else:
            raise TypeError("Data should be bytes or string.")

    def pipe(self, output_stream, buffer_size=1024):
        """将当前流的数据逐块写入目标输出流。

        Args:
            output_stream: 目标 Stream 实例。
            buffer_size: 每块传输的字节数。

        Raises:
            TypeError: 当目标输出流不是 Stream 实例时抛出。
        """
        if not isinstance(output_stream, Stream):
            raise TypeError("Output stream should be an instance of Stream.")

        while True:
            chunk = self.read(buffer_size)
            if not chunk:
                break
            output_stream.write(chunk)
    
    @staticmethod
    def to_readable(
        value: Any,
    ) -> BinaryIO:
        """
        Assert a value, if it is a readable, return it, otherwise throws
        @return: the readable value
        """
        if isinstance(value, str):
            value = value.encode('utf-8')

        if isinstance(value, bytes):
            value = BytesIO(value)
        elif not isinstance(value, READABLE):
            raise ValueError(f'The value is not a readable')
        return value

    @staticmethod
    def to_writeable(
        value: Any,
    ) -> WRITABLE:
        """
        Assert a value, if it is a writeable, return it, otherwise throws
        @return: the writeable value
        """
        if isinstance(value, str):
            value = StringIO(value)

        elif isinstance(value, bytes):
            value = BytesIO(value)
        elif not isinstance(value, WRITABLE):
            raise ValueError(f'The value is not a writeable')
        return value
    
    @staticmethod
    async def _parse_sse_stream(wrapper: SSEResponseWrapper) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Analyze SSE stream data
        """
        buffer = ""
        current_event = Event()
        
        MAX_BUFFER_SIZE = 1024 * 1024  # 1MB
        dec = codecs.getincrementaldecoder('utf-8')()
        
        async for chunk in wrapper:
            try:
                chunk_str = dec.decode(chunk)
            except UnicodeDecodeError:
                chunk_str = chunk.decode('utf-8', errors='replace')
            
            if len(buffer) + len(chunk_str) > MAX_BUFFER_SIZE:
                import logging
                logging.warning("SSE stream data too large, skipping chunk")
                continue
                
            buffer += chunk_str

            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.rstrip('\r')  # Remove \r
                
                if not line.strip():
                    if current_event.data is not None:
                        yield {
                            'id': current_event.id,
                            'event': current_event.event or 'message',
                            'data': current_event.data,
                            'retry': current_event.retry
                        }
                        current_event = Event()
                    continue
                
                if line.startswith(':'):
                    continue
                
                if ':' in line:
                    match = sse_line_pattern.match(line)
                    if match:
                        name = match.group('name').strip()
                        value = match.group('value').strip()
                        
                        if name == 'event':
                            current_event.event = value
                        elif name == 'id':
                            current_event.id = value
                        elif name == 'data':
                            if current_event.data is None:
                                current_event.data = value
                            else:
                                current_event.data += '\n' + value
                        elif name == 'retry':
                            try:
                                current_event.retry = int(value)
                            except ValueError:
                                pass
                else:
                    if current_event.data is None:
                        current_event.data = line
                    else:
                        current_event.data += '\n' + line

        if buffer.strip() and current_event.data is not None:
            yield {
                'id': current_event.id,
                'event': current_event.event or 'message',
                'data': current_event.data,
                'retry': current_event.retry
            }

    @staticmethod
    async def _parse_sse_stream_from_response(response) -> AsyncGenerator[Dict[str, Any], None]:
        """从 aiohttp 响应对象中异步解析 SSE 事件流。

        Args:
            response: aiohttp 响应对象，需具备 content 属性。

        Yields:
            解析出的 SSE 事件字典（含 id、event、data、retry 字段）。
        """
        buffer = ""
        current_event = Event()

        async for chunk in response.content.iter_chunked(8192):
            try:
                chunk_str = chunk.decode('utf-8')
            except UnicodeDecodeError:
                continue
            
            buffer += chunk_str
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.rstrip('\r')
                
                if not line.strip():
                    if current_event.data is not None:
                        yield {
                            'id': current_event.id,
                            'event': current_event.event or 'message',
                            'data': current_event.data,
                            'retry': current_event.retry
                        }
                        current_event = Event()
                    continue
                
                if line.startswith(':'):
                    continue
                
                if ':' in line:
                    match = sse_line_pattern.match(line)
                    if match:
                        name = match.group('name').strip()
                        value = match.group('value').strip()
                        
                        if name == 'event':
                            current_event.event = value
                        elif name == 'id':
                            current_event.id = value
                        elif name == 'data':
                            if current_event.data is None:
                                current_event.data = value
                            else:
                                current_event.data += '\n' + value
                        elif name == 'retry':
                            try:
                                current_event.retry = int(value)
                            except ValueError:
                                pass
                else:
                    if current_event.data is None:
                        current_event.data = line
                    else:
                        current_event.data += '\n' + line

        if buffer.strip() and current_event.data is not None:
            yield {
                'id': current_event.id,
                'event': current_event.event or 'message',
                'data': current_event.data,
                'retry': current_event.retry
            }
    
    @staticmethod
    def _parse_sse_stream_sync(wrapper: SyncSSEResponseWrapper) -> Generator[Dict[str, Any], None, None]:
        """
        Analyze SSE stream data (synchronous version)
        """
        buffer = ""
        current_event = Event()

        for chunk in wrapper:
            # Decoding byte data into strings
            try:
                chunk_str = chunk.decode('utf-8')
            except UnicodeDecodeError:
                # If decoding fails, skip this chunk
                continue
            
            buffer += chunk_str
            
            # Split processing by row
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.rstrip('\r')  # Remove \r
                
                if not line.strip():
                    if current_event.data is not None:
                        yield {
                            'id': current_event.id,
                            'event': current_event.event or 'message',
                            'data': current_event.data,
                            'retry': current_event.retry
                        }
                        current_event = Event()
                    continue
                
                # Skip comment lines
                if line.startswith(':'):
                    continue
                
                if ':' in line:
                    match = sse_line_pattern.match(line)
                    if match:
                        name = match.group('name').strip()
                        value = match.group('value').strip()
                        
                        if name == 'event':
                            current_event.event = value
                        elif name == 'id':
                            current_event.id = value
                        elif name == 'data':
                            if current_event.data is None:
                                current_event.data = value
                            else:
                                current_event.data += '\n' + value
                        elif name == 'retry':
                            try:
                                current_event.retry = int(value)
                            except ValueError:
                                pass
                else:
                    if current_event.data is None:
                        current_event.data = line
                    else:
                        current_event.data += '\n' + line

        if buffer.strip() and current_event.data is not None:
            yield {
                'id': current_event.id,
                'event': current_event.event or 'message',
                'data': current_event.data,
                'retry': current_event.retry
            }

    @staticmethod
    def _parse_sse_stream_from_response_sync(response) -> Generator[Dict[str, Any], None, None]:
        """
        Parse SSE stream from requests response object (synchronous version)
        """
        buffer = ""
        current_event = Event()

        for chunk in response.iter_content(chunk_size=8192):
            try:
                chunk_str = chunk.decode('utf-8')
            except UnicodeDecodeError:
                continue
            
            buffer += chunk_str
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.rstrip('\r')
                
                if not line.strip():
                    if current_event.data is not None:
                        yield {
                            'id': current_event.id,
                            'event': current_event.event or 'message',
                            'data': current_event.data,
                            'retry': current_event.retry
                        }
                        current_event = Event()
                    continue
                
                if line.startswith(':'):
                    continue
                
                if ':' in line:
                    match = sse_line_pattern.match(line)
                    if match:
                        name = match.group('name').strip()
                        value = match.group('value').strip()
                        
                        if name == 'event':
                            current_event.event = value
                        elif name == 'id':
                            current_event.id = value
                        elif name == 'data':
                            if current_event.data is None:
                                current_event.data = value
                            else:
                                current_event.data += '\n' + value
                        elif name == 'retry':
                            try:
                                current_event.retry = int(value)
                            except ValueError:
                                pass
                else:
                    if current_event.data is None:
                        current_event.data = line
                    else:
                        current_event.data += '\n' + line

        if buffer.strip() and current_event.data is not None:
            yield {
                'id': current_event.id,
                'event': current_event.event or 'message',
                'data': current_event.data,
                'retry': current_event.retry
            }
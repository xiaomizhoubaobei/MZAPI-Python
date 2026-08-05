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
_MZAPI_ORIGIN = "mzapi-aliyun-tea-util-client-2026-qxx"


"""
阿里云 Tea 工具包客户端工具模块

提供阿里云 Tea 工具包所需的通用工具能力，涵盖
字节/字符串/JSON 互转、可读流同步/异步读取、nonce 生成、
表单序列化、类型断言与 HTTP 状态码判断等静态方法。

包含的类：
  - Client：Tea 工具包工具类，提供全静态工具方法。
"""

import json
import platform
import time
import Tea
import asyncio
import threading
import random
import hashlib

from email.utils import formatdate
from urllib.parse import urlencode
from io import BytesIO

from Tea.model import TeaModel
from Tea.stream import READABLE
from typing import Any, BinaryIO, Dict, List

_process_start_time = int(time.time() * 1000)
_seqId = 0


class Client:
    """阿里云 Tea 工具包工具类。

    以静态方法提供数据转换、流式读取、签名辅助、类型断言
    与 HTTP 状态判断等通用能力，供上层阿里云认证模块调用。
    """

    class __ModelEncoder(json.JSONEncoder):
        """JSON 编码器，将 TeaModel 序列化为字典、bytes 解码为字符串。"""

        def default(self, o: Any) -> Any:
            if isinstance(o, TeaModel):
                return o.to_map()
            elif isinstance(o, bytes):
                return o.decode('utf-8')
            super().default(o)

    @staticmethod
    def __read_part(f, size=1024):
        """分块读取流对象。

        Args:
            f: 可读的文件对象。
            size: 每次读取的字节数，默认 1024。

        Yields:
            每次读取到的字节块。
        """
        while True:
            part = f.read(size)
            if part:
                yield part
            else:
                return

    @staticmethod
    def __get_default_agent():
        """生成默认的 User-Agent 字符串，包含平台、机器架构与运行库版本信息。"""
        return f'AlibabaCloud ({platform.system()}; {platform.machine()}) ' \
               f'Python/{platform.python_version()} Core/{Tea.__version__} TeaDSL/1'

    @staticmethod
    def to_bytes(
        val: str,
    ) -> bytes:
        """将字符串（UTF-8）转换为字节对象。

        Args:
            val: 待转换的值，可为 bytes、str 或其他对象。

        Returns:
            转换后的字节对象。
        """
        if isinstance(val, bytes):
            return val
        elif isinstance(val, str):
            return val.encode(encoding="utf-8")
        else:
            return str(val).encode(encoding="utf-8")

    @staticmethod
    def to_string(
        val: bytes,
    ) -> str:
        """将字节对象转换为字符串（UTF-8）。

        Args:
            val: 待转换的值，可为 str、bytes 或其他对象。

        Returns:
            转换后的字符串。
        """
        if isinstance(val, str):
            return val
        elif isinstance(val, bytes):
            return val.decode('utf-8')
        else:
            return str(val)

    @staticmethod
    def parse_json(
        val: str,
    ) -> Any:
        """按 JSON 格式解析字符串。

        Args:
            val: 待解析的 JSON 字符串。

        Returns:
            解析后的结果。

        Raises:
            RuntimeError: 当字符串无法按 JSON 格式解析时抛出。
        """
        try:
            return json.loads(val)
        except ValueError:
            raise RuntimeError(f'Failed to parse the value as json format, Value: "{val}".')

    @staticmethod
    async def read_as_bytes_async(stream) -> bytes:
        """异步从可读流中读取数据并拼接为字节对象。

        Args:
            stream: 可读流。

        Returns:
            读取到的字节结果。
        """
        if isinstance(stream, bytes):
            return stream
        elif isinstance(stream, str):
            return bytes(stream, encoding='utf-8')
        else:
            return await stream.read()

    @staticmethod
    async def read_as_string_async(stream) -> str:
        """异步从可读流中读取数据并转换为字符串。

        Args:
            stream: 可读流。

        Returns:
            读取到的字符串结果。
        """
        buff = await Client.read_as_bytes_async(stream)
        return Client.to_string(buff)

    @staticmethod
    async def read_as_json_async(stream) -> Any:
        """异步从可读流中读取数据并按 JSON 格式解析。

        Args:
            stream: 可读流。

        Returns:
            解析后的结果。
        """
        return Client.parse_json(
            await Client.read_as_string_async(stream)
        )

    @staticmethod
    def read_as_bytes(stream) -> bytes:
        """从可读流中同步读取数据并拼接为字节对象。

        Args:
            stream: 可读流。

        Returns:
            读取到的字节结果。
        """
        if isinstance(stream, READABLE):
            b = b''
            for part in Client.__read_part(stream, 1024):
                b += part
            return b
        elif isinstance(stream, bytes):
            return stream
        else:
            return bytes(stream, encoding='utf-8')

    @staticmethod
    def read_as_string(stream) -> str:
        """从可读流中同步读取数据并转换为字符串。

        Args:
            stream: 可读流。

        Returns:
            读取到的字符串结果。
        """
        buff = Client.read_as_bytes(stream)
        return Client.to_string(buff)

    @staticmethod
    def read_as_json(stream) -> Any:
        """从可读流中同步读取数据并按 JSON 格式解析。

        Args:
            stream: 可读流。

        Returns:
            解析后的结果。
        """
        return Client.parse_json(Client.read_as_string(stream))

    @staticmethod
    def get_nonce() -> str:
        """生成随机 nonce 字符串。

        基于进程启动时间、线程 ID、当前时间、自增序号与随机数拼接后，
        计算 MD5 十六进制摘要作为 nonce 值。

        Returns:
            生成的 nonce 字符串。
        """
        global _seqId
        thread_id = threading.get_ident()
        current_time = int(time.time() * 1000)
        seq = _seqId
        _seqId += 1
        randNum = random.getrandbits(64)
        msg = f'{_process_start_time}-{thread_id}-{current_time}-{seq}-{randNum}'
        md5 = hashlib.md5()
        md5.update(msg.encode('utf-8'))
        return md5.hexdigest()

    @staticmethod
    def get_date_utcstring() -> str:
        """获取当前日期的 UTC 格式字符串，遵循 RFC 1123（如 'Thu, 06 Feb 2020 07:32:54 GMT'）。

        Returns:
            UTC 格式的日期字符串。
        """
        return formatdate(usegmt=True)

    @staticmethod
    def default_string(
        real: str,
        default: str,
    ) -> str:
        """若 real 未设置，则返回默认字符串值。

        Args:
            real: 实际字符串值。
            default: 默认字符串值。

        Returns:
            返回 real（非 None）或 default。
        """
        return real if real is not None else default

    @staticmethod
    def default_number(
        real: int,
        default: int,
    ) -> int:
        """若 real 未设置，则返回默认数字值。

        Args:
            real: 实际数值。
            default: 默认数值。

        Returns:
            返回 real（非 None）或 default。
        """
        return real if real is not None else default

    @staticmethod
    def to_form_string(
        val: dict,
    ) -> str:
        """将字典格式化为表单字符串，形如 a=a%20b%20c。

        Args:
            val: 表单字段字典。

        Returns:
            表单编码后的字符串；字典为空时返回空字符串。
        """
        if not val:
            return ""
        keys = sorted(list(val))
        dic = {k: val[k] for k in keys if not isinstance(val[k], READABLE)}
        return urlencode(dic)

    @staticmethod
    def to_jsonstring(
        val: Any,
    ) -> str:
        """将值按 JSON 格式序列化为字符串。

        Args:
            val: 待序列化的值。

        Returns:
            JSON 格式字符串。
        """
        if isinstance(val, str):
            return str(val)
        return json.dumps(
            val, cls=Client.__ModelEncoder, ensure_ascii=False, separators=(",", ":")
        )

    @staticmethod
    def empty(
        val: str,
    ) -> bool:
        """检查字符串是否为空。

        Args:
            val: 待检查的字符串。

        Returns:
            字符串为 None 或长度为零时返回 True，否则返回 False。
        """
        return not val

    @staticmethod
    def equal_string(
        val1: str,
        val2: str,
    ) -> bool:
        """比较两个字符串是否相等。

        Args:
            val1: 第一个字符串。
            val2: 第二个字符串。

        Returns:
            相等时返回 True，否则返回 False。
        """
        return val1 == val2

    @staticmethod
    def equal_number(
        val1: int,
        val2: int,
    ) -> bool:
        """比较两个数字是否相等。

        Args:
            val1: 第一个数字。
            val2: 第二个数字。

        Returns:
            相等时返回 True，否则返回 False。
        """
        return val1 == val2

    @staticmethod
    def is_unset(
        value: Any,
    ) -> bool:
        """检查一个值是否未设置。

        Args:
            value: 待检查的值。

        Returns:
            值为 None 时返回 True，否则返回 False。
        """
        return value is None

    @staticmethod
    def stringify_map_value(
        m: Dict[str, Any],
    ) -> Dict[str, str]:
        """将字典中的值统一转换为字符串形式。

        Args:
            m: 原始字典。

        Returns:
            值为字符串形式的字典。
        """
        if m is None:
            return {}

        dic_result = {}
        for k, v in m.items():
            if v is not None:
                if isinstance(v, bytes):
                    v = v.decode('utf-8')
                else:
                    v = str(v)
            dic_result[k] = v
        return dic_result

    @staticmethod
    def anyify_map_value(
        m: Dict[str, str],
    ) -> Dict[str, Any]:
        """将字典值转换为任意类型（当前实现原样返回）。

        Args:
            m: 原始字典。

        Returns:
            原样返回的字典。
        """
        return m

    @staticmethod
    def assert_as_boolean(
        value: Any,
    ) -> bool:
        """断言一个值为布尔类型。

        Args:
            value: 待断言的值。

        Returns:
            布尔值。

        Raises:
            ValueError: 当值不是布尔类型时抛出。
        """
        if not isinstance(value, bool):
            raise ValueError(f'{value} is not a bool')
        return value

    @staticmethod
    def assert_as_string(
        value: Any,
    ) -> str:
        """断言一个值为字符串类型。

        Args:
            value: 待断言的值。

        Returns:
            字符串值。

        Raises:
            ValueError: 当值不是字符串类型时抛出。
        """
        if not isinstance(value, str):
            raise ValueError(f'{value} is not a str')
        return value

    @staticmethod
    def assert_as_bytes(
        value: Any,
    ) -> bytes:
        """断言一个值为字节类型。

        Args:
            value: 待断言的值。

        Returns:
            字节值。

        Raises:
            ValueError: 当值不是字节类型时抛出。
        """
        if not isinstance(value, bytes):
            raise ValueError(f'{value} is not a bytes')
        return value

    @staticmethod
    def assert_as_number(
        value: Any,
    ) -> int:
        """断言一个值为数字类型（int 或 float）。

        Args:
            value: 待断言的值。

        Returns:
            数字值。

        Raises:
            ValueError: 当值不是数字类型时抛出。
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f'{value} is not a number')
        return value

    @staticmethod
    def assert_as_integer(
        value: Any,
    ) -> int:
        """断言一个值为整数类型。

        Args:
            value: 待断言的值。

        Returns:
            整数值。

        Raises:
            ValueError: 当值不是整数类型时抛出。
        """
        if not isinstance(value, int):
            raise ValueError(f'{value} is not a int number')
        return value

    @staticmethod
    def assert_as_map(
        value: Any,
    ) -> Dict[str, Any]:
        """断言一个值为字典类型。

        Args:
            value: 待断言的值。

        Returns:
            字典值。

        Raises:
            ValueError: 当值不是字典类型时抛出。
        """
        if not isinstance(value, dict):
            raise ValueError(f'{value} is not a dict')
        return value

    @staticmethod
    def get_user_agent(
        user_agent: str,
    ) -> str:
        """获取 User-Agent。

        若传入的 user_agent 非空，则与默认 User-Agent 拼接后返回，
        否则返回默认 User-Agent。

        Args:
            user_agent: 自定义的 User-Agent，可为空。

        Returns:
            拼接后的 User-Agent 字符串。
        """
        if user_agent:
            return f'{Client.__get_default_agent()} {user_agent}'
        return Client.__get_default_agent()

    @staticmethod
    def is_2xx(
        code: int,
    ) -> bool:
        """判断状态码是否为 2xx。

        Args:
            code: HTTP 状态码。

        Returns:
            状态码在 [200, 300) 范围内时返回 True，否则返回 False。
        """
        return 200 <= code < 300

    @staticmethod
    def is_3xx(
        code: int,
    ) -> bool:
        """判断状态码是否为 3xx。

        Args:
            code: HTTP 状态码。

        Returns:
            状态码在 [300, 400) 范围内时返回 True，否则返回 False。
        """
        return 300 <= code < 400

    @staticmethod
    def is_4xx(
        code: int,
    ) -> bool:
        """判断状态码是否为 4xx。

        Args:
            code: HTTP 状态码。

        Returns:
            状态码在 [400, 500) 范围内时返回 True，否则返回 False。
        """
        return 400 <= code < 500

    @staticmethod
    def is_5xx(
        code: int,
    ) -> bool:
        """判断状态码是否为 5xx。

        Args:
            code: HTTP 状态码。

        Returns:
            状态码在 [500, 600) 范围内时返回 True，否则返回 False。
        """
        return 500 <= code < 600

    @staticmethod
    def validate_model(
        m: TeaModel,
    ) -> None:
        """校验数据模型。

        Args:
            m: 待校验的模型对象。
        """
        if isinstance(m, TeaModel):
            m.validate()

    @staticmethod
    def to_map(
        in_: TeaModel,
    ) -> Dict[str, Any]:
        """将模型对象转换为字典。

        Args:
            in_: 待转换的模型对象。

        Returns:
            转换后的字典；非模型对象原样返回。
        """
        if isinstance(in_, TeaModel):
            return in_.to_map()
        else:
            return in_

    @staticmethod
    def sleep(
        millisecond: int,
    ) -> None:
        """同步挂起当前线程指定的毫秒数。

        Args:
            millisecond: 挂起的毫秒数。
        """
        time.sleep(millisecond / 1000)

    @staticmethod
    async def sleep_async(
            millisecond: int,
    ) -> None:
        """异步挂起指定的毫秒数。

        Args:
            millisecond: 挂起的毫秒数。
        """
        await asyncio.sleep(millisecond / 1000)

    @staticmethod
    def to_array(
        input: Any,
    ) -> List[Dict[str, Any]]:
        """将输入转换为数组（列表）。

        输入中的 TeaModel 元素会转换为字典，其余元素原样保留。

        Args:
            input: 可迭代的输入，可为 None。

        Returns:
            转换后的列表；输入为 None 时返回空列表。
        """
        if input is None:
            return []

        out = []
        for i in input:
            if isinstance(i, TeaModel):
                out.append(i.to_map())
            else:
                out.append(i)
        return out

    @staticmethod
    def assert_as_readable(
        value: Any,
    ) -> BinaryIO:
        """断言一个值为可读流。

        字符串与字节值会被转换为 BytesIO，其余值须为可读流对象。

        Args:
            value: 待断言的值。

        Returns:
            可读流对象。

        Raises:
            ValueError: 当值既非字符串/字节也非可读流时抛出。
        """
        if isinstance(value, str):
            value = value.encode('utf-8')

        if isinstance(value, bytes):
            value = BytesIO(value)
        elif not isinstance(value, READABLE):
            raise ValueError(f'The value is not a readable')
        return value

    @staticmethod
    def assert_as_array(
        value: Any,
    ) -> list:
        """断言一个值为列表类型。

        Args:
            value: 待断言的值。

        Returns:
            列表值。

        Raises:
            ValueError: 当值不是列表类型时抛出。
        """
        if not isinstance(value, list):
            raise ValueError('The value is not a list')
        return value

    @staticmethod
    def get_host_name() -> str:
        """获取当前机器的主机名。

        Returns:
            主机名字符串；获取失败时返回空字符串。
        """
        import socket
        try:
            return socket.gethostname()
        except Exception:
            return ''

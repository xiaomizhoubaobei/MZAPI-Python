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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-form-2026-qxx"


"""
表单工具模块

提供表单字符串序列化与 multipart/form-data 流式上传能力，
支持普通字段与文件字段混合的请求体构造。

包含的类：
  - Form：表单工具类，负责表单字符串与文件表单流的构造
  - FileFormInputStream：文件表单输入流，按边界分割构造 multipart 请求体
  - FileField：文件字段模型，描述上传文件的基础信息

包含的函数：
  - _length：计算输入对象的内容长度
"""

import os
import sys
from _io import BytesIO
import random
from mzapi.utlis.aliyunauth.darabonba.utils.stream import BaseStream, READABLE
from mzapi.utlis.aliyunauth.darabonba.core import DaraModel
from urllib.parse import urlencode


class Form:
    """表单工具类，提供表单字符串与文件表单流的构造能力。"""

    @staticmethod
    def to_form_string(
        val: dict,
    ) -> str:
        """
        Format a map to form string, like a=a%20b%20c
        @return: the form string
        """
        if not val:
            return ""
        keys = sorted(list(val))
        dic = {k: val[k] for k in keys if not isinstance(val[k], READABLE)}
        return urlencode(dic)

    @staticmethod
    def get_boundary():
        """生成随机的 multipart 边界字符串（14 位数字）。

        Returns:
            由随机数生成的边界字符串。
        """
        result = '%s' % int(random.random() * 100000000000000)
        return result.zfill(14)

    @staticmethod
    def to_file_form(form, boundary):
        """根据表单数据与边界构造文件表单输入流。

        Args:
            form: 表单字段与文件字段构成的字典。
            boundary: multipart 边界字符串。

        Returns:
            FileFormInputStream 实例。
        """
        return FileFormInputStream(form, boundary)


def _length(o):
    """计算输入对象的内容长度。

    Args:
        o: 支持 len 属性、BytesIO、文件对象或内置 len 的对象。

    Returns:
        对象的内容字节长度。
    """
    if hasattr(o, 'len'):
        return o.len
    elif isinstance(o, BytesIO):
        return o.getbuffer().nbytes
    elif hasattr(o, 'fileno'):
        return os.path.getsize(o.name)
    return len(o)


class FileFormInputStream(BaseStream):
    """文件表单输入流，按边界构造 multipart/form-data 请求体。

    支持普通字段与文件字段混合，可流式读取完整的 multipart 内容。
    """

    def __init__(self, form, boundary, size=1024):
        """初始化文件表单输入流。

        Args:
            form: 表单字段与文件字段构成的字典。
            boundary: multipart 边界字符串。
            size: 读取缓冲区大小，默认 1024。
        """
        super().__init__(size)
        self.form = form
        self.boundary = boundary
        self.file_size_left = 0

        self.forms = {}
        self.files = {}
        self.files_keys = []
        self._to_map()

        self.form_str = b''
        self._build_str_forms()
        self.str_length = len(self.form_str)

    def _to_map(self):
        """将表单数据拆分为普通字段与文件字段。"""
        for k, v in self.form.items():
            if isinstance(v, FileField):
                self.files[k] = v
                self.files_keys.append(k)
            else:
                self.forms[k] = v

    def _build_str_forms(self):
        """构造普通字段部分的 multipart 字符串内容。"""
        form_str = ''
        str_fmt = '--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'
        forms_list = sorted(list(self.forms))
        for key in forms_list:
            value = self.forms[key]
            form_str += str_fmt % (self.boundary, key, value)
        self.form_str = form_str.encode('utf-8')

    def _get_stream_length(self):
        """计算整个 multipart 请求体的总长度。

        Returns:
            请求体的总字节长度。
        """
        file_length = 0
        for k, ff in self.files.items():
            field_length = len(ff.filename.encode('utf-8')) + len(ff.content_type) +\
                           len(k.encode('utf-8')) + len(self.boundary) + 78

            file_length += _length(ff.content) + field_length

        stream_length = self.str_length + file_length + len(self.boundary) + 6
        return stream_length

    def __len__(self):
        """返回 multipart 请求体的总长度。"""
        return self._get_stream_length()

    def __iter__(self):
        """返回迭代器自身，支持 for 循环流式读取。"""
        return self

    def __next__(self):
        """返回下一个分片数据，循环模式读取。"""
        return self.read(self.size, loop=True)

    def file_str(self, size):
        """构造文件字段部分的 multipart 内容。

        Args:
            size: 本次可读取的字节数。

        Returns:
            文件字段部分的字节内容。
        """
        # handle file object
        form_str = b''
        start_fmt = '--%s\r\nContent-Disposition: form-data; name="%s";'
        content_fmt = b' filename="%s"\r\nContent-Type: %s\r\n\r\n%s'

        if self.file_size_left:
            for key in self.files_keys[:]:
                if size <= 0:
                    break
                file_field = self.files[key]
                file_content = file_field.content.read(size)
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')

                if self.file_size_left <= size:
                    form_str += b'%s\r\n' % file_content
                    self.file_size_left = 0
                    size -= len(file_content)
                    self.files_keys.remove(key)
                else:
                    form_str += file_content
                    self.file_size_left -= size
                    size -= len(file_content)
        else:
            for key in self.files_keys[:]:
                if size <= 0:
                    break
                file_field = self.files[key]

                file_size = _length(file_field.content)
                self.file_size_left = file_size
                file_content = file_field.content.read(size)
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')

                # build form_str
                start = start_fmt % (self.boundary, key)
                content = content_fmt % (
                    file_field.filename.encode('utf-8'),
                    file_field.content_type.encode('utf-8'),
                    file_content
                )
                if self.file_size_left < size:
                    form_str += b'%s%s\r\n' % (start.encode('utf-8'), content)
                    self.file_size_left = 0
                    size -= len(file_content)
                    self.files_keys.remove(key)
                else:
                    form_str += b'%s%s' % (start.encode('utf-8'), content)
                    self.file_size_left -= size
                    size -= len(file_content)

        return form_str

    def read(self, size=None, loop=False):
        """按指定大小读取 multipart 请求体的下一分片。

        Args:
            size: 本次读取的字节数，None 表示读取全部剩余内容。
            loop: 迭代模式标志，为 True 时读取完抛出 StopIteration。

        Returns:
            请求体的下一分片字节内容。
        """
        if not self.files_keys and not self.form_str:
            self.refresh()
            if loop:
                raise StopIteration
            else:
                return b''

        if size is None:
            size = sys.maxsize

        if self.form_str:
            form_str = self.form_str[:size]
            self.form_str = self.form_str[size:]
            if len(form_str) < size:
                form_str += self.file_str(size)
        else:
            form_str = self.file_str(size)

        if not self.form_str and not self.files_keys:
            form_str += b'--%s--\r\n' % self.boundary.encode('utf-8')
        return form_str

    def refresh_cursor(self):
        """将所有文件内容游标重置到起始位置。"""
        for ff in self.files.values():
            if hasattr(ff.content, 'seek'):
                ff.content.seek(0, 0)

    def refresh(self):
        """重置输入流状态，重新构造字段并重置文件游标。"""
        self.file_size_left = 0
        self._to_map()
        self._build_str_forms()
        self.refresh_cursor()


class FileField(DaraModel):
    """文件字段模型，描述 multipart 表单中的上传文件信息。"""

    def __init__(self, filename=None, content_type=None, content=None):
        """初始化文件字段。

        Args:
            filename: 文件名。
            content_type: 文件内容的 MIME 类型。
            content: 文件内容对象（可读流）。
        """
        self.filename = filename
        self.content_type = content_type
        self.content = content

    def validate(self):
        """校验文件字段必填项，缺失时抛出异常。"""
        self.validate_required(self.filename, 'filename')
        self.validate_required(self.content_type, 'content_type')
        self.validate_required(self.content, 'content')

    def to_map(self):
        """将文件字段转换为字典表示。

        Returns:
            包含 filename、contentType、content 的字典。
        """
        result = {}
        result['filename'] = self.filename
        result['contentType'] = self.content_type
        result['content'] = self.content
        return result

    def from_map(self, map={}):
        """从字典还原文件字段属性。

        Args:
            map: 包含文件字段信息的字典。

        Returns:
            当前 FileField 实例。
        """
        self.filename = map.get('filename')
        self.content_type = map.get('contentType')
        self.content = map.get('content')
        return self

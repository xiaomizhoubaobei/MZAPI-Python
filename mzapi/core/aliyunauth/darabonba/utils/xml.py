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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-xml-2026-qxx"


"""
XML 工具模块

提供 XML 字符串与字典 / DaraModel 模型之间的相互转换能力，
支持 dict、列表等嵌套结构的序列化与反序列化。

包含的类：
  - XML：XML 转换工具类，提供 parse_xml 与 to_xml 静态方法
"""

from xml.etree import ElementTree
from mzapi.utlis.aliyunauth.darabonba.model import DaraModel
from collections import defaultdict


class XML:
    """XML 转换工具类，实现 XML 与字典 / 模型之间的互转。"""

    # 可被当作列表处理的类型集合
    _LIST_TYPE = (list, tuple, set)

    @staticmethod
    def __get_xml_factory(elem, val, parent_element=None):
        """根据值的类型递归构造 XML 子节点。

        Args:
            elem: 当前 XML 元素。
            val: 待写入的值，可为 dict、list 或基础类型。
            parent_element: 父级 XML 元素，列表展开时使用。

        Raises:
            RuntimeError: 当列表没有根标签时抛出。
        """
        if val is None:
            return

        if isinstance(val, dict):
            XML.__get_xml_by_dict(elem, val)
        elif isinstance(val, XML._LIST_TYPE):
            if parent_element is None:
                raise RuntimeError("Missing root tag")
            XML.__get_xml_by_list(elem, val, parent_element)
        else:
            elem.text = str(val)

    @staticmethod
    def __get_xml_by_dict(elem, val):
        """将字典键值对转换为 XML 子节点。

        Args:
            elem: 父级 XML 元素。
            val: 待转换的字典。
        """
        for k in val:
            sub_elem = ElementTree.SubElement(elem, k)
            XML.__get_xml_factory(sub_elem, val[k], elem)

    @staticmethod
    def __get_xml_by_list(elem, val, parent_element):
        """将列表值展开为同标签的多个 XML 子节点。

        Args:
            elem: 当前 XML 元素。
            val: 待转换的列表。
            parent_element: 父级 XML 元素。
        """
        i = 0
        tag_name = elem.tag
        if val.__len__() > 0:
            XML.__get_xml_factory(elem, val[0], parent_element)

        for item in val:
            if i > 0:
                sub_elem = ElementTree.SubElement(parent_element, tag_name)
                XML.__get_xml_factory(sub_elem, item, parent_element)
            i = i + 1

    @staticmethod
    def _parse_xml(t):
        """将 XML 元素递归解析为字典。

        Args:
            t: XML 元素。

        Returns:
            解析后的字典结构。
        """
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(XML._parse_xml, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}

        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())

        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d

    @staticmethod
    def parse_xml(body, response=None):
        """
        Parse body into the response, and put the resposne into a object
        @param body: source content
        @param response: target model
        @return the final object
        """
        return XML._parse_xml(ElementTree.fromstring(body))

    @staticmethod
    def to_xml(body):
        """
        Parse body as a xml string
        @param body: source body
        @return the xml string
        """
        if body is None:
            return

        dic = {}
        if isinstance(body, DaraModel):
            dic = body.to_map()
        elif isinstance(body, dict):
            dic = body

        if dic.__len__() == 0:
            return ""
        else:
            result_xml = '<?xml version="1.0" encoding="utf-8"?>'
            for k in dic:
                elem = ElementTree.Element(k)
                XML.__get_xml_factory(elem, dic[k])
                result_xml += bytes.decode(ElementTree.tostring(elem), encoding="utf-8")
            return result_xml

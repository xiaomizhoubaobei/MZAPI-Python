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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-map-2026-qxx"


"""
字典映射工具模块

提供字典数据与 JSON 字符串之间的转换能力。

包含的类：
  - Map：字典映射包装类，可将其内部数据序列化为 JSON 字符串
"""

import json


class Map:
    """字典映射包装类，持有底层数据并提供 JSON 序列化能力。"""

    def __init__(self, data):
        """初始化 Map 实例。

        Args:
            data: 待包装的字典数据。
        """
        self.data = data

    @staticmethod
    def to_json(map_instance):
        """将 Map 实例内部数据序列化为 JSON 字符串。

        Args:
            map_instance: Map 类型的实例。

        Returns:
            序列化后的 JSON 字符串。

        Raises:
            ValueError: 当入参不是 Map 实例时抛出。
            Exception: 当数据不可序列化时抛出。
        """
        if not isinstance(map_instance, Map):
            raise ValueError("Input must be an instance of Map")
        try:
            return json.dumps(map_instance.data)
        except TypeError as e:
            raise Exception(f"Serialization error: {e}")

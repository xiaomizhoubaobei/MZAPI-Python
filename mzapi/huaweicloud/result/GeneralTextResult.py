# coding: utf-8
#
# Copyright 2026 祁筱欣
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from typing import Any, Optional, List


class GeneralTextWordsBlockList:
    """
    通用文字识别文字块列表

    Attributes:
      openapi_types (dict): 键为属性名，值为属性类型。
      attribute_map (dict): 键为属性名，值为 JSON 定义中的键。
    """
    sensitive_list = []

    openapi_types = {
        'words': 'str',
        'confidence': 'float',
        'location': 'list[list[int]]'
    }

    attribute_map = {
        'words': 'words',
        'confidence': 'confidence',
        'location': 'location'
    }

    def __init__(
        self,
        words: Optional[str] = None,
        confidence: Optional[float] = None,
        location: Optional[List[List[int]]] = None
    ):
        """
        GeneralTextWordsBlockList

        :param words: 文字块内容
        :type words: str
        :param confidence: 置信度，取值范围0~100
        :type confidence: float
        :param location: 文字块坐标
        :type location: list[list[int]]
        """
        self._words = None
        self._confidence = None
        self._location = None
        self.discriminator = None

        if words is not None:
            self.words = words
        if confidence is not None:
            self.confidence = confidence
        if location is not None:
            self.location = location

    @property
    def words(self) -> Optional[str]:
        """获取此 GeneralTextWordsBlockList 的 words 属性。"""
        return self._words

    @words.setter
    def words(self, words: Optional[str]) -> None:
        """设置此 GeneralTextWordsBlockList 的 words 属性。"""
        self._words = words

    @property
    def confidence(self) -> Optional[float]:
        """获取此 GeneralTextWordsBlockList 的 confidence 属性。"""
        return self._confidence

    @confidence.setter
    def confidence(self, confidence: Optional[float]) -> None:
        """设置此 GeneralTextWordsBlockList 的 confidence 属性。"""
        self._confidence = confidence

    @property
    def location(self) -> Optional[List[List[int]]]:
        """获取此 GeneralTextWordsBlockList 的 location 属性。"""
        return self._location

    @location.setter
    def location(self, location: Optional[List[List[int]]]) -> None:
        """设置此 GeneralTextWordsBlockList 的 location 属性。"""
        self._location = location

    def to_dict(self) -> dict[str, Any]:
        """以字典形式返回模型属性"""
        result = {}

        for attr, _ in self.openapi_types.items():
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                if attr in self.sensitive_list:
                    result[attr] = "****"
                else:
                    result[attr] = value

        return result

    def to_str(self) -> str:
        """返回模型的字符串表示"""
        import simplejson as json
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self) -> str:
        """用于 `print` 输出"""

    def __eq__(self, other: Any) -> bool:
        """如果两个对象相等则返回 True"""
        if not isinstance(other, GeneralTextWordsBlockList):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        """如果两个对象不相等则返回 True"""
        return not self == other


class GeneralTextResult:
    """
    通用文字识别结果

    Attributes:
      openapi_types (dict): 键为属性名，值为属性类型。
      attribute_map (dict): 键为属性名，值为 JSON 定义中的键。
    """
    sensitive_list = []

    openapi_types = {
        'direction': 'float',
        'words_block_count': 'int',
        'words_block_list': 'list[GeneralTextWordsBlockList]',
        'markdown_result': 'str'
    }

    attribute_map = {
        'direction': 'direction',
        'words_block_count': 'words_block_count',
        'words_block_list': 'words_block_list',
        'markdown_result': 'markdown_result'
    }

    def __init__(
        self,
        direction: Optional[float] = None,
        words_block_count: Optional[int] = None,
        words_block_list: Optional[List[GeneralTextWordsBlockList]] = None,
        markdown_result: Optional[str] = None
    ):
        """
        GeneralTextResult

        :param direction: 图片朝向
        :type direction: float
        :param words_block_count: 识别文字块数目
        :type words_block_count: int
        :param words_block_list: 识别文字块列表
        :type words_block_list: list[GeneralTextWordsBlockList]
        :param markdown_result: 所有文字块拼接的识别结果
        :type markdown_result: str
        """
        self._direction = None
        self._words_block_count = None
        self._words_block_list = None
        self._markdown_result = None
        self.discriminator = None

        self.direction = direction
        self.words_block_count = words_block_count
        self.words_block_list = words_block_list
        if markdown_result is not None:
            self.markdown_result = markdown_result

    @property
    def direction(self) -> Optional[float]:
        """获取此 GeneralTextResult 的 direction 属性。"""
        return self._direction

    @direction.setter
    def direction(self, direction: Optional[float]) -> None:
        """设置此 GeneralTextResult 的 direction 属性。"""
        self._direction = direction

    @property
    def words_block_count(self) -> Optional[int]:
        """获取此 GeneralTextResult 的 words_block_count 属性。"""
        return self._words_block_count

    @words_block_count.setter
    def words_block_count(self, words_block_count: Optional[int]) -> None:
        """设置此 GeneralTextResult 的 words_block_count 属性。"""
        self._words_block_count = words_block_count

    @property
    def words_block_list(self) -> Optional[List[GeneralTextWordsBlockList]]:
        """获取此 GeneralTextResult 的 words_block_list 属性。"""
        return self._words_block_list

    @words_block_list.setter
    def words_block_list(self, words_block_list: Optional[List[GeneralTextWordsBlockList]]) -> None:
        """设置此 GeneralTextResult 的 words_block_list 属性。"""
        self._words_block_list = words_block_list

    @property
    def markdown_result(self) -> Optional[str]:
        """获取此 GeneralTextResult 的 markdown_result 属性。"""
        return self._markdown_result

    @markdown_result.setter
    def markdown_result(self, markdown_result: Optional[str]) -> None:
        """设置此 GeneralTextResult 的 markdown_result 属性。"""
        self._markdown_result = markdown_result

    def to_dict(self) -> dict[str, Any]:
        """以字典形式返回模型属性"""
        result = {}

        for attr, _ in self.openapi_types.items():
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                if attr in self.sensitive_list:
                    result[attr] = "****"
                else:
                    result[attr] = value

        return result

    def to_str(self) -> str:
        """返回模型的字符串表示"""
        import simplejson as json
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self) -> str:
        """用于 `print` 输出"""
        return self.to_str()

    def __eq__(self, other: Any) -> bool:
        """如果两个对象相等则返回 True"""
        if not isinstance(other, GeneralTextResult):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        """如果两个对象不相等则返回 True"""
        return not self == other
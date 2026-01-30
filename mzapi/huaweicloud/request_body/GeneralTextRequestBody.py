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

from typing import Any, Optional


class GeneralTextRequestBody:
    """
    通用文字识别请求体

    Attributes:
      openapi_types (dict): 键为属性名，值为属性类型。
      attribute_map (dict): 键为属性名，值为 JSON 定义中的键。
    """
    sensitive_list = []

    openapi_types = {
        'image': 'str',
        'url': 'str',
        'detect_direction': 'bool',
        'quick_mode': 'bool',
        'character_mode': 'bool',
        'language': 'str',
        'single_orientation_mode': 'bool',
        'pdf_page_number': 'int',
        'return_markdown_result': 'bool'
    }

    attribute_map = {
        'image': 'image',
        'url': 'url',
        'detect_direction': 'detect_direction',
        'quick_mode': 'quick_mode',
        'character_mode': 'character_mode',
        'language': 'language',
        'single_orientation_mode': 'single_orientation_mode',
        'pdf_page_number': 'pdf_page_number',
        'return_markdown_result': 'return_markdown_result'
    }

    def __init__(
        self,
        image: Optional[str] = None,
        url: Optional[str] = None,
        detect_direction: Optional[bool] = None,
        quick_mode: Optional[bool] = None,
        character_mode: Optional[bool] = None,
        language: Optional[str] = None,
        single_orientation_mode: Optional[bool] = None,
        pdf_page_number: Optional[int] = None,
        return_markdown_result: Optional[bool] = None
    ):
        """
        GeneralTextRequestBody

        :param image: 图片的Base64编码，与url二选一
        :type image: str
        :param url: 图片的URL路径，与image二选一
        :type url: str
        :param detect_direction: 图片朝向检测开关
        :type detect_direction: bool
        :param quick_mode: 快速模式开关
        :type quick_mode: bool
        :param character_mode: 单字符模式开关
        :type character_mode: bool
        :param language: 语种选择
        :type language: str
        :param single_orientation_mode: 单朝向模式开关
        :type single_orientation_mode: bool
        :param pdf_page_number: 指定PDF页码识别
        :type pdf_page_number: int
        :param return_markdown_result: 返回文字块拼接结果开关
        :type return_markdown_result: bool
        """
        self._image = None
        self._url = None
        self._detect_direction = None
        self._quick_mode = None
        self._character_mode = None
        self._language = None
        self._single_orientation_mode = None
        self._pdf_page_number = None
        self._return_markdown_result = None
        self.discriminator = None

        if image is not None:
            self.image = image
        if url is not None:
            self.url = url
        if detect_direction is not None:
            self.detect_direction = detect_direction
        if quick_mode is not None:
            self.quick_mode = quick_mode
        if character_mode is not None:
            self.character_mode = character_mode
        if language is not None:
            self.language = language
        if single_orientation_mode is not None:
            self.single_orientation_mode = single_orientation_mode
        if pdf_page_number is not None:
            self.pdf_page_number = pdf_page_number
        if return_markdown_result is not None:
            self.return_markdown_result = return_markdown_result

    @property
    def image(self) -> Optional[str]:
        """获取此 GeneralTextRequestBody 的 image 属性。"""
        return self._image

    @image.setter
    def image(self, image: Optional[str]) -> None:
        """设置此 GeneralTextRequestBody 的 image 属性。"""
        self._image = image

    @property
    def url(self) -> Optional[str]:
        """获取此 GeneralTextRequestBody 的 url 属性。"""
        return self._url

    @url.setter
    def url(self, url: Optional[str]) -> None:
        """设置此 GeneralTextRequestBody 的 url 属性。"""
        self._url = url

    @property
    def detect_direction(self) -> Optional[bool]:
        """获取此 GeneralTextRequestBody 的 detect_direction 属性。"""
        return self._detect_direction

    @detect_direction.setter
    def detect_direction(self, detect_direction: Optional[bool]) -> None:
        """设置此 GeneralTextRequestBody 的 detect_direction 属性。"""
        self._detect_direction = detect_direction

    @property
    def quick_mode(self) -> Optional[bool]:
        """获取此 GeneralTextRequestBody 的 quick_mode 属性。"""
        return self._quick_mode

    @quick_mode.setter
    def quick_mode(self, quick_mode: Optional[bool]) -> None:
        """设置此 GeneralTextRequestBody 的 quick_mode 属性。"""
        self._quick_mode = quick_mode

    @property
    def character_mode(self) -> Optional[bool]:
        """获取此 GeneralTextRequestBody 的 character_mode 属性。"""
        return self._character_mode

    @character_mode.setter
    def character_mode(self, character_mode: Optional[bool]) -> None:
        """设置此 GeneralTextRequestBody 的 character_mode 属性。"""
        self._character_mode = character_mode

    @property
    def language(self) -> Optional[str]:
        """获取此 GeneralTextRequestBody 的 language 属性。"""
        return self._language

    @language.setter
    def language(self, language: Optional[str]) -> None:
        """设置此 GeneralTextRequestBody 的 language 属性。"""
        self._language = language

    @property
    def single_orientation_mode(self) -> Optional[bool]:
        """获取此 GeneralTextRequestBody 的 single_orientation_mode 属性。"""
        return self._single_orientation_mode

    @single_orientation_mode.setter
    def single_orientation_mode(self, single_orientation_mode: Optional[bool]) -> None:
        """设置此 GeneralTextRequestBody 的 single_orientation_mode 属性。"""
        self._single_orientation_mode = single_orientation_mode

    @property
    def pdf_page_number(self) -> Optional[int]:
        """获取此 GeneralTextRequestBody 的 pdf_page_number 属性。"""
        return self._pdf_page_number

    @pdf_page_number.setter
    def pdf_page_number(self, pdf_page_number: Optional[int]) -> None:
        """设置此 GeneralTextRequestBody 的 pdf_page_number 属性。"""
        self._pdf_page_number = pdf_page_number

    @property
    def return_markdown_result(self) -> Optional[bool]:
        """获取此 GeneralTextRequestBody 的 return_markdown_result 属性。"""
        return self._return_markdown_result

    @return_markdown_result.setter
    def return_markdown_result(self, return_markdown_result: Optional[bool]) -> None:
        """设置此 GeneralTextRequestBody 的 return_markdown_result 属性。"""
        self._return_markdown_result = return_markdown_result

    def to_dict(self) -> dict[str, Any]:
        """以字典形式返回模型属性（只包含非 None 的值）"""
        result = {}

        for attr, _ in self.openapi_types.items():
            value = getattr(self, attr)
            if value is None:
                continue  # 跳过 None 值

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
        if not isinstance(other, GeneralTextRequestBody):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        """如果两个对象不相等则返回 True"""
        return not self == other
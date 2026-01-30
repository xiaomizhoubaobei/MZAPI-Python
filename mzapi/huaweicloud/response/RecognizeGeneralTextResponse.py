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

from mzapi.huaweicloud.result.GeneralTextResult import GeneralTextResult, GeneralTextWordsBlockList


class RecognizeGeneralTextResponse:
    """
    通用文字识别响应

    Attributes:
      openapi_types (dict): 键为属性名，值为属性类型。
      attribute_map (dict): 键为属性名，值为 JSON 定义中的键。
    """
    sensitive_list = []

    openapi_types = {
        'result': 'GeneralTextResult',
        'x_request_id': 'str'
    }

    attribute_map = {
        'result': 'result',
        'x_request_id': 'X-Request-Id'
    }

    def __init__(
        self,
        result: Optional[GeneralTextResult] = None,
        x_request_id: Optional[str] = None
    ):
        """
        RecognizeGeneralTextResponse

        :param result: 识别结果
        :type result: GeneralTextResult
        :param x_request_id: 请求ID
        :type x_request_id: str
        """
        self._result = None
        self._x_request_id = None
        self.discriminator = None

        if result is not None:
            self.result = result
        if x_request_id is not None:
            self.x_request_id = x_request_id

    @property
    def result(self) -> Optional[GeneralTextResult]:
        """获取此 RecognizeGeneralTextResponse 的 result 属性。"""
        return self._result

    @result.setter
    def result(self, result: Optional[GeneralTextResult]) -> None:
        """设置此 RecognizeGeneralTextResponse 的 result 属性。"""
        self._result = result

    @property
    def x_request_id(self) -> Optional[str]:
        """获取此 RecognizeGeneralTextResponse 的 x_request_id 属性。"""
        return self._x_request_id

    @x_request_id.setter
    def x_request_id(self, x_request_id: Optional[str]) -> None:
        """设置此 RecognizeGeneralTextResponse 的 x_request_id 属性。"""
        self._x_request_id = x_request_id

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
        if not isinstance(other, RecognizeGeneralTextResponse):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        """如果两个对象不相等则返回 True"""
        return not self == other

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'RecognizeGeneralTextResponse':
        """
        从字典创建响应对象

        :param data: 响应数据字典
        :return: RecognizeGeneralTextResponse 实例
        """
        response = RecognizeGeneralTextResponse()

        if 'result' in data:
            result_data = data['result']
            result = GeneralTextResult(
                direction=result_data.get('direction'),
                words_block_count=result_data.get('words_block_count'),
                words_block_list=None,
                markdown_result=result_data.get('markdown_result')
            )

            # 处理 words_block_list
            if 'words_block_list' in result_data:
                words_blocks = []
                for block_data in result_data['words_block_list']:
                    block = GeneralTextWordsBlockList(
                        words=block_data.get('words'),
                        confidence=block_data.get('confidence'),
                        location=block_data.get('location')
                    )
                    words_blocks.append(block)
                result.words_block_list = words_blocks

            response.result = result

        if 'X-Request-Id' in data:
            response.x_request_id = data['X-Request-Id']

        return response
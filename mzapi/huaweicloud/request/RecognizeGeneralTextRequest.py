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

from mzapi.huaweicloud.request_body.GeneralTextRequestBody import GeneralTextRequestBody


class RecognizeGeneralTextRequest:
    """
    通用文字识别请求

    Attributes:
      openapi_types (dict): 键为属性名，值为属性类型。
      attribute_map (dict): 键为属性名，值为 JSON 定义中的键。
    """
    sensitive_list = []

    openapi_types = {
        'enterprise_project_id': 'str',
        'body': 'GeneralTextRequestBody'
    }

    attribute_map = {
        'enterprise_project_id': 'Enterprise-Project-Id',
        'body': 'body'
    }

    def __init__(
        self,
        enterprise_project_id: Optional[str] = None,
        body: Optional[GeneralTextRequestBody] = None
    ):
        """
        RecognizeGeneralTextRequest

        :param enterprise_project_id: 企业项目ID
        :type enterprise_project_id: str
        :param body: 请求体
        :type body: GeneralTextRequestBody
        """
        self._enterprise_project_id = None
        self._body = None
        self.discriminator = None

        if enterprise_project_id is not None:
            self.enterprise_project_id = enterprise_project_id
        if body is not None:
            self.body = body

    @property
    def enterprise_project_id(self) -> Optional[str]:
        """获取此 RecognizeGeneralTextRequest 的 enterprise_project_id 属性。"""
        return self._enterprise_project_id

    @enterprise_project_id.setter
    def enterprise_project_id(self, enterprise_project_id: Optional[str]) -> None:
        """设置此 RecognizeGeneralTextRequest 的 enterprise_project_id 属性。"""
        self._enterprise_project_id = enterprise_project_id

    @property
    def body(self) -> Optional[GeneralTextRequestBody]:
        """获取此 RecognizeGeneralTextRequest 的 body 属性。"""
        return self._body

    @body.setter
    def body(self, body: Optional[GeneralTextRequestBody]) -> None:
        """设置此 RecognizeGeneralTextRequest 的 body 属性。"""
        self._body = body

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
        if not isinstance(other, RecognizeGeneralTextRequest):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        """如果两个对象不相等则返回 True"""
        return not self == other
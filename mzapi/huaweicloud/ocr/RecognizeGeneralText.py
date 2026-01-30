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

from typing import Optional

from mzapi.huaweicloud.request_body.GeneralTextRequestBody import GeneralTextRequestBody
from mzapi.huaweicloud.response.RecognizeGeneralTextResponse import RecognizeGeneralTextResponse
from mzapi.utlis.huawei_auth import HuaweiCloudAuth
from mzapi.utlis.project_id_helper import ProjectIdHelper


class RecognizeGeneralText:
    """
    华为云通用文字识别 (General Text OCR)
    文档: https://support.huaweicloud.com/api-ocr/ocr_03_0042.html
    """

    def __init__(self, access_key: str, secret_key: str, project_id: Optional[str] = None):
        """
        初始化

        :param access_key: 华为云 Access Key ID
        :param secret_key: 华为云 Secret Access Key
        :param project_id: 华为云项目ID（可选）。如果不提供，将自动从IAM服务查询
        """
        self.auth = HuaweiCloudAuth(access_key, secret_key)
        self._service = "ocr"
        self._resource_path = "/v2/{project_id}/ocr/general-text"
        self._project_id = project_id  # 项目ID（可选）

    def recognize(
        self,
        region: str = "cn-east-3",
        image_base64: Optional[str] = None,
        image_url: Optional[str] = None,
        detect_direction: bool = False,
        quick_mode: bool = False,
        character_mode: bool = False,
        language: Optional[str] = None,
        single_orientation_mode: bool = False,
        pdf_page_number: Optional[int] = None,
        return_markdown_result: bool = False,
        enterprise_project_id: Optional[str] = None
    ) -> RecognizeGeneralTextResponse:
        """
        识别图片中的通用文字

        :param image_base64: 图片的 Base64 编码。与 image_url 二选一。
                            要求单个图片、PDF文件其对应的Base64编码不超过10MB。
                            图片最小边不小于15px，最长边不超过30000px。
                            支持格式：JPEG、JPG、PNG、BMP、GIF、TIFF、WEBP、PCX、ICO、PSD、PDF
        :param image_url: 图片的 URL 路径。与 image_base64 二选一。
                         支持公网 http/https url 和 OBS 提供的 url。
        :param detect_direction: 是否检测图片朝向。默认为 false。
        :param quick_mode: 快速模式开关，针对单行文字图片。默认为 false。
        :param character_mode: 单字符模式开关。默认为 false。
        :param language: 语种选择。可选值：auto, ms, uk, hi, ru, vi, id, th, zh, ar, de,
                        la, fr, it, es, pt, ro, pl, am, ja, ko, tr, no, da, sv, km, he
        :param single_orientation_mode: 单朝向模式开关。默认为 false。
        :param pdf_page_number: 指定 PDF 页码识别。默认识别第1页。
        :param return_markdown_result: 是否返回文字块拼接结果。默认为 false。
        :param enterprise_project_id: 企业项目ID。
        :param region: 区域标识符（例如：cn-north-4）
        :return: RecognizeGeneralTextResponse 响应对象
        """
        if not image_base64 and not image_url:
            raise ValueError("image_base64 和 image_url 至少传入一个")

        # 获取 project_id（自动查询或使用用户提供的）
        project_id = ProjectIdHelper.get_project_id(
            access_key=self.auth.access_key,
            secret_key=self.auth.secret_key,
            region=region,
        )

        # 创建请求体（只传递用户显式设置的参数）
        body_kwargs = {}
        if image_base64 is not None:
            body_kwargs['image'] = image_base64
        if image_url is not None:
            body_kwargs['url'] = image_url
        if not detect_direction:
            body_kwargs['detect_direction'] = detect_direction
        if not quick_mode:
            body_kwargs['quick_mode'] = quick_mode
        if not character_mode:
            body_kwargs['character_mode'] = character_mode
        if language is not None:
            body_kwargs['language'] = language
        if not single_orientation_mode:
            body_kwargs['single_orientation_mode'] = single_orientation_mode
        if pdf_page_number is not None:
            body_kwargs['pdf_page_number'] = pdf_page_number
        if not return_markdown_result:
            body_kwargs['return_markdown_result'] = return_markdown_result

        body = GeneralTextRequestBody(**body_kwargs)

        # 根据 region 动态生成 endpoint
        endpoint = f"ocr.{region}.myhuaweicloud.com"

        # 替换 resource_path 中的 project_id
        resource_path = self._resource_path.replace("{project_id}", project_id)

        # 发送请求（body 只包含请求体内容，enterprise_project_id 通过 headers 传递）
        # 注意：OCR 服务使用标准认证 (SDK-HMAC-SHA256)，不是派生认证
        response_data = self.auth.send_request(
            method="POST",
            uri=resource_path,
            headers={"Content-Type": "application/json;charset=UTF-8"},
            body=body.to_dict(),
            host=endpoint,
            region_id=region,
            service_name=self._service,
            enterprise_project_id=enterprise_project_id,
            use_derived_auth=False  # 使用标准认证
        )

        # 解析响应
        return RecognizeGeneralTextResponse.from_dict(response_data)
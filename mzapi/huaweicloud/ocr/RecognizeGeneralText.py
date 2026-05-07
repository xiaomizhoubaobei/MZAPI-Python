# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0.
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-hwc-recognize-general-text-2026-qxx"

from typing import Optional

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkocr.v1.region.ocr_region import OcrRegion
from huaweicloudsdkocr.v1 import (
    OcrClient,
    RecognizeGeneralTextRequest,
    RecognizeGeneralTextResponse as OcrRecognizeGeneralTextResponse,
    GeneralTextRequestBody,
)


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
        self._ak = access_key
        self._sk = secret_key
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
    ) -> OcrRecognizeGeneralTextResponse:
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

        # 创建凭证
        credentials = BasicCredentials(ak=self._ak, sk=self._sk)
        if self._project_id:
            credentials.with_project_id(self._project_id)

        # 构建客户端
        client = OcrClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(OcrRegion.value_of(region)) \
            .build()

        # 构建请求体
        body = GeneralTextRequestBody(
            image=image_base64,
            url=image_url,
            detect_direction=detect_direction,
            quick_mode=quick_mode,
            character_mode=character_mode,
            language=language,
            single_orientation_mode=single_orientation_mode,
            pdf_page_number=pdf_page_number,
            return_markdown_result=return_markdown_result
        )

        # 构建请求
        request = RecognizeGeneralTextRequest()
        request.body = body
        if enterprise_project_id:
            request.enterprise_project_id = enterprise_project_id

        # 发送请求并返回响应
        try:
            response = client.recognize_general_text(request)
            return response
        except exceptions.ClientRequestException as e:
            raise Exception(
                f"华为云OCR请求失败: 状态码={e.status_code}, "
                f"错误码={e.error_code}, 错误信息={e.error_msg}"
            )
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-aliyun-ocr-recognize-all-text-2026-qxx"

"""
阿里云 OCR - 识别全部文字（RecognizeAllText）实现

提供阿里云 OCR RecognizeAllText API 的具体实现类。
本模块封装了阿里云 OCR API 2021-07-07 版本的调用。

API 文档参考：
    https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizealltext
"""

from typing import Optional, Union

from darabonba.runtime import RuntimeOptions

from mzapi.core.aliyunauth import utils_models
from mzapi.core.aliyunauth.client import Client as AliyunOpenApiClient


# OCR API 默认版本
_API_VERSION = "2021-07-07"

# 默认端点
_DEFAULT_ENDPOINT = "ocr-api.cn-hangzhou.aliyuncs.com"


class RecognizeAllTextResponse:
    """RecognizeAllText 接口的响应封装。

    Attributes:
        status_code: HTTP 状态码。
        headers: 响应头。
        body: 响应体（JSON 解析后的 dict）。
    """

    def __init__(
        self,
        status_code: int = None,
        headers: dict = None,
        body: dict = None,
    ):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body or {}


class RecognizeAllText:
    """阿里云 OCR - 识别全部文字（RecognizeAllText）。

    基于阿里云 OpenAPI RPC 风格调用 OCR 服务，支持 URL 和 Base64 两种
    图片输入方式，以及丰富的可选参数控制输出格式。

    Attributes:
        client: 内部使用的阿里云 OpenAPI 客户端。
        endpoint: API 端点地址。

    使用示例::

        >>> from mzapi.aliyun.ocr import RecognizeAllText
        >>> client = RecognizeAllText(
        ...     access_key_id="your_ak",
        ...     access_key_secret="your_sk",
        ...     endpoint="ocr-api.cn-hangzhou.aliyuncs.com",
        ... )
        >>> result = client.recognize(url="https://example.com/image.jpg")
        >>> print(result.body["Data"]["Content"])
    """

    def __init__(
        self,
        access_key_id: str = None,
        access_key_secret: str = None,
        security_token: str = None,
        endpoint: str = None,
        protocol: str = "HTTPS",
        read_timeout: int = None,
        connect_timeout: int = None,
    ):
        """初始化 RecognizeAllText 客户端。

        Args:
            access_key_id: 阿里云 AccessKey ID。
            access_key_secret: 阿里云 AccessKey Secret。
            security_token: STS 安全令牌（可选，用于临时凭证）。
            endpoint: API 端点地址，默认为 ``ocr-api.cn-hangzhou.aliyuncs.com``。
            protocol: HTTP 协议，默认 HTTPS。
            read_timeout: 读取超时（毫秒）。
            connect_timeout: 连接超时（毫秒）。
        """
        self.endpoint = endpoint or _DEFAULT_ENDPOINT
        config = utils_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            security_token=security_token,
            endpoint=self.endpoint,
            protocol=protocol,
            read_timeout=read_timeout,
            connect_timeout=connect_timeout,
        )
        self.client = AliyunOpenApiClient(config)

    def recognize(
        self,
        url: str = None,
        body: str = None,
        output_char_info: bool = None,
        output_table: bool = None,
        output_figure: bool = None,
        output_formula: bool = None,
        output_barcode: bool = None,
        output_qrcode: bool = None,
        output_seal: bool = None,
        output_handwriting: bool = None,
        output_stamp: bool = None,
        output_kv_pair: bool = None,
        output_coordinate: bool = None,
        type: str = None,
        min_size: int = None,
        max_side: int = None,
        cut_type: int = None,
        need_rotate: bool = None,
        need_sort: bool = None,
        multi_language: str = None,
    ) -> RecognizeAllTextResponse:
        """调用 RecognizeAllText 接口识别图片中的全部文字。

        Args:
            url: 图片的 URL 地址（与 ``body`` 二选一）。
            body: 图片的 Base64 编码数据（与 ``url`` 二选一）。
            output_char_info: 是否输出字符级信息。
            output_table: 是否输出表格结构。
            output_figure: 是否输出图片区域信息。
            output_formula: 是否输出公式信息。
            output_barcode: 是否输出条码信息。
            output_qrcode: 是否输出二维码信息。
            output_seal: 是否输出印章信息。
            output_handwriting: 是否输出手写体信息。
            output_stamp: 是否输出票据/印章信息。
            output_kv_pair: 是否输出键值对信息。
            output_coordinate: 是否输出坐标信息。
            type: 识别类型，可选 ``Advanced``（高级版）或 ``Simple``（基础版）。
            min_size: 最小文字尺寸（像素），小于此值的文字将被忽略。
            max_side: 图片最大边长（像素），超过将被缩放。
            cut_type: 切割类型：``0`` 自动切割（默认）、``1`` 不切割。
            need_rotate: 是否需要自动旋转。
            need_sort: 是否需要排序。
            multi_language: 多语言支持，如 ``auto``、``zh``、``en`` 等。

        Returns:
            RecognizeAllTextResponse: 包含 status_code、headers 和 body 的响应对象。

        Raises:
            Exception: 当 API 调用失败时抛出异常。

        示例::

            >>> # URL 方式
            >>> result = client.recognize(url="https://example.com/image.jpg")
            >>> # Base64 方式
            >>> result = client.recognize(body="iVBORw0KGgo...")
            >>> # 带可选参数
            >>> result = client.recognize(
            ...     url="https://example.com/image.jpg",
            ...     output_table=True,
            ...     output_coordinate=True,
            ...     type="Advanced",
            ... )
        """
        # 构造业务请求参数
        biz_params = {}
        if url is not None:
            biz_params["Url"] = url
        if body is not None:
            biz_params["Body"] = body
        if output_char_info is not None:
            biz_params["OutputCharInfo"] = output_char_info
        if output_table is not None:
            biz_params["OutputTable"] = output_table
        if output_figure is not None:
            biz_params["OutputFigure"] = output_figure
        if output_formula is not None:
            biz_params["OutputFormula"] = output_formula
        if output_barcode is not None:
            biz_params["OutputBarcode"] = output_barcode
        if output_qrcode is not None:
            biz_params["OutputQrcode"] = output_qrcode
        if output_seal is not None:
            biz_params["OutputSeal"] = output_seal
        if output_handwriting is not None:
            biz_params["OutputHandwriting"] = output_handwriting
        if output_stamp is not None:
            biz_params["OutputStamp"] = output_stamp
        if output_kv_pair is not None:
            biz_params["OutputKVPair"] = output_kv_pair
        if output_coordinate is not None:
            biz_params["OutputCoordinate"] = output_coordinate
        if type is not None:
            biz_params["Type"] = type
        if min_size is not None:
            biz_params["MinSize"] = min_size
        if max_side is not None:
            biz_params["MaxSide"] = max_side
        if cut_type is not None:
            biz_params["CutType"] = cut_type
        if need_rotate is not None:
            biz_params["NeedRotate"] = need_rotate
        if need_sort is not None:
            biz_params["NeedSort"] = need_sort
        if multi_language is not None:
            biz_params["MultiLanguage"] = multi_language

        # 构造 RPC 风格的请求参数
        params = utils_models.Params(
            action="RecognizeAllText",
            version=_API_VERSION,
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="AK",
            body_type="json",
            req_body_type="json",
            style="RPC",
        )

        request = utils_models.OpenApiRequest(
            body=biz_params,
            query={},
        )

        runtime = RuntimeOptions()

        resp = self.client.do_rpcrequest(
            action="RecognizeAllText",
            version=_API_VERSION,
            protocol="HTTPS",
            method="POST",
            auth_type="AK",
            body_type="json",
            request=request,
            runtime=runtime,
        )

        return RecognizeAllTextResponse(
            status_code=resp.get("statusCode"),
            headers=resp.get("headers", {}),
            body=resp.get("body", {}),
        )


__all__ = [
    "RecognizeAllText",
    "RecognizeAllTextResponse",
]

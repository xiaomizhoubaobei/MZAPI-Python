# -*- coding: utf-8 -*-

import json
import logging

# 标准库导入
from typing import List, Optional

# 第三方库导入
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models

# 本地模块导入
from ...utlis import ImageValidator


class GeneralBasicOCR:
    def __init__(self, secret_id: str, secret_key: str, token: str = None):
        """初始化腾讯云OCR客户端
        
        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
            token: 临时密钥Token(可选)
            
        Raises:
            TencentCloudSDKException: 初始化失败时抛出
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化腾讯云OCR客户端")
        try:
            # 实例化认证对象
            self.cred = credential.Credential(secret_id, secret_key, token)
            self.logger.debug("认证对象创建成功")
            
            # 配置HTTP和客户端选项
            http_profile = HttpProfile()
            http_profile.endpoint = "ocr.tencentcloudapi.com"
            
            client_profile = ClientProfile()
            client_profile.http_profile = http_profile
            
            self.client = ocr_client.OcrClient(self.cred, "", client_profile)
            self.validate_url = ImageValidator.ImageValidator
            self.logger.info("OCR客户端初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化失败: {str(e)}")
            raise TencentCloudSDKException("初始化失败", str(e))

    def recognize(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        is_pdf: bool = False,
        pdf_page_number: int = 1,
        item_names: Optional[List[str]] = None,
        return_full_text: bool = False,
        config_id: str = "General",
        enable_seal_recognize: bool = False,
    ) -> str:
        """
           识别图片或PDF中的文字。

           Args:
               image_url: 图片URL。支持的图片格式包括 PNG、JPG、JPEG，暂不支持 GIF 格式。
                   图片的 Base64 编码后大小不能超过 10MB，且需在 3 秒内下载完成。
                   图片的像素应介于 20 至 10000 之间。建议将图片存储于腾讯云。
                   如果同时提供 `image_base64`，则优先使用 `image_url`。
               image_base64: 图片的 Base64 编码数据。支持的图片格式包括 PNG、JPG、JPEG，暂不支持 GIF 格式。
                   图片的 Base64 编码后大小不能超过 10MB。建议将图片存储于腾讯云。
               is_pdf: 是否开启 PDF 识别。默认为 `False`，开启后支持图片和 PDF 的识别。
               pdf_page_number: 需要识别的 PDF 页面的页码。仅支持单页识别，当上传的是 PDF 文件且 `is_pdf` 设置为 `True` 时生效，默认值为 1。
               item_names: 自定义结构化识别功能返回的字段名称列表。例如，若只想返回姓名和性别，则设置该参数为 `["姓名", "性别"]`。
               return_full_text: 是否返回全文字段，默认为 `False`。
               config_id: 配置 ID，支持多种场景的识别模板：
                   - General: 通用场景
                   - OnlineTaxiItinerary: 网约车行程单
                   - RideHailingDriverLicense: 网约车驾驶证
                   - RideHailingTransportLicense: 网约车运输证
                   - WayBill: 快递运单
                   - AccountOpeningPermit: 银行开户许可证
                   - InvoiceEng: 国际发票模板
                   - Coin: 钱币识别模板
                   - OnboardingDocuments: 入职材料识别
                   - PropertyOwnershipCertificate: 房产证识别
                   - RealEstateCertificate: 不动产权证识别
                   - HouseEncumbranceCertificate: 他权证识别
                   - CarInsurance: 车险保单
                   - MultiRealEstateCertificate: 房产证、不动产证、产权证等材料合一模板
               enable_seal_recognize: 是否开启印章识别，默认为 `False`。

           Returns:
               str: 识别结果的 JSON 字符串。

           Raises:
               ValueError: 当未提供 `image_url` 或 `image_base64` 时抛出。
               TencentCloudSDKException: 调用腾讯云 OCR API 时抛出。可能的原因包括 API 调用超时、认证失败、图片格式不支持、鉴权失败等。

           Note:
               - 如果同时提供 `image_url` 和 `image_base64`，则优先使用 `image_url`。
               - PDF 识别支持单页，`pdf_page_number` 必须为正整数。
               - 图片 URL 或 Base64 数据的大小、像素和格式需符合相关限制。
               - 印章识别仅在支持相关模板的场景时有效。
           """
        if not image_url and not image_base64:
            self.logger.warning("未提供image_url或image_base64参数")
            raise ValueError("必须提供image_url或image_base64参数")
            
        # 验证图片URL格式和类型
        if image_url:
            try:
                self.validate_url.validate_url(
                    image_url,
                    allowed_extensions=['.jpg', '.jpeg', '.png']
                )
                if len(image_url) > 2000:
                    self.logger.warning("图片URL长度超过2000字符，可能导致请求失败")
            except ValueError as e:
                self.logger.warning(f"图片URL验证失败: {str(e)}")
                raise
            
        if image_base64 and len(image_base64) > 10 * 1024 * 1024:
            self.logger.warning("Base64图片数据大小超过10MB限制")
            
        try:
            self.logger.info(f"开始识别请求，配置ID: {config_id}")
            self.logger.debug(f"请求参数: image_url={image_url}, is_pdf={is_pdf}, pdf_page_number={pdf_page_number}")
            
            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageUrl": image_url,
                "ImageBase64": image_base64,
                "IsPdf": is_pdf,
                "PdfPageNumber": pdf_page_number,
                "ItemNames": item_names or [],
                "ReturnFullText": return_full_text,
                "ConfigId": config_id,
                "EnableSealRecognize": enable_seal_recognize,
            }
            # 移除None值参数
            params = {k: v for k, v in params.items() if v is not None}
            
            req.from_json_string(json.dumps(params))
            if pdf_page_number < 1:
                self.logger.warning(f"PDF页码{pdf_page_number}小于1，将使用默认值1")
                
            resp = self.client.GeneralBasicOCR(req)
            
            self.logger.info("识别请求成功完成")
            if len(resp.to_json_string()) > 10000:
                self.logger.warning("识别结果过大，可能影响性能")
            self.logger.debug(f"识别结果: {resp.to_json_string()[:20]}...")  # 只记录前20字符避免日志过大
            
            return resp.to_json_string()
            
        except TencentCloudSDKException as err:
            error_msg = f"识别请求失败: {str(err)}"
            self.logger.error(error_msg)
            if "timeout" in str(err).lower():
                self.logger.warning("API请求超时，请检查网络连接或增加超时设置")
            elif "auth" in str(err).lower():
                self.logger.warning("认证失败，请检查SecretId和SecretKey")
            raise TencentCloudSDKException(error_msg) from err

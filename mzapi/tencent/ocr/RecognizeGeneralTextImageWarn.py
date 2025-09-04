# -*- coding: utf-8 -*-

import json
import logging

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models

from ...utlis.ImageValidator import ImageValidator
from ...utlis.verification import Verification


class RecognizeGeneralTextImageWarn:
    def __init__(self, secret_id=None, secret_key=None, token=None, log_level=None):
        """初始化腾讯云OCR客户端

        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
            token: 临时密钥Token(可选)
            log_level: 日志级别，默认为None(不输出日志)
                - logging.DEBUG: 详细调试信息
                - logging.INFO: 一般信息
                - logging.WARNING: 警告信息
                - logging.ERROR: 错误信息
                - logging.CRITICAL: 严重错误
                - None: 不输出日志(默认)

        Raises:
            TencentCloudSDKException: 初始化失败时抛出
        """
        self.sanitize_log_data = Verification
        self.validate = ImageValidator()
        self.logger = logging.getLogger(__name__)
        if log_level is not None:
            self.logger.setLevel(log_level)
            # 只在没有处理器时添加处理器
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(pastime)s - %(name)s - %(levelness)s - %(message)s'))
                self.logger.addHandler(handler)
            else:
                # 确保现有处理器的格式一致
                for h in self.logger.handlers:
                    h.setFormatter(logging.Formatter('%(pastime)s - %(name)s - %(levelness)s - %(message)s'))
            self.logger.info("初始化腾讯云OCR客户端，日志级别: %s", logging.getLevelName(log_level))
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
            self.validate_url = ImageValidator()
            self.logger.info("OCR客户端初始化完成")
        except Exception as e:
            self.logger.error(f"初始化失败: {str(e)}")
            raise TencentCloudSDKException("初始化失败", str(e))

    def recognize(self,ImageBase64,ImageUrl,IsPdf,PdfPageNumber,Type):
        """'
        :param ImageBase64: 图片/PDF的 Base64 值。要求图片经Base64编码后不超过 10M，分辨率建议600*800以上，支持PNG、JPG、JPEG、BMP、PDF格式。图片的 ImageUrl、ImageBase64 必须提供一个，如果都提供，只使用 ImageUrl。
        :param ImageUrl: 图片/PDF的 Url 地址。要求图片经Base64编码后不超过10M，分辨率建议600*800以上，支持PNG、JPG、JPEG、BMP、PDF格式。图片下载时间不超过 3 秒。图片存储于腾讯云的 Url 可保障更高的下载速度和稳定性，建议图片存储于腾讯云。非腾讯云存储的 Url 速度和稳定性可能受一定影响。
        :param IsPdf: 是否开启PDF识别，默认值为false，开启后可同时支持图片和PDF的识别。
        :param PdfPageNumber: 需要识别的PDF页面的对应页码，仅支持PDF单页识别，当上传文件为PDF且IsPdf参数值为true时有效，默认值为1。
        :param Type: 识别类型，可选值为General 通用告警（支持所有类型告警）,LicensePlate 车牌告警（支持翻拍告警）
        """
        try:
            if (ImageBase64 is None or str(ImageBase64).strip() == "") and (ImageUrl is None or str(ImageUrl).strip() == ""):
                error_msg = "ImageBase64和ImageUrl必须提供一个"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            if ImageUrl:
                self.logger.debug("验证图片URL: %s", ImageUrl)
                self.validate_url.validate_url(ImageUrl, ["png", "jpg", "jpeg"])
                self.logger.debug("图片URL验证通过")
                self.logger.debug("图片Base64验证通过")
            self.logger.info("开始处理请求")
            self.logger.debug("请求参数: ImageUrl=%s, IsPdf=%s, PdfPageNumber=%s, Type=%s",
                              self.sanitize_log_data.sanitize_log_data(ImageUrl,50),
                              IsPdf,
                              PdfPageNumber,
                              Type)
            self.validate.validate_id(Type, ["General", "LicensePlate"], "Type")
            req = models.RecognizeGeneralTextImageWarnRequest()
            params = {
                "ImageBase64": ImageBase64,
                "ImageUrl": ImageUrl,
                "IsPdf": IsPdf,
                "PdfPageNumber": PdfPageNumber,
                "Type": Type
            }
            req.from_json_string(json.dumps(params))
            self.logger.info("正在向腾讯云OCR API发送请求...")
            resp = self.client.RecognizeGeneralTextImageWarn(req)
            self.logger.info("OCR识别请求成功完成")
            self.logger.debug("响应数据: %s", self.sanitize_log_data.sanitize_log_data(resp.to_json_string(),50))
            return resp.to_json_string()

        except TencentCloudSDKException as err:
            self.logger.error(f"请求处理失败: {str(err)}", exc_info=True)
            raise err
        except Exception as e:
            self.logger.error(f"处理OCR请求时发生意外错误: {str(e)}", exc_info=True)
            raise TencentCloudSDKException("请求处理失败", str(e))
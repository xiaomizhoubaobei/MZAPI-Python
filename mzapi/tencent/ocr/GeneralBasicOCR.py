# -*- coding: utf-8 -*-

import json
import logging
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models

from ...utlis.ImageValidator import ImageValidator


class GeneralBasicOCR:
    def __init__(self, secret_id=None, secret_key=None, token=None, log_level=logging.INFO):
            """初始化腾讯云OCR客户端

            Args:
                secret_id: 腾讯云SecretId
                secret_key: 腾讯云SecretKey
                token: 临时密钥Token(可选)
                log_level: 日志级别，默认为logging.INFO
                    - logging.DEBUG: 详细调试信息
                    - logging.INFO: 一般信息(默认)
                    - logging.WARNING: 警告信息
                    - logging.ERROR: 错误信息
                    - logging.CRITICAL: 严重错误

            Raises:
                TencentCloudSDKException: 初始化失败时抛出
            """
            self.logger = logging.getLogger(__name__)
            # 确保日志级别设置正确
            self.logger.setLevel(log_level)
            # 只在没有处理器时添加处理器
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                self.logger.addHandler(handler)
            else:
                # 确保现有处理器的格式一致
                for h in self.logger.handlers:
                    h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
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
        
    def set_log_level(self, level):
        """设置日志级别
        
        Args:
            level: 日志级别 (logging.DEBUG/INFO/WARNING/ERROR/CRITICAL)
        """
        self.logger.setLevel(level)
        self.logger.info("日志级别已设置为: %s", logging.getLevelName(level))

    def recognize(self, ImageBase64=None, ImageUrl=None, Scene=None, LanguageType=None, 
                 IsPdf=None, PdfPageNumber=None, IsWords=None):
        """
            执行OCR识别
            :param ImageBase64: 图片/PDF的 Base64 值。要求图片/PDF经Base64编码后不超过 10M，分辨率建议600*800以上，支持PNG、JPG、JPEG、BMP、PDF格式。图片的 ImageUrl、ImageBase64 必须提供一个，如果都提供，只使用 ImageUrl。
            :param ImageUrl: 图片/PDF的 Url 地址。要求图片/PDF经Base64编码后不超过 10M，分辨率建议600*800以上，支持PNG、JPG、JPEG、BMP、PDF格式。图片下载时间不超过 3秒。图片存储于腾讯云的 Url 可保障更高的下载速度和稳定性，建议图片存储于腾讯云。非腾讯云存储的 Url 速度和稳定性可能受一定影响。
            :param Scene: 保留字段。
            :param LanguageType: 识别语言类型。支持自动识别语言类型，同时支持自选语言种类，默认中英文混合(zh)。各种语言均支持与英文混合的文字识别。可选值包括：
                - zh：中英混合
                - zh_rare：支持生僻字、繁体字、数字、特殊符号
                - auto：自动识别
                - mix：多语言混排场景
                - jap：日语
                - kor：韩语
                - spa：西班牙语
                - fre：法语
                - ger：德语
                - por：葡萄牙语
                - vie：越语
                - may：马来语
                - rus：俄语
                - ita：意大利语
                - hol：荷兰语
                - swe：瑞典语
                - fin：芬兰语
                - dan：丹麦语
                - nor：挪威语
                - hun：匈牙利语
                - tha：泰语
                - hi：印地语
                - ara：阿拉伯语
            :param IsPdf: 是否开启PDF识别，默认值为false，开启后可同时支持图片和PDF的识别。
            :param PdfPageNumber: 需要识别的PDF页面的对应页码，仅支持PDF单页识别，当上传文件为PDF且IsPdf参数值为true时有效，默认值为1。
            :param IsWords: 是否返回单字信息，默认false。
            :return: 识别结果，返回为JSON字符串格式，包含文本识别结果、方向信息及可能的错误信息。
            """
        try:
            self.logger.info("开始执行OCR识别")
            self.logger.debug(f"输入参数: ImageUrl={ImageUrl}, LanguageType={LanguageType}, IsPdf={IsPdf}")
            
            if ImageBase64 is None and ImageUrl is None:
                error_msg = "ImageBase64和ImageUrl必须提供一个"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
            if ImageUrl:
                self.logger.debug(f"验证图片URL: {ImageUrl}")
                self.validate_url.validate_url(ImageUrl, ["png", "jpg", "jpeg", "bmp", "pdf"])
                self.logger.debug("图片URL验证通过")

            # 准备请求参数
            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageBase64": ImageBase64,
                "ImageUrl": ImageUrl,
                "Scene": Scene,
                "LanguageType": LanguageType,
                "IsPdf": IsPdf,
                "PdfPageNumber": PdfPageNumber,
                "IsWords": IsWords
            }
            self.logger.debug(f"请求参数: {params}")
            
            req.from_json_string(json.dumps(params))
            self.logger.info("正在向腾讯云OCR API发送请求...")
            
            # 执行OCR识别
            resp = self.client.GeneralBasicOCR(req)
            self.logger.info("OCR识别请求成功完成")
            self.logger.debug(f"响应数据: {resp.to_json_string()}")  # 只记录前200字符避免日志过大
            
            return resp.to_json_string()

        except TencentCloudSDKException as err:
            self.logger.error(f"OCR识别失败: {str(err)}", exc_info=True)
            raise err
        except Exception as e:
            self.logger.error(f"处理OCR请求时发生意外错误: {str(e)}", exc_info=True)
            raise TencentCloudSDKException("OCR处理错误", str(e))

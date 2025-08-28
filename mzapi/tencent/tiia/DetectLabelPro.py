# -*- coding: utf-8 -*-

import json
import logging

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tiia.v20190529 import tiia_client, models

from ...utlis.ImageValidator import ImageValidator


class DetectLabelPro:
    def __init__(self, secret_id, secret_key, region):
        """
        :param secret_id: 用户的腾讯云账户SecretId
        :param secret_key: 用户的腾讯云账户SecretKey
        :param region: 腾讯云地域
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tiia.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = tiia_client.TiiaClient(cred, region, clientProfile)
        self.validate_url = ImageValidator.validate_url

    def detectlabelpro(self, ImageUrl, ImageBase64):
        """
        :param ImageUrl: 图片 URL 地址。
        图片限制：
        图片格式：PNG、JPG、JPEG、BMP。
        图片大小：所下载图片经Base64编码后不超过4M。图片下载时间不超过3秒。
        建议：
        图片像素：大于50*50像素，否则影响识别效果；
        长宽比：长边:短边<5；
        接口响应时间会受到图片下载时间的影响，建议使用更可靠的存储服务，推荐将图片存储在腾讯云COS。
        :param ImageBase64: 图片 Base64 编码数据。
        与ImageUrl同时存在时优先使用ImageUrl字段。
        图片限制：
        图片格式：PNG、JPG、JPEG、BMP。
        图片大小：经Base64编码后不超过4M。
        注意：图片需要Base64编码,并且要去掉编码头部。
        :return:
        """
        # 优先使用ImageUrl，验证URL参数
        if ImageUrl:
            self.logger.info(f"Validating image URL: {ImageUrl}")
            try:
                self.validate_url(ImageUrl)
                self.logger.debug(f"Image URL validation passed: {ImageUrl}")
            except ValueError as e:
                self.logger.warning(f"Image URL validation warning: {str(e)}")
                raise
        elif not ImageBase64:
            error_msg = "必须提供ImageUrl或ImageBase64参数"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        try:
            self.logger.info("Creating DetectLabelPro request")
            req = models.DetectLabelProRequest()
            params = {
                "ImageUrl": ImageUrl,
                "ImageBase64": ImageBase64
            }
            req.from_json_string(json.dumps(params))
            self.logger.debug(f"Request params: {params}")
            
            self.logger.info("Sending request to Tencent Cloud API")
            resp = self.client.DetectLabelPro(req)
            if not resp:
                self.logger.warning("Received empty response from Tencent Cloud API")
            self.logger.info("Request completed successfully")
            
            return resp.to_json_string()
        except TencentCloudSDKException as err:
            self.logger.error(f"Tencent Cloud API error: {str(err)}")
            return err
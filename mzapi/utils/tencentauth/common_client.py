# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION - DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0.
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-txc-common-client-2026-qxx"


import os
import json

from mzapi.utlis.tencentauth.abstract_client import AbstractClient
from mzapi.utlis.tencentauth.exception.tencent_cloud_sdk_exception import TencentCloudSDKException


class CommonClient(AbstractClient):
    """General client for all products.

     With CommonClient, you only need to install the tencentcloud-sdk-python-common package to access APIs of all products.
     See GitHub examples for usage details: https://github.com/TencentCloud/tencentcloud-sdk-python/tree/master/examples/common_client

    :param service: Product name
    :type service: str
    :param version: Version of API
    :type version: str
    :param credential: Request credential
    :type credential: mzapi.utlis.tencentauth.credential.Credential or mzapi.utlis.tencentauth.credential.STSAssumeRoleCredential or None
    :param region: Request region
    :type region: str
    :param profile: Request SDK profile
    :type profile: mzapi.utlis.tencentauth.profile.client_profile.ClientProfile
    """

    def __init__(self, service, version, credential, region, profile=None):
        if region is None or version is None or service is None:
            raise TencentCloudSDKException("CommonClient Parameter Error, "
                                           "credential region version service all required.")
        self._apiVersion = version
        self._service = service
        super(CommonClient, self).__init__(credential, region, profile)

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

"""华为云区域提供者

实现 RegionProviderChain，从环境变量和配置文件中发现区域信息。"""

import os
from abc import abstractmethod, ABC

from huaweicloudsdkcore.region.cache import ProfileRegionCache, EnvRegionCache
from huaweicloudsdkcore.region.region import Region


class RegionProvider(ABC):

    def __init__(self, service_name):
        self._service_name = service_name.upper()

    @abstractmethod
    def get_region(self, region_id):
        pass


class RegionProviderChain(RegionProvider):

    def __init__(self, service_name, providers):
        super().__init__(service_name)
        self._providers = providers

    def get_region(self, region_id):
        for provider in self._providers:
            region = provider.get_region(region_id)
            if region:
                return region
        return None

    @staticmethod
    def get_default_region_provider_chain(service_name):
        providers = [EnvRegionProvider(service_name), ProfileRegionProvider(service_name)]
        return RegionProviderChain(service_name, providers)


class EnvRegionProvider(RegionProvider):
    _REGION_ENV_PREFIX = "HUAWEICLOUD_SDK_REGION"

    def get_region(self, region_id):

        cache = EnvRegionCache()
        region = cache.get(self._service_name)
        if region:
            return region

        env_name = "{}_{}_{}".format(self._REGION_ENV_PREFIX, self._service_name, region_id.replace("-", "_").upper())
        endpoint = os.getenv(env_name)
        if not endpoint:
            return None

        endpoints = endpoint.split(',')
        region = Region(region_id, *endpoints)
        cache.set(self._service_name + region_id, region)
        return region


class ProfileRegionProvider(RegionProvider):
    def get_region(self, region_id):
        return ProfileRegionCache().get(self._service_name + region_id)

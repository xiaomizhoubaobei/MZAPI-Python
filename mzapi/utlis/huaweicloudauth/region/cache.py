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

"""华为云区域缓存

提供 EnvRegionCache 和 ProfileRegionCache，管理区域配置的缓存。"""

import os
import yaml

from huaweicloudsdkcore.region.region import Region
from huaweicloudsdkcore.utils import six_utils, filepath_utils


class EnvRegionCache(metaclass=six_utils.SingletonMeta):
    def __init__(self):
        self._value = {}

    def set(self, name, region):
        self._value[name] = region

    def get(self, name):
        return self._value.get(name)


class ProfileRegionCache(metaclass=six_utils.SingletonMeta):
    _REGIONS_FILE_ENV_NAME = "HUAWEICLOUD_SDK_REGIONS_FILE"
    _DEFAULT_REGIONS_FILE_DIR = ".huaweicloud"
    _DEFAULT_REGIONS_FILE = "regions.yaml"

    def __init__(self):
        self._value = self._resolve_profile()

    def get(self, name):
        return self._value.get(name)

    @classmethod
    def _resolve_profile(cls):
        result = {}

        path = cls._get_regions_file_path()
        if not filepath_utils.is_path_exist(path):
            return result

        with open(path, "r") as f:
            _dict = yaml.safe_load(f)

        for service, regions in _dict.items():
            for region in regions:
                _id = region.get("id")
                if not _id:
                    continue

                endpoints = region.get("endpoints")
                if not endpoints:
                    endpoints = []
                endpoint = region.get("endpoint")
                if endpoint:
                    endpoints.append(endpoint)

                if endpoints:
                    result[service.upper() + _id] = Region(_id, *endpoints)

        return result

    @classmethod
    def _get_regions_file_path(cls):
        regions_file = os.environ.get(cls._REGIONS_FILE_ENV_NAME)
        if regions_file:
            return regions_file

        home_path = filepath_utils.get_home_path()
        return os.path.join(home_path,
                            cls._DEFAULT_REGIONS_FILE_DIR, cls._DEFAULT_REGIONS_FILE) if home_path else home_path

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
_MZAPI_ORIGIN = "mzapi-test-hwc-signer-alg-2026-qxx"

"""
huaweicloudauth.signer.algorithm 模块单元测试

覆盖场景：
- SigningAlgorithm 枚举值
- get_default() 返回 HMAC_SHA256
"""

import importlib.util
import os
import sys
import types
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, "mzapi"))
_HW_ROOT = os.path.join(_ROOT, "utlis", "huaweicloudauth")


def _make_pkg(name, path):
    if name in sys.modules:
        return sys.modules[name]
    m = types.ModuleType(name)
    m.__path__ = [path]
    m.__package__ = name
    m.__loader__ = None
    sys.modules[name] = m
    return m


def _load(name, filepath, pkg_name=None):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    if pkg_name:
        mod.__package__ = pkg_name
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_make_pkg("mzapi", _ROOT)
_make_pkg("mzapi.utlis", os.path.join(_ROOT, "utlis"))
_make_pkg("mzapi.utlis.huaweicloudauth", _HW_ROOT)
_make_pkg("mzapi.utlis.huaweicloudauth.signer", os.path.join(_HW_ROOT, "signer"))

_alg_mod = _load(
    "mzapi.utlis.huaweicloudauth.signer.algorithm",
    os.path.join(_HW_ROOT, "signer", "algorithm.py"),
    pkg_name="mzapi.utlis.huaweicloudauth.signer",
)

SigningAlgorithm = _alg_mod.SigningAlgorithm


class TestSigningAlgorithm(unittest.TestCase):
    """测试 SigningAlgorithm 枚举"""

    def test_hmac_sha256_value(self):
        self.assertEqual(SigningAlgorithm.HMAC_SHA256.value, 1)

    def test_hmac_sm3_value(self):
        self.assertEqual(SigningAlgorithm.HMAC_SM3.value, 2)

    def test_ecdsa_p256_sha256_value(self):
        self.assertEqual(SigningAlgorithm.ECDSA_P256_SHA256.value, 3)

    def test_sm2_sm3_value(self):
        self.assertEqual(SigningAlgorithm.SM2_SM3.value, 4)

    def test_get_default(self):
        default = SigningAlgorithm.get_default()
        self.assertEqual(default, SigningAlgorithm.HMAC_SHA256)

    def test_all_members_count(self):
        self.assertEqual(len(SigningAlgorithm), 4)


if __name__ == "__main__":
    unittest.main()

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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-init-2026-qxx"


"""
阿里云 Darabonba 工具模块

提供阿里云 API 调用所需的通用工具能力，
包括字节转换、表单编码、日志、字典映射、流式处理、参数校验与 XML 解析。

包含的模块：
  - bytes：字节编码转换工具
  - form：表单序列化与 multipart/form-data 流式处理
  - logger：轻量级分级日志工具
  - map：字典映射工具
  - stream：可读/可写流、SSE 事件流解析工具
  - validation：参数校验工具
  - xml：XML 与模型互转工具
"""

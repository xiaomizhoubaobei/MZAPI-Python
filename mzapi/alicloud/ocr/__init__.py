# MIT License
#
# Copyright (c) 2026 祁筱欣
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-alicloud-ocr-2026-qxx"

"""
阿里云 OCR 服务模块

提供阿里云 OCR（光学字符识别）服务的具体实现类。
本模块封装了阿里云 OCR API 2021-07-07 版本的调用。

当前支持的识别能力：
  - RecognizeAllText：识别全部文字（通用 OCR）

使用示例：
    >>> from mzapi.alicloud.ocr import RecognizeAllText
    >>> client = RecognizeAllText(
    ...     access_key_id="your_access_key_id",
    ...     access_key_secret="your_access_key_secret",
    ...     endpoint="ocr-api.cn-hangzhou.aliyuncs.com",
    ... )
    >>> result = client.recognize(url="https://example.com/image.jpg")
    >>> print(result.body["Data"]["Content"])

API 文档参考：
    https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizealltext
"""

from .recognize_all_text import RecognizeAllText, RecognizeAllTextResponse

__all__ = [
    "RecognizeAllText",
    "RecognizeAllTextResponse",
]

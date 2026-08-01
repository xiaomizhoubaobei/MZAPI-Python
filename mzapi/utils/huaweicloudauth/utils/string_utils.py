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

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-hwc-utils-string-2026-qxx"

"""华为云字符串工具

提供字符串脱敏、格式化等字符串处理函数。"""

def camel_to_underline(camel_format):
    underline_format = ''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += _s_ if _s_.islower() or _s_.isdigit() else '_' + _s_.lower()
    return underline_format.strip('_')


def underline_to_camel(underline_format):
    camel_format = ''
    if isinstance(underline_format, str):
        for _s_ in underline_format.split('_'):
            camel_format += _s_.capitalize()
    return camel_format


def replace_invalid_character(text):
    """ Convert non-ASCII printable characters and spaces to underscores. """
    return ''.join(
        char if 32 < ord(char) <= 126 else '_'
        for char in text
    )


def mask(text: str, ratio: float = 0.7, char: str = '*') -> str:
    if not text or ratio <= 0:
        return text

    if ratio >= 1:
        return char * len(text)

    mask_len = int(len(text) * ratio)
    start = max(0, (len(text) - mask_len) // 2)
    end = min(len(text), start + mask_len)
    return text[:start] + char * mask_len + text[end:]

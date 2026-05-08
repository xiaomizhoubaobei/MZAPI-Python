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

"""华为云文件路径工具

提供路径存在性检查、Home 目录获取等文件路径操作函数。"""

import os
from sys import platform


def get_home_path():
    home_path = None
    if platform.startswith("win32"):
        home_path = os.environ.get("USERPROFILE")
    elif platform.startswith("linux") or platform.startswith("darwin"):
        home_path = os.environ.get("HOME")

    return home_path


def is_path_exist(path):
    if not path:
        return False
    return os.path.exists(path)


def ensure_file_in_rb_mode(_file):
    if isinstance(_file, str):
        if not os.path.isfile(_file):
            raise ValueError("invalid file path: " + _file)
        return open(_file, "rb")

    if not hasattr(_file, "read") or not hasattr(_file, "mode"):
        raise TypeError("invalid file type")

    if _file.mode != "rb":
        _file.close()
        raise ValueError("invalid file mode, please open the file in 'rb' mode")
    return _file

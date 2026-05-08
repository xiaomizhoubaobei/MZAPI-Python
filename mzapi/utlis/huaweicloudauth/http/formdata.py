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

"""华为云表单数据处理

提供 FormFile 类，处理 multipart/form-data 格式的文件上传。"""

import os
from mimetypes import MimeTypes
from huaweicloudsdkcore.utils.filepath_utils import ensure_file_in_rb_mode


class FormFile:
    TYPE = "file"

    def __init__(self, f, content_type=None):
        """This class is used for the formdata.

        :param f: An opened file or file path, for example, f = open("demo.txt", "rb") or f = "/tmp/log.txt"
        :type f: stream or str
        :param content_type: the content type of the file
        :type content_type: str
        """
        self._file = ensure_file_in_rb_mode(f)
        self._content_type = content_type

    def close(self):
        if hasattr(self._file, "closed") and not self._file.closed:
            self._file.close()

    @property
    def path(self):
        return self._file.name

    @property
    def abs_path(self):
        return os.path.abspath(self.path)

    @property
    def name(self):
        name = self._file.name
        if "\\" in name:
            return name.split("\\")[-1]
        elif "/" in name:
            return name.split("/")[-1]
        else:
            return name

    @property
    def content_type(self):
        mime_type = MimeTypes().guess_type(self.abs_path)
        return mime_type[0]

    def convert_to_file_tuple(self):
        return (self.name, self._file, str(self._content_type)) if self._content_type else (self.name, self._file)

    def __del__(self):
        self.close()

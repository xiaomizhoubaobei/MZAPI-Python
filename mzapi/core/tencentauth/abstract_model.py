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
_MZAPI_ORIGIN = "mzapi-txc-abstract-model-2026-qxx"


import json
import sys


class AbstractModel(object):
    """Base class for all models."""
    _headers = None

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers):
        self._headers = headers

    def _serialize(self, allow_none=False):
        d = vars(self)
        ret = {}
        for k in d:
            if k == "_headers":
                continue
            if isinstance(d[k], AbstractModel):
                r = d[k]._serialize(allow_none)
            elif isinstance(d[k], list):
                r = list()
                for tem in d[k]:
                    if isinstance(tem, AbstractModel):
                        r.append(tem._serialize(allow_none))
                    else:
                        r.append(
                            tem.encode("UTF-8") if isinstance(tem, type(u"")) and sys.version_info[0] == 2 else tem)
            else:
                r = d[k].encode("UTF-8") if isinstance(d[k], type(u"")) and sys.version_info[0] == 2 else d[k]
            if allow_none or r is not None:
                ret[k[1].upper() + k[2:]] = r
        return ret


    def _deserialize(self, params):
        return None

    def to_json_string(self, *args, **kwargs):
        """Serialize obj to a JSON formatted str, ensure_ascii is False by default"""
        if "ensure_ascii" not in kwargs:
            kwargs["ensure_ascii"] = False
        return json.dumps(self._serialize(allow_none=True), *args, **kwargs)

    def from_json_string(self, jsonStr):
        """Deserialize a JSON formatted str to a Python object

        :param jsonStr: JSON formatted string
        :type jsonStr: str
        """
        params = json.loads(jsonStr)
        self._deserialize(params)

    def __repr__(self):
        return "%s" % self.to_json_string()

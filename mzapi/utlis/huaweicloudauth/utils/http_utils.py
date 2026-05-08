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

"""华为云 HTTP 工具函数

提供参数序列化、类型转换、请求头选择等 HTTP 辅助函数。"""

import datetime
import decimal

from huaweicloudsdkcore.http.formdata import FormFile
from huaweicloudsdkcore.http.primitive_types import PRIMITIVE_TYPES
from huaweicloudsdkcore.http.bson_types import BSON_TYPES


def sanitize_for_serialization(obj):
    if obj is None:
        return None

    elif isinstance(obj, PRIMITIVE_TYPES):
        return obj

    elif isinstance(obj, decimal.Decimal):
        return obj

    elif isinstance(obj, list):
        return [sanitize_for_serialization(sub_obj) for sub_obj in obj]

    elif isinstance(obj, tuple):
        return tuple(sanitize_for_serialization(sub_obj) for sub_obj in obj)

    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    elif isinstance(obj, FormFile):
        return obj

    elif isinstance(obj, dict):
        obj_dict = obj

    else:
        obj_dict = {obj.attribute_map[attr]: getattr(obj, attr) for attr, _ in obj.openapi_types.items()
                    if getattr(obj, attr) is not None}

    return {key: sanitize_for_serialization(val) for key, val in obj_dict.items()}


def sanitize_for_bson_serialization(obj):
    if obj is None:
        return None

    elif isinstance(obj, PRIMITIVE_TYPES):
        return obj

    elif isinstance(obj, decimal.Decimal):
        return obj

    elif isinstance(obj, list):
        return [sanitize_for_bson_serialization(sub_obj) for sub_obj in obj]

    elif isinstance(obj, tuple):
        return tuple(sanitize_for_bson_serialization(sub_obj) for sub_obj in obj)

    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj

    elif isinstance(obj, FormFile):
        return obj

    elif isinstance(obj, dict):
        obj_dict = obj

    elif isinstance(obj, BSON_TYPES):
        return obj

    else:
        obj_dict = {obj.attribute_map[attr]: getattr(obj, attr) for attr, _ in obj.openapi_types.items()
                    if getattr(obj, attr) is not None}

    return {key: sanitize_for_bson_serialization(val) for key, val in obj_dict.items()}


def dict_params_to_tuple(k, v):
    tuple_list = []
    if isinstance(v, list):
        if len(v) == 0:
            tuple_list.append((k, []))
        else:
            for value in v:
                list_value_to_tuple(tuple_list, k, value)
    elif isinstance(v, dict):
        for key, value in v.items():
            temp = dict_params_to_tuple(k + '[' + str(key) + ']', value)
            if isinstance(temp, list):
                for i in temp:
                    tuple_list.append(i)
            else:
                tuple_list.append(temp)
    else:
        tuple_list.append((k, v))
    return tuple_list


def list_value_to_tuple(tuple_list, key, value):
    if isinstance(value, dict):
        for kk, vv in value.items():
            tuple_list.append(dict_params_to_tuple(key + '[' + str(kk) + ']', vv))
    elif isinstance(value, list):
        if len(value) == 0:
            tuple_list.append((key, []))
        else:
            for i in value:
                tuple_list.append((key, value[i]))
    else:
        tuple_list.append((key, value))


def parameters_to_tuples(params, collection_formats):
    new_params = []
    if collection_formats is None:
        collection_formats = {}
    for k, v in params.items() if isinstance(params, dict) else params:
        if k in collection_formats:
            collection_format = collection_formats[k]
            if collection_format == 'multi':
                new_params.extend((k, value) for value in v)
            else:
                new_params.append(
                    (k, ','.join(str(value) for value in v)))
        else:
            if isinstance(v, dict):
                value_tuples = parameters_to_tuples(v, collection_formats)
                for value_tuple in value_tuples:
                    new_params.append((k, "%s=%s" % (value_tuple[0], value_tuple[1])))
            else:
                new_params.append((k, v))
    return new_params


def select_header_accept(accepts):
    if not accepts:
        return ''
    accepts = [x.lower() for x in accepts]
    if 'application/json' in accepts:
        return 'application/json'
    else:
        return ', '.join(accepts)


def select_header_content_type(content_types):
    if not content_types:
        return 'application/json'
    content_types = [x.lower() for x in content_types]
    if 'application/json' in content_types or '*/*' in content_types:
        return 'application/json'
    else:
        return content_types[0]

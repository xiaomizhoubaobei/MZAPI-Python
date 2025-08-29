# -*- coding: utf-8 -*-

import re
from urllib.parse import urlparse
from typing import Optional, List

class ImageValidator:
    @staticmethod
    def validate_url(ImageUrl: str, allowed_extensions: List[str]) -> None:
        """验证图片URL是否符合要求
        
        Args:
            ImageUrl: 图片URL地址
            allowed_extensions: 允许的图片格式列表，如['.jpg', '.png']
        Raises:
            ValueError: 如果URL不符合要求
        """
        # 验证图片格式
        path = urlparse(ImageUrl).path
        if not any(path.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"图片格式不支持，仅支持: {', '.join(allowed_extensions)}")
        
        # 验证URL格式
        if not re.match(r'^https?://', ImageUrl):
            raise ValueError("图片URL必须以http://或https://开头")

    @staticmethod
    def validate_id(id_to_check: str, allowed_ids: List[str], id_name: str = "ID") -> None:
        """验证ID是否在允许的列表中
        
        Args:
            id_to_check: 要验证的ID
            allowed_ids: 允许的ID列表
            id_name: ID的名称(用于错误消息)
        Raises:
            ValueError: 如果ID不在允许的列表中
        """
        if id_to_check not in allowed_ids:
            raise ValueError(f"无效的{id_name}，允许的{id_name}有: {', '.join(allowed_ids)}")
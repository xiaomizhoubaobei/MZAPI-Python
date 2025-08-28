# -*- coding: utf-8 -*-

import re
from urllib.parse import urlparse

class ImageValidator:
    @staticmethod
    def validate_url(ImageUrl):
        """验证图片URL是否符合要求
        
        Args:
            ImageUrl (str): 图片URL地址
            
        Raises:
            ValueError: 如果URL不符合要求
        """
        # 验证图片格式
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
        path = urlparse(ImageUrl).path
        if not any(path.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"图片格式不支持，仅支持: {', '.join(allowed_extensions)}")
        
        # 验证URL格式
        if not re.match(r'^https?://', ImageUrl):
            raise ValueError("图片URL必须以http://或https://开头")
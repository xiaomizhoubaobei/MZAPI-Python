# coding: utf-8
#
# Copyright 2026 祁筱欣
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
华为云 Project ID 辅助类

用于从华为云 IAM 服务自动查询项目ID
"""
from typing import Dict, Optional


class ProjectIdHelper:
    """
    华为云 Project ID 辅助类
    
    提供从 IAM 服务自动查询项目ID的功能
    
    示例项目ID: 0b312c45c300f5b22fb6c0112091933a
    """
    
    # 项目ID缓存，避免重复查询
    _cache: Dict[str, str] = {}
    
    @staticmethod
    def get_project_id(
        access_key: str,
        secret_key: str,
        region: str,
        project_id: Optional[str] = None
    ) -> str:
        """
        获取 project_id
        
        :param access_key: 华为云 Access Key ID
        :param secret_key: 华为云 Secret Access Key
        :param region: 区域ID
        :param project_id: 用户手动指定的项目ID（可选）
        :return: project_id
        :raises Exception: 当查询失败或找到多个项目时抛出异常
        """
        # 如果用户显式提供了 project_id，直接使用
        if project_id:
            return project_id
        
        # 从缓存中获取
        cache_key = f"{access_key}:{region}"
        if cache_key in ProjectIdHelper._cache:
            return ProjectIdHelper._cache[cache_key]
        
        # 从 IAM 服务查询 project_id
        project_id = ProjectIdHelper._query_from_iam(access_key, secret_key, region)
        
        # 缓存结果
        ProjectIdHelper._cache[cache_key] = project_id
        
        return project_id
    
    @staticmethod
    def _query_from_iam(access_key: str, secret_key: str, region: str) -> str:
        """
        从 IAM 服务查询 project_id
        
        响应格式:
        {
            "projects": [
                {
                    "domain_id": "65382450e8f64ac0870cd180d14e684b",
                    "is_domain": false,
                    "parent_id": "65382450e8f64ac0870cd180d14e684b",
                    "name": "cn-north-4",
                    "description": "",
                    "links": {
                        "next": null,
                        "previous": null,
                        "self": "https://www.example.com/v3/projects/a4a5d4098fb4474fa22"
                    },
                    "id": "a4a5d4098fb4474fa22cd05f897d6b99",
                    "enabled": true
                }
            ],
            "links": {
                "next": null,
                "previous": null,
                "self": "https://www.example.com/v3/projects"
            }
        }
        
        :param access_key: 华为云 Access Key ID
        :param secret_key: 华为云 Secret Access Key
        :param region: 区域ID
        :return: project_id
        :raises Exception: 当查询失败或找到多个项目时抛出异常
        """
        from huaweicloudsdkcore.auth.credentials import BasicCredentials
        from huaweicloudsdkcore.http.http_config import HttpConfig
        from huaweicloudsdkcore.http.http_client import HttpClient
        from huaweicloudsdkcore.http.http_handler import HttpHandler
        from huaweicloudsdkcore.exceptions.exception_handler import DefaultExceptionHandler
        from huaweicloudsdkcore.auth.internal import IamHelper
        import logging
        
        # 创建 BasicCredentials 实例（不传入 project_id，让它自动查询）
        credentials = BasicCredentials(ak=access_key, sk=secret_key)
        
        # 创建 HTTP 配置
        config = HttpConfig.get_default_config()
        
        # 创建 HTTP 处理器
        http_handler = HttpHandler()
        
        # 创建异常处理器
        exception_handler = DefaultExceptionHandler()
        
        # 创建日志记录器
        logger = logging.getLogger('HuaweiCloud-SDK-ProjectIdHelper')
        logger.propagate = False
        
        # 创建 HTTP 客户端
        http_client = HttpClient(config, http_handler, exception_handler, logger)
        
        try:
            # 获取 IAM 端点
            iam_endpoint = IamHelper.get_iam_endpoint(region)
            
            # 构造 IAM 请求
            req = IamHelper.get_keystone_list_projects_request(config, iam_endpoint, region_id=region)
            
            # 发送请求
            logger.info("从 IAM 服务查询 project_id: %s", iam_endpoint)
            response = http_client.do_request_sync(credentials.process_auth_request(req, http_client).result())
            
            # 解析响应
            import json
            data = json.loads(response.content)
            projects = data.get("projects", [])
            
            if not projects:
                trace_id = response.headers.get("X-IAM-Trace-Id")
                raise Exception(
                    f"在区域 '{region}' 中未找到项目，请确认项目存在，X-IAM-Trace-Id={trace_id}"
                )
            
            if len(projects) > 1:
                project_ids = ",".join([p["id"] for p in projects])
                raise Exception(
                    f"找到多个项目ID: [{project_ids}]，请手动指定 project_id"
                )
            
            project = projects[0]
            project_id = project["id"]
            
            logger.info("成功获取 project_id: %s", project_id)
            logger.info("项目详情: name=%s, domain_id=%s, enabled=%s", 
                       project.get("name"), project.get("domain_id"), project.get("enabled"))
            
            return project_id
            
        except Exception as e:
            if "Exception" in str(type(e)):
                raise Exception(f"从 IAM 查询 project_id 失败: {e}")
            else:
                raise Exception(f"从 IAM 查询 project_id 失败: {e}")
    
    @staticmethod
    def clear_cache():
        """
        清空项目ID缓存
        
        当需要强制重新查询项目ID时使用
        """
        ProjectIdHelper._cache.clear()
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
_MZAPI_ORIGIN = "mzapi-aliyun-gateway-spi-client-2026-qxx"


"""
网关 SPI 客户端模块

实现阿里云网关 SPI（Service Provider Interface，服务提供者接口）的拦截器客户端，
为请求处理链路提供配置修改、请求修改与响应修改三个拦截钩子，
并同时支持同步与异步两种调用方式。

包含的类：
  - Client：网关 SPI 客户端
"""

from alibabacloud_gateway_spi import models as gateway_spi_models


class Client:
    """阿里云网关 SPI 拦截器客户端。

    提供配置修改（modify_configuration）、请求修改（modify_request）与
    响应修改（modify_response）三个核心拦截钩子，每个钩子均包含
    同步与异步两种实现，供上层网关实现类继承并覆写。
    """

    def __init__(self):
        """初始化客户端实例。"""

    def modify_configuration(
        self,
        context: gateway_spi_models.InterceptorContext,
        attribute_map: gateway_spi_models.AttributeMap,
    ) -> None:
        """同步修改网关配置。

        在请求处理前根据拦截上下文与属性映射调整网关配置。

        Args:
            context: 拦截上下文，包含请求、配置与响应信息。
            attribute_map: 属性映射，用于传递附加信息。

        Raises:
            Exception: 该接口为抽象接口，需由子类覆写实现。
        """
        raise Exception('Un-implemented')

    async def modify_configuration_async(
        self,
        context: gateway_spi_models.InterceptorContext,
        attribute_map: gateway_spi_models.AttributeMap,
    ) -> None:
        """异步修改网关配置。

        与 modify_configuration 功能一致，以异步方式在请求处理前
        根据拦截上下文与属性映射调整网关配置。

        Args:
            context: 拦截上下文，包含请求、配置与响应信息。
            attribute_map: 属性映射，用于传递附加信息。

        Raises:
            Exception: 该接口为抽象接口，需由子类覆写实现。
        """
        raise Exception('Un-implemented')

    def modify_request(
        self,
        context: gateway_spi_models.InterceptorContext,
        attribute_map: gateway_spi_models.AttributeMap,
    ) -> None:
        """同步修改请求。

        在请求发送前根据拦截上下文与属性映射对请求进行加工处理，
        如补充请求头、签名等信息。

        Args:
            context: 拦截上下文，包含请求、配置与响应信息。
            attribute_map: 属性映射，用于传递附加信息。

        Raises:
            Exception: 该接口为抽象接口，需由子类覆写实现。
        """
        raise Exception('Un-implemented')

    async def modify_request_async(
        self,
        context: gateway_spi_models.InterceptorContext,
        attribute_map: gateway_spi_models.AttributeMap,
    ) -> None:
        """异步修改请求。

        与 modify_request 功能一致，以异步方式在请求发送前
        对请求进行加工处理。

        Args:
            context: 拦截上下文，包含请求、配置与响应信息。
            attribute_map: 属性映射，用于传递附加信息。

        Raises:
            Exception: 该接口为抽象接口，需由子类覆写实现。
        """
        raise Exception('Un-implemented')

    def modify_response(
        self,
        context: gateway_spi_models.InterceptorContext,
        attribute_map: gateway_spi_models.AttributeMap,
    ) -> None:
        """同步修改响应。

        在响应返回后根据拦截上下文与属性映射对响应进行加工处理。

        Args:
            context: 拦截上下文，包含请求、配置与响应信息。
            attribute_map: 属性映射，用于传递附加信息。

        Raises:
            Exception: 该接口为抽象接口，需由子类覆写实现。
        """
        raise Exception('Un-implemented')

    async def modify_response_async(
        self,
        context: gateway_spi_models.InterceptorContext,
        attribute_map: gateway_spi_models.AttributeMap,
    ) -> None:
        """异步修改响应。

        与 modify_response 功能一致，以异步方式在响应返回后
        对响应进行加工处理。

        Args:
            context: 拦截上下文，包含请求、配置与响应信息。
            attribute_map: 属性映射，用于传递附加信息。

        Raises:
            Exception: 该接口为抽象接口，需由子类覆写实现。
        """
        raise Exception('Un-implemented')

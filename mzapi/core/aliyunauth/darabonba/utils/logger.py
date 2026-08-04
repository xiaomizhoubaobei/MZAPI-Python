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
_MZAPI_ORIGIN = "mzapi-aliyun-utils-logger-2026-qxx"


"""
日志工具模块

提供轻量级分级日志打印能力，支持 DEBUG、INFO、WARNING、ERROR、CRITICAL 五个级别，
可通过 set_level 动态调整当前输出级别，通过 format 自定义日志格式。

包含的类：
  - Logger：分级日志工具类，提供各级别的日志打印方法
"""


class Logger:
    """轻量级分级日志工具类。

    提供按级别过滤的日志输出，级别低于当前设置时会被过滤。
    """

    # 日志级别名称与数值的映射关系
    levels = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }

    # 当前日志输出级别，默认输出 DEBUG 及以上级别
    current_level = levels['DEBUG']
    # 日志输出格式模板
    log_format = "{levelname}: {message}"

    @staticmethod
    def log(level_name, message):
        """按指定级别输出日志，低于当前级别时忽略。

        Args:
            level_name: 日志级别名称（DEBUG/INFO/WARNING/ERROR/CRITICAL）。
            message: 日志内容。
        """
        if Logger.levels[level_name] >= Logger.current_level:
            print(Logger.log_format.format(levelname=level_name, message=message))

    @staticmethod
    def info(message):
        """输出 INFO 级别日志。"""
        Logger.log('INFO', message)

    @staticmethod
    def debug(message):
        """输出 DEBUG 级别日志。"""
        Logger.log('DEBUG', message)

    @staticmethod
    def warning(message):
        """输出 WARNING 级别日志。"""
        Logger.log('WARNING', message)

    @staticmethod
    def error(message):
        """输出 ERROR 级别日志。"""
        Logger.log('ERROR', message)

    @staticmethod
    def critical(message):
        """输出 CRITICAL 级别日志。"""
        Logger.log('CRITICAL', message)

    @staticmethod
    def set_level(level_name):
        """设置当前日志输出级别。

        Args:
            level_name: 目标级别名称，须为 levels 中的合法级别。

        Raises:
            ValueError: 当级别名称非法时抛出。
        """
        if level_name in Logger.levels:
            Logger.current_level = Logger.levels[level_name]
        else:
            raise ValueError(f"Invalid log level: {level_name}")

    @staticmethod
    def format(log_format):
        """自定义日志输出格式模板。

        Args:
            log_format: 日志格式模板字符串，支持 {levelname}、{message} 占位符。
        """
        Logger.log_format = log_format

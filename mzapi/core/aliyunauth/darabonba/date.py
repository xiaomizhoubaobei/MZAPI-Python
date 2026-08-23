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
_MZAPI_ORIGIN = "mzapi-aliyun-darabonba-date-2026-qxx"


"""
日期工具模块

提供日期解析、格式化、时间戳转换以及日期加减与差值计算的能力，
支持 Java SimpleDateFormat 风格的格式化占位符（如 yyyy、MM、dd 等）。
"""

from datetime import datetime, timedelta


class Date:
    """日期对象，封装 datetime，提供 darabonba 风格的日期操作接口。"""

    def __init__(self, date_input):
        """初始化日期对象，尝试使用多种常见格式解析输入的日期字符串。

        Args:
            date_input: 待解析的日期字符串。

        Raises:
            ValueError: 当所有支持的格式都无法解析该字符串时抛出。
        """
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f %z %Z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]

        self.date = None
        for format in formats:
            try:
                self.date = datetime.strptime(date_input, format)
                break
            except ValueError:
                continue

        if self.date is None:
            raise ValueError(f"unable to parse date: {date_input}")

    def strftime(self, layout):
        """按指定模板格式化日期，支持 Java 风格占位符（yyyy、MM、dd 等）。

        Args:
            layout: 格式化模板字符串。

        Returns:
            格式化后的日期字符串。
        """
        layout = layout.replace("yyyy", "%Y")
        layout = layout.replace("MM", "%m")
        layout = layout.replace("dd", "%d")
        layout = layout.replace("hh", "%H")
        layout = layout.replace("mm", "%M")
        layout = layout.replace("ss", "%S")
        layout = layout.replace("a", "%p")
        layout = layout.replace("EEEE", "%A")
        layout = layout.replace("E", "%a")
        return self.date.strftime(layout)

    def timestamp(self):
        """返回当前日期的 Unix 时间戳（秒）。

        Returns:
            整数形式的时间戳。
        """
        return int(self.date.timestamp())

    def sub(self, unit, amount):
        """从当前日期减去指定单位的时间量。

        Args:
            unit: 时间单位（second、minute、hour、day、week、month、year 及其复数形式）。
            amount: 减去的数量。

        Returns:
            计算后的新 Date 对象。
        """
        if unit in ["second", "seconds"]:
            return Date((self.date - timedelta(seconds=amount)).isoformat())
        elif unit in ["minute", "minutes"]:
            return Date((self.date - timedelta(minutes=amount)).isoformat())
        elif unit in ["hour", "hours"]:
            return Date((self.date - timedelta(hours=amount)).isoformat())
        elif unit in ["day", "days"]:
            return Date((self.date - timedelta(days=amount)).isoformat())
        elif unit in ["week", "weeks"]:
            return Date((self.date - timedelta(weeks=amount)).isoformat())
        elif unit in ["month", "months"]:
            return Date((self.date.replace(month=self.date.month - amount)).isoformat())
        elif unit in ["year", "years"]:
            return Date((self.date.replace(year=self.date.year - amount)).isoformat())

    def add(self, unit, amount):
        """在当前日期上加上指定单位的时间量。

        Args:
            unit: 时间单位（second、minute、hour、day、week、month、year 及其复数形式）。
            amount: 增加的数量。

        Returns:
            计算后的新 Date 对象。
        """
        if unit in ["second", "seconds"]:
            return Date((self.date + timedelta(seconds=amount)).isoformat())
        elif unit in ["minute", "minutes"]:
            return Date((self.date + timedelta(minutes=amount)).isoformat())
        elif unit in ["hour", "hours"]:
            return Date((self.date + timedelta(hours=amount)).isoformat())
        elif unit in ["day", "days"]:
            return Date((self.date + timedelta(days=amount)).isoformat())
        elif unit in ["week", "weeks"]:
            return Date((self.date + timedelta(weeks=amount)).isoformat())
        elif unit in ["month", "months"]:
            new_month = self.date.month + amount
            new_year = self.date.year + (new_month - 1) // 12
            new_month = (new_month - 1) % 12 + 1
            if self.date.day > 28:
                if new_month == 2:
                    new_day = min(self.date.day, 29)
                    if new_day == 29 and not (new_year % 4 == 0 and (new_year % 100 != 0 or new_year % 400 == 0)):
                        new_day = 28
                else:
                    new_day = min(self.date.day, [31, 30][new_month % 2])
            else:
                new_day = self.date.day

            new_date = self.date.replace(year=new_year, month=new_month, day=new_day)
            return Date(new_date.isoformat())
        elif unit in ["year", "years"]:
            return Date((self.date.replace(year=self.date.year + amount)).isoformat())

    def diff(self, unit, diff_date):
        """计算当前日期与目标日期的差值。

        Args:
            unit: 差值单位（second、minute、hour、day、week、month、year）。
            diff_date: 目标 Date 对象。

        Returns:
            以指定单位表示的整数值差。
        """
        if unit in ["second", "seconds"]:
            return int((self.date - diff_date.date).total_seconds())
        elif unit in ["minute", "minutes"]:
            return int((self.date - diff_date.date).total_seconds() / 60)
        elif unit in ["hour", "hours"]:
            return int((self.date - diff_date.date).total_seconds() / 3600)
        elif unit in ["day", "days"]:
            return int((self.date - diff_date.date).total_seconds() / (3600 * 24))
        elif unit in ["week", "weeks"]:
            return int((self.date - diff_date.date).total_seconds() / (3600 * 24 * 7))
        elif unit in ["month", "months"]:
            return (self.date.year - diff_date.date.year) * 12 + (self.date.month - diff_date.date.month)
        elif unit in ["year", "years"]:
            return self.date.year - diff_date.date.year

    def hour(self):
        """返回小时数（0-23）。"""
        return self.date.hour

    def minute(self):
        """返回分钟数（0-59）。"""
        return self.date.minute

    def second(self):
        """返回秒数（0-59）。"""
        return self.date.second

    def month(self):
        """返回月份（1-12）。"""
        return self.date.month

    def day_of_month(self):
        """返回当月第几天（1-31）。"""
        return self.date.day

    def day_of_week(self):
        """返回星期几，以周日为 7、周一为 1。"""
        weekday = self.date.weekday() + 1  # Monday is 0 in python, so
        return weekday % 7 or 7  # Convert to Sunday = 7

    def week_of_year(self):
        """返回该日期在一年中的第几周（ISO 标准）。"""
        return self.date.isocalendar()[1]

    def year(self):
        """返回年份。"""
        return self.date.year

    def UTC(self):
        """返回带时区信息的完整日期时间字符串。"""
        return self.date.strftime("%Y-%m-%d %H:%M:%S.%f %z %Z")

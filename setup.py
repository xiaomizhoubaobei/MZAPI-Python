#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mzapi-python",  # 安装时使用的名称
    version="0.0.2",
    author="祁潇潇",
    author_email="qixiaoxin@stu.sqxy.edu.cn",
    description="MZAPI的python的SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaomizhoubaobei/MZAPI-Python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7",
    install_requires=[
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ]
    },
    keywords="API SDK MZAPI PYTHON",
    project_urls={
        "Bug Reports": "https://github.com/xiaomizhoubaobei/MZAPI-Python/issues",
        "Source": "https://github.com/xiaomizhoubaobei/MZAPI-Python",
        "Homepage": "https://pypi.org/project/mzapi-python",
        "Download" :"https://pypi.org/project/mzapi-python/#files",
        "Changelog" : "https://github.com/xiaomizhoubaobei/MZAPI-Python/CHANGELOG.md",
        "Documentation" : "https://docs.mizhoubaobei.top",
        "GitHub" : "https://github.com/xiaomizhoubaobei/MZAPI-Python",
    },
)
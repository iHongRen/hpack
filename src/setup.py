# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
from setuptools import setup, find_packages

setup(
    name='hpack',
    version='1.0.0',
    packages=find_packages(),
    package_data={
        '': ['*', '**/*'],  # 包含所有包下的所有文件和子目录文件
    },
    entry_points={
        'console_scripts': [
            'hpack = hpack.main:main',
        ],
    },
    install_requires=[
        # 列出项目依赖的库，如 'requests'
        'json5',
        'segno'
    ],
    python_requires='>=3.7',  # 指定 Python 版本要求
)
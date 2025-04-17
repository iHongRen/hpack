# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='hpack',
    version='0.1',
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
        'oss2',
        'json5',
        'segno'
    ],
    python_requires='>=3.6',  # 指定 Python 版本要求
)
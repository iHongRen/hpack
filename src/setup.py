# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os

from setuptools import find_packages, setup

from harmony_hpack.version import __version__

current_dir = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(current_dir, '..', 'README.md')

# 读取 README.md 文件内容
try:
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "README file not found."

setup(
    name='harmony-hpack',
    version=__version__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        '': ['*', '**/*'],  # 包含所有包下的所有文件和子目录文件
    },
    entry_points={
        'console_scripts': [
            'hpack = harmony_hpack.main:main',
        ],
    },
    install_requires=[
        # 列出项目依赖的库，如 'requests'
        'json5',
        'segno',
        'prompt_toolkit'
    ],
    python_requires='>=3.7',  # 指定 Python 版本要求
)
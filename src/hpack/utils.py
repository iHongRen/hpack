# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import hashlib
import os
import shutil
import sys
from datetime import datetime

# 定义颜色代码
RED = '\033[31m'
BLUE = '\033[34m'
ENDC = '\033[0m'


def printError(message, end='\n'):
    print(RED + message + ENDC, end=end)


def printSuccess(message, end='\n'):
    print(BLUE + message + ENDC, end=end)


def isWin():
    return sys.platform.startswith('win')


def format_size(size):
    power = 1024
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power:
        size /= power
        n += 1
    return f"{size:.0f}{power_labels[n]}"


def get_directory_size(directory):
    total_size = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.hap') and not file.endswith('.hsp'):
                continue
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except FileNotFoundError:
                continue
    return format_size(total_size)
    

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()




def timeit(func, printName=''):
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} 开始执行")
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        execution_time = end_time - start_time
        
        total_seconds = execution_time.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        print(f"{ printName if printName else func.__name__} 执行耗时 {minutes} 分钟 {seconds:.2f} 秒")
    
        return result

    return wrapper


def get_python_command():
    # 检查系统中是否存在 python3
    if shutil.which("python3"):
        return "python3"
    # 如果没有 python3，则使用 python
    elif shutil.which("python"):
        return "python"
    else:
        raise EnvironmentError("未找到可用的 Python 解释器，请确保已安装 Python。")
   
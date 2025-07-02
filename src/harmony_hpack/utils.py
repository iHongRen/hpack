# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import hashlib
import os
import shutil
import sys
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style


def isWin():
    return sys.platform.startswith('win')

# 定义颜色代码
RED = '\033[31m' if isWin() else ''
BLUE = '\033[34m' if isWin() else ''
ENDC = '\033[0m' if isWin() else ''


def printError(message, end='\n'):
    print(RED + message + ENDC, end=end)


def printSuccess(message, end='\n'):
    print(BLUE + message + ENDC, end=end)


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



def timeit(printName=''):
    def decorator(func):
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
    return decorator


def get_python_command():
    # 返回当前正在运行的 Python 解释器的绝对路径。
    # 这是最可靠的方式，可以确保子进程使用与当前脚本相同的解释器，
    # 无论是在全局环境、虚拟环境，还是在 Windows/Linux/macOS。
    return sys.executable
   


def select_items(items, prompt_text="请选择:"):
    if len(items) == 0:
        return None
    
    if len(items) == 1:
        return 0
     
    current_index = 0
    kb = KeyBindings()

    @kb.add("up")
    def _(event):
        nonlocal current_index
        current_index = max(0, current_index - 1)

    @kb.add("down")
    def _(event):
        nonlocal current_index
        current_index = min(len(items) - 1, current_index + 1)

    @kb.add("enter")
    def _(event):
        event.app.exit(result=items[current_index])

    style = Style.from_dict({
        'selected': 'fg:ansibrightblue',
        'normal': 'fg:ansigray',
        'prompt': 'fg:ansigreen'
    })

    session = PromptSession()

    def get_display_text():
        return [(('class:prompt', prompt_text + '\n'))] + [
            (('class:selected' if i == current_index else 'class:normal'), f"{'❯' if i == current_index else ' '} {option}\n")
            for i, option in enumerate(items)
        ]

    session.prompt(get_display_text, key_bindings=kb, style=style)

    # 清空 prompt_text 和选项区域
    print("\033[F" * (len(items) + 2), end="")  # 回退光标到 prompt_text 开始位置并覆盖

    return current_index
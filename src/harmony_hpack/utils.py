# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style


def isWin():
    return sys.platform.startswith('win')

# 定义颜色代码
RED = '\033[31m' if not isWin() else ''
BLUE = '\033[34m' if not isWin() else ''
ENDC = '\033[0m' if not isWin() else ''


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


def decode_cmd_output(value):
    """Normalize subprocess stdout/stderr to text."""
    if value is None:
        return ''
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return str(value)


def format_cmd_error(error, prefix):
    """Include command stderr/stdout in failure messages.

    subprocess.CalledProcessError.__str__ only reports the exit code, so
    captured PackFile.py / java output is otherwise swallowed.
    """
    parts = [f"{prefix}: {error}"]
    stderr = decode_cmd_output(getattr(error, 'stderr', None)).strip()
    stdout = decode_cmd_output(getattr(error, 'stdout', None)).strip()
    if stderr:
        parts.append(f"stderr:\n{stderr}")
    if stdout:
        parts.append(f"stdout:\n{stdout}")
    return '\n'.join(parts)


def resolve_file_path(path, base_dir):
    """Resolve an absolute path, or a path relative to base_dir.

    Uses os.path.isabs so Linux does not treat a leading '\\' as absolute
    (the previous startswith('/', '\\\\') check was Windows-oriented).
    """
    if path is None:
        return None
    path = os.path.expanduser(str(path).strip())
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.normpath(path)
    if base_dir:
        return os.path.normpath(os.path.join(base_dir, path))
    return os.path.normpath(path)


def missing_file_message(label, looked_in):
    paths = looked_in if isinstance(looked_in, (list, tuple)) else [looked_in]
    shown = ', '.join(os.path.abspath(p) if p else '<empty>' for p in paths)
    return f"未找到{label}，已查找: {shown}"


def require_existing_file(path, base_dir, label):
    """Resolve path and raise a looked-in message when the file is missing."""
    if not path:
        raise Exception(f"{label} 路径未配置")
    resolved = resolve_file_path(path, base_dir)
    if resolved and os.path.isfile(resolved):
        return resolved
    raise Exception(missing_file_message(label, resolved or path))


def interpret_will_pack_result(returncode, stdout, stderr, command):
    """Decide whether willPack output is usable, or raise with stderr."""
    stdout = decode_cmd_output(stdout).strip()
    stderr = decode_cmd_output(stderr).strip()
    if returncode == 0:
        return stdout, None
    if stdout:
        warning = f"执行 willPack 退出码 {returncode}，已捕获 stdout，继续打包。"
        if stderr:
            warning += f"\nwillPack / PackFile.py stderr:\n{stderr}"
        return stdout, warning
    error = subprocess.CalledProcessError(
        returncode, command, output=stdout, stderr=stderr
    )
    raise Exception(format_cmd_error(error, "执行 willPack 失败"))


def packfile_env(extra_env=None):
    """Force UTF-8 IO so PackFile.py Chinese output is stable on Linux C locale."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    return env


def missing_modules_message(build_dir):
    looked = os.path.abspath(build_dir)
    if not os.path.isdir(build_dir):
        return f"无法获取打包模块信息：构建目录不存在，已查找: {looked}"
    return (
        f"无法获取打包模块信息：在 {looked} 中未找到 .hap/.hsp 文件。"
        f"通常是构建或签名未产出包，请查看上方 willPack / hvigorw / 签名命令的 stderr，"
        f"不要仅根据签名文件配置判断。"
    )


def resolve_hvigorw_command():
    """Locate hvigorw.

    packSign uses shell=isWin() so Windows can find hvigorw.bat in cwd.
    Linux does not search cwd unless '.' is on PATH, so also look at ./hvigorw.
    """
    found = shutil.which('hvigorw')
    if found:
        return found

    candidates = [
        os.path.join(os.getcwd(), 'hvigorw'),
        os.path.join(os.getcwd(), 'hvigorw.bat'),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate

    raise Exception(missing_file_message('hvigorw', ['hvigorw'] + candidates))



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
# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os
import sys
import importlib.util
import shutil
import subprocess  
import json
# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path
sys.path.append(current_dir)

from version import __version__
from pack_sign import packSign
from sign_info import signInfo
from toolConfig import ToolConfig
from utils import timeit

def get_python_command():
    # 检查系统中是否存在 python3
    if shutil.which("python3"):
        return "python3"
    # 如果没有 python3，则使用 python
    elif shutil.which("python"):
        return "python"
    else:
        raise EnvironmentError("未找到可用的 Python 解释器，请确保已安装 Python。")
        
def init_command():
    hpack_dir = os.path.join(os.getcwd(), ToolConfig.HpackDir)
    if os.path.exists(hpack_dir):
        print("init 失败：hpack 目录已存在。")
        return
    try:
        os.makedirs(hpack_dir)
        absPath = os.path.dirname(os.path.abspath(__file__))
        template_file_path = os.path.join(absPath, 'config.py')
        config_file_path = os.path.join(hpack_dir, 'config.py')

        # 复制配置文件
        shutil.copy2(template_file_path, config_file_path)

        # 获取 sign 文件夹路径
        sign_folder_path = os.path.join(absPath, 'sign')
        target_sign_folder_path = os.path.join(hpack_dir, 'sign')

        if os.path.exists(sign_folder_path):
            # 复制 sign 文件夹
            shutil.copytree(sign_folder_path, target_sign_folder_path)
        else:
            print(sign_folder_path)
            print("警告：sign 文件夹不存在，无法复制。")

        # 复制 Packfile.py 文件
        pack_file_path = os.path.join(absPath, 'Packfile.py')
        target_pack_file_path = os.path.join(hpack_dir, 'Packfile.py')
        shutil.copy2(pack_file_path, target_pack_file_path)

        print("init 成功：已在 hpack 目录下创建 config.py 文件并复制 sign 文件夹和 Packfile.py 文件。")
    except OSError as e:
        print(f"init 失败：创建目录或文件时出错 - {e}")
    except shutil.Error as e:
        print(f"init 失败：复制文件或文件夹时出错 - {e}")

@timeit
def pack_command(desc):
    config = get_config()
    if config is None:
        return

    # 获取 Packfile.py 的路径
    pack_file_path = os.path.join(os.getcwd(), ToolConfig.HpackDir, 'Packfile.py')

    # 检查 Packfile.py 是否存在
    if not os.path.exists(pack_file_path):
        print(f"Packfile.py 文件不存在: {pack_file_path}")
        return

    # 获取 Python 命令
    python_cmd = get_python_command()

    # 执行 Packfile.py 的 packBefore 函数
    try:
        subprocess.run([python_cmd, pack_file_path, '--before'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"执行 Packfile.py 的 packBefore 时出错: {e}")
        return

    # 执行 packSign 和 signInfo
    packSign(config)
    result = signInfo(config, desc)  # 获取返回的 JSON 数据

    # 执行 Packfile.py 的 packAfter 函数，并传递 JSON 数据
    try:
        if result:
            result_json = json.dumps(result, ensure_ascii=False, indent=4)  # 将字典转换为 JSON 字符串
            process = subprocess.run(
                [python_cmd, pack_file_path, '--after'], 
                input=result_json,  # 将 JSON 数据通过标准输入传递
                text=True,  # 指定输入为文本
                check=True
            )
        else:
            print("signInfo 未返回有效的结果，跳过 packAfter.")
    except subprocess.CalledProcessError as e:
        print(f"执行 PackFile.py 的 packAfter 时出错: {e}")

def get_config():
    config_file_path = os.path.join(os.getcwd(), ToolConfig.HpackDir, 'config.py')
    if os.path.exists(config_file_path):
        try:
            # 获取 config.py 文件的规格
            spec = importlib.util.spec_from_file_location("config", config_file_path)
            # 创建模块对象
            config_module = importlib.util.module_from_spec(spec)
            # 执行模块代码
            spec.loader.exec_module(config_module)

            # 获取 Config 类
            Config = getattr(config_module, 'Config')
            return Config
        except Exception as e:
            print(f"读取 config.py 文件时出错 - {e}")
    else:
        print("pack 失败：hpack/config.py 文件不存在，请先执行 hpack init。")
    return None


def show_version():
    print(f"hpack 版本: {__version__}")


def show_help():
    help_text = f"""
使用方法: hpack [选项] [命令]

选项:
  -v, --version  显示版本信息
  -h, --help     显示帮助信息

命令:
  init           初始化 hpack 目录并创建配置文件
  pack [desc]    执行打包签名和上传, 更新说明可选

版本: {__version__}
"""
    print(help_text)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-v', '--version']:
            show_version()
        elif sys.argv[1] in ['-h', '--help']:
            show_help()
        elif sys.argv[1] == 'init':
            init_command()
        elif sys.argv[1] == 'pack':
            if len(sys.argv) > 2:
                desc = sys.argv[2]
            else:
                desc = ""
            pack_command(desc)
        else:
            print("无效的命令或选项，请使用 'hpack -h' 查看帮助信息。")
    else:
        print("无效的命令，请使用 'hpack -h' 查看帮助信息。")


if __name__ == "__main__":
    main()

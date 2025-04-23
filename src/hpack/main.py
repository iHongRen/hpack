# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import importlib.util
import json
import os
import shutil
import subprocess
import sys

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path
sys.path.append(current_dir)

from packSign import pack_sign
from signInfo import sign_info
from template import handle_template
from toolConfig import ToolConfig
from utils import get_python_command, printError, printSuccess, timeit
from version import __version__


def init_command():
    """初始化 hpack 目录"""
    hpack_dir = ToolConfig.HpackDir
    if os.path.exists(hpack_dir):
        printError("init 失败：hpack 目录已存在。")
        return

    try:
        os.makedirs(hpack_dir)
        absPath = os.path.dirname(os.path.abspath(__file__))

        # 复制配置文件
        shutil.copy2(os.path.join(absPath, 'config.py'), os.path.join(hpack_dir, 'config.py'))

        # 复制 sign 文件夹
        shutil.copytree(os.path.join(absPath, 'sign'), os.path.join(hpack_dir, 'sign'))

        # 复制 PackFile.py 文件
        shutil.copy2(os.path.join(absPath, 'PackFile.py'), os.path.join(hpack_dir, 'PackFile.py'))

        printSuccess("hpack 初始化完成。请修改配置：", end='')
        print("""
hpack/
  config.py # 配置文件
  sign/  # 替换自己的签名证书文件
  Packfile.py 打包完成后的回调文件
""")
    except Exception as e:
        printError(f"init 失败 - {e}")

@timeit
def pack_command(desc):
    """主打包逻辑"""
    Config = get_config()
    if Config is None:
        return

    # 执行打包流程
    willPack_output = execute_will_pack()
    packInfo = execute_pack_sign_and_info(Config, desc)
    if packInfo is None:
        return
    
    if willPack_output:
        packInfo['willPack_output'] = willPack_output

    res = handle_template(Config, packInfo)
    if not res:
        return
    
    execute_did_pack(packInfo)


def execute_will_pack():
    """执行 PackFile.py 的 willPack 方法"""
    pack_file_path = os.path.join(ToolConfig.HpackDir, 'PackFile.py')
    python_cmd = get_python_command()

    try:
        process = subprocess.run(
            [python_cmd, pack_file_path, '--will'],
            capture_output=True,
            text=True,
            check=True
        )
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        printError(f"执行 willPack 时出错: {e}")
        return None


def execute_pack_sign_and_info(config, desc):
    """执行打包签名和信息生成"""
    try:
        pack_sign(config)
        return sign_info(config, desc)
    except Exception as e:
        printError(f"执行打包签名或生成信息时出错: {e}")
        return None


def execute_did_pack(packInfo):
    """执行 PackFile.py 的 didPack 方法"""
    pack_file_path = os.path.join(ToolConfig.HpackDir, 'PackFile.py')
    python_cmd = get_python_command()

    try:
        packJson = json.dumps(packInfo, ensure_ascii=False, indent=4)
        subprocess.run(
            [python_cmd, pack_file_path, '--did'],
            input=packJson,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        printError(f"执行 didPack 时出错: {e}")



def template_command(tname="default"):
    names = get_template_filenames()
    if not tname in names:
        printError(f"该模板不存在，模板可选值：{names}")
        return
    
    hpack_dir = ToolConfig.HpackDir
    if not os.path.exists(hpack_dir):
        printError("请先初始化：hpack init")
        return
    
    try:
        template_path = os.path.join(ToolConfig.TemplateDir, f"{tname}.html")
        target_template_path = os.path.join(hpack_dir, "index.html")
        if os.path.exists(target_template_path):
            printError(f"html模板文件已存在：{target_template_path}")
            return
        shutil.copy2(template_path, target_template_path)
        printSuccess(f"{tname} 风格模板已生成：{target_template_path}")
    except OSError as e:
        printError(f"html模板文件生成 失败 - {e}")
    

def get_template_filenames():
    template_dir = ToolConfig.TemplateDir
    filenames = []
    if os.path.exists(template_dir):
        for filename in os.listdir(template_dir):
            if os.path.isfile(os.path.join(template_dir, filename)):
                name, _ = os.path.splitext(filename)
                filenames.append(name)
    return filenames
    

def get_config():
    config_file_path = os.path.join(ToolConfig.HpackDir, 'config.py')
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
            printError(f"读取 config.py 文件时出错 - {e}")
    else:
        printError("pack 失败：hpack/config.py 文件不存在，请先执行 hpack init。")
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
  init, i              初始化 hpack 目录并创建配置文件
  pack, p [desc]       执行打包签名和上传, desc 可选
  template, t [tname]  生成 index.html 模板文件，tname 可选值：{get_template_filenames()}，默认为 default
版本: {__version__}
"""
    print(help_text)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-v', '--version']:
            show_version()
        elif sys.argv[1] in ['-h', '--help']:
            show_help()
        elif sys.argv[1] in ['init', 'i']:
            init_command()
        elif sys.argv[1] in ['pack', 'p']:
            if len(sys.argv) > 2:
                desc = sys.argv[2]
            else:
                desc = ""
            pack_command(desc)
        elif sys.argv[1] in ['template', 't']:
            if len(sys.argv) > 2:
                tname = sys.argv[2]
            else:
                tname = "default"
            template_command(tname)
        else:
            print("无效的命令或选项，请使用 'hpack -h' 查看帮助信息。")
    else:
        print("无效的命令，请使用 'hpack -h' 查看帮助信息。")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from tkinter import E

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path
sys.path.append(current_dir)

import json5
import segno
from hdc import install_command, show_targets, show_udid
from packSign import pack_sign
from sign import sign_command
from signInfo import sign_info
from template import handle_template
from toolConfig import ToolConfig
from utils import (BLUE, ENDC, RED, get_python_command, printError,
                   printSuccess, select_items, timeit)
from version import __version__


def init_command():
    hpack_dir = ToolConfig.HpackDir
    if os.path.exists(hpack_dir):
        raise Exception("init 失败 - hpack 目录已存在。")


    try:
        os.makedirs(hpack_dir)
        absPath = os.path.dirname(os.path.abspath(__file__))
        shutil.copy2(os.path.join(absPath, 'config.py'), os.path.join(hpack_dir, 'config.py'))
        shutil.copytree(os.path.join(absPath, 'sign'), os.path.join(hpack_dir, 'sign'))
        shutil.copy2(os.path.join(absPath, 'PackFile.py'), os.path.join(hpack_dir, 'PackFile.py'))
        printSuccess("hpack 初始化完成。请修改配置：", end='')
        print("""
hpack/
  config.py # 配置文件
  sign/  # 替换自己的签名证书文件
  Packfile.py 打包完成后的回调文件
""", end='')
    except Exception as e:
        raise Exception(f"init 失败 - {e}")


def get_products():
    try:
        with open("build-profile.json5", "r", encoding="utf-8") as f:
            products = json5.load(f).get("app", {}).get("products", [])
            if not products:
                raise Exception("build-profile.json5 中未找到产品配置")
            return products
    except Exception as e:
        raise Exception(f"读取 build-profile.json5 文件时出错 - {e}")


def get_selected_product(Config):
    products = get_products()
    if not products:
        raise Exception("未找到可用的产品配置")

    if hasattr(Config, 'HvigorwCommand') and Config.HvigorwCommand:
        name = next((item.split('=')[1] for item in Config.HvigorwCommand if item.startswith('product=')), None)
        product = next((p for p in products if p.get('name') == name), None)
        if not product:
            raise Exception(f"未找到指定的产品: {name}")
        return product

    if hasattr(Config, 'Product') and Config.Product:
        product = next((p for p in products if p.get('name') == Config.Product), None)
        if not product:
            raise Exception(f"未找到指定的产品: {Config.Product}")
        return product

    items = [item.get('name') for item in products]
    index = select_items(items, prompt_text="请选择要打包的 product:")
    if index is None:
        raise Exception("用户取消了产品选择")
    printSuccess(f"开始打包 product: {items[index]}")
    return products[index]


def pack_command(desc, forced_debug=None):
    Config = get_config()
    if not Config:
        raise Exception("无法读取配置文件")



    selected_product = get_selected_product(Config)
    if not selected_product:
        raise Exception("无法获取产品配置")

    do_pack(Config, selected_product, desc, forced_debug=forced_debug)


@timeit(printName='打包')
def do_pack(Config, selected_product, desc, forced_debug=None):
    willPack_output = execute_will_pack()
    
    try:
        packInfo = execute_pack_sign_and_info(
            Config,
            selected_product,
            desc,
            forced_debug=forced_debug
        )
            
        if not packInfo:
            # 打包失败，调用 failPack 并终止
            errorInfo = {
                'error': '打包签名或生成信息失败',
                'product': selected_product.get('name', ''),
                'desc': desc,
                'timestamp': datetime.now().isoformat()
            }
            execute_fail_pack(errorInfo)
            raise Exception("打包签名或生成信息失败")

        if willPack_output:
            packInfo['willPack_output'] = willPack_output

    
        handle_template(Config, packInfo)
        execute_did_pack(packInfo)
    except Exception as e:
        # 捕获所有打包过程中的异常
        errorInfo = {
            'error': str(e),
            'error_type': type(e).__name__,
            'product': selected_product.get('name', ''),
            'desc': desc,
            'timestamp': datetime.now().isoformat()
        }
        execute_fail_pack(errorInfo)
        # 重新抛出异常，让上层调用者知道打包失败
        raise e


def execute_will_pack():
    try:
        pack_file_path = os.path.join(ToolConfig.HpackDir, 'PackFile.py')
        process = subprocess.run(
            [get_python_command(), pack_file_path, '--will'],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        ret = process.stdout.strip()
        return ret

    except subprocess.CalledProcessError as e:
        raise Exception(f"执行 willPack 失败 - {e}")


def execute_pack_sign_and_info(config, selected_product, desc, forced_debug=None):
    pack_sign(config, selected_product, forced_debug=forced_debug)
    return sign_info(config, selected_product, desc, forced_debug=forced_debug)


def execute_did_pack(packInfo):
    try:
        pack_file_path = os.path.join(ToolConfig.HpackDir, 'PackFile.py')
        packJson = json.dumps(packInfo, ensure_ascii=False, indent=4)
        subprocess.run(
            [get_python_command(), pack_file_path, '--did'],
            input=packJson,
            text=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        raise Exception(f"执行 didPack 时出错 - {e}")


def execute_fail_pack(errorInfo):
    try:
        pack_file_path = os.path.join(ToolConfig.HpackDir, 'PackFile.py')
        errorJson = json.dumps(errorInfo, ensure_ascii=False, indent=4)
        subprocess.run(
            [get_python_command(), pack_file_path, '--fail'],
            input=errorJson,
            text=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        raise Exception(f"执行 failPack 时出错 - {e}")


def template_command(tname="default"):
    if tname not in get_template_filenames():
        raise Exception(f"该模板不存在，模板可选值：{get_template_filenames()}")

    hpack_dir = ToolConfig.HpackDir
    if not os.path.exists(hpack_dir):
        raise Exception("请先初始化：hpack init")

    try:
        template_path = os.path.join(ToolConfig.TemplateDir, f"{tname}.html")
        target_template_path = os.path.join(hpack_dir, "index.html")
        if os.path.exists(target_template_path):
            raise Exception(f"html模板文件已存在：{target_template_path}")
        shutil.copy2(template_path, target_template_path)
        printSuccess(f"{tname} 风格模板已生成：{target_template_path}")
    except OSError as e:
        raise Exception(f"html模板文件生成 失败 - {e}")



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
    try:
        spec = importlib.util.spec_from_file_location("config", os.path.join(ToolConfig.HpackDir, 'config.py'))
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        config = getattr(config_module, 'Config', None)
        if config is None:
            raise Exception("config.py 文件中未找到 Config 配置")
        return config
    except Exception as e:
        raise Exception(f"读取 config.py 文件时出错 - {e}")


def show_version():
    print(f"hpack 版本: {__version__}")

def get_build_product_dirs():
    build_dir = ToolConfig.BuildDir
    if not os.path.exists(build_dir):
        return []
    product_dirs = [d for d in os.listdir(build_dir) if os.path.isdir(os.path.join(build_dir, d))]
    return product_dirs

def show_help():
    print(f"""
hpack: v{__version__} - 鸿蒙应用打包、签名、安装和上传工具
文档: {BLUE}https://github.com/iHongRen/hpack{ENDC}

{BLUE}查看:{ENDC}
  -v, --version  显示版本信息
  -h, --help     显示帮助信息
  -u, --udid     显示设备的 UDID
  targets        显示连接的设备列表

{BLUE}执行:{ENDC}
  init                   初始化 hpack 目录并创建配置文件
  pack, p [desc]         执行打包签名和上传, desc 打包描述，可选
  pr [desc]              执行 release 打包，忽略 config.py 中的 Debug 配置
  pd [desc]              执行 debug 打包，忽略 config.py 中的 Debug 配置
  template, t [tname]    用于自定义模板时，生成 index.html 模板文件，tname 可选值：{get_template_filenames()}，默认为 default

{BLUE}安装包:{ENDC}
  install, i [-product]   将打包后的产物安装到设备，product 为你的产物名，默认为 default，需要先 hapck pack 打包。
  示例： hpack i -myproduct   # 安装 myproduct 产物，注意加上横杠(-）

  install, i signedPath   为已签名包的目录或文件路径，支持 .app、.hap文件或目录。
  示例1：hpack i ./xx.app
  示例2：hpack i ./xx.hap
  示例3：hpack i ./build/default

{BLUE}签名:{ENDC}
  sign, s unsignedPath certPath
  unsignedPath 为待签名的目录或文件路径，支持 .app、.hap、.hsp 文件或目录。
  certPath 为签名证书配置文件路径。
  示例1：hpack s ./xx.app ./sign/cert.py
  示例2：hpack s ./xx.hap ./sign/cert.py
  示例3：hpack s ./build/default ./sign/cert.py

  /sign 目录的结构如下：
    ├── cert.py
    ├── certFile.cer
    ├── keystore.p12
    └── profile.p7b

  cert.py 签名证书配置文件示例如下：
  # -*- coding: utf-8 -*-
  Alias = 'key alias' 
  KeyPwd = 'key password' 
  KeystorePwd = 'store password' 
  Cert ='./certFile.cer'  # 相对于cert.py的路径
  Profile = './profile.p7b' # 相对于cert.py的路径
  Keystore =  './keystore.p12' # 相对于cert.py的路径

  赞助: {BLUE}https://ihongren.github.io/donate.html{ENDC}
""", end='')


def main():
    try:
        if len(sys.argv) < 2:
            print("无效的命令，请使用 'hpack -h' 查看帮助信息。")
            sys.exit(1)
            
        commands = {
            '-v': show_version, '--version': show_version,
            '-h': show_help, '--help': show_help,
            '-u': show_udid, '--udid': show_udid,
            'targets': show_targets,
            'init': init_command,
            'pack': lambda: pack_command(sys.argv[2] if len(sys.argv) > 2 else ""),
            'p': lambda: pack_command(sys.argv[2] if len(sys.argv) > 2 else ""),
            'pr': lambda: pack_command(sys.argv[2] if len(sys.argv) > 2 else "", forced_debug=False),
            'pd': lambda: pack_command(sys.argv[2] if len(sys.argv) > 2 else "", forced_debug=True),
            'template': lambda: template_command(sys.argv[2] if len(sys.argv) > 2 else "default"),
            't': lambda: template_command(sys.argv[2] if len(sys.argv) > 2 else "default"),
            'install': lambda: install_command(sys.argv[2] if len(sys.argv) > 2 else "-default"),
            'i': lambda: install_command(sys.argv[2] if len(sys.argv) > 2 else "-default"),
            'sign': lambda: sign_command(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""),
            's': lambda: sign_command(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""),
        }
        
        command = sys.argv[1]
        if command in commands:
            commands[command]()
        else:
            print("无效的命令，请使用 'hpack -h' 查看帮助信息。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        printError("\n用户中断操作")
        sys.exit(130)  # 130 是 SIGINT 的标准退出码
    except Exception as e:
        printError(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

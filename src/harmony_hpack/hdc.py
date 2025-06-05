import os
import shutil
import subprocess
import zipfile

from toolConfig import ToolConfig
from utils import isWin, printError, printSuccess, select_items


def runCommand(commands, capture_output=False):
    return subprocess.run(commands, check=True, shell=isWin(), capture_output=capture_output)


def show_targets():
    """列出设备列表
    hdc list targets
    """
    try:
        runCommand(["hdc", "list", "targets"])
    except subprocess.CalledProcessError as e:
        printError(f"列出设备出错: {e}")


def get_targets():
    """获取设备列表
    hdc list targets
    """
    try:
        result = runCommand(["hdc", "list", "targets"], True)
        devices = result.stdout.decode().splitlines()
        return devices
    except subprocess.CalledProcessError as e:
        printError(f"获取设备列表出错: {e}")
        return []
    except Exception as e:
        printError(f"发生错误: {e}")
        return []


def show_udid():
    """执行获取udid操作
    hdc -t xx shell bm get --udid
    """
    try:
        targets = get_targets()
        if not targets:
            printError("没有找到可用的设备")
            return
        for target in targets:
            print(f"设备: {target}:")
            runCommand(["hdc", "-t", target, "shell", "bm", "get", "--udid"])
    except subprocess.CalledProcessError as e:
        printError(f"获取udid出错: {e}")


def install_command(product="-default"):
    """执行安装操作
    hdc list targets
    hdc shell mkdir data/local/tmp/hpack
    hdc file send "./hpack/build/default/hsp1-default-signed.hsp" "data/local/tmp/hpack"
    hdc file send "./hpack/build/default/hsp2-default-signed.hsp" "data/local/tmp/hpack"
    hdc file send "./hpack/build/default/entry-default-signed.hap" "data/local/tmp/hpack"
    hdc shell bm install -p data/local/tmp/hpack      
    hdc shell rm -rf data/local/tmp/hpack 
    """

    try:
        targets = get_targets()
        if not targets:
            printError("没有找到可用的设备")
            return
        index = select_items(targets, "请选择要安装的设备:")
        target = targets[index]
        printSuccess(f"正在安装到设备: {target}")
        tmpPath = "data/local/tmp/hpack-install-dir"

        runCommand(["hdc", "-t", target, "shell", "rm", "-rf", tmpPath])
        runCommand(["hdc", "-t", target, "shell", "mkdir", tmpPath])

        if product.endswith('.app'):
            # 解压缩
            zip_ref = zipfile.ZipFile(product, 'r')
            extract_dir = product[:-4]  # 去掉.app后缀
            zip_ref.extractall(extract_dir)
            zip_ref.close()
            productPath = os.path.join(extract_dir)
        elif product.startswith('-'):
            productPath = os.path.join(ToolConfig.BuildDir, product[1:])
        else:
            productPath = os.path.join(product)

        if not os.path.exists(productPath):
            printError(f"构建产物目录 {productPath} 不存在")
            return
        
        haphspFiles = []
        if product.endswith('.hap'):
            haphspFiles.append(productPath)
        else:
            # 直接获取第一层内容
            with os.scandir(productPath) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.endswith(('.hap', '.hsp')):
                        haphspFiles.append(entry.path)
        
        if not haphspFiles:
            printError(f"没有找到 hap/hsp 文件")
            return
        
        for file in haphspFiles:
            runCommand(["hdc", "-t", target, "file", "send", file, tmpPath])
          
        runCommand(["hdc", "-t", target, "shell", "bm", "install", "-p", tmpPath])
        runCommand(["hdc", "-t", target, "shell", "rm", "-rf", tmpPath])

        # print(ret.stdout.decode())


        if product.endswith('.app'):
            # 删除解压目录
            shutil.rmtree(extract_dir, ignore_errors=True)

    except subprocess.CalledProcessError as e:
        printError(f"安装操作出错: {e}")



import os
import subprocess

from toolConfig import ToolConfig
from utils import isWin, printError, select_items


def show_targets():
    """列出设备列表
    hdc list targets
    """
    try:
        subprocess.run(["hdc", "list", "targets"], check=True, shell=isWin())
    except subprocess.CalledProcessError as e:
        printError(f"列出设备出错: {e}")


def get_targets():
    """获取设备列表
    hdc list targets
    """
    try:
        result = subprocess.run(["hdc", "list", "targets"], check=True, shell=isWin(), capture_output=True)
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
            subprocess.run(["hdc", "-t", target, "shell", "bm", "get", "--udid"], check=True, shell=isWin())
    except subprocess.CalledProcessError as e:
        printError(f"获取udid出错: {e}")


def install_command(product="default"):
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
        target = select_items(targets, "请选择要安装的设备:")
        tmpPath = "data/local/tmp/tmp-hpack-install-dir"
        subprocess.run(["hdc", "-t", target, "shell", "rm", "-rf", tmpPath], check=True, shell=isWin())
        subprocess.run(["hdc", "-t", target, "shell", "mkdir", tmpPath], check=True, shell=isWin())

        productPath = os.path.join(ToolConfig.BuildDir, product)
        if not os.path.exists(productPath):
            printError(f"构建产物目录 {productPath} 不存在")
            return
        haphspFiles = []
        for root, dirs, files in os.walk(productPath):
            for file in files:
                if file.endswith(('.hap', '.hsp')):
                    haphspFiles.append(os.path.join(root, file))
        
        if not haphspFiles:
            printError(f"没有找到 hap/hsp 文件")
            return
        for file in haphspFiles:
            subprocess.run(["hdc", "-t", target, "file", "send", file, tmpPath], check=True, shell=isWin())

        subprocess.run(["hdc", "-t", target, "shell", "bm", "install", "-p", tmpPath], check=True, shell=isWin())

        subprocess.run(["hdc", "-t", target, "shell", "rm", "-rf", tmpPath], check=True, shell=isWin())

        print(f"安装完成")
    except subprocess.CalledProcessError as e:
        printError(f"安装操作出错: {e}")
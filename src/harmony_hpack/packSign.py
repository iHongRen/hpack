# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os
import shutil
import subprocess

from toolConfig import ToolConfig
from utils import isWin, printError, timeit


@timeit()
def clean():
    """执行清理操作"""
    try:
        subprocess.run(["hvigorw", "clean", "--no-daemon"], check=True, shell=isWin())
    except subprocess.CalledProcessError as e:
        printError(f"清理操作出错: {e}")


@timeit()
def sync():
    """执行同步操作"""
    try:
        subprocess.run(["hvigorw", "--sync", "--no-daemon"], check=True, shell=isWin())
    except subprocess.CalledProcessError as e:
        printError(f"同步操作出错: {e}")

@timeit()
def buildHapHsp(Config, product):
    """构建 Hap & Hsp"""
    try:
        if hasattr(Config, 'HvigorwCommand') and len(Config.HvigorwCommand) > 0:
            command = Config.HvigorwCommand
        else:
            debug = "true" if hasattr(Config, 'Debug') and Config.Debug else "false"
            command = [
                'hvigorw', 'assembleHap', 'assembleHsp', 
                '--mode', 'module', 
                '-p', f"product={product.get('name')}", 
                '-p', f"debuggable={debug}",
                '--no-daemon'
            ]
        subprocess.run(command, check=True, shell=isWin())
        print("构建 Hap Hsp 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建 Hap 出错: {e}")
        return False


def mkBuildDir(productName):
    """处理 hpack/build 目录，若存在则删除再创建"""
    build_dir  = os.path.join(ToolConfig.BuildDir, productName)
    if os.path.exists(build_dir) and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
        print(f"已删除 {build_dir} 目录。")
    os.makedirs(build_dir, exist_ok=True)
    print(f"已创建 {build_dir} 目录。")

@timeit()
def signHapHsp(Config, productName):
    """对 Hap&Hsp 文件进行签名"""
    result = []
    source_dir = os.getcwd()
    for root, dirs, files in os.walk(source_dir):
        # 排除 oh_modules 和 hpack 目录
        dirs[:] = [d for d in dirs if d not in ToolConfig.ExcludeDirs]
        for file in files:
            if file.endswith(('-unsigned.hap', '-unsigned.hsp')):
                result.append(os.path.join(root, file))
     
    for file in result:
        sign(Config, file, productName)


def sign(Config, unsigned_file_path, productName):
    """对未签名文件进行签名"""
    print(f"路径: {unsigned_file_path}")
    file_name = os.path.basename(unsigned_file_path)
    build_dir  = ToolConfig.BuildDir
    signed_file_path = os.path.join(build_dir,productName, file_name.replace("unsigned", "signed"))
    
    command = [
        'java', '-jar', ToolConfig.HapSignTool,
        'sign-app',
        '-keyAlias', Config.Alias,
        '-signAlg', 'SHA256withECDSA',
        '-mode', 'localSign',
        '-appCertFile', os.path.join(ToolConfig.HpackDir, Config.Cert),
        '-profileFile', os.path.join(ToolConfig.HpackDir, Config.Profile),
        '-inFile', unsigned_file_path,
        '-keystoreFile', os.path.join(ToolConfig.HpackDir, Config.Keystore),
        '-outFile', signed_file_path,
        '-keyPwd', Config.KeyPwd,
        '-keystorePwd', Config.KeystorePwd,
        '-signCode', '1'
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        printError(f"签名 {unsigned_file_path} 出错: {e}")


def pack_sign(Config, product):
    clean()
    sync()
    if not buildHapHsp(Config, product):
        return
    productName = product.get('name')
    mkBuildDir(productName)
    signHapHsp(Config, productName)


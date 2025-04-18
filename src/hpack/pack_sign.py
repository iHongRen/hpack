# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os
import subprocess
import shutil
import sys

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path
sys.path.append(current_dir)

from utils import printError, isWin, timeit
from toolConfig import ToolConfig


@timeit
def clean():
    """执行清理操作"""
    try:
        subprocess.run(["hvigorw", "clean", "--no-daemon"], check=True, shell=isWin())
    except subprocess.CalledProcessError as e:
        printError(f"清理操作出错: {e}")


def mkBuildDir():
    """处理 hpack/build 目录，若存在则删除再创建"""
    build_dir  = ToolConfig.BuildDir
    if os.path.exists(build_dir) and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
        print(f"已删除 {build_dir} 目录。")
    os.makedirs(build_dir, exist_ok=True)
    print(f"已创建 {build_dir} 目录。")

@timeit
def buildHapHsp():
    """构建 Hap & Hsp"""
    try:
        subprocess.run(['hvigorw', 'assembleHap', 'assembleHsp', '--mode', 'module', '-p', 'product=default', '-p', 'debuggable=true','--no-daemon'], check=True, shell=isWin())
        print("构建 Hap Hsp 完成")
    except subprocess.CalledProcessError as e:
        print(f"构建 Hap 出错: {e}")


@timeit
def signHapHsp(Config):
    """对 Hap&Hsp 文件进行签名"""
    result = []
    source_dir = os.getcwd()
    for root, dirs, files in os.walk(source_dir):
        # 排除 oh_modules 和 pack 目录
        dirs[:] = [d for d in dirs if d not in ToolConfig.ExcludeDirs]
        for file in files:
            if file.endswith(('-unsigned.hap', '-unsigned.hsp')):
                result.append(os.path.join(root, file))
     
    for file in result:
        sign(Config, file)


def sign(Config, unsigned_file_path):
    """对未签名文件进行签名"""
    print(f"路径: {unsigned_file_path}")
    file_name = os.path.basename(unsigned_file_path)
    build_dir  = ToolConfig.BuildDir
    signed_file_path = os.path.join(build_dir, file_name.replace("unsigned", "signed"))
    
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


def packSign(Config):
    clean()
    buildHapHsp()
    mkBuildDir()
    signHapHsp(Config)


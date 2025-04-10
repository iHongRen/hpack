# -*- coding: utf-8 -*-

#  @author : @cxy
#  @date : 2025/4/10
#  @github : https://github.com/iHongRen/hpack

import os
import subprocess
import shutil
from utils import printError, isWin, timeit
from config import Config


@timeit
def clean():
    """执行清理操作"""
    try:
        subprocess.run(["hvigorw", "clean", "--no-daemon"], check=True, shell=isWin())
    except subprocess.CalledProcessError as e:
        printError(f"清理操作出错: {e}")


def mkBuildDir():
    """处理 pack/build 目录，若存在则删除再创建"""
    build_dir = Config.BuildDir
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
def signHapHsp():
    """对 Hap&Hsp 文件进行签名"""
    result = []
    source_dir = os.path.join('.') 
    for root, dirs, files in os.walk(source_dir):
        # 排除 oh_modules 和 pack 目录
        dirs[:] = [d for d in dirs if d not in Config.ExcludeDirs]
        for file in files:
            if file.endswith(('-unsigned.hap', '-unsigned.hsp')):
                result.append(os.path.join(root, file))
     
    for file in result:
        sign(file)


def sign(unsigned_file_path):
    """对未签名文件进行签名"""
    print(f"路径: {unsigned_file_path}")
    file_name = os.path.basename(unsigned_file_path)
    signed_file_path = os.path.join(Config.BuildDir, file_name.replace("unsigned", "signed"))
    
    command = [
        'java', '-jar', Config.HapSignTool,
        'sign-app',
        '-keyAlias', Config.Alias,
        '-signAlg', 'SHA256withECDSA',
        '-mode', 'localSign',
        '-appCertFile', Config.Cert,
        '-profileFile', Config.Profile,
        '-inFile', unsigned_file_path,
        '-keystoreFile', Config.Keystore,
        '-outFile', signed_file_path,
        '-keyPwd', Config.KeyPwd,
        '-keystorePwd', Config.KeystorePwd,
        '-signCode', '1'
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        printError(f"签名 {unsigned_file_path} 出错: {e}")


def packSign():
    clean()
    buildHapHsp()
    mkBuildDir()
    signHapHsp()


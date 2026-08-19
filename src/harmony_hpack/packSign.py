# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os
import shutil
import subprocess

from toolConfig import ToolConfig
from utils import (format_cmd_error, isWin, require_existing_file,
                   resolve_hvigorw_command, timeit)


def run_hvigorw(args, error_prefix):
    command = [resolve_hvigorw_command(), *args]
    try:
        subprocess.run(command, check=True, shell=isWin())
    except FileNotFoundError as e:
        raise Exception(f"{error_prefix}: 未找到命令，已查找: {command[0]} - {e}")
    except subprocess.CalledProcessError as e:
        raise Exception(format_cmd_error(e, error_prefix))


@timeit()
def clean():
    """执行清理操作"""
    run_hvigorw(["clean", "--no-daemon"], "清理操作失败")


@timeit()
def sync():
    """执行同步操作"""
    run_hvigorw(["--sync", "--no-daemon"], "同步操作失败")

@timeit()
def buildHapHsp(Config, product, forced_debug=None):
    """构建 Hap & Hsp"""
    try:
        if hasattr(Config, 'HvigorwCommand') and len(Config.HvigorwCommand) > 0:
            command = list(Config.HvigorwCommand)
            if command and command[0] == 'hvigorw':
                command[0] = resolve_hvigorw_command()
        else:
            debug_enabled = forced_debug if forced_debug is not None else (
                hasattr(Config, 'Debug') and Config.Debug
            )
            debug = "true" if debug_enabled else "false"
            command = [
                resolve_hvigorw_command(), 'assembleHap', 'assembleHsp',
                '--mode', 'module', 
                '-p', f"product={product.get('name')}", 
                '-p', f"debuggable={debug}",
                '--no-daemon'
            ]
        subprocess.run(command, check=True, shell=isWin())
        print("构建 Hap Hsp 完成")
    except FileNotFoundError as e:
        looked = command[0] if command else 'hvigorw'
        raise Exception(f"构建 Hap/Hsp 出错: 未找到命令，已查找: {looked} - {e}")
    except subprocess.CalledProcessError as e:
        raise Exception(format_cmd_error(e, "构建 Hap/Hsp 出错"))


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
            elif '_hsp' in root and file.endswith('.hsp') and not file.endswith('-signed.hsp'):
                # 未签名的 集成态hsp 文件
                result.append(os.path.join(root, file))

    if not result:
        raise Exception(
            f"未找到需要签名的 Hap 或 Hsp 文件，已在 {source_dir} 查找 "
            f"*-unsigned.hap / *-unsigned.hsp（排除目录: {ToolConfig.ExcludeDirs}）"
        )

    for file in result:
        sign(Config, file, productName)


def sign(Config, unsigned_file_path, productName):
    """对未签名文件进行签名"""
    print(f"路径: {unsigned_file_path}")
    file_name = os.path.basename(unsigned_file_path)
    build_dir  = ToolConfig.BuildDir
    signed_file_path = os.path.join(build_dir,productName, file_name.replace("unsigned", "signed"))
    
    cert_file = require_existing_file(Config.Cert, ToolConfig.HpackDir, '证书 Cert')
    profile_file = require_existing_file(Config.Profile, ToolConfig.HpackDir, 'Profile')
    keystore_file = require_existing_file(Config.Keystore, ToolConfig.HpackDir, 'Keystore')
    if not os.path.isfile(ToolConfig.HapSignTool):
        raise Exception(f"未找到签名工具，已查找: {ToolConfig.HapSignTool}")

    command = [
        'java', '-jar', ToolConfig.HapSignTool,
        'sign-app',
        '-keyAlias', Config.Alias,
        '-signAlg', 'SHA256withECDSA',
        '-mode', 'localSign',
        '-appCertFile', cert_file,
        '-profileFile', profile_file,
        '-inFile', unsigned_file_path,
        '-keystoreFile', keystore_file,
        '-outFile', signed_file_path,
        '-keyPwd', Config.KeyPwd,
        '-keystorePwd', Config.KeystorePwd,
        '-signCode', '1'
    ]
    try:
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if process.stdout:
            print(process.stdout, end='')
        if process.stderr:
            print(process.stderr, end='')
    except subprocess.CalledProcessError as e:
        raise Exception(format_cmd_error(e, f"签名文件 {unsigned_file_path} 失败"))


def pack_sign(Config, product, forced_debug=None):
    clean()
    sync()
    buildHapHsp(Config, product, forced_debug=forced_debug)
    productName = product.get('name')
    mkBuildDir(productName)
    signHapHsp(Config, productName)

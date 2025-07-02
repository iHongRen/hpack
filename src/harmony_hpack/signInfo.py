# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import json
import os
import subprocess
from datetime import datetime

import json5
import segno  # 生成二维码
from toolConfig import ToolConfig
from utils import calculate_sha256, get_directory_size, printError


def read_app_info():
    # MARK: 另一种方法是读取打包后的pack.info
    json_path = os.path.join("AppScope", "app.json5")
    if not os.path.exists(json_path):
        printError(f"AppScope/app.json5 文件不存在: {json_path}")
        return None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            app_info = json5.load(f)
            app = app_info.get("app", {})
            bundle_name = app.get("bundleName")
            version_code = app.get("versionCode")
            version_name = app.get("versionName")
            return bundle_name, version_code, version_name
    except Exception as e:
        printError(f"读取 AppScope/app.json5 文件时出错: {e}")
        return None
    return None


def read_api_version():
    json_path = os.path.join("build-profile.json5")
    if not os.path.exists(json_path):
        printError(f"build-profile.json5 文件不存在: {json_path}")
        return None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json5.load(f)
            try:
                api_version = data.get("app").get("products")[0].get("compatibleSdkVersion")
                print(f"compatibleSdkVersion 的值为: {api_version}")
            except (KeyError, IndexError):
                print("未找到 compatibleSdkVersion 的值。")
            return api_version
    except Exception as e:
        printError(f"读取 build-profile.json5 文件时出错: {e}")
        return None
    return None


def get_module_infos(build_dir, remotePath):
    result = []
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            if file.endswith(("-signed.hsp", "-signed.hap")):
                file_path = os.path.join(root, file)
                sha256 = calculate_sha256(file_path)
                name = file.split("-")[0]
                if file.endswith(".hap"):
                    _type = "entry"
                else:
                    _type = "share"
                package_url = f"{remotePath}/{file}"
                file_info = {
                    "name": name,
                    "type": _type,
                    "deviceTypes": ["tablet", "phone"],
                    "packageUrl": package_url,
                    "packageHash": sha256,
                }
                result.append(file_info)    
    return result


def create_unsign_manifest(Config, build_dir, remotePath, bundle_name, version_code, version_name, apiVersion):

    modules = get_module_infos(build_dir,remotePath)
    if not modules:
        printError("无法获取打包模块信息，hap、hsp 包签名失败，请检查你的签名文件配置。")
        return False
  

    # 定义要写入文件的数据
    data = {
        "app": {
            "bundleName": bundle_name,
            "bundleType": "app",
            "versionCode": version_code,
            "versionName": version_name,
            "label": Config.AppName,
            "deployDomain": Config.DeployDomain,
            "icons": {
                "normal": Config.AppIcon,
                "large": Config.AppIcon,
            },
            "minAPIVersion": apiVersion,
            "targetAPIVersion": apiVersion,
            "modules": modules
        }
    }

    # 定义目标目录和文件名
    file_path = os.path.join(build_dir, ToolConfig.UnsignManifestFile)

 
    # 将数据写入 JSON5 文件
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"成功生成文件 {file_path}")
    except Exception as e:
        printError(f"写入文件时出错: {e}")
        return False

    return True


def create_sign_manifest(Config, build_dir):
    # 打印签名开始信息
    print("----开始签名 manifest.json5----")
    inputFile = os.path.join(build_dir , ToolConfig.UnsignManifestFile) 
    outputFile = os.path.join(build_dir , ToolConfig.SignedManifestFile) 
    keystore = os.path.join(ToolConfig.HpackDir ,Config.Keystore)
    KeystorePwd = Config.KeystorePwd
    KeyPwd = Config.KeyPwd

    # 定义签名命令
    sign_command = [
        'java','-jar',ToolConfig.ManifestSignTool,
        '-operation', 'sign',
        '-mode', 'localjks',
        '-inputFile', inputFile,
        '-outputFile', outputFile,
        '-keystore', keystore,
        '-keystorepasswd', KeystorePwd,
        '-keyaliaspasswd', KeyPwd,
        '-privatekey', Config.Alias
    ]

    try:
        # 执行签名命令
        subprocess.run(sign_command, check=True)
    except subprocess.CalledProcessError as e:
        printError(f"签名过程出错: {e}")
        return False    

    # 打印验证开始信息
    print("----验证签名 manifest.json5----")

    # 定义验证命令
    verify_command = [
        'java','-jar', ToolConfig.ManifestSignTool,
        '-operation', 'verify',
        '-inputFile', outputFile,
        '-keystore', keystore,
        '-keystorepasswd', KeystorePwd
    ]

    try:
        # 执行验证命令
        subprocess.run(verify_command, check=True)
    except subprocess.CalledProcessError as e:
        printError(f"验证过程出错: {e}")
        return False
        
    return True



def sign_info(Config, selected_product, desc=""):

    bundle_name, version_code, version_name = read_app_info()
 
    if 'bundleName' in selected_product:
        bundle_name = selected_product.get('bundleName')

    if 'versionCode' in selected_product:
        version_code = selected_product.get('versionCode')

    if 'versionName' in selected_product:
        version_name = selected_product.get('versionName')

    if not bundle_name or not version_code or not version_name:
        printError("无法获取 bundleName、versionCode 或 versionName，无法处理 manifest.json5 文件。")
        return
    
    remote_dir = datetime.now().strftime("%Y%m%d%H%M%S")
    remotePath = f"{Config.BaseURL}/{remote_dir}"

    productName = selected_product.get('name')
    build_dir = os.path.join(ToolConfig.BuildDir, productName)
    
    if 'compatibleSdkVersion' in selected_product:
        apiVersion = selected_product.get('compatibleSdkVersion')
    else:
        apiVersion = read_api_version()
    if apiVersion is None:
        printError("无法获取 compatibleSdkVersion")
        return

    unsignRet = create_unsign_manifest(Config, build_dir, remotePath, bundle_name, version_code, version_name,apiVersion)
    if not unsignRet:
        return

    signRet = create_sign_manifest(Config, build_dir)
    if not signRet:
        return
    
    size = get_directory_size(build_dir)

    # 生成二维码
    index_url = f"{remotePath}/index.html"
    qr = segno.make(index_url)
    qrcode = qr.svg_data_uri(scale=10)
    
    manifest_url = f"{remotePath}/{ToolConfig.SignedManifestFile}"

    packInfo = {
        "bundle_name": bundle_name,
        "version_code": version_code,
        "version_name": version_name,
        "size": size,
        "desc": desc,
        "build_dir": build_dir,
        "remote_dir": remote_dir,
        "manifest_url": manifest_url,
        "qrcode": qrcode,
        "index_url": index_url,
        "product": productName,
    }
    
    return packInfo


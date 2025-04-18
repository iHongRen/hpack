# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os
import json
import oss2  # 先安装 pip3 install oss2
import json5  # 先安装 pip3 install json5
import segno  # 先安装 pip3 install segno 生成二维码

from datetime import datetime
from string import Template
import subprocess

from .utils import printError, printSuccess, get_directory_size,calculate_sha256
from .toolConfig import ToolConfig

def upload_to_oss(Config, target_dir, timestamp):
    if len(os.listdir(target_dir)) == 0:
        printError(f"无法上传空的目录 {target_dir}")
        return False

    auth = oss2.Auth(Config.Access_key_id, Config.Access_key_secret)
    bucket = oss2.Bucket(auth, Config.Endpoint, Config.Bucket_name)

    for root, _, files in os.walk(target_dir):
        for file in files:
            if file == ToolConfig.UnsignManifestFile:
                continue
            
            file_path = os.path.join(root, file)
            try:
                print(f"正在上传： {file} ")
                romotePath = f"{Config.Bucket_dir}/{timestamp}/{file}"
                result = bucket.put_object_from_file(romotePath, file_path)
                if result.status == 200:
                    print(f"文件 {file} 上传到 OSS 成功。")      
                else:
                    printError(f"文件 {file} 上传到 OSS 失败，状态码: {result.status}。")

            except Exception as e:
                printError(f"文件 {file} 上传到 OSS 时出现异常: {e}。")
                return False


    printSuccess("所有文件上传到 OSS 成功。")
    return True


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
                api_version = data["app"]["products"][0]["compatibleSdkVersion"]
                print(f"compatibleSdkVersion 的值为: {api_version}")
            except (KeyError, IndexError):
                print("未找到 compatibleSdkVersion 的值。")
            return api_version
    except Exception as e:
        printError(f"读取 AppScope/app.json5 文件时出错: {e}")
        return None
    return None


def get_module_infos(Config, target_dir, timestamp):
    result = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(("-signed.hsp", "-signed.hap")):
                file_path = os.path.join(root, file)
                sha256 = calculate_sha256(file_path)
                name = file.split("-")[0]
                if file.endswith(".hap"):
                    _type = "entry"
                else:
                    _type = "share"
                package_url = f"{Config.BaseURL}/{timestamp}/{file}"
                file_info = {
                    "name": name,
                    "type": _type,
                    "deviceTypes": ["tablet", "phone"],
                    "packageUrl": package_url,
                    "packageHash": sha256,
                }
                result.append(file_info)    
    return result

def create_unsign_manifest(Config, target_dir, timestamp, bundle_name, version_code, version_name):
    apiVersion = read_api_version()
    if apiVersion is None:
        printError("无法获取 sdk api version，无法处理 manifest.json5 文件。")
        return False


    modules = get_module_infos(Config, target_dir,timestamp)
    if not modules:
        printError("无法获取打包模块信息，无法处理 manifest.json5 文件。")
        return False
  

    # 定义要写入文件的数据
    data = {
        "app": {
            "bundleName": bundle_name,
            "bundleType": "app",
            "versionCode": version_code,
            "versionName": version_name,
            "label": Config.AppName,
            "deployDomain": Config.Cname,
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
    file_path = os.path.join(target_dir, ToolConfig.UnsignManifestFile)

 
    # 将数据写入 JSON5 文件
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"成功生成文件 {file_path}")
    except Exception as e:
        printError(f"写入文件时出错: {e}")
        return False

    return True


def create_sign_manifest(Config, target_dir):
    # 打印签名开始信息
    print("----开始签名 manifest.json5----")
    inputFile = os.path.join(target_dir , ToolConfig.UnsignManifestFile) 
    outputFile = os.path.join(target_dir , ToolConfig.SignedManifestFile) 
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


def handle_html_index(Config, target_dir, timestamp, version_name, version_code, size, desc, packText):
    file_path = os.path.join(target_dir, "index.html")
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 要编码的内容
    data = f"{Config.BaseURL}/{timestamp}/index.html"
    # 生成二维码
    qr = segno.make(data)
    svg_string = qr.svg_data_uri(scale=10)

    # 读取 HTML 模板文件
    template_path = ToolConfig.IndexTemplateHtml
    with open(template_path, "r", encoding="utf-8") as template_file:
        html = template_file.read()

    template = Template(html)
    html_template = template.safe_substitute(
        app_icon=Config.AppIcon,
        version_name=version_name,
        version_code=version_code,
        date=date,
        size=size,
        desc=desc,
        timestamp=timestamp,
        svg_string=svg_string,
        baseUrl=Config.BaseURL,
        packText=packText
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_template)


def signUploader(Config, desc=""):

    bundle_name, version_code, version_name = read_app_info()
    if not bundle_name or not version_code or not version_name:
        printError("无法获取版本信息，无法处理 manifest.json5 文件。")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    target_dir = ToolConfig.BuildDir

    unsignRet = create_unsign_manifest(Config, target_dir, timestamp, bundle_name, version_code, version_name)
    if not unsignRet:
        return

    signRet = create_sign_manifest(Config, target_dir)
    if not signRet:
        return
    
    size = get_directory_size(target_dir)

    handle_html_index(Config, target_dir, timestamp, version_name, version_code, size, desc, Config.AppName)

    # 上传 ./build 里面的文件到 OSS
    upload_to_oss(Config, target_dir, timestamp)

    printSuccess(f"打包完成，版本：{version_name}，版本号：{version_code}，大小：{size}")
    printSuccess(f"请访问 {Config.BaseURL}/{timestamp}/index.html")


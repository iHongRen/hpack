# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
 
import argparse
import json
import os
import sys
from datetime import datetime
from string import Template

import oss2  # pip/pip3 install oss2

from config import Config


class OSSConfig:
    """阿里云OSS配置， 先安装 pip install oss2"""
    Access_key_id = ''
    Access_key_secret = ''
    Endpoint = 'https://oss-cn-chengdu.aliyuncs.com'
    Bucket_name = ''
    Bucket_dir = 'hpack'


def ossUpload(packInfo):
    """_summary_: 上传打包结果到 OSS"""

    # 初始化 OSS 客户端
    auth = oss2.Auth(OSSConfig.Access_key_id, OSSConfig.Access_key_secret)
    bucket = oss2.Bucket(auth, OSSConfig.Endpoint, OSSConfig.Bucket_name)

    build_dir = packInfo.get("build_dir")
    remote_dir = packInfo.get("remote_dir")

    # 上传 hpack/build/[product] 目录里的打包文件到 OSS
    if len(os.listdir(build_dir)) == 0:
        print(f"无法上传空的目录 {build_dir}")
        return False

    for root, _, files in os.walk(build_dir):
        for file in files:
            # 跳过 unsign_manifest.json5
            if file == "unsign_manifest.json5":
                continue

            file_path = os.path.join(root, file)
            try:
                print(f"正在上传： {file} ")
                remotePath = f"{OSSConfig.Bucket_dir}/{remote_dir}/{file}"
                result = bucket.put_object_from_file(remotePath, file_path)
                if result.status == 200:
                    print(f"文件 {file} 上传到 OSS 成功。")
                else:
                    print(f"文件 {file} 上传到 OSS 失败，状态码: {result.status}。")
                    return False
            except Exception as e:
                print(f"文件 {file} 上传到 OSS 时出现异常: {e}。")
                return False

    return True


def customTemplateHtml(templateInfo):
    """_summary_: 用于生成 index.html 模板，并自定义"""
    packInfo = templateInfo.get("packInfo")
    html = templateInfo.get("html")
    
    # 填充模板变量
    template = Template(html)
    html_template = template.safe_substitute(
        app_icon=Config.AppIcon,
        title=Config.AppName,
        badge=Config.Badge,
        date=packInfo.get("date"),
        version_name=packInfo.get("version_name"),
        version_code=packInfo.get("version_code"),
        size=packInfo.get("size"),
        desc=packInfo.get("desc"),
        manifest_url=packInfo.get("manifest_url"),
        qrcode=packInfo.get("qrcode")
    )
    sys.stdout.buffer.write(html_template.encode('utf-8'))
    sys.stdout.flush()


def willPack():
    """_summary_: 打包前调用"""
    # 打包前传值，可以在这里读取一些工程配置，再传递给打包脚本
    willParams = json.dumps({"data": "打包前传值"}, ensure_ascii=False)
    sys.stdout.buffer.write(willParams.encode('utf-8'))
    sys.stdout.flush()


def didPack(packInfo):
    """_summary_: 打包后回调，通常在这里上传打包结果到服务器
    """
    print("============打印打包信息:============")
    print(json.dumps(packInfo, indent=4, ensure_ascii=False))
    print("================================")
    # 上传到 OSS
    ossRes = ossUpload(packInfo)

def failPack(errorInfo):
    """_summary_: 打包失败回调，处理打包失败后的错误信息
    """
    print("============打包失败信息:============")
    print(json.dumps(errorInfo, indent=4, ensure_ascii=False))
    print("================================")
    print("打包失败，请检查错误信息并修复问题后重试")


if __name__ == "__main__":
    """_summary_: 无需修改"""
    parser = argparse.ArgumentParser(description="Packfile script")
    parser.add_argument('--will', action='store_true', help="Execute willPack")
    parser.add_argument('--did', action='store_true', help="Execute didPack")
    parser.add_argument('--fail', action='store_true', help="Execute failPack")
    parser.add_argument('--t', action='store_true', help="Execute templateHtml")
    args = parser.parse_args()

    if args.will:
        willPack()
    elif args.did:
        packInfo = json.loads(sys.stdin.read())  
        didPack(packInfo)
    elif args.fail:
        errorInfo = json.loads(sys.stdin.read())
        failPack(errorInfo)
    elif args.t:
        print("用于生成 index.html 模板，并自定义")
        # 修改 config.py 中的 IndexTemplate 为 custom，执行 hpack t [模板名]
        # 打开下面注释，前往README.md文档中找到 customTemplateHtml 方法并添加到PackFile.py文件
        templateInfo = json.loads(sys.stdin.read())
        customTemplateHtml(templateInfo) 
    else:
        print("无效的参数，请使用 --will 、--did、--t")
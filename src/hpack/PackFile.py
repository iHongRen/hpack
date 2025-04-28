# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import argparse
import json
import os
import sys
from datetime import datetime
from string import Template

import oss2  # pip3 install oss2
from config import Config


class OSSConfig: 
    # 如果您需要使用OSS, 需要先安装 pip3 install oss2
    # 阿里云OSS配置 - 如果您不使用阿里云OSS，则不用修改
    Access_key_id = 'your Access_key_id'
    Access_key_secret = 'your Access_key_secret'
    Endpoint = 'your Endpoint'
    Bucket_name = 'your Bucket_name'
    Bucket_dir = 'hpack'

def ossUpload(packInfo):
    """_summary_: 上传打包结果到 OSS"""
    
    build_dir = packInfo["build_dir"]
    remote_dir = packInfo["remote_dir"]
   
    # 上传 hpack/build/{product} 目录里的打包文件到 OSS
    if len(os.listdir(build_dir)) == 0:
        print(f"无法上传空的目录 {build_dir}")
        return False

    auth = oss2.Auth(OSSConfig.Access_key_id, OSSConfig.Access_key_secret)
    bucket = oss2.Bucket(auth, OSSConfig.Endpoint, OSSConfig.Bucket_name)

    for root, _, files in os.walk(build_dir):
        for file in files:
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

            except Exception as e:
                print(f"文件 {file} 上传到 OSS 时出现异常: {e}。")
                return False

    print("\033[34m所有文件上传到 OSS 成功。\033[0m")
    return True


def willPack():
    """_summary_: 打包前调用"""
    print("willPack 打包前传值，使用的 print")


def didPack(packInfo):
    """_summary_: 打包后回调，通常在这里上传打包结果到服务器
    """
 
    # 打包完成后，上传到 OSS， 你也可以上传到自己的服务器
    result = ossUpload(packInfo)
    if not result:
        return

    # print("============打印打包信息:============")
    # print(json.dumps(packInfo, indent=4, ensure_ascii=False))
    # print("================================")

    url = f"{Config.BaseURL}/{packInfo['remote_dir']}/index.html" 
    print(f"\033[0m请访问 {url}\033[0m")


# def customTemplateHtml(templateInfo):
#     packInfo = templateInfo["packInfo"]
#     html = templateInfo["html"]

#     date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
#     # 请修改自定义的 hapck/index.html
#     # 完成对应 $变量的填充
#     template = Template(html)
#     html_template = template.safe_substitute(
#         app_icon=Config.AppIcon,
#         title=Config.AppName,
#         badge=Config.Badge,
#         date=date,
#         version_name=packInfo["version_name"],
#         version_code=packInfo["version_code"],
#         size=packInfo["size"],
#         desc=packInfo["desc"],
#         manifest_url=packInfo["manifest_url"],
#         qrcode=packInfo["qrcode"]
#     )
#     print(html_template)  # 打印到标准输出，用于传参，不可删除


if __name__ == "__main__":
    """_summary_: 无需修改"""
    parser = argparse.ArgumentParser(description="Packfile script")
    parser.add_argument('--will', action='store_true', help="Execute willPack")
    parser.add_argument('--did', action='store_true', help="Execute didPack")
    parser.add_argument('--t', action='store_true', help="Execute templateHtml")
    args = parser.parse_args()

    if args.will:
        willPack()
    elif args.did:
        packInfo = json.loads(sys.stdin.read())  
        didPack(packInfo)
    elif args.t:
        # 从标准输入读取 JSON 数据
        templateInfo = json.loads(sys.stdin.read())  
        # customTemplateHtml(templateInfo) 
    else:
        print("无效的参数，请使用 --will 或 --did。")
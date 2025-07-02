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
    
    build_dir = packInfo.get("build_dir")
    remote_dir = packInfo.get("remote_dir")
   
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

    print("所有文件上传到 OSS 成功。")
    return True


def willPack():
    """_summary_: 打包前调用"""
    willParams = json.dumps({"data": "打包前传值"},ensure_ascii=False)
    # 打包前传值，可以在这里读取一些工程配置，再传递给打包脚本
    sys.stdout.buffer.write(willParams.encode('utf-8'))
    sys.stdout.flush()

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

    # 获取打包结果的远程目录
    url = f"{Config.BaseURL}/{packInfo.get('remote_dir')}/index.html" 
    # 打印访问链接
    print(f"请访问 {url}")


# def customTemplateHtml(templateInfo):
#     packInfo = templateInfo.get("packInfo")
#     html = templateInfo.get("html")

#     date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
#     # 请修改自定义的 hapck/index.html
#     # 完成对应 $变量的填充
#     template = Template(html)
#     html_template = template.safe_substitute(
#         app_icon=Config.AppIcon,
#         title=Config.AppName,
#         badge=Config.Badge,
#         date=date,
#         version_name=packInfo.get("version_name"),
#         version_code=packInfo.get("version_code"),
#         size=packInfo.get("size"),
#         desc=packInfo.get("desc"),
#         manifest_url=packInfo.get("manifest_url"),
#         qrcode=packInfo.get("qrcode")
#     )
#     sys.stdout.buffer.write(html_template.encode('utf-8'))
#     sys.stdout.flush()



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
        templateInfo = json.loads(sys.stdin.read())  
        # 从标准输入读取 JSON 数据，使用自定义 index.html，
        # 修改 config.py 中的 IndexTemplate，执行 hpack t [模板名]
        # 打开下面注释
        # customTemplateHtml(templateInfo) 
    else:
        print("无效的参数，请使用 --will 、--did、--t")
# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import argparse
import json
import os
import sys

import oss2  # pip3 install oss2
from config import Config


def willPack():
    """_summary_: 打包前调用"""
    print("============开始打包=============")


def didPack():
    """_summary_: 打包后回调，通常在这里上传打包结果到服务器和自定义index.html
    """
    # 从标准输入读取 JSON 数据
    packJson = sys.stdin.read()
    packInfo = json.loads(packJson)  
    
    # 打包完成后，上传到 OSS， 你也可以上传到自己的服务器
    upload_to_oss(Config, packInfo)

    # print("============打印打包信息:============")
    # print(json.dumps(packInfo, indent=4, ensure_ascii=False))
    # print("================================")

    url = f"{Config.BaseURL}/{packInfo['remote_dir']}/index.html" 
    print(f"\033[0m请访问 {url}\033[0m")


def upload_to_oss(Config, packInfo):
    """_summary_: 上传打包结果到 OSS"""
    
    build_dir = packInfo["build_dir"]
    remote_dir = packInfo["remote_dir"]
   
    # 上传 hpack/build 目录里的打包文件到 OSS
    if len(os.listdir(build_dir)) == 0:
        print(f"无法上传空的目录 {build_dir}")
        return False

    auth = oss2.Auth(Config.Access_key_id, Config.Access_key_secret)
    bucket = oss2.Bucket(auth, Config.Endpoint, Config.Bucket_name)

    for root, _, files in os.walk(build_dir):
        for file in files:
            if file == "unsign_manifest.json5":
                continue
            
            file_path = os.path.join(root, file)
            try:
                print(f"正在上传： {file} ")
                remotePath = f"{Config.Bucket_dir}/{remote_dir}/{file}"
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


if __name__ == "__main__":
    """_summary_: 无需修改"""
    parser = argparse.ArgumentParser(description="Packfile script")
    parser.add_argument('--will', action='store_true', help="Execute willPack")
    parser.add_argument('--did', action='store_true', help="Execute didPack")
    args = parser.parse_args()

    if args.will:
        willPack()
    elif args.did:
        didPack() 
    else:
        print("无效的参数，请使用 --will 或 --did。")
# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# 请参考部分代码，复制到你的 PackFile.py 文件中
 
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
    Access_key_id = 'your_access_key_id'
    Access_key_secret = 'your_access_key_secret'
    Endpoint = 'your_endpoint'
    Bucket_name = 'your_bucket_name'
    Bucket_dir = 'hpack'


# 初始化 OSS 客户端
auth = oss2.Auth(OSSConfig.Access_key_id, OSSConfig.Access_key_secret)
bucket = oss2.Bucket(auth, OSSConfig.Endpoint, OSSConfig.Bucket_name)

def ossUpload(packInfo):
    """_summary_: 上传打包结果到 OSS"""
    
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

    
def uploadHistoryJson(packInfo):
    """_summary_: 上传 history.json 到 OSS， history.html 直接访问这个json加载历史数据"""
    historyJsonPath = OSSConfig.Bucket_dir +'/history.json'
    try:
        data = bucket.get_object(historyJsonPath)
        historyJson = json.loads(data.read())
    except Exception as e:
        historyJson = []

    # 选取需要的数据拼接
    historyJson.append({
        "version": packInfo.get("version_name"),
        "build": packInfo.get("version_code"),
        "size": packInfo.get("size"),
        "desc": packInfo.get("desc"),
        "index_url": packInfo.get("index_url"),
        "manifest_url": packInfo.get("manifest_url"),
        "date": packInfo.get("date"),
        "packText": '测试包', # 这里可以自定义，比如自己写代码获取当前打包类型(测试、验收、正式等)
    })
    # 只保留最多1000条
    if len(historyJson) > 1000:
        historyJson = historyJson[-1000:]

    try:
        data = json.dumps(historyJson, ensure_ascii=False, indent=4)
        result = bucket.put_object(historyJsonPath, data)
        if result.status == 200:
            print(f"文件 history.json 上传到 OSS 成功。")
            return True
        else:
            print(f"文件 history.json 上传到 OSS 失败，状态码: {result.status}。")
    except Exception as e:
        print(f"文件 history.json 上传到 OSS 时出现异常: {e}。")
    return False


def willPack():
    """_summary_: 打包前调用"""
    willParams = json.dumps({"data": "打包前传值"}, ensure_ascii=False)
    # 打包前传值，可以在这里读取一些工程配置，再传递给打包脚本
    sys.stdout.buffer.write(willParams.encode('utf-8'))
    sys.stdout.flush()


def didPack(packInfo):
    """_summary_: 打包后回调，通常在这里上传打包结果到服务器
    """
    # 上传到 OSS
    ossRes = ossUpload(packInfo)
    # 上传历史json, 如果不需要，可以注释掉
    historyRes = uploadHistoryJson(packInfo)

    if ossRes and historyRes:
        print("============打印打包信息:============")
        print(json.dumps(packInfo, indent=4, ensure_ascii=False))
        print("================================")


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
        pass
    else:
        print("无效的参数，请使用 --will 、--did、--t")
# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# 请参考部分代码，复制到你的 PackFile.py 文件中
# 蒲公英只支持单个 hap 文件

import argparse
import json
import os
import sys
from datetime import datetime
from string import Template

from config import Config
from pgyer import upload_pgyer


# 上传完成回调
def upload_complete_callback(isSuccess, result):
  if isSuccess:
    print('上传完成')
  else:
    print('上传失败')

def pgyUpload(packInfo):
    """_summary_: 上传到蒲公英"""
    # 鸿蒙 HarmonyOS App 如何内测分发: https://www.pgyer.com/doc/view/harmonyos
    # demo: https://github.com/PGYER/upload-app-api-example/tree/main/python-demo

    # 1、先下载 demo 中的文件 upload_pgyer.py, 放到和 PackFile.py 同级目录
    # https://github.com/PGYER/upload-app-api-example/blob/main/python-demo/utils/upload_pgyer.py
    
    # 2、安装依赖： pip install requests

    # 3、去蒲公英官网申请 API KEY，完善信息。

    # .hap (HarmonyOS)，xxxxx 修改为你的打包后的文件名
    app_path = f"{packInfo['appPath']}/xxxxx.hap"  # 例如: '/path/to/app.ipa' 或 '/path/to/app.apk' 或 '/path/to/app.hap' 
    pgyer_api_key = '<your api key>' # API KEY
    pgyer_password = '<your app install password>' # 安装密码

    pgyer.upload_to_pgyer(
        path = app_path, 
        api_key = pgyer_api_key, 
        install_type = 2,  # 1:公开 2:密码安装 3:邀请安装
        password=pgyer_password, 
        update_description=packInfo.get("desc"),
        callback=upload_complete_callback
    )


def willPack():
    """_summary_: 打包前调用"""
    willParams = json.dumps({"data": "打包前传值"}, ensure_ascii=False)
    # 打包前传值，可以在这里读取一些工程配置，再传递给打包脚本
    sys.stdout.buffer.write(willParams.encode('utf-8'))
    sys.stdout.flush()


def didPack(packInfo):
    """_summary_: 打包后回调，通常在这里上传打包结果到服务器
    """
    # 上传到蒲公英
    pgyUpload(packInfo)
   
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
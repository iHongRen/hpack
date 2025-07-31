# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# 自定义 index.html 模板示例
 
import argparse
import json
import os
import sys
from datetime import datetime
from string import Template

from config import Config


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
    willParams = json.dumps({"data": "打包前传值"},ensure_ascii=False)
    sys.stdout.buffer.write(willParams.encode('utf-8'))
    sys.stdout.flush()


def didPack(packInfo):
    """_summary_: 打包后回调，通常在这里上传打包结果到服务器
    """
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
        print("用于生成 index.html 模板，并自定义")
        # 修改 config.py 中的 IndexTemplate 为 custom，执行 hpack t [模板名]
        templateInfo = json.loads(sys.stdin.read())
        customTemplateHtml(templateInfo) 
    else:
        print("无效的参数，请使用 --will 、--did、--t")
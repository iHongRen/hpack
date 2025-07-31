# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# Webhook 使用示例
# 先安装依赖：pip install requests

import argparse
import json
import os
import sys
from datetime import datetime
from string import Template

from config import Config
from DingTalkBot import DingTalkBot
from WeComBot import WeComBot
from FeishuBot import FeishuBot


def dingtalk(packInfo):
    """_summary_: 钉钉机器人"""
    WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=你的token"
    bot = DingTalkBot(WEBHOOK)
    bot.send_text("测试")
    bot.send_link(title="Python官网", text="Python官方网站", message_url="https://www.python.org/")
    bot.send_markdown(title="Markdown测试", text="## 二级标题\n- 列表1\n- 列表2")

def wecom(packInfo):
    """_summary_: 企业微信机器人"""
    WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"
    bot = WeComBot(WEBHOOK)
    bot.send_text(content="测试")
    bot.send_markdown(content="## 二级标题\n- 列表1\n- 列表2")

def feishu(packInfo):
    """_summary_: 飞书机器人"""
    WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook"
    bot = FeishuBot(WEBHOOK)
    bot.send_text(content="测试")
    bot.send_markdown(content="## 二级标题\n- 列表1\n- 列表2")


def willPack(packInfo):
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
    # 处理上传完成后...
    # 上报到钉钉机器人
    dingtalk(packInfo)
    # 上报到企业微信机器人
    wecom(packInfo)
    # 上报到飞书机器人
    feishu(packInfo)


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
        # 打开下面注释，前往README.md文档中找到 customTemplateHtml 方法并添加到PackFile.py文件
        # templateInfo = json.loads(sys.stdin.read())
        # customTemplateHtml(templateInfo) 
    else:
        print("无效的参数，请使用 --will 、--did、--t")
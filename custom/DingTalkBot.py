# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# 都是ai写的，作者没有测试环境，所以如果遇到问题，欢迎提交issue。
# 钉钉机器人
# 文档：https://open.dingtalk.com/document/orgapp/assign-a-webhook-url-to-an-internal-chatbot

import json
from typing import List, Optional

import requests


class DingTalkBot:
    def __init__(self, webhook: str):
        self.webhook = webhook
        self.headers = {'Content-Type': 'application/json;charset=utf-8'}
    
    def send_text(self, content: str, at_mobiles: List[str] = None, is_at_all: bool = False):
        """发送文本消息"""
        data = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": is_at_all
            }
        }
        return self._send(data)
    
    def send_link(self, title: str, text: str, message_url: str, pic_url: Optional[str] = None):
        """发送链接卡片"""
        data = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "messageUrl": message_url,
                "picUrl": pic_url or ""
            }
        }
        return self._send(data)
    
    def send_markdown(self, title: str, text: str, at_mobiles: List[str] = None, is_at_all: bool = False):
        """发送Markdown消息"""
        data = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": is_at_all
            }
        }
        return self._send(data)
    
    def _send(self, data: dict):
        """发送请求的内部方法"""
        try:
            response = requests.post(
                url=self.webhook,
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()  # 抛出HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

# 使用示例
if __name__ == "__main__":
    WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=你的token"
    bot = DingTalkBot(WEBHOOK)
    
    # 发送文本消息
    bot.send_text("测试文本消息", at_mobiles=["13800138000"])
    
    # 发送链接
    bot.send_link(
        title="Python官网",
        text="Python官方网站",
        message_url="https://www.python.org/"
    )
    
    # 发送Markdown
    bot.send_markdown(
        title="Markdown测试",
        text="## 二级标题\n- 列表1\n- 列表2"
    )

# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# 都是ai写的，作者没有测试环境，所以如果遇到问题，欢迎提交issue。
# 企业微信机器人
# 文档：https://developer.work.weixin.qq.com/document/path/99110

import base64
import hashlib
import json
from typing import List, Optional

import requests


class WeComBot:
    """企业微信机器人Webhook工具类"""
    def __init__(self, webhook_url: str):
        """
        初始化机器人
        :param webhook_url: 企业微信机器人的Webhook地址
        """
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json;charset=utf-8"}

    def _send_request(self, data: dict) -> dict:
        """
        发送请求到企业微信API
        :param data: 消息数据
        :return: 响应结果
        """
        try:
            response = requests.post(
                url=self.webhook_url,
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def send_text(self, content: str, mentioned_list: List[str] = None, mentioned_mobile_list: List[str] = None) -> dict:
        """
        发送文本消息
        :param content: 消息内容
        :param mentioned_list: 要@的成员ID列表
        :param mentioned_mobile_list: 要@的手机号列表
        :return: 响应结果
        """
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or [],
                "mentioned_mobile_list": mentioned_mobile_list or []
            }
        }
        return self._send_request(data)

    def send_image(self, image_path: str) -> dict:
        """
        发送图片消息
        :param image_path: 图片本地路径
        :return: 响应结果
        """
        # 读取图片并进行Base64编码
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # 计算图片MD5
        image_md5 = hashlib.md5(image_data).hexdigest()
        image_base64 = base64.b64encode(image_data).decode()

        data = {
            "msgtype": "image",
            "image": {
                "base64": image_base64,
                "md5": image_md5
            }
        }
        return self._send_request(data)

    def send_markdown(self, content: str) -> dict:
        """
        发送Markdown消息
        :param content: Markdown内容
        :return: 响应结果
        """
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        return self._send_request(data)

    def send_news(self, articles: List[dict]) -> dict:
        """
        发送图文消息
        :param articles: 图文列表，每个元素包含title、description、url、picurl
        :return: 响应结果
        """
        data = {
            "msgtype": "news",
            "news": {
                "articles": articles
            }
        }
        return self._send_request(data)

# 使用示例
if __name__ == "__main__":
    # 替换为你的企业微信机器人Webhook地址
    WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"
    
    # 初始化机器人
    bot = WeComBot(WEBHOOK_URL)
    
    # 1. 发送文本消息（带@功能）
    text_result = bot.send_text(
        content="这是一条企业微信测试消息",
        mentioned_mobile_list=["13800138000"]  # @指定手机号
    )
    print("文本消息发送结果:", text_result)
    
    # 2. 发送Markdown消息
    markdown_content = """
    # 标题一
    ## 标题二
    - 列表项1
    - 列表项2
    > 引用内容
    **加粗文本**
    [链接文字](https://work.weixin.qq.com/)
    """
    markdown_result = bot.send_markdown(content=markdown_content)
    print("Markdown消息发送结果:", markdown_result)
    
    # 3. 发送图文消息
    news_result = bot.send_news([
        {
            "title": "企业微信官网",
            "description": "企业微信，高效办公的正确打开方式",
            "url": "https://work.weixin.qq.com/",
            "picurl": "https://picsum.photos/200/300"  # 图片URL
        }
    ])
    print("图文消息发送结果:", news_result)
    
    # 4. 发送图片消息（请替换为实际图片路径）
    # image_result = bot.send_image(image_path="./test.jpg")
    # print("图片消息发送结果:", image_result)
    
# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# 都是ai写的，作者没有测试环境，所以如果遇到问题，欢迎提交issue。
# 飞书机器人
# 文档：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot

import base64
import hashlib
import json
from typing import Dict, List, Optional

import requests


class FeishuBot:
    """飞书机器人Webhook工具类"""
    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        """
        初始化飞书机器人
        :param webhook_url: 飞书机器人Webhook地址
        :param secret: 签名密钥（设置了安全验证时需要）
        """
        self.webhook_url = webhook_url
        self.secret = secret
        self.headers = {"Content-Type": "application/json;charset=utf-8"}

    def _get_signature(self) -> Dict[str, str]:
        """生成签名参数（当设置了secret时）"""
        if not self.secret:
            return {}
            
        import time
        timestamp = str(int(time.time()))
        sign_str = f"{timestamp}\n{self.secret}"
        hmac_code = hashlib.sha256(sign_str.encode("utf-8")).digest()
        signature = base64.b64encode(hmac_code).decode("utf-8")
        return {"timestamp": timestamp, "sign": signature}

    def _send_request(self, msg_type: str, content: Dict) -> Dict:
        """发送请求到飞书API"""
        # 构建完整URL（包含签名参数）
        params = self._get_signature()
        url = self.webhook_url
        if params:
            url += f"?timestamp={params['timestamp']}&sign={params['sign']}"

        data = {
            "msg_type": msg_type,
            "content": content
        }

        try:
            response = requests.post(
                url=url,
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def send_text(self, text: str, at_all: bool = False, at_users: List[str] = None) -> Dict:
        """
        发送文本消息
        :param text: 消息内容
        :param at_all: 是否@所有人
        :param at_users: 要@的用户open_id列表
        :return: 响应结果
        """
        mentions = []
        if at_all:
            mentions.append({"user_id": "all"})
        if at_users:
            mentions.extend([{"user_id": uid} for uid in at_users])

        content = {
            "text": text,
            "mentioned_list": mentions
        }
        return self._send_request("text", content)

    def send_image(self, image_path: str) -> Dict:
        """
        发送图片消息
        :param image_path: 本地图片路径
        :return: 响应结果
        """
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode()
        image_md5 = hashlib.md5(image_data).hexdigest()

        content = {
            "image_key": "",  # 留空即可，飞书会自动处理
            "base64": image_base64,
            "md5": image_md5
        }
        return self._send_request("image", content)

    def send_post(self, title: str, content: List[List[Dict]]) -> Dict:
        """
        发送富文本消息（Post格式）
        :param title: 标题
        :param content: 内容块，格式示例：
            [
                [{"tag": "text", "text": "第一行文本"}],
                [{"tag": "a", "text": "链接", "href": "https://feishu.cn"}]
            ]
        :return: 响应结果
        """
        post_content = {
            "title": title,
            "content": content
        }
        return self._send_request("post", {"post": {"zh_cn": post_content}})

    def send_share_chat(self, chat_id: str) -> Dict:
        """
        发送分享群聊消息
        :param chat_id: 群聊ID
        :return: 响应结果
        """
        return self._send_request("share_chat", {"chat_id": chat_id})

# 使用示例
if __name__ == "__main__":
    # 替换为你的飞书机器人Webhook和secret（secret可选）
    WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址"
    SECRET = "你的签名密钥（如果设置了的话）"  # 可选，设置了安全验证则需要

    # 初始化机器人
    bot = FeishuBot(WEBHOOK_URL, SECRET)

    # 1. 发送文本消息
    text_result = bot.send_text(
        text="这是一条飞书测试消息",
        at_all=False,
        at_users=["ou_xxxxxx"]  # 替换为实际用户的open_id
    )
    print("文本消息结果:", text_result)

    # 2. 发送富文本消息（Post格式）
    post_content = [
        [{"tag": "text", "text": "第一行文本 "}, {"tag": "emoji", "id": "1"}],
        [{"tag": "a", "text": "飞书官网", "href": "https://feishu.cn"}],
        [{"tag": "at", "user_id": "all"}]  # @所有人
    ]
    post_result = bot.send_post(
        title="富文本消息标题",
        content=post_content
    )
    print("富文本消息结果:", post_result)

    # 3. 发送图片消息（请替换为实际图片路径）
    # image_result = bot.send_image(image_path="./test.png")
    # print("图片消息结果:", image_result)

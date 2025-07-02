# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack

import json
import os
import subprocess
from datetime import datetime
from string import Template

from toolConfig import ToolConfig
from utils import get_python_command, printError


def handle_custom_html(packInfo):
    template_path = os.path.join(ToolConfig.HpackDir, "index.html")
    if not os.path.exists(template_path):
        printError("自定义的 hpack/index.html 文件不存在，请先执行 hpack t [tname] 命令，或手动创建 index.html 文件。")
        return False

    try:
        with open(template_path, "r", encoding="utf-8") as template_file:
            templateHtml = template_file.read()

        data = {
            "html": templateHtml,
            "packInfo": packInfo
        }
        dataJson = json.dumps(data)

        pack_file_path = os.path.join(ToolConfig.HpackDir, 'PackFile.py')
        python_cmd = get_python_command()

        process = subprocess.run(
            [python_cmd, pack_file_path, '--t'],
            input=dataJson,
            text=True,
            capture_output=True,
            check=True,
            encoding='utf-8'
        )
        html = process.stdout.strip()
        
        file_path = os.path.join(packInfo.get("build_dir"), "index.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
            return True
    except Exception as e:
        printError(f"处理模板 HTML 时出错: {e}")
        return False


def handle_template_html(Config, packInfo):
    try:
        template_path = os.path.join(ToolConfig.TemplateDir, f"{Config.IndexTemplate}.html")
        with open(template_path, "r", encoding="utf-8") as template_file:
            html = template_file.read()

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        template = Template(html)
        html_template = template.safe_substitute(
            app_icon=Config.AppIcon,
            title=Config.AppName,
            badge=Config.Badge,
            date=date,
            version_name=packInfo.get("version_name"),
            version_code=packInfo.get("version_code"),
            size=packInfo.get("size"),
            desc=packInfo.get("desc"),
            manifest_url=packInfo.get("manifest_url"),
            qrcode=packInfo.get("qrcode")
        )

        file_path = os.path.join(packInfo.get("build_dir"), "index.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        return True
    except Exception as e:
        printError(f"处理模板 HTML 时出错: {e}")
        return False

def handle_template(Config, packInfo):
    """处理模板 HTML"""
    if Config.IndexTemplate == "custom" or not Config.IndexTemplate:
        return handle_custom_html(packInfo)
    else:
        return handle_template_html(Config, packInfo)

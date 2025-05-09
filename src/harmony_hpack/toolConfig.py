# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os


class ToolConfig: 
    CurrentDir = os.path.dirname(os.path.abspath(__file__))
    TemplateDir = os.path.join(CurrentDir, 'templates')

    HpackDir = 'hpack'
    BuildDir = os.path.join(HpackDir, 'build')

    # 打包工具配置 - 无需修改
    SignDir = 'hap-manifest-sign-tool'
    HapSignTool = os.path.join(CurrentDir, SignDir, 'hap-sign-tool.jar')
    ManifestSignTool = os.path.join(CurrentDir, SignDir, 'manifest-sign-tool-1.0.0.jar')
    ExcludeDirs = ['oh_modules', HpackDir] # 查找已构建的包时排除的目录
    
    # 文件命名 - 无需修改
    UnsignManifestFile = "unsign_manifest.json5"
    SignedManifestFile = "manifest.json5"

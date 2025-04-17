# -*- coding: utf-8 -*-

#  @author : @cxy
#  @date : 2025/4/10
#  @github : https://github.com/iHongRen/hpack
 
import os
class ToolConfig: 
    BuildDir = 'build'
    IndexTemplateHtml = 'index_template.html'

    # 打包工具配置 - 无需修改
    SignDir = 'hap-manifest-sign-tool'
    HapSignTool = os.path.join(SignDir, 'hap-sign-tool.jar')
    ManifestSignTool = os.path.join(SignDir, 'manifest-sign-tool-1.0.0.jar')
    ExcludeDirs = ['oh_modules', 'hpack'] # 查找已构建的包时排除的目录
    
    # 文件命名 - 无需修改
    UnsignManifestFile = "unsign_manifest.json5"
    SignedManifestFile = "manifest.json5"

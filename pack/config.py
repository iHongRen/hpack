# -*- coding: utf-8 -*-

#  @author : @cxy
#  @date : 2025/4/10
#  @github : https://github.com/iHongRen/hpack
 
import os
class Config: 
    # 阿里云OSS配置
    Access_key_id = 'your Access_key_id'
    Access_key_secret = 'your Access_key_secret'
    Endpoint = 'your Endpoint'
    Bucket_name = 'your Bucket_name'
    Bucket_dir = 'hpack'
    Cname = 'your cname'
    BaseURL = f"https://{Cname}/{Bucket_dir}"

    # 应用名称和图标 - 有想法的可自行修改代码，从工程项目中获取
    AppName = 'hpack'
    AppIcon = f"https://{Cname}/xx/AppIcon.png"
    
    # 打包签名配置 
    PackDir = 'pack'
    SignDir = 'sign'
    Cert = os.path.join(PackDir, SignDir, 'release.cer') 
    Profile = os.path.join(PackDir, SignDir, 'test_release.p7b')  
    Keystore =  os.path.join(PackDir, SignDir, 'harmony.p12') 
    Alias = 'your key alias'
    KeyPwd = 'your key password'
    KeystorePwd = 'your store password'
    
    # 打包工具配置 - 无需修改
    BuildDir = os.path.join(PackDir, 'build') 
    HapSignTool = os.path.join(PackDir, 'hap-sign-tool.jar')
    IndexTemplateHtml  = os.path.join(PackDir, 'index_template.html')
    ManifestSignTool = os.path.join(PackDir, 'manifest-sign-tool' , 'manifest-sign-tool-1.0.0.jar')
    ExcludeDirs = ['oh_modules', 'pack'] # 查找已构建的包时排除的目录
    
    # 文件命名 - 无需修改
    UnsignManifestFile = "unsign_manifest.json5"
    SignedManifestFile = "manifest.json5"

# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os


class Config: 
    # 阿里云OSS配置 - 如果您不使用阿里云OSS，则不用修改
    Access_key_id = 'your Access_key_id'
    Access_key_secret = 'your Access_key_secret'
    Endpoint = 'your Endpoint'
    Bucket_name = 'your Bucket_name'
    Bucket_dir = 'hpack'
    
    # 安装包存放的服务器的域名 --- 必填项
    DeployDomain = 'static.hpack.com'
    
    # 安装包存放的服务器地址，必须是 https --- 必填项
    BaseURL = f"https://{DeployDomain}/{Bucket_dir}"

    # 应用信息 
    AppIcon = f"{BaseURL}/AppIcon.png"  # --- 必填项
    AppName = 'hpack'
    Badge = '鸿蒙版'
    
    # index模板选择, 可选值为 [default, tech, cartoon, tradition, custom]
    # 如果是 custom，则表示自定义模板，需要自己在 hpack 目录写一个 index.html，
    # 打包完成后进行内容填充，再写入 hpack/build 目录
    IndexTemplate = "default"  

    # 打包签名配置 
    Alias = 'your key alias'  # --- 必填项
    KeyPwd = 'your key password'  # --- 必填项
    KeystorePwd = 'your store password'  # --- 必填项
    # 替换 hapck/sign 目录下的证书文件，如替换的文件名一致，则不用修改
    SignDir = 'sign'
    Cert = os.path.join(SignDir, 'release.cer') 
    Profile = os.path.join(SignDir, 'test_release.p7b')  
    Keystore =  os.path.join(SignDir, 'harmony.p12') 
    
   
    
    
    
   

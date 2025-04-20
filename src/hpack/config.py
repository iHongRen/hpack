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
    
    # 安装包存放的服务器地址的域名 - 如 static.hpack.com
    DeployDomain = 'your cname'
    
    # 安装包存放的服务器地址，必须是 https
    BaseURL = f"https://{DeployDomain}/{Bucket_dir}"

    # 应用名称和图标 
    AppName = 'hpack'
    AppIcon = f"{BaseURL}/AppIcon.png"
    
    # 打包签名配置 
    Alias = 'your key alias'
    KeyPwd = 'your key password'
    KeystorePwd = 'your store password'
    # 替换 hapck/sign 目录下的证书文件
    SignDir = 'sign'
    Cert = os.path.join(SignDir, 'release.cer') 
    Profile = os.path.join(SignDir, 'test_release.p7b')  
    Keystore =  os.path.join(SignDir, 'harmony.p12') 
    
    
   

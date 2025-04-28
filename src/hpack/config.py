# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack
 
import os


class Config: 
    # 安装包存放的服务器的域名 --- 必填项
    DeployDomain = 'static.hpack.com'
    
    # 安装包存放的服务器地址，必须是 https --- 必填项
    BaseURL = f"https://{DeployDomain}/hpack"

    # 应用信息 
    AppIcon = f"{BaseURL}/AppIcon.png"  # --- 必填项
    AppName = 'hpack'
    Badge = '鸿蒙版'
    
    # index模板选择, 可选值为 [default, simple, tech, cartoon, tradition, custom]
    # 如果是 custom，则表示自定义模板，需要自己在 hpack/ 下目录写一个 index.html 
    # 或者使用 hpack t [tname] 命令生成模板 index.html
    # 打包完成后进行内容填充，再写入 hpack/build/{product} 目录
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
    
    # 设置默认打包 product
    # 优先使用这个指定的 product。
    # 不设置，则通过读 build-prodile.json5 获取，存在多个时，打包前会提示选择
    Product = ""  

    # 编译模式，默认是 debug 模式，release 模式需要设置为False
    Debug = True  

    # 用于完全自定义 hvigorw 构建命令，配置后 Product、Debug 无效
    # hvigorw 使用 https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-hvigor-commandline
    # 使用示例：
    # [
    #    'hvigorw', 'assembleHap', 'assembleHsp', 
    #    '--mode', 'module', 
    #    '-p', 'product=default', 
    #    '-p', 'debuggable=true',
    #    '--no-daemon'
    # ]
    HvigorwCommand = [] 
    
    
    
   

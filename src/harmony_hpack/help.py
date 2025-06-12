from version import __version__

f"""
hpack: v{__version__} - 鸿蒙应用打包、签名、安装和上传工具
查看:
  -v, --version  显示版本信息
  -h, --help     显示帮助信息
  -u, --udid     显示设备的 UDID
  targets        显示连接的设备列表

执行:
  init                   初始化 hpack 目录并创建配置文件
  pack, p [desc]         执行打包签名和上传, desc 打包描述，可选
  template, t [tname]    用于自定义模板时，生成 index.html 模板文件，tname 可选值：{get_template_filenames()}，默认为 default

安装包:
  install, i [-product]   将打包后的产物安装到设备，product 为你的产物名，默认为 default，需要先 hapck pack 打包。
  示例： hpack i -myproduct   # 安装 myproduct 产物，注意加上横杠(-）

  install, i signedPath   为已签名包的目录或文件路径，支持 .app、.hap文件或目录。
  示例1：hpack i ./xx.app
  示例2：hpack i ./xx.hap
  示例3：hpack i ./build/default

签名:
  sign, s unsignedPath certPath
  unsignedPath 为待签名的目录或文件路径，支持 .app、.hap、.hsp 文件或目录。
  certPath 为签名证书配置文件路径。
  示例1：hpack s ./xx.app ./sign/cert.py
  示例2：hpack s ./xx.hap ./sign/cert.py
  示例3：hpack s ./build/default ./sign/cert.py

  cert.py 签名证书配置文件示例如下：
  # -*- coding: utf-8 -*-
  Alias = 'key alias' 
  KeyPwd = 'key password' 
  KeystorePwd = 'store password' 
  Cert ='./cert.cer'  # 相对于证书配置文件的路径
  Profile = './profile.p7b' # 相对于证书配置文件的路径
  Keystore =  './keystore.p12' # 相对于证书配置文件的路径

  github: https://github.com/iHongRen/hpack
  """
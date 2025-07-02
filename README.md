# hpack - 鸿蒙 HarmonyOS 内测打包分发工具

![image](https://img.shields.io/badge/version-1.0.6-blue) 

[官网](https://ihongren.github.io/hpack.html) &nbsp;&nbsp; [更新日志](https://github.com/iHongRen/hpack/blob/main/CHANGELOG.md) &nbsp;&nbsp;[deepwiki](https://deepwiki.com/iHongRen/hpack)

## 简介

**[hpack](https://github.com/iHongRen/hpack)** `[h-pack]`是一个专为鸿蒙 HarmonyOS 打造的内测分发工具，借助它，你只需一行命令，就能轻松完成鸿蒙应用的构建、打包、签名，并将其上传至服务器进行内测分发。

这大大简化了开发流程，提高了开发效率，让你能更专注于应用的开发和优化。


## 功能特性

- **打包签名**：自动打出所有的 hap 和 hsp 包，并对它们进行签名。
- **签名 manifest.json5**：读取应用打包数据，自动生成已签名的 `manifest.json5` 文件。
- **分发 index 页**：自动生成分发页，提供多种 HTML 模板，同时支持自定义模板，满足不同的展示需求。
- **二维码生成**：自动生成应用的二维码，方便内测人员快速下载和安装。
- **OSS 上传**：如果完成配置，可将打包好的所有文件上传到阿里云 OSS 。
- **查看连接的设备**：显示所有正在连接的设备名 `hpack targets`。
- **查看UDID**:  显示所有正在连接的设备 UDID `hapck -u`。
- **命令安装**：支持命令安装已签名的 .app、.hap 和包目录。示例： `hpack install xx.app`。
- **签名**：支持对未签名的 .app、.hap、.hsp 和包目录签名。示例:  `hpack s ./xx.app ./sign/cert.py`




## 安装使用


```sh
pip3 install harmony-hpack

# 查看安装成功：
# hpack -h

# 如果安装失败，尝试使用：
# sudo -H pip3 install harmony-hpack

# 指定源安装： 
# pip3 install -i  https://pypi.org/simple harmony-hpack
# pip3 install -i  https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple harmony-hpack
# pip3 install -i  https://mirrors.aliyun.com/pypi/simple harmony-hpack
# pip3 install -i  https://mirrors.cloud.tencent.com/pypi/simple harmony-hpack

# 卸载： 
# pip3 uninstall harmony-hpack
```


在阅读以下内容之前，我们建议你先详细阅读鸿蒙官方文档 [HarmonyOS 应用内部测试](https://developer.huawei.com/consumer/cn/doc/app/agc-help-harmonyos-internaltest-0000001937800101#section042515172197)。

**准备工作**，你需要生成这三个文件：

1、发布证书： .cer 格式

2、内部测试 Profile:  .p7b  格式

3、私钥文件： .p12 格式

**官方给出的内部测试流程大致如下：**

![img](https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/3.jpeg) 



#### 预置环境：

DevEco-Studio ：鸿蒙开发 IDE， 同时集成了各种命令工具

JDK 17+： 签名工具需要。 

python3.7+ ： hpack 由 python 编写，执行环境

```sh
# 在你使用的终端中，检查以下工具是否成功安装：

java --version

python3 --version   # 或 python

pip3 --version      # 或 pip

hvigorw -v   # DevEco-Studio 自带，其他终端使用需设置环境变量，请看下面 Tips

hdc -v # DevEco-Studio 自带，其他终端使用需设置环境变量
```



####  安装 hpack

```sh
pip3 install harmony-hpack # 最新版本 pip3 install harmony-hpack==1.0.6

# 如果安装失败，Win 使用管理员权限
# Mac 尝试使用 sudo 权限：
# sudo -H pip3 install harmony-hpack
```

#### 初始化

在**项目根目录**下执行以下命令，初始化 `hpack` 目录并创建配置文件：

```bash
hpack init   
```

初始化完成后，会在项目根目录下生成 `hpack` 目录，包含以下文件和文件夹：

```shell
.
├── config.py # 配置文件，服务器、应用信息和打包签名等相关信息。
├── Packfile.py # 打包完成后的回调文件，可用于自定义上传和处理逻辑。
└── sign # 存放签名证书文件，需替换为您的证书文件。

```

#### 修改配置

打开 `hpack/config.py` 文件，根据实际情况修改配置信息：

```python
class Config: 
    # 安装包存放的服务器的域名 
    DeployDomain = 'static.hpack.com'
    
    # 安装包存放的服务器地址，必须是 https
    BaseURL = f"https://{DeployDomain}/hpack"

    # 应用信息 
    AppIcon = f"{BaseURL}/AppIcon.png"
    AppName = 'hpack'
    Badge = '鸿蒙版'
    
    # index模板选择, 可选值为 [default, simple, tech, cartoon, tradition, custom]
    # 如果是 custom，则表示自定义模板，需要自己在 hpack 目录写一个 index.html，
    # 打包完成后进行内容填充，再写入 hpack/build/{product} 目录
    IndexTemplate = "default" 

    # 打包签名配置 
    Alias = 'your key alias'
    KeyPwd = 'your key password'
    KeystorePwd = 'your store password'
    # 替换 hapck/sign 目录下的证书文件
    SignDir = 'sign'
    Cert = os.path.join(SignDir, 'release.cer') 
    Profile = os.path.join(SignDir, 'test_release.p7b')  
    Keystore =  os.path.join(SignDir, 'harmony.p12')
    
    
    # 以下是 v1.0.1 新增自定义构建配置 ===================
    # 从v1.0.0升级上来的，可自行加上
    
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
```



替换 `hapck/sign` 目录下的**证书文件**

```shell
.
├── harmony.p12   # 私钥文件
├── release.cer   # 发布证书
└── test_release.p7b  # 内部测试Profile
```



#### 打包

执行以下命令进行打包、签名和上传操作，可选择性地添加更新说明：

```sh
hpack pack "修复了一些已知问题，优化了性能" # 缩写 hpack p [desc]
```

打包完成后，所有打包的文件都在 `hpack/build/{product}` 目录下。  



##### 上传

如果使用阿里云OSS 作为存储服务，需要先安装 oss2：

```sh
pip3 install oss2
```

打开 `Packfile.py` 完成配置：

```python
class OSSConfig: 
    # 如果您需要使用OSS, 需要先安装 pip3 install oss2
    # 如果您不使用阿里云OSS，则不用修改
    Access_key_id = 'your Access_key_id'
    Access_key_secret = 'your Access_key_secret'
    Endpoint = 'your Endpoint'
    Bucket_name = 'your Bucket_name'
    Bucket_dir = 'hpack'
```

如果是使用的是其他服务器，则需要自己编写上传代码：

```python
def didPack(packInfo):
    """_summary_: 打包后回调，通常在这里上传打包结果到服务器
    """
    # 打包结果在hapck/build/{product}，编写你的上传逻辑
```



#### 运行示例图
- 开始打包  
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/0.png"><br>

- 多 product，可选择
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/2.png"><br>

- 打包完成  
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/1.png"><br>

- 扫码安装  
  <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/install.png" width=300>
  <br>



#### 其他命令

**查看帮助**

```sh
hpack -h # 或 hpack help

hpack 命令帮助:  
查看:
  -v, --version  显示版本信息
  -h, --help     显示帮助信息
  -u, --udid     显示设备的 UDID
  targets        显示连接的设备列表

执行:
  init                   初始化 hpack 目录并创建配置文件
  pack, p [desc]         执行打包签名和上传, desc 打包描述，可选
  template, t [tname]    生成 index.html 模板文件，tname 可选值：['default', 'cartoon', 'tech', 'tradition', 'simple']，默认为 default

安装包:
  install, i [-product]   将打包后的产物安装到设备，需要先 hapck pack 打包。
  示例： hpack i -myproduct   # 安装 myproduct 产物，注意加上横杠(-）

  install, i signedPath   为已签名包的目录或文件路径，支持 .app、.hap文件或目录。
  示例1：hpack i ./xx.app
  示例2：hpack i ./xx.hap
  示例3：hpack i ./build/default

签名：
  sign, s unsignedPath certPath
  unsignedPath 为待签名的目录或文件路径，支持 .app、.hap、.hsp 文件或目录。
  certPath 为签名证书配置文件路径。
  示例1：hpack s ./xx.app ./sign/cert.py
  示例2：hpack s ./xx.hap ./sign/cert.py
  示例3：hpack s ./build/default ./sign/cert.py

  /sign 目录的结构如下：
    ├── cert.py
    ├── certFile.cer
    ├── keystore.p12
    └── profile.p7b

  cert.py 签名证书配置文件示例如下：
  # -*- coding: utf-8 -*-
  Alias = 'key alias' 
  KeyPwd = 'key password' 
  KeystorePwd = 'store password' 
  Cert ='./certFile.cer'  # 相对于cert.py的路径
  Profile = './profile.p7b' # 相对于cert.py的路径
  Keystore =  './keystore.p12' # 相对于cert.py的路径
```

**查看版本**

```bash
hpack -v # 或 hpack --version
```
**查看 UDID**

```sh
hpack -u # 或 hpack --udid
```

**查看连接设备**

```sh
hpack targets
```

**对包签名**  

  ```sh
hpack sign,s unsignedPath certPath
# unsignedPath 为待签名的目录或文件路径，支持 .app、.hap、.hsp 文件或目录。
# certPath 为签名证书配置文件路径。
  
示例1：hpack s ./xx.app ./sign/cert.py
示例2：hpack s ./xx.hap ./sign/cert.py
示例3：hpack s ./build/default ./sign/cert.py

/sign 目录的结构如下：
  ├── cert.py
  ├── certFile.cer
  ├── keystore.p12
  └── profile.p7b

cert.py 签名证书配置文件示例如下：
# -*- coding: utf-8 -*-
Alias = 'key alias' 
KeyPwd = 'key password' 
KeystorePwd = 'store password' 
Cert ='./certFile.cer'  # 相对于cert.py的路径
Profile = './profile.p7b' # 相对于cert.py的路径
Keystore =  './keystore.p12' # 相对于cert.py的路径
  ```
**安装本地包**  

  ```sh
# 1、将 hapck pack 打包产物安装到设备，product 为你的产物名，默认为 default。
hpack i [-product]  # 示例： hpack i -myproduct

# 2、将已签名的 xx.app 或者 xx.hap 包安装到设备。
hpack i xx.app或xx.hap # 示例： hpack i ./build/default/xx.hap

# 3、将指定目录下的所有 hap 和 hsp 包安装到设备。
hpack i haphspPath # 示例：hpack i ./hpack/build/default
  ```

<br>


#### 模板图预览

[hpack](https://github.com/iHongRen/hpack) 提供多种内置分发页模板，满足不同风格的需求

```python
# config.py 
# index模板选择, 可选值为 [default, simple, tech, cartoon, tradition, custom]
IndexTemplate = "default" 
```

| <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/default.png" width="300"> | <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/simple.png" width="300"> | <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/tech.png" width="300"> |
| :---: | :---: | :---: |
| default 默认风格 | simple 简单 | tech 科技 |

| <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/cartoon.png" width="300"> | <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/tradition.png" width="300"> |
| :---: | :---: |
| cartoon 卡通 | tradition 传统 |



## 如何自定义分发页 index.html

1、修改 `config.py` 文件的模板配置项为 `custom` 

```python
IndexTemplate = 'custom'  # 表面自定义模板
```

2、如果你想使用 [hpack](https://github.com/iHongRen/hpack) 提供的 HTML 模板来做进一步修改，可以执行以下命令：

```bash
hpack template [tname] # 缩写 hpack t tech
```

`tname` 可选值为 `default`, `simple`, `tech`, `cartoon`, `tradition`，如果不指定，默认使用 `default` 模板。

这个命令会在 `hpack/` 目录下生成对应的` index.html` 模板文件。

如果不使用模板，则需要手动新建` index.html` 文件到 `hpack/` 目录。

3、在 `Packfile.py` 打开关于自定义模板的注释：

```python
def customTemplateHtml(templateInfo):
    packInfo = templateInfo["packInfo"]
    html = templateInfo["html"]

    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 请修改自定义的 hapck/index.html
    # 完成对应 $变量的填充
    template = Template(html)
    html_template = template.safe_substitute(
        app_icon=Config.AppIcon,
        title=Config.AppName,
        badge=Config.Badge,
        date=date,
        version_name=packInfo["version_name"],
        version_code=packInfo["version_code"],
        size=packInfo["size"],
        desc=packInfo["desc"],
        manifest_url=packInfo["manifest_url"],
        qrcode=packInfo["qrcode"]
    )
    print(html_template)  # 打印到标准输出，用于传参，不可删除
    

# 调用 customTemplateHtml
if __name__ == "__main__":    
    ...省略的代码
    elif args.t:
        # 从标准输入读取 JSON 数据
        templateInfo = json.loads(sys.stdin.read())  
        customTemplateHtml(templateInfo) 
```

4、执行打包命令 `hpack p '自定义index.html'`



## 打包后信息说明

```python
# 在 PackFile.py 中，打包完成后会调用这个方法，通常在这里上传打包结果到服务器
def didPack(packInfo):
   print(json.dumps(packInfo, indent=4, ensure_ascii=False))
    
# 打印结果
{
    "bundle_name": "com.cxy.hpack",
    "version_code": 1000000,
    "version_name": "1.0.0",
    "size": "281KB",
    "desc": "打包说明",
    "build_dir": "hpack/build/default",
    "remote_dir": "20250605200049",
    "manifest_url": "https://服务器域名/hpack/20250605200049/manifest.json5",
    "qrcode": "data:image/svg+xml;charset=utf-8,xxx...", # 二维码base64
    "index_url": "https://服务器域名/hpack/20250605200049/index.html",
    "product": "default",  # 选择的product
    "willPack_output": "willPack中打包前传入的参数"
}
```




## Tips:

1、在**非 DevEco-Studio** 的终端执行命令时，需要配置 `hvigorw` 的环境变量

```sh
# Mac
export DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk

# win
https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-hvigor-commandline


# 查看是否成功
hvigorw -v
```

2、如果已安装的 App 和准备要安装的 App 打包证书不一致，需先卸载已安装的 App 。

3、安装时鸿蒙会进行联网校验，手机如果开了代理需要注意下。

4、安装出错时会有提示，根据错误码找原因。[错误码说明](https://developer.huawei.com/consumer/cn/doc/app/agc-help-harmonyos-internaltest-0000001937800101#section10455110143313)。

5、在 `.gitigore` 文件中添加忽略  python 生成的临时文件。

```txt
.gitigore 文件
# 忽略 __pycache__ 目录
__pycache__/
```

6、使用调试.p7b，打出来的包只能本地命令安装，不能通过 DeepLink 形式安装。需使用**内部测试 Profile.p7b**。



## 贡献

如果你有任何建议或发现了 bug，欢迎提交 issues 或 pull requests，让 [hpack](https://github.com/iHongRen/hpack) 变得更好！




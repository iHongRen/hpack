# 🚀 hpack - 鸿蒙 HarmonyOS 内测签名打包分发工具


<div align="center">  

![Version](https://img.shields.io/badge/version-1.0.8-blue?style=flat-square)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)
[🌐 **官网**](https://ihongren.github.io/hpack.html)   •   [📋 **更新日志**](https://github.com/iHongRen/hpack/blob/main/CHANGELOG.md)   •   [📚 **deepwiki**](https://deepwiki.com/iHongRen/hpack)  

</div>

## 简介

**[hpack](https://github.com/iHongRen/hpack)** `[h-pack]` 是一个专为鸿蒙 HarmonyOS 打造的内测分发工具，完成配置后，你只需一行命令，就能轻松完成鸿蒙应用的构建、签名，上传、分发、安装。



## 功能特性

- 📦 **打包签名**：自动打出所有的 `hap` 和 `hsp` 包，并对它们进行签名
- 📝 **签名 manifest.json5**：读取应用打包数据，自动生成已签名 `manifest.json5` 文件
- 🌐 **分发 index 页**：自动生成分发页，提供多种 HTML 模板，支持自定义模板
- 📱 **二维码生成**：自动生成应用的二维码，方便内测人员快速下载和安装
- ☁️ **OSS 上传**：支持将打包文件上传到阿里云 OSS，以及自定义上传
- 📱 **显示设备**：显示正在连接的设备 `hpack targets`
- 🆔 **查看UDID**：显示正在连接设备的 UDID `hpack -u`
- ✍️ **签名工具**：支持对未签名的 `.app`、`.hap`、`.hsp` 和包目录签名
- 💾 **命令安装**：支持通过命令安装已签名的 `.app`、`.hap` 和包目录



## 安装使用

### 快速安装

```bash
pip install harmony-hpack
```

<details>
<summary>🔥 国内镜像源安装（推荐）</summary>

```bash
# 清华源
pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple harmony-hpack

# 阿里源
pip install -i https://mirrors.aliyun.com/pypi/simple harmony-hpack

# 腾讯源
pip install -i https://mirrors.cloud.tencent.com/pypi/simple harmony-hpack

# 官方源
pip install -i https://pypi.org/simple harmony-hpack
```

</details>

<details>
<summary>🔨 其他操作</summary>

```bash
# 验证安装
hpack -h

# 升级
pip install --upgrade harmony-hpack

# 卸载
pip uninstall harmony-hpack

# 配置镜像源
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

</details>

### 准备工作

> 💡 **重要提示**：在开始之前，建议先阅读鸿蒙官方文档 [HarmonyOS 应用内部测试](https://developer.huawei.com/consumer/cn/doc/app/agc-help-harmonyos-internaltest-0000001937800101#section042515172197)

你需要准备以下三个证书文件：

| 文件类型 | 格式 | 说明 |
|---------|------|------|
| 发布证书 | `.cer` | 由AGC颁发的数字证书，用于验证应用的身份和签名            |
| 内部测试 Profile | `.p7b` | 包含了包名、数字证书信息、申请的权限列表、设备列表等信息 |
| 公私钥文件 | `.p12` | 包含非对称加密中使用的公钥和私钥 |

**官方内部测试流程：**

<div align="center">
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/3.jpeg" alt="HarmonyOS 内部测试流程" style="max-width: 100%; height: auto;">
</div> 



### 环境要求

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| **hvigorw**、**hdc** (可选) | 最新版 | DevEco Studio 自带集成，可单独安装 |
| **JDK** | 17+ | 签名工具依赖 |
| **Python** | 3.10+ | hpack 运行环境 |

**环境检查命令：**

```bash
# 检查各工具是否正确安装
java --version          # 检查 JDK 版本
python --version       # 检查 Python 版本
hvigorw -v              # 检查 hvigorw（需配置环境变量）
hdc -v                  # 检查 hdc（需配置环境变量）
```

> ⚠️ **注意**：`hvigorw` 和 `hdc` 是 DevEco-Studio 自带工具，在其他终端工具下使用，需要设置环境变量，详见下方 Tips 部分。



## 快速开始

### 1、初始化项目

在**项目根目录**下执行初始化命令：

```bash
hpack init
```

初始化完成后，会生成 `hpack` 目录结构：

```
hpack/
├── config.py      # 配置文件：服务器、应用信息和打包签名等
├── Packfile.py    # 回调文件：打包完成后的自定义处理逻辑
└── sign/          # 证书目录：存放签名证书文件
```

### 2、修改配置

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



**替换证书文件**

将你的证书文件放入 `hpack/sign/` 目录：

```
sign/
├── harmony.p12        # 公私钥文件
├── release.cer        # 发布证书  
└── test_release.p7b   # 内部测试Profile
```



### 3、开始打包

执行打包命令，可选择性地添加更新说明：

```bash
# 完整命令
hpack pack "修复了一些已知问题，优化了性能"

# 简写形式
hpack p "更新说明"
```

✅ **打包完成后**，所有文件将保存在 `hpack/build/{product}/` 目录下。  



### 4、配置上传（可选）

<details>
<summary>☁️ 阿里云 OSS 上传配置</summary>

**安装依赖：**
```bash
pip3 install oss2
```

**配置 OSS：**
打开 `Packfile.py` 完成配置：

```python
class OSSConfig: 
    # OSS 配置信息
    Access_key_id = 'your_access_key_id'
    Access_key_secret = 'your_access_key_secret'
    Endpoint = 'your_endpoint'
    Bucket_name = 'your_bucket_name'
    Bucket_dir = 'hpack'
```

</details>

<details>
<summary>⚒️ 自定义服务器上传</summary>

如果使用其他服务器，需要在`didPack`中编写上传代码：

```python
def didPack(packInfo):
    """打包后回调，通常在这里上传打包结果到服务器"""
    # 打包结果在 hpack/build/{product}，编写你的上传逻辑
    pass
```

</details>



## 运行示例

### 🚀 开始打包
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/0.png" alt="开始打包" style="max-width: 100%; height: auto;">

### 🎯 选择 Product
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/2.png" alt="选择Product" style="max-width: 100%; height: auto;">

### ✅ 打包完成
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/1.png" alt="打包完成" style="max-width: 100%; height: auto;">


### 📱 扫码安装
<img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/install.png" alt="扫码安装" width="300" style="max-width: 100%; height: auto;">


## 命令参考

<details>
<summary>📖 查看帮助</summary>

```bash
hpack -h  # 或 hpack help
```

**命令分类：**

### 查看命令
| 命令 | 说明 |
|------|------|
| `hpack -v, --version` | 显示版本信息 |
| `hpack -h, --help` | 显示帮助信息 |
| `hpack -u, --udid` | 显示设备的 UDID |
| `hpack targets` | 显示连接的设备列表 |

### 执行命令
| 命令 | 说明 |
|------|------|
| `hpack init` | 初始化 hpack 目录并创建配置文件 |
| `hpack pack, p [desc]` | 执行打包签名和上传，desc 为打包描述（可选） |
| `hpack template, t [tname]` | 生成 index.html 模板文件 |

</details>

<details>
<summary>📱 安装命令</summary>

### 安装打包产物
```bash
# 安装指定 product 的产物
hpack i -myproduct  # 注意加上横杠(-)
```

### 安装已签名包
```bash
# 安装 .app 文件
hpack i ./xx.app

# 安装 .hap 文件  
hpack i ./xx.hap

# 安装目录下所有包
hpack i ./build/default
```

</details>

<details>
<summary>✍️ 签名命令</summary>

### 基本语法
```bash
hpack sign,s <unsignedPath> <certPath>
```

### 使用示例
```bash
# 签名 .app 文件
hpack s ./xx.app ./sign/cert.py

# 签名 .hap 文件
hpack s ./xx.hap ./sign/cert.py

# 签名目录
hpack s ./build/default ./sign/cert.py
```

### 证书目录结构
```
sign/
├── cert.py          # 签名配置文件
├── certFile.cer     # 证书文件
├── keystore.p12     # 公私钥文件
└── profile.p7b      # Profile 文件
```

### cert.py 配置示例
```python
# -*- coding: utf-8 -*-
Alias = 'key alias' 
KeyPwd = 'key password' 
KeystorePwd = 'store password' 
Cert = './certFile.cer'      # 相对于cert.py的路径
Profile = './profile.p7b'    # 相对于cert.py的路径
Keystore = './keystore.p12'  # 相对于cert.py的路径
```

</details>

<br>

## 模板预览

hpack 提供多种内置分发页模板，满足不同风格的需求：

```python
# config.py 中配置模板
IndexTemplate = "default"  # 可选值：[default, simple, tech, cartoon, tradition, custom]
```

| <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/default.png" width="300"> | <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/simple.png" width="300"> | <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/tech.png" width="300"> |
| :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
|                       default 默认风格                       |                         simple 简单                          |                          tech 科技                           |

| <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/cartoon.png" width="300"> | <img src="https://raw.githubusercontent.com/iHongRen/hpack/main/screenshots/tradition.png" width="300"> |
| :----------------------------------------------------------: | :----------------------------------------------------------: |
|                         cartoon 卡通                         |                        tradition 传统                        |



## 自定义分发页

#### 1、启用自定义模板
修改 `config.py` 文件：
```python
IndexTemplate = 'custom'  # 启用自定义模板
```

#### 2、生成模板文件
使用内置模板作为基础：
```bash
# 生成指定模板
hpack template [tname]  # 简写：hpack t tech

# 可选模板：default, simple, tech, cartoon, tradition
# 不指定则默认使用 default 模板
```

> 💡 **提示**：命令会在 `hpack/` 目录下生成对应的 `index.html` 模板文件

#### 3、配置模板处理
在 `Packfile.py` 中启用自定义模板处理：

```python
def customTemplateHtml(templateInfo):
    packInfo = templateInfo["packInfo"]
    html = templateInfo["html"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 填充模板变量
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
    print(html_template)  # ⚠️ 不可删除，用于传参

# 调用处理函数
if __name__ == "__main__":    
    # ...省略的代码
    elif args.t:
        templateInfo = json.loads(sys.stdin.read())  
        customTemplateHtml(templateInfo) 
```

#### 4、执行打包
```bash
hpack p '自定义index.html'
```



## 📊 打包信息说明

打包完成后，`PackFile.py` 中的 `didPack` 方法会接收到详细的打包信息：

```python
def didPack(packInfo):
    """打包完成回调，通常在这里上传打包结果到服务器"""
    print(json.dumps(packInfo, indent=4, ensure_ascii=False))
```

### 信息字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `bundle_name` | String | 应用包名 |
| `version_code` | Number | 版本号 |
| `version_name` | String | 版本名称 |
| `size` | String | 包大小 |
| `desc` | String | 打包说明 |
| `build_dir` | String | 本地构建目录 |
| `remote_dir` | String | 远程目录名（时间戳） |
| `manifest_url` | String | manifest.json5 文件 URL |
| `qrcode` | String | 二维码 base64 数据 |
| `index_url` | String | 分发页面 URL |
| `product` | String | 选择的 product |
| `willPack_output` | String | 打包前传入的参数 |

### 示例输出
```json
{
    "bundle_name": "com.cxy.hpack",
    "version_code": 1000000,
    "version_name": "1.0.0",
    "size": "281KB",
    "desc": "打包说明",
    "build_dir": "hpack/build/default",
    "remote_dir": "20250605200049",
    "manifest_url": "https://服务器域名/hpack/20250605200049/manifest.json5",
    "qrcode": "data:image/svg+xml;charset=utf-8,xxx...",
    "index_url": "https://服务器域名/hpack/20250605200049/index.html",
    "product": "default",
    "willPack_output": "willPack中打包前传入的参数"
}
```



## 💡 Tips

<details>
<summary>🔧 环境配置</summary>

### 配置环境变量
在**非 DevEco-Studio** 终端中使用时需要配置：

```bash
# macOS
# .zshrc 文件
export DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk

# 验证配置
hvigorw -v


# Windows
# 参考官方文档：https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-hvigor-commandline
```

### Git 忽略配置
在 `.gitignore` 文件中添加：
```gitignore
# 忽略 Python 临时文件
__pycache__/
```

</details>

<details>
<summary>⚠️ 常见问题</summary>

### 证书相关
- **证书不一致**：如果已安装的 App 和准备安装的 App 打包证书不一致，需先卸载已安装的 App
- **Profile 类型**：
  - 使用**调试.p7b**：只能本地命令安装
  - 使用**内部测试 Profile.p7b**：才能通过 **DeepLink** (链接) 形式安装

### 网络相关
- **联网校验**：安装时鸿蒙会进行联网校验，如果验证失败，尝试关闭代理
- **错误码**：安装出错时会有提示，可根据 [错误码说明](https://developer.huawei.com/consumer/cn/doc/app/agc-help-internal-test-errorcode-0000002295325157) 查找原因

</details>



## 支持项目

如果 hpack 对你有帮助，请考虑：
- ⭐ 给项目点个 Star
- 🔄 分享给更多开发者
- 💬 在社区中推荐使用

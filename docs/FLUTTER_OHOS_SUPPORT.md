# Flutter 鸿蒙项目支持

hpack 工具现已支持 Flutter 鸿蒙项目的打包、签名和分发。

## 功能特点

✅ **自动检测**: 自动识别 Flutter 鸿蒙项目  
✅ **完整流程**: 支持 Flutter 构建 + 鸿蒙签名的完整流程  
✅ **环境检查**: 自动检查 Flutter 和鸿蒙开发环境  
✅ **混合模式**: 支持 Flutter + 鸿蒙原生混合项目  
✅ **错误处理**: 完整的错误处理和 `--fail` 回调支持  

## 项目结构要求

Flutter 鸿蒙项目需要包含以下结构：

```
your_flutter_ohos_project/
├── pubspec.yaml          # Flutter 项目配置
├── lib/                  # Flutter 代码目录
├── ohos/                 # 鸿蒙平台目录
│   ├── build-profile.json5
│   ├── AppScope/
│   │   └── app.json5
│   └── hvigorfile.ts
└── build/                # 构建输出目录
    └── ohos/
```

## 环境要求

### 必需工具

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| Flutter SDK | 3.16.0+ | 支持鸿蒙平台的 Flutter 版本 |
| Dart SDK | 3.2.0+ | Flutter 自带 |
| DevEco Studio | 最新版 | 鸿蒙开发工具 |
| hvigorw | 最新版 | 鸿蒙构建工具 |
| hdc | 最新版 | 鸿蒙调试工具 |
| JDK | 17+ | 签名工具依赖 |
| Python | 3.10+ | hpack 运行环境 |

### 环境检查命令

```bash
flutter --version       # 检查 Flutter 版本
flutter doctor          # 检查 Flutter 环境
hvigorw -v             # 检查鸿蒙构建工具
hdc -v                 # 检查鸿蒙调试工具
java --version         # 检查 JDK 版本
python --version       # 检查 Python 版本
```

## 快速开始

### 1. 初始化 hpack

在 Flutter 鸿蒙项目根目录执行：

```bash
hpack init
```

### 2. 配置 hpack

将 `flutter_ohos_config_example.py` 重命名为 `config.py` 并放置在 `hpack/` 目录下：

```bash
cp flutter_ohos_config_example.py hpack/config.py
```

编辑 `hpack/config.py`，修改以下必填项：

```python
class Config:
    # 服务器配置
    DeployDomain = 'your-domain.com'  # 你的域名
    BaseURL = f"https://{DeployDomain}/flutter-apps"
    
    # 应用信息
    AppIcon = f"{BaseURL}/app_icon.png"  # 应用图标URL
    AppName = '你的Flutter应用'
    
    # 签名配置
    Alias = 'your_key_alias'
    KeyPwd = 'your_key_password'
    KeystorePwd = 'your_store_password'
```

### 3. 配置签名证书

将你的签名证书文件放置在 `hpack/sign/` 目录下：

```
hpack/sign/
├── flutter_release.cer      # 证书文件
├── flutter_profile.p7b      # 配置文件
└── flutter_harmony.p12      # 密钥库文件
```

### 4. 执行打包

```bash
hpack pack "Flutter鸿蒙版本 v1.0.0"
```

## 构建流程

hpack 对 Flutter 鸿蒙项目的构建流程：

1. **项目检测**: 自动检测是否为 Flutter 鸿蒙项目
2. **环境检查**: 验证 Flutter 和鸿蒙开发环境
3. **Flutter 清理**: 执行 `flutter clean`（可配置）
4. **依赖获取**: 执行 `flutter pub get`（可配置）
5. **Flutter 构建**: 执行 `flutter build ohos`
6. **鸿蒙构建**: 如果有原生部分，执行 `hvigorw` 构建
7. **文件签名**: 对生成的 .hap/.hsp 文件进行签名
8. **信息生成**: 生成应用信息和分发页面
9. **回调执行**: 执行 `--did` 成功回调

## 配置选项

### Flutter 特殊配置

```python
class Config:
    # 构建模式
    Debug = True  # True: debug模式, False: release模式
    
    # 构建前操作
    FlutterCleanBeforeBuild = True    # 是否执行 flutter clean
    FlutterPubGetBeforeBuild = True   # 是否执行 flutter pub get
    
    # 自定义构建参数
    FlutterBuildArgs = [
        '--tree-shake-icons',
        '--dart-define=FLAVOR=production'
    ]
    
    # 混合模式
    FlutterHybridMode = True  # 是否同时构建原生部分
    
    # 环境检查
    CheckFlutterEnvironment = True
    RequiredFlutterVersion = "3.16.0"  # 可选的版本要求
```

### 版本信息获取

hpack 会自动从以下位置获取版本信息：

1. **pubspec.yaml**: Flutter 项目版本
   ```yaml
   version: 1.0.0+1  # versionName+versionCode
   ```

2. **ohos/AppScope/app.json5**: 鸿蒙应用信息
   ```json5
   {
     "app": {
       "bundleName": "com.example.flutter_ohos",
       "versionCode": 1,
       "versionName": "1.0.0"
     }
   }
   ```

## 错误处理

### 常见问题

1. **Flutter 命令不可用**
   ```
   解决方案: 确保 Flutter SDK 已安装并配置环境变量
   ```

2. **hvigorw 命令不可用**
   ```
   解决方案: 确保 DevEco Studio 已安装并配置环境变量
   ```

3. **构建输出文件未找到**
   ```
   解决方案: 检查 Flutter 构建是否成功，查看 build/ohos 目录
   ```

4. **签名失败**
   ```
   解决方案: 检查签名证书配置和文件路径
   ```

### 失败回调

当 Flutter 项目打包失败时，会调用 `--fail` 回调，错误信息包含：

```json
{
    "error": "具体错误信息",
    "error_type": "异常类型",
    "product": "产品名称",
    "desc": "打包描述",
    "timestamp": "时间戳",
    "project_type": "flutter_ohos"
}
```

## 高级用法

### 自定义构建脚本

在 `PackFile.py` 中可以针对 Flutter 项目进行特殊处理：

```python
def willPack():
    """打包前调用"""
    # 检查是否为 Flutter 项目
    if os.path.exists('pubspec.yaml'):
        print("检测到 Flutter 项目，执行预处理...")
        # 执行 Flutter 特定的预处理逻辑
    
    willParams = json.dumps({"project_type": "flutter_ohos"}, ensure_ascii=False)
    sys.stdout.buffer.write(willParams.encode('utf-8'))
    sys.stdout.flush()

def didPack(packInfo):
    """打包成功回调"""
    project_type = packInfo.get('project_type', 'unknown')
    
    if project_type == 'flutter_ohos':
        print("Flutter 鸿蒙项目打包成功！")
        # 执行 Flutter 特定的后处理逻辑
        # 例如：上传到 Flutter 应用商店、发送通知等
    
    # 通用处理逻辑...

def failPack(errorInfo):
    """打包失败回调"""
    project_type = errorInfo.get('project_type', 'unknown')
    
    if project_type == 'flutter_ohos':
        print("Flutter 鸿蒙项目打包失败！")
        # 执行 Flutter 特定的错误处理
        # 例如：发送错误报告、清理临时文件等
    
    # 通用错误处理...
```

### 持续集成

在 CI/CD 环境中使用：

```yaml
# GitHub Actions 示例
name: Flutter OHOS Build
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.16.0'
    
    - name: Setup DevEco Studio
      # 安装鸿蒙开发工具...
    
    - name: Setup hpack
      run: |
        pip install hpack
        hpack init
        # 配置签名证书...
    
    - name: Build Flutter OHOS
      run: hpack pack "CI Build ${{ github.sha }}"
```

## 贡献

欢迎为 Flutter 鸿蒙支持功能贡献代码和建议！

- 提交 Issue: 报告问题或建议新功能
- 提交 PR: 贡献代码改进
- 文档完善: 帮助完善使用文档

## 更新日志

- **v1.1.0**: 新增 Flutter 鸿蒙项目支持
  - 自动检测 Flutter 鸿蒙项目
  - 支持 Flutter 构建流程
  - 完整的环境检查
  - 混合模式支持
  - 错误处理和回调支持
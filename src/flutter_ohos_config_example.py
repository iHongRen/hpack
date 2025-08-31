# -*- coding: utf-8 -*-
# Flutter 鸿蒙项目 hpack 配置示例
# 将此文件重命名为 config.py 并放置在 hpack/ 目录下

import os


class Config: 
    # ==================== 基础配置 ====================
    
    # 安装包存放的服务器的域名 --- 必填项
    DeployDomain = 'your-domain.com'
    
    # 安装包存放的服务器地址，必须是 https --- 必填项
    BaseURL = f"https://{DeployDomain}/flutter-ohos-apps"

    # 应用信息 
    AppIcon = f"{BaseURL}/flutter_app_icon.png"  # --- 必填项
    AppName = 'Flutter鸿蒙应用'
    Badge = 'Flutter版'
    
    # ==================== Flutter 特殊配置 ====================
    
    # Flutter 构建模式
    # True: debug 模式 (flutter build ohos --debug)
    # False: release 模式 (flutter build ohos --release)
    Debug = True
    
    # Flutter 构建目标
    # 可选值: 'ohos' (默认)
    FlutterTarget = 'ohos'
    
    # 是否在构建前执行 flutter clean
    FlutterCleanBeforeBuild = True
    
    # 是否在构建前执行 flutter pub get
    FlutterPubGetBeforeBuild = True
    
    # Flutter 自定义构建参数
    # 例如: ['--tree-shake-icons', '--dart-define=FLAVOR=production']
    FlutterBuildArgs = []
    
    # ==================== 鸿蒙签名配置 ====================
    
    # 打包签名配置 
    Alias = 'your_flutter_key_alias'  # --- 必填项
    KeyPwd = 'your_flutter_key_password'  # --- 必填项
    KeystorePwd = 'your_flutter_store_password'  # --- 必填项
    
    # 证书文件路径 (相对于 hpack/sign 目录)
    SignDir = 'sign'
    Cert = os.path.join(SignDir, 'flutter_release.cer') 
    Profile = os.path.join(SignDir, 'flutter_profile.p7b')  
    Keystore = os.path.join(SignDir, 'flutter_harmony.p12') 
    
    # ==================== 产品配置 ====================
    
    # 设置默认打包 product
    # 对于 Flutter 项目，通常使用 'default'
    Product = "default"
    
    # 如果需要完全自定义构建命令，可以使用此配置
    # 注意：Flutter 项目建议使用 Flutter 相关配置而不是直接使用 hvigorw
    HvigorwCommand = []
    
    # ==================== 模板配置 ====================
    
    # index模板选择
    # 可选值为 [default, simple, tech, cartoon, tradition, custom]
    IndexTemplate = "tech"  # Flutter 项目推荐使用 tech 模板
    
    # ==================== 历史版本配置 ====================
    
    # 历史版本按钮配置
    HistoryBtn = True
    HistoryBtnTitle = "历史版本"
    HistoryBtnUrl = f"{BaseURL}/history.html"
    
    # ==================== Flutter 特定的高级配置 ====================
    
    # 是否启用 Flutter 混合模式
    # True: 同时构建 Flutter 和鸿蒙原生部分
    # False: 仅构建 Flutter 部分
    FlutterHybridMode = True
    
    # Flutter 输出目录自定义
    # 默认会自动检测 build/ohos 和 ohos/build 目录
    FlutterOutputDirs = [
        'build/ohos',
        'ohos/build'
    ]
    
    # 构建后的清理配置
    CleanAfterBuild = False  # 是否在构建后清理临时文件
    
    # ==================== 环境检查配置 ====================
    
    # 是否在构建前检查 Flutter 环境
    CheckFlutterEnvironment = True
    
    # 必需的 Flutter 版本 (可选)
    # 例如: "3.16.0" 或 None 表示不检查版本
    RequiredFlutterVersion = None
    
    # 必需的 Dart 版本 (可选)
    RequiredDartVersion = None


# ==================== Flutter 项目检测配置 ====================

# 用于检测 Flutter 鸿蒙项目的文件和目录
FLUTTER_OHOS_INDICATORS = {
    'required_files': [
        'pubspec.yaml',
        'lib',
        'ohos'
    ],
    'required_ohos_files': [
        'ohos/build-profile.json5',
        'ohos/AppScope',
        'ohos/hvigorfile.ts'
    ],
    'pubspec_keywords': [
        'ohos',
        'harmony',
        'harmonyos'
    ]
}

# ==================== 使用说明 ====================
"""
Flutter 鸿蒙项目使用 hpack 的步骤：

1. 确保你的 Flutter 项目支持鸿蒙平台
2. 在项目根目录执行: hpack init
3. 将此配置文件重命名为 config.py 并放置在 hpack/ 目录下
4. 修改配置文件中的必填项（DeployDomain、AppIcon、签名配置等）
5. 将你的签名证书文件放置在 hpack/sign/ 目录下
6. 执行打包命令: hpack pack "版本描述"

注意事项：
- 确保 Flutter SDK 已安装并配置环境变量
- 确保鸿蒙开发工具已安装并配置环境变量
- 首次构建可能需要较长时间下载依赖
- 建议在构建前先手动执行一次 flutter build ohos 确保环境正常

支持的命令：
- hpack pack: 打包 Flutter 鸿蒙应用
- hpack install: 安装到设备
- hpack sign: 签名已构建的应用
"""
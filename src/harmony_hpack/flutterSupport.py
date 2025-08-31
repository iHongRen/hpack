# -*- coding: utf-8 -*-
# @github : https://github.com/iHongRen/hpack
# Flutter 鸿蒙项目支持模块

import os
import subprocess
import json
from utils import isWin, printError, printSuccess, timeit


def is_flutter_ohos_project():
    """检测是否为 Flutter 鸿蒙项目"""
    # 检查关键文件和目录
    flutter_indicators = [
        'pubspec.yaml',           # Flutter 项目标识
        'ohos',                   # 鸿蒙目录
        'lib',                    # Flutter 代码目录
    ]
    
    ohos_indicators = [
        'ohos/build-profile.json5',
        'ohos/AppScope',
        'ohos/hvigorfile.ts'
    ]
    
    # 检查 Flutter 标识
    flutter_exists = all(os.path.exists(indicator) for indicator in flutter_indicators)
    
    # 检查鸿蒙标识
    ohos_exists = all(os.path.exists(indicator) for indicator in ohos_indicators)
    
    # 检查 pubspec.yaml 中是否包含鸿蒙相关配置
    pubspec_has_ohos = False
    if os.path.exists('pubspec.yaml'):
        try:
            with open('pubspec.yaml', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ohos' in content.lower() or 'harmony' in content.lower():
                    pubspec_has_ohos = True
        except Exception:
            pass
    
    return flutter_exists and ohos_exists and pubspec_has_ohos


def get_flutter_ohos_config():
    """获取 Flutter 鸿蒙项目配置"""
    config = {
        'flutter_version': None,
        'ohos_sdk_version': None,
        'build_mode': 'debug',
        'target_platform': 'ohos'
    }
    
    # 获取 Flutter 版本
    try:
        result = subprocess.run(['flutter', '--version'], 
                              capture_output=True, text=True, check=True)
        config['flutter_version'] = result.stdout.split('\n')[0]
    except Exception:
        pass
    
    # 读取 pubspec.yaml 获取更多信息
    if os.path.exists('pubspec.yaml'):
        try:
            with open('pubspec.yaml', 'r', encoding='utf-8') as f:
                content = f.read()
                # 这里可以解析更多配置信息
        except Exception:
            pass
    
    return config


@timeit()
def flutter_clean():
    """Flutter 清理操作"""
    try:
        subprocess.run(['flutter', 'clean'], check=True, shell=isWin())
        printSuccess("Flutter clean 完成")
    except subprocess.CalledProcessError as e:
        printError(f"Flutter clean 失败: {e}")
        raise Exception(f"Flutter clean 失败: {e}")


@timeit()
def flutter_pub_get():
    """Flutter 依赖获取"""
    try:
        subprocess.run(['flutter', 'pub', 'get'], check=True, shell=isWin())
        printSuccess("Flutter pub get 完成")
    except subprocess.CalledProcessError as e:
        printError(f"Flutter pub get 失败: {e}")
        raise Exception(f"Flutter pub get 失败: {e}")


@timeit()
def flutter_build_ohos(config, product):
    """构建 Flutter 鸿蒙应用"""
    try:
        # 基础构建命令
        command = ['flutter', 'build', 'ohos']
        
        # 添加构建模式
        if hasattr(config, 'Debug') and not config.Debug:
            command.append('--release')
        else:
            command.append('--debug')
        
        # 添加产品配置
        if product and product.get('name'):
            # Flutter 可能需要特定的产品配置参数
            pass
        
        # 执行构建
        subprocess.run(command, check=True, shell=isWin())
        printSuccess("Flutter build ohos 完成")
        return True
        
    except subprocess.CalledProcessError as e:
        printError(f"Flutter build ohos 失败: {e}")
        raise Exception(f"Flutter build ohos 失败: {e}")


def get_flutter_ohos_build_outputs():
    """获取 Flutter 鸿蒙构建输出"""
    build_outputs = []
    
    # Flutter 鸿蒙构建输出通常在 build/ohos/ 目录
    build_dir = 'build/ohos'
    if os.path.exists(build_dir):
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith(('.hap', '.hsp', '.app')):
                    build_outputs.append(os.path.join(root, file))
    
    # 也检查 ohos/build/ 目录
    ohos_build_dir = 'ohos/build'
    if os.path.exists(ohos_build_dir):
        for root, dirs, files in os.walk(ohos_build_dir):
            for file in files:
                if file.endswith(('.hap', '.hsp', '.app')):
                    build_outputs.append(os.path.join(root, file))
    
    return build_outputs


def flutter_ohos_pack_sign(config, product):
    """Flutter 鸿蒙项目打包签名流程"""
    printSuccess("开始 Flutter 鸿蒙项目打包...")
    
    # 1. Flutter 清理
    flutter_clean()
    
    # 2. Flutter 依赖获取
    flutter_pub_get()
    
    # 3. Flutter 构建
    flutter_build_ohos(config, product)
    
    # 4. 检查构建输出
    build_outputs = get_flutter_ohos_build_outputs()
    if not build_outputs:
        raise Exception("Flutter 构建完成但未找到输出文件")
    
    printSuccess(f"找到构建输出文件: {len(build_outputs)} 个")
    for output in build_outputs:
        print(f"  - {output}")
    
    # 5. 如果有鸿蒙原生部分，继续使用 hvigorw 构建
    if os.path.exists('ohos/hvigorfile.ts'):
        printSuccess("检测到鸿蒙原生部分，继续使用 hvigorw 构建...")
        
        # 切换到 ohos 目录执行构建
        original_dir = os.getcwd()
        try:
            os.chdir('ohos')
            
            # 执行 hvigorw 构建
            from packSign import sync, buildHapHsp, mkBuildDir, signHapHsp
            
            sync()
            if not buildHapHsp(config, product):
                raise Exception("鸿蒙原生部分构建失败")
            
            productName = product.get('name') if product else 'default'
            mkBuildDir(productName)
            signHapHsp(config, productName)
            
        finally:
            os.chdir(original_dir)
    
    printSuccess("Flutter 鸿蒙项目打包完成")


def get_flutter_ohos_app_info():
    """获取 Flutter 鸿蒙应用信息"""
    app_info = {
        'bundleName': None,
        'versionCode': None,
        'versionName': None
    }
    
    # 从 pubspec.yaml 获取版本信息
    if os.path.exists('pubspec.yaml'):
        try:
            with open('pubspec.yaml', 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('version:'):
                        version_line = line.split(':', 1)[1].strip()
                        if '+' in version_line:
                            version_name, version_code = version_line.split('+')
                            app_info['versionName'] = version_name.strip()
                            app_info['versionCode'] = int(version_code.strip())
                        else:
                            app_info['versionName'] = version_line
                    elif line.strip().startswith('name:'):
                        app_name = line.split(':', 1)[1].strip()
                        # 可以作为默认的 bundleName
                        if not app_info['bundleName']:
                            app_info['bundleName'] = app_name
        except Exception as e:
            printError(f"读取 pubspec.yaml 失败: {e}")
    
    # 从 ohos/AppScope/app.json5 获取鸿蒙应用信息
    ohos_app_json = 'ohos/AppScope/app.json5'
    if os.path.exists(ohos_app_json):
        try:
            import json5
            with open(ohos_app_json, 'r', encoding='utf-8') as f:
                ohos_app_info = json5.load(f)
                app = ohos_app_info.get('app', {})
                if app.get('bundleName'):
                    app_info['bundleName'] = app.get('bundleName')
                if app.get('versionCode'):
                    app_info['versionCode'] = app.get('versionCode')
                if app.get('versionName'):
                    app_info['versionName'] = app.get('versionName')
        except Exception as e:
            printError(f"读取 ohos/AppScope/app.json5 失败: {e}")
    
    return app_info


def validate_flutter_ohos_environment():
    """验证 Flutter 鸿蒙开发环境"""
    issues = []
    
    # 检查 Flutter 命令
    try:
        subprocess.run(['flutter', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("Flutter 命令不可用，请确保 Flutter SDK 已安装并配置环境变量")
    
    # 检查 hvigorw 命令（如果有鸿蒙原生部分）
    if os.path.exists('ohos/hvigorfile.ts'):
        try:
            subprocess.run(['hvigorw', '-v'], 
                          capture_output=True, check=True, shell=isWin())
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("hvigorw 命令不可用，请确保鸿蒙开发工具已安装并配置环境变量")
    
    return issues
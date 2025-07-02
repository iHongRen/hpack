# -*- coding: utf-8 -*-
#  @github : https://github.com/iHongRen/hpack

import importlib.util
import os
import shutil
import subprocess
import zipfile

from toolConfig import ToolConfig

# 证书配置文件示例 cert.py
# Alias = 'key alias' 
# KeyPwd = 'key password' 
# KeystorePwd = 'store password' 
# Cert ='./cert.cer'  # 相对于证书配置文件的路径
# Profile = './profile.p7b' # 相对于证书配置文件的路径
# Keystore =  './keystore.p12' # 相对于证书配置文件的路径
  

def sign_command(unsignedPath, certPath):
    """签名指定路径的文件或目录"""
    CertConfig = read_cert_config(certPath)
    if not CertConfig:
        return

    certDir = os.path.dirname(certPath)
    Cert = CertConfig.get('Cert')
    if not Cert.startswith(('/', '\\')):
        CertConfig['Cert'] = os.path.join(certDir,Cert)

    Profile = CertConfig.get('Profile')
    if not Profile.startswith(('/', '\\')):
        CertConfig['Profile'] = os.path.join(certDir,Profile)

    Keystore = CertConfig.get('Keystore')
    if not Keystore.startswith(('/', '\\')):
        CertConfig['Keystore'] = os.path.join(certDir,Keystore)

    if os.path.isdir(unsignedPath):
        dirname = os.path.dirname(unsignedPath)
        basename = 'hpack-signed-' + os.path.basename(unsignedPath)
        signed_dir = os.path.join(dirname, basename)
        sign_dir(unsignedPath, signed_dir, CertConfig)
    elif unsignedPath.endswith('.app'):
        sign_app(unsignedPath, CertConfig)
    elif unsignedPath.endswith(('.hap', '.hsp')):
        signed_dir = os.path.dirname(unsignedPath)
        sign_file(unsignedPath, signed_dir, CertConfig)
    else:
        print(f"无效的路径: {unsignedPath}，请提供一个目录或 .app、.hap、.hsp 文件。")



def read_cert_config(certPath):
    try:
        file_name = os.path.basename(certPath)
        name = os.path.splitext(file_name)[0]
        spec = importlib.util.spec_from_file_location(name, os.path.join(certPath))
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        variables = dir(config_module)
        variables = [var for var in variables if not var.startswith('__')]
        
        config = {}
        for var in variables:
            config[var] = getattr(config_module, var)
        
        return config
    except Exception as e:
        print(f"读取 {certPath} 证书文件时出错 - {e}")



def sign_app(app_path, CertConfig):
    """解压 app 文件夹"""
    with zipfile.ZipFile(app_path, 'r') as zip_ref:
        file_name = os.path.basename(app_path)
        dir_name = os.path.splitext(file_name)[0]
        unzip_dir_name = 'hpack-unzip-' + dir_name
        unzip_dir = os.path.join(os.path.dirname(app_path), unzip_dir_name)
        zip_ref.extractall(unzip_dir)

         # 删除 __MACOSX 文件夹（如果存在）
        macosx_dir = os.path.join(unzip_dir, '__MACOSX')
        if os.path.exists(macosx_dir):
            shutil.rmtree(macosx_dir)

        signed_dir_name = 'hpack-signed-' + dir_name
        signed_dir = os.path.join(os.path.dirname(app_path), signed_dir_name)
        ret = sign_dir(unzip_dir, signed_dir, CertConfig)
        shutil.rmtree(unzip_dir)
        if ret is True:
            zip_app(signed_dir)
        shutil.rmtree(signed_dir)



def zip_app(signed_app_dir):
    """压缩 app 文件夹"""
    file_name = os.path.basename(signed_app_dir)
    zip_file_path = os.path.join(signed_app_dir + '.app')
    
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
         with os.scandir(signed_app_dir) as entries:
            for entry in entries:
                file_path = entry.path
                arcname = os.path.relpath(file_path, signed_app_dir)
                zipf.write(file_path, arcname)

    print(f"签名完成: {zip_file_path}")



def sign_dir(unsign_dir, signed_dir, CertConfig):
    """签名文件夹"""
    result = []
    with os.scandir(unsign_dir) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(('.hap', '.hsp')):
                result.append(entry.path)

    for file in result:
       ret = sign_file(file, signed_dir, CertConfig)
       if ret is None:
           return False
           
    return True


def sign_file(unsigned_file_path, signed_dir, CertConfig):
    """签名单个文件"""
    file_name = os.path.basename(unsigned_file_path)
    signed_file_path = os.path.join(signed_dir, 'hpack-signed-' + file_name)
    if signed_dir:
        os.makedirs(signed_dir, exist_ok=True)
    command = [
        'java', '-jar', ToolConfig.HapSignTool,
        'sign-app',
        '-keyAlias', CertConfig.get('Alias'),
        '-signAlg', 'SHA256withECDSA',
        '-mode', 'localSign',
        '-appCertFile', CertConfig.get('Cert'),
        '-profileFile', CertConfig.get('Profile'),
        '-inFile', unsigned_file_path,
        '-keystoreFile', CertConfig.get('Keystore'),
        '-outFile', signed_file_path,
        '-keyPwd', CertConfig.get('KeyPwd'),
        '-keystorePwd', CertConfig.get('KeystorePwd'),
        '-signCode', '1'
    ]
    try:
        subprocess.run(command, check=True)
        return signed_file_path
    except subprocess.CalledProcessError as e:
        print(f"签名 {unsigned_file_path} 出错: {e}")
        return None



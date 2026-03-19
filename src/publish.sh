#!/bin/bash
set -e  # 任何命令执行失败立即退出脚本

# ===================== 配置项（可根据需要修改） =====================
# 包名前缀（需和 setup.py 中的 name 一致）
PACKAGE_NAME="harmony_hpack"
# Python 命令（根据环境调整为 python/python3）
PYTHON_CMD="python3"
PIP_CMD="pip3"
# PyPI 仓库名称（默认 pypi，如需测试仓库可改为 testpypi）
REPOSITORY="pypi"

# ===================== 核心函数 =====================
# 1. 清理旧打包文件
clean_old_build() {
    echo -e "\033[36m[1/6] 清理旧的打包文件...\033[0m"
    rm -rf build dist *.egg-info
}

# 2. 执行打包
build_package() {
    echo -e "\033[36m[2/6] 执行打包（sdist + bdist_wheel）...\033[0m"
    $PYTHON_CMD setup.py sdist bdist_wheel
    
    # 检查打包是否成功
    if [ ! -d "dist" ] || [ -z "$(ls dist/)" ]; then
        echo -e "\033[31m[错误] 打包失败，dist 目录为空！\033[0m"
        exit 1
    fi
}

# 3. 动态提取版本号（从 dist 目录的 tar.gz 文件中解析）
get_package_version() {
    echo -e "\033[36m[3/6] 提取包版本号...\033[0m"
    # 匹配 dist 目录下的 tar.gz 包文件，提取版本号
    TAR_FILE=$(ls dist/${PACKAGE_NAME}-*.tar.gz 2>/dev/null | head -n1)
    if [ -z "$TAR_FILE" ]; then
        echo -e "\033[31m[错误] 未找到 ${PACKAGE_NAME} 的 tar.gz 包！\033[0m"
        exit 1
    fi
    
    # 正则提取版本号（格式：包名-版本号.tar.gz）
    PACKAGE_VERSION=$(echo $TAR_FILE | sed -E "s/.*${PACKAGE_NAME}-(.*)\.tar\.gz/\1/")
    echo -e "✅ 提取到版本号：${PACKAGE_VERSION}"
    echo -e "✅ 包文件路径：${TAR_FILE}"
}

# 4. 本地安装验证包
install_package_locally() {
    echo -e "\033[36m[4/6] 本地安装包验证...\033[0m"
    $PIP_CMD install --force-reinstall $TAR_FILE
    echo -e "✅ 本地安装验证完成"
}

# 5. twine 检查包完整性
check_package() {
    echo -e "\033[36m[5/6] 使用 twine 检查包完整性...\033[0m"
    twine check dist/*
    echo -e "✅ twine 检查通过"
}

# 6. 上传到 PyPI
upload_package() {
    echo -e "\033[36m[6/6] 上传包到 ${REPOSITORY}...\033[0m"
    read -p "⚠️ 确认上传 ${PACKAGE_NAME}-${PACKAGE_VERSION} 到 ${REPOSITORY}？(y/n) " -n 1 -r
    echo -e "\n"
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        twine upload --verbose --repository ${REPOSITORY} dist/*
        echo -e "\033[32m🎉 包 ${PACKAGE_NAME}-${PACKAGE_VERSION} 上传成功！\033[0m"
    else
        echo -e "\033[33m[取消] 上传操作已取消\033[0m"
        exit 0
    fi
}

# ===================== 主流程 =====================
main() {
    echo -e "\033[34m===== 开始打包发布 ${PACKAGE_NAME} =====\033[0m"
    
    clean_old_build
    build_package
    get_package_version
    # install_package_locally
    check_package
    upload_package
    
    echo -e "\033[32m===== 发布流程全部完成 =====\033[0m"
}

# 执行主流程
main
# --fail 功能说明

## 概述

新增了 `--fail` 功能，用于处理打包过程中的所有失败情况。当打包失败时，系统会自动调用 `--fail` 回调函数并立即终止打包流程。

## 功能特点

1. **自动触发**: 当打包过程中任何步骤失败时，自动调用 `--fail` 功能
2. **立即终止**: 调用 `--fail` 后立即终止打包流程，不会继续执行后续步骤
3. **详细错误信息**: 提供详细的错误信息，包括错误类型、产品名称、时间戳等

## 错误信息格式

`--fail` 接收的错误信息为 JSON 格式，包含以下字段：

```json
{
    "error": "具体错误信息",
    "error_type": "错误类型",
    "product": "产品名称",
    "desc": "打包描述",
    "timestamp": "错误发生时间戳"
}
```

## 触发场景

`--fail` 功能会在以下情况下被触发：

1. **清理操作失败**: `hvigorw clean` 命令执行失败
2. **同步操作失败**: `hvigorw --sync` 命令执行失败
3. **构建失败**: `hvigorw assembleHap assembleHsp` 命令执行失败
4. **签名失败**: Hap/Hsp 文件签名过程失败
5. **应用信息读取失败**: 无法读取 `AppScope/app.json5` 文件
6. **版本信息获取失败**: 无法获取 `bundleName`、`versionCode` 或 `versionName`
7. **API版本获取失败**: 无法获取 `compatibleSdkVersion`
8. **Manifest创建失败**: 创建或签名 `manifest.json5` 文件失败
9. **模板处理失败**: HTML 模板处理过程失败

## 自定义处理

你可以在 `PackFile.py` 文件中的 `failPack` 函数中自定义失败处理逻辑：

```python
def failPack(errorInfo):
    """_summary_: 打包失败回调，处理打包失败后的错误信息
    """
    print("============打包失败信息:============")
    print(json.dumps(errorInfo, indent=4, ensure_ascii=False))
    print("================================")
    print("打包失败，请检查错误信息并修复问题后重试")
    
    # 在这里添加你的自定义处理逻辑
    # 例如：发送通知、记录日志、上传错误信息等
```

## 使用示例

### 手动测试 --fail 功能

```bash
# 创建测试错误信息
echo '{
    "error": "测试错误",
    "error_type": "TestError",
    "product": "test_product",
    "desc": "测试描述",
    "timestamp": "2024-01-01T12:00:00"
}' | python3 harmony_hpack/PackFile.py --fail
```

### 在打包过程中自动触发

当执行 `hpack pack` 命令时，如果任何步骤失败，系统会自动调用 `--fail` 功能。

## 与现有功能的关系

- `--will`: 打包前调用
- `--did`: 打包成功后调用  
- `--fail`: 打包失败时调用（新增）

这三个回调函数覆盖了打包流程的所有关键节点，确保你可以在任何情况下都能得到相应的通知和处理。
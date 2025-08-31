# 版本更新：

[v1.1.0](https://github.com/iHongRen/hpack/releases/tag/v1.1.0)  — 2025.08.31

1、新增了 `--fail` 功能，用于处理打包过程中的失败情况。

如果是从老版本版本升级，需要自己添加 `--fail`处理代码。

```python
# PackFile.py
def failPack(errorInfo):
    """_summary_: 打包失败回调，处理打包失败后的错误信息
    """
    print("============打包失败信息:============")
    print(json.dumps(errorInfo, indent=4, ensure_ascii=False))
    print("================================")
    print("打包失败，请检查错误信息并修复问题后重试")


if __name__ == "__main__":
    """_summary_: 无需修改"""
		#...
    parser.add_argument('--fail', action='store_true', help="Execute failPack")
		#...
    elif args.fail:
        errorInfo = json.loads(sys.stdin.read())
        failPack(errorInfo)
   
```






[v1.0.9](https://github.com/iHongRen/hpack/releases/tag/v1.0.9)  — 2025.07.31

1. 新增支持历史版本

2. 新增支持 webhook

   

[v1.0.8](https://github.com/iHongRen/hpack/releases/tag/v1.0.8)  — 2025.07.16  

1. 新增对集成态 hsp 包的支持

2. 非 url 编码路径问题修复  

  

[v1.0.7](https://github.com/iHongRen/hpack/releases/tag/v1.0.7)  — 2025.07.02  

1. 兼容 Windows

   ```python
   # 修改 PackFile.py 中 willPack 和 customTemplateHtml 方法传参方式。
   # 将 print 改为下面：
   sys.stdout.buffer.write(willParams.encode('utf-8'))
   sys.stdout.flush()
   ```




[v1.0.6](https://github.com/iHongRen/hpack/releases/tag/v1.0.6)  — 2025.06.12  

1. 新增对.app、.hap、.hsp文件和包目录进行签名

  示例1：hpack s ./xx.app ./sign/cert.py

  示例2：hpack s ./xx.hap ./sign/cert.py

  示例3：hpack s ./build/default ./sign/cert.py



[v1.0.5](https://github.com/iHongRen/hpack/releases/tag/v1.0.5)  — 2025.06.06  

1. 修改 version_code、version_name 优先从选择的 product 配置里获取  

2. 修改命令 hpack install [product] 改为 `hpack install [-product]`，多加了个横杠 -   

3. 新增命令支持安装已签名的 app 或者 hap 包 `hpack install xx.app / xx.hap` 

4. 新增命令支持指定目录安装 `hpack install 安装包所在目录` 

   

[v1.0.4](https://github.com/iHongRen/hpack/releases/tag/v1.0.4)  — 2025.05.09  

- 单引号问题



[v1.0.3](https://github.com/iHongRen/hpack/releases/tag/v1.0.3)  — 2025.05.09  

-  调整源码目录名为 hpack -> harmony_hpack，以防与其他库冲突



[v1.0.2](https://github.com/iHongRen/hpack/releases/tag/v1.0.2)  -- 2025.05.07

1. 新增封装 hdc 命令，简化使用。先确保自己的终端能使用 `hdc -v`
2. 新增查看连接设备 `hpack targets`
3. 新增查看 UDID `hpack -u`
4. 新增直接安装构建包 `hpack install [product]` 



[v1.0.1](https://github.com/iHongRen/hpack/releases/tag/v1.0.1)  -- 2025.04.28

1. 新增对多 product 的支持
2. 新增配置参数 Product、 Debug 、HvigorwCommand
3. 打包后目录结构调整为 `hpack/build/{product}`，升级到此版本后，原 `hpack/build` 目录下残留的打包文件可自行删除。
4. `hpack init` 不再支持缩写 `hpack i` , `hpack i`留作它用



[v1.0.0](https://github.com/iHongRen/hpack/releases/tag/v1.0.0)  -- 2025.04.24

* 全新的命令形式：hpack pack [更新说明]  



[v0.0.1](https://github.com/iHongRen/hpack/tree/0.0.1)  -- 2025.04.10

*  python3 ./pack/main.py [更新说明]
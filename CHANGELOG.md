# 版本更新：


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
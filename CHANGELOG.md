# 版本更新：



[v1.0.3](https://github.com/iHongRen/hpack/releases/tag/v1.0.3)  — 2025.05.09  
1、调整源码目录名为 hpack -> harmony_hpack，以防与其他库冲突


[v1.0.2](https://github.com/iHongRen/hpack/releases/tag/v1.0.2)  -- 2025.05.07

封装 hdc 命令，简化使用。先确保自己的终端能使用 `hdc -v`

1. 新增查看连接设备 `hpack targets`
2. 新增查看 UDID `hpack -u`
3. 新增直接安装构建包 `hpack install [product]` 

[v1.0.1](https://github.com/iHongRen/hpack/releases/tag/v1.0.1)  -- 2025.04.28

1. 新增对多 product 的支持
2. 新增配置参数 Product、 Debug 、HvigorwCommand
3. 打包后目录结构调整为 `hpack/build/{product}`，升级到此版本后，原 `hpack/build` 目录下残留的打包文件可自行删除。
4. `hpack init` 不再支持缩写 `hpack i` , `hpack i`留作它用

[v1.0.0](https://github.com/iHongRen/hpack/releases/tag/v1.0.0)  -- 2025.04.24
* 全新的命令形式：hpack pack [更新说明]  


[v0.0.1](https://github.com/iHongRen/hpack/tree/0.0.1)  -- 2025.04.10

*  python3 ./pack/main.py [更新说明]
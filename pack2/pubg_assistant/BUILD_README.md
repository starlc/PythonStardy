# PUBG Assistant 打包说明

本文档介绍如何将PUBG Assistant打包为可执行文件。

## 打包步骤

1. 确保所有依赖项已安装：

```
pip install -r requirements.txt
```

2. 运行打包脚本：

```
python build.py
```

3. 打包完成后，可执行文件将位于`dist`目录中。

## 注意事项

- 打包脚本会自动检查并创建必要的资源目录和文件。
- 打包过程中可能需要管理员权限来创建`D:\pubg`目录（配置文件保存位置）。
- 如果您遇到`RuntimeError: Calling Tcl from different apartment`错误，表示Tkinter在多线程环境中出现问题，请使用最新版本的UI管理器代码。

## 运行打包后的程序

1. 从`dist`目录中找到`PUBG_Assistant.exe`文件。
2. 双击运行该文件。
3. 程序会在`D:\pubg`目录中保存配置文件。

## 常见问题

### 1. 打包后程序无法启动

- 检查是否有杀毒软件拦截程序运行
- 尝试在命令行中运行程序以查看错误信息
- 确保所需的配置目录（`D:\pubg`）存在且可写入

### 2. UI界面显示异常

- 检查屏幕分辨率设置，程序默认支持2560x1440和2313x1440分辨率
- 修改`resolution_config.py`中的UI位置配置

### 3. 找不到资源文件

- 确保打包时包含了所有资源目录
- 检查`resources`目录中是否存在必要的文件 
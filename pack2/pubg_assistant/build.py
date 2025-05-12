#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PUBG Assistant 打包脚本
"""

import os
import sys
import shutil
import subprocess

def check_dependencies():
    """检查并安装依赖项"""
    required_packages = [
        "pyinstaller",
        "tkinter",
        "pynput",
        "PIL",
        "numpy",
        "cv2",
        "mss",
        "pyttsx3"
    ]
    
    print("检查依赖项...")
    missing_packages = []
    package_mapping = {
        "PIL": "pillow",
        "cv2": "opencv-python",
        "pyinstaller": "pyinstaller",
    }
    
    for package in required_packages:
        try:
            if package == "tkinter":
                import tkinter
            elif package == "pyinstaller":
                # 特殊处理 pyinstaller，因为它是命令行工具
                try:
                    # 尝试执行 pyinstaller 命令检查是否安装
                    import subprocess
                    result = subprocess.run(["pyinstaller", "--version"], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE,
                                           text=True,
                                           shell=True)
                    if result.returncode == 0:
                        print(f"√ {package} 已安装 (版本: {result.stdout.strip()})")
                        continue
                    else:
                        raise ImportError("PyInstaller 命令不可用")
                except Exception:
                    # 尝试通过模块导入检查
                    try:
                        import PyInstaller
                        print(f"√ {package} 已安装")
                        continue
                    except ImportError:
                        raise ImportError("PyInstaller 模块不可用")
            else:
                __import__(package)
            print(f"√ {package} 已安装")
        except ImportError as e:
            print(f"× {package} 未安装: {str(e)}")
            pkg_name = package_mapping.get(package, package)
            missing_packages.append(pkg_name)
    
    if missing_packages:
        print("\n需要安装以下依赖包:")
        for package in missing_packages:
            if package != "tkinter":
                print(f"- {package}")
        
        answer = input("\n是否自动安装这些依赖包？(y/n): ")
        if answer.lower() == 'y':
            print("\n开始安装依赖包...")
            for package in missing_packages:
                if package != "tkinter":
                    print(f"安装 {package}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("所有依赖包安装完成")
        else:
            print("\n请手动安装依赖包后再运行此脚本")
            if "tkinter" in missing_packages:
                print("注意: tkinter需要通过操作系统包管理器安装，例如:")
                print("  Ubuntu/Debian: sudo apt-get install python3-tk")
                print("  CentOS/RHEL: sudo yum install python3-tkinter")
                print("  Windows: 通常包含在Python安装中，如果缺失，请重新安装Python并勾选tcl/tk选项")
            return False
    
    print("所有依赖项已满足")
    return True

def main():
    """打包主程序"""
    # 检查依赖项
    if not check_dependencies():
        return 1
    
    # 调试模式开关，控制是否显示控制台窗口
    debug_mode = False  # 设置为True可以在运行时看到控制台输出，便于调试错误
    
    # 打包命令参数说明
    # -F: 创建单个可执行文件
    # -w: 不显示控制台窗口
    # -n: 指定输出文件名
    # -i: 指定图标文件
    # --add-data: 添加资源文件，格式为 源路径;目标路径
    
    # 检查图标文件是否存在
    icon_file = "icon/2313.ico"
    if not os.path.exists(icon_file):
        print(f"错误: 图标文件 {icon_file} 不存在")
        return 1
    
    # 检查主程序文件是否存在
    main_file = "pubg_assistant/main.py"
    if not os.path.exists(main_file):
        print(f"错误: 主程序文件 {main_file} 不存在")
        return 1
    
    # 检查entry.py是否存在，不存在则创建
    entry_script = "entry.py"
    if not os.path.exists(entry_script):
        with open(entry_script, "w") as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# 添加当前目录到sys.path以便找到模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 调试输出，帮助诊断模块导入问题
print("Python路径:", sys.path)
print("当前目录:", current_dir)

try:
    # 直接使用相对路径导入main函数
    print("尝试导入main函数...")
    from pubg_assistant.main import main
    print("成功导入main函数")
    
    if __name__ == "__main__":
        print("开始执行main函数")
        main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("尝试列出可用模块...")
    try:
        import pkgutil
        print("根目录下的模块:")
        for module in pkgutil.iter_modules():
            print(f"- {module.name}")
        
        # 尝试导入pubg_assistant包
        print("\\n尝试导入pubg_assistant包...")
        import pubg_assistant
        print("pubg_assistant包内容:", dir(pubg_assistant))
    except Exception as e2:
        print(f"诊断过程中出现错误: {e2}")
""")
        print(f"已创建入口脚本 {entry_script}")
    
    # 定义可能存在的资源目录
    resource_dirs = [
        'resources/25601440',  # 枪械图像目录
        'resources/23131440',  # 枪械图像目录
        'resources/dict',      # 枪械配置文件目录
        'resources/temp2313',  # 临时图片目录
        'resources/posturetemp'  # 姿势检测临时图片目录
    ]
    
    # 检查资源目录是否存在，输出状态
    print("\n检查资源目录:")
    for res_dir in resource_dirs:
        if os.path.exists(res_dir):
            print(f"√ {res_dir} 目录已存在")
        else:
            print(f"× {res_dir} 目录不存在，将不会被打包")
    
    # 构建资源文件参数（只包含存在的目录）
    resource_params = ""
    for res_dir in resource_dirs:
        if os.path.exists(res_dir):
            # 目标路径应该保持相同的目录结构
            target_dir = res_dir
            # 在Windows上，PyInstaller使用分号分隔源路径和目标路径
            resource_params += f" --add-data={res_dir};{target_dir}"
    
    # 检查资源参数是否为空
    if not resource_params:
        print("\n警告: 未发现任何资源目录，程序可能无法正常运行")
        answer = input("是否继续打包？(y/n): ")
        if answer.lower() != 'y':
            print("打包已取消")
            return 1
    
    # 添加源代码目录作为资源，确保可以动态导入
    code_dir = "pubg_assistant"
    if os.path.exists(code_dir) and os.path.isdir(code_dir):
        # 使用特定的导入结构参数
        resource_params += f" --additional-hooks-dir=. --paths=. --hidden-import=pubg_assistant.config.resolution_config"
        # 添加所有可能的子模块
        for root, dirs, files in os.walk(code_dir):
            for dir_name in dirs:
                if not dir_name.startswith("__"):
                    module_path = os.path.join(root, dir_name).replace("\\", "/").replace("/", ".")
                    resource_params += f" --hidden-import={module_path}"
        # 添加代码目录
        resource_params += f" --add-data={code_dir};{code_dir}"
    
    # 构建打包命令
    if debug_mode:
        # 调试模式：显示控制台窗口
        cmd = f"pyinstaller -F -w -n auto -i {icon_file} {resource_params} {entry_script}"
    else:
        # 正常模式：不显示控制台窗口
        cmd = f"pyinstaller -F -w -n auto -i {icon_file} {resource_params} {entry_script}"
    
    print("\n开始打包程序...")
    print(f"执行命令: {cmd}")
    
    # 执行打包命令
    result = os.system(cmd)
    
    if result == 0:
        print("\n打包成功! 可执行文件位于 dist 目录中")
        print("资源文件已经被打包到可执行文件中，不再需要单独复制resources目录")
        print("直接运行exe文件即可，无需额外的依赖文件")
        
        # 复制readme文件
        if os.path.exists("README.md"):
            shutil.copy("README.md", "dist/")
            print("已复制README.md到dist目录")
            
        # 创建D:\pubg目录（配置文件保存位置）
        pubg_dir = "D:\\pubg"
        if not os.path.exists(pubg_dir):
            try:
                os.makedirs(pubg_dir, exist_ok=True)
                print(f"已创建配置目录: {pubg_dir}")
            except:
                print(f"无法创建配置目录: {pubg_dir}，程序运行时可能需要手动创建")
    else:
        print(f"\n打包失败，错误代码: {result}")
    
    return result

if __name__ == "__main__":
    print("======= PUBG Assistant 打包工具 =======\n")
    # 执行打包
    sys.exit(main()) 
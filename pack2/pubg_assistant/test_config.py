#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试配置和资源加载的脚本
"""

import os
import sys

# 设置工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 添加项目根目录到Python路径
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    print("测试配置管理器...")
    from pubg_assistant.config.config_manager import ConfigManager
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    print(f"配置目录: {config_manager.config_dir}")
    print(f"资源目录: {config_manager.resources_base}")
    print(f"字典目录: {config_manager.dict_dir}")
    
    # 测试加载字典
    gun_dict = config_manager.load_gun_names()
    print(f"加载枪械字典: {'成功' if gun_dict is not None else '失败'}")
    
    # 测试加载名称列表
    gun_names = config_manager.load_gun_names()
    print(f"加载枪械名称列表: {'成功，包含{len(gun_names)}项' if gun_names else '失败'}")
    
    # 测试ResolutionConfig
    print("\n测试分辨率配置...")
    from pubg_assistant.config.resolution_config import ResolutionConfig
    
    resolution_config = ResolutionConfig()
    print(f"UI位置: {resolution_config.get_ui_position()}")
    print(f"资源目录: {resolution_config.resources_dir}")
    
    # 测试图像处理器
    print("\n测试图像处理器...")
    from pubg_assistant.processors.image_processor import ImageProcessor
    
    image_processor = ImageProcessor(resolution_config)
    print(f"图像处理器初始化成功")
    print(f"使用模板匹配算法: {image_processor.is_using_template_matching()}")

    print("\n所有测试完成")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

input("按任意键退出...") 
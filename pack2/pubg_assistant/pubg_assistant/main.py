#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUBG Assistant主程序
"""

import os
import sys
import time
import ctypes

from pubg_assistant.config.resolution_config import ResolutionConfig
from pubg_assistant.config.config_manager import ConfigManager
from pubg_assistant.managers.ui_manager import UIManager
from pubg_assistant.managers.input_manager import InputManager
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.processors.action_processor import ActionProcessor
from pubg_assistant.monitors.posture_monitor import PostureMonitor

def main():
    """主函数"""
    
    # 控制台设置
    os.system("title PUBG Assistant")
    os.system("mode con cols=50 lines=30")
    
    # 初始化模块
    print("初始化中...")
    
    # 1. 初始化分辨率配置
    resolution_config = ResolutionConfig()
    print("分辨率配置初始化完成")
    
    # 2. 初始化配置管理器
    config_manager = ConfigManager()
    print("配置管理器初始化完成")
    
    # 3. 初始化UI管理器
    ui_manager = UIManager()
    ui_position = resolution_config.get_ui_position()
    ui_manager.start_display("启动中...", ui_position["x"], ui_position["y"])
    print("UI管理器初始化完成")
    
    # 4. 初始化图像处理器
    image_processor = ImageProcessor(resolution_config)
    print("图像处理器初始化完成")
    
    # 5. 初始化动作处理器
    action_processor = ActionProcessor(image_processor, config_manager, ui_manager)
    print("动作处理器初始化完成")
    
    # 6. 初始化姿势监控器
    posture_monitor = PostureMonitor(image_processor, config_manager, action_processor)
    posture_monitor.daemon = True
    posture_monitor.start()
    posture_monitor.pause()  # 默认暂停状态
    print("姿势监控器初始化完成")
    
    # 7. 初始化输入管理器
    input_manager = InputManager()
    input_manager.set_action_processor(action_processor)
    input_manager.set_posture_monitor(posture_monitor)
    input_manager.start()
    print("输入管理器初始化完成")
    
    print("所有模块初始化完成，程序已启动")
    
    try:
        # 主循环，保持程序运行
        while True:
            # 更新UI状态
            action_processor._update_display()
            
            # 检查是否请求退出程序
            if action_processor.is_exit_requested():
                break
                
            # 短暂休眠，降低CPU使用率
            time.sleep(0.1)
    except KeyboardInterrupt:
        # 处理Ctrl+C退出
        print("正在退出程序...")
    finally:
        # 停止所有线程和服务
        posture_monitor.stop()
        input_manager.stop()
        ui_manager.stop_display()
        print("所有服务已停止，程序已退出")

if __name__ == "__main__":
    main()

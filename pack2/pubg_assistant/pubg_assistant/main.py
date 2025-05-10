#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUBG Assistant 主程序
"""

import os
import sys
import time
import ctypes
import argparse
import traceback
import tkinter as tk

from pubg_assistant.config.resolution_config import ResolutionConfig
from pubg_assistant.config.config_manager import ConfigManager
from pubg_assistant.managers.ui_manager import UIManager
from pubg_assistant.managers.input_manager import InputManager
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.processors.action_processor import ActionProcessor
from pubg_assistant.monitors.posture_monitor import PostureMonitor
from pubg_assistant.core.logging import setup_default_logger
from pubg_assistant.core.exceptions import PubgAssistantError

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PUBG Assistant - 绝地求生游戏助手')
    parser.add_argument('--resolution', type=str, help='游戏分辨率，格式为 宽x高，例如 2560x1440')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--save-temp', action='store_true', help='保存临时图片（用于调试）')
    return parser.parse_args()

def initialize_modules(logger, resolution=None, save_temp_images=False):
    """初始化所有模块
    
    Args:
        logger: 日志器
        resolution: 分辨率设置，格式为 (width, height)
        save_temp_images: 是否保存临时图片
        
    Returns:
        tuple: 所有初始化的模块
    """
    # 1. 初始化分辨率配置
    if resolution:
        width, height = resolution
        resolution_config = ResolutionConfig(width=width, height=height)
    else:
        resolution_config = ResolutionConfig()
    logger.info(f"分辨率配置初始化完成: {resolution_config.width}x{resolution_config.height}")
    
    # 2. 初始化配置管理器
    config_manager = ConfigManager()
    logger.info("配置管理器初始化完成")
    
    # 3. 初始化UI管理器
    ui_manager = UIManager()
    ui_position = resolution_config.get_ui_position()
    ui_manager.start_display("启动中...", ui_position["x"], ui_position["y"])
    logger.info(f"UI管理器初始化完成，显示位置: x={ui_position['x']}, y={ui_position['y']}")
    
    # 4. 初始化图像处理器
    image_processor = ImageProcessor(resolution_config, save_temp_images=save_temp_images)
    logger.info("图像处理器初始化完成")
    
    # 5. 初始化动作处理器
    action_processor = ActionProcessor(image_processor, config_manager, ui_manager)
    logger.info("动作处理器初始化完成")
    
    # 6. 初始化姿势监控器
    posture_monitor = PostureMonitor(image_processor, config_manager, action_processor)
    posture_monitor.daemon = True
    posture_monitor.start()
    posture_monitor.pause()  # 默认暂停状态
    logger.info("姿势监控器初始化完成")
    
    # 7. 初始化输入管理器
    input_manager = InputManager()
    input_manager.set_action_processor(action_processor)
    input_manager.set_posture_monitor(posture_monitor)
    input_manager.start()
    logger.info("输入管理器初始化完成")
    
    return (resolution_config, config_manager, ui_manager, 
            image_processor, action_processor, posture_monitor, input_manager)

def show_splash_screen():
    """显示启动画面"""
    print("=" * 50)
    print("  PUBG Assistant v1.1.0")
    print("=" * 50)
    print("  按键说明:")
    print("  - [1]/[2]: 切换/识别武器")
    print("  - [`]: 锁定/解锁武器栏")
    print("  - [F1]: 关闭宏")
    print("  - [F8]: 切换匹配算法")
    print("  - [F9]: 退出程序")
    print("  - [NumLock]: 切换武器配置状态")
    print("  - [鼠标侧键X2]: 开始/停止姿势检测")
    print("=" * 50)

def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置日志
        log_level = 'DEBUG' if args.debug else 'INFO'
        console_level = 'INFO' if args.debug else 'WARNING'  # 调试模式下显示INFO级别日志，否则只显示WARNING及以上
        logger = setup_default_logger(console_level=console_level)
        
        # 设置控制台
        os.system("title Assistant v1.1.0")
        os.system("mode con cols=50 lines=30")
        show_splash_screen()
        
        # 创建隐藏的tkinter根窗口，用于保持UI更新
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 解析分辨率
        resolution = None
        if args.resolution:
            try:
                width, height = map(int, args.resolution.lower().split('x'))
                resolution = (width, height)
                logger.info(f"使用指定分辨率: {width}x{height}")
            except Exception as e:
                logger.error(f"分辨率格式错误: {args.resolution}, 使用默认分辨率")
                resolution = None
        
        # 初始化模块
        logger.info("开始初始化所有模块...")
        modules = initialize_modules(logger, resolution, args.save_temp)
        (resolution_config, config_manager, ui_manager, 
         image_processor, action_processor, posture_monitor, input_manager) = modules
        logger.info("所有模块初始化完成，程序已启动")
        
        # 终止标志
        exit_flag = [False]
        
        # 定义更新函数
        def update_loop():
            try:
                # 更新UI状态
                action_processor._update_display()
                
                # 更新tkinter窗口
                root.update()
                
                # 检查是否请求退出程序
                if action_processor.is_exit_requested():
                    logger.info("接收到退出请求，准备退出程序")
                    exit_flag[0] = True
                    return
                
                # 继续更新循环
                root.after(100, update_loop)
            except Exception as e:
                logger.error(f"更新循环出错: {str(e)}")
                exit_flag[0] = True
        
        # 启动更新循环
        root.after(100, update_loop)
        
        # 主循环
        try:
            # 运行tkinter主循环直到退出标志被设置
            while not exit_flag[0]:
                root.update()
                time.sleep(0.01)  # 短暂休眠以减少CPU使用
        except KeyboardInterrupt:
            logger.info("接收到键盘中断信号，准备退出程序")
        finally:
            # 停止所有线程和服务
            logger.info("正在停止所有服务...")
            posture_monitor.stop()
            input_manager.stop()
            ui_manager.stop_display()
            if root:
                try:
                    root.destroy()
                except:
                    pass
            logger.info("所有服务已停止，程序已退出")
    
    except PubgAssistantError as e:
        print(f"程序错误: {e}")
        if args and args.debug:
            traceback.print_exc()
    except Exception as e:
        print(f"未知错误: {e}")
        traceback.print_exc()
    finally:
        print("程序已退出。按任意键关闭窗口...")
        input()

if __name__ == "__main__":
    main()

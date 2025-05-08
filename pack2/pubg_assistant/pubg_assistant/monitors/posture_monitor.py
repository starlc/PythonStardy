#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
姿势监控模块
负责监控玩家姿势状态
"""

import threading
import time

class PostureMonitor(threading.Thread):
    """姿势监控线程，负责监控玩家姿势状态"""
    
    def __init__(self, image_processor=None, config_manager=None, action_processor=None):
        """初始化姿势监控器
        
        Args:
            image_processor: 图像处理器
            config_manager: 配置管理器
            action_processor: 动作处理器
        """
        super(PostureMonitor, self).__init__()
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        
        self.image_processor = image_processor
        self.config_manager = config_manager
        self.action_processor = action_processor
    
    def run(self):
        """线程运行方法"""
        while self.__running.is_set():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            self._check_posture()  # 姿势判断
            time.sleep(1)  # 休眠1秒
    
    def _check_posture(self):
        """检测姿势"""
        if self.action_processor:
            self.action_processor.check_posture()
        elif self.image_processor and self.config_manager:
            # 如果没有动作处理器，但有图像处理器和配置管理器，直接处理
            posture = self.image_processor.detect_posture()
            self.config_manager.save_config("posture", str(posture))
    
    def pause(self):
        """暂停线程"""
        self.__flag.clear()  # 设置为False, 让线程阻塞
    
    def resume(self):
        """恢复线程"""
        self.__flag.set()  # 设置为True, 让线程停止阻塞
    
    def stop(self):
        """停止线程"""
        self.__flag.set()  # 将线程从暂停状态恢复, 如果已经暂停的话
        self.__running.clear()  # 设置为False
    
    def set_image_processor(self, image_processor):
        """设置图像处理器
        
        Args:
            image_processor: 图像处理器
        """
        self.image_processor = image_processor
    
    def set_config_manager(self, config_manager):
        """设置配置管理器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
    
    def set_action_processor(self, action_processor):
        """设置动作处理器
        
        Args:
            action_processor: 动作处理器
        """
        self.action_processor = action_processor
    
    
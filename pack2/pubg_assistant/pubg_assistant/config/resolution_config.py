#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分辨率配置模块
负责管理游戏分辨率相关的配置
"""

import os

class ResolutionConfig:
    """分辨率配置类"""
    
    def __init__(self, width=2560, height=1440):
        """初始化分辨率配置
        
        Args:
            width: 屏幕宽度，默认2560
            height: 屏幕高度，默认1440
        """
        self.width = width
        self.height = height
        
        # 计算资源目录的基础路径（项目根目录下的resources文件夹）
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        resources_base = os.path.join(base_dir, "resources")
        
        # 根据分辨率选择配置
        if width == 2560 and height == 1440:
            self.resources_dir = os.path.join(resources_base, "25601440")
            # 绝对位置配置
            self.ui_position = {"x": 1560, "y": 1370}
            self.weapon_area = {
                "left": 1940, "top": 1325, "width": 195, "height": 100
            }
            self.weapon_area_2 = {
                "left": 1940, "top": 1245, "width": 195, "height": 100
            }
            self.posture_area_1 = {
                "left": 962, "top": 1308, "width": 5, "height": 5
            }
            self.posture_area_2 = {
                "left": 960, "top": 1315, "width": 5, "height": 5
            }
        elif width == 2313 and height == 1440:
            self.resources_dir = os.path.join(resources_base, "23131440")
            # 绝对位置配置
            self.ui_position = {"x": 1400, "y": 1370}
            self.weapon_area = {
                "left": 1755, "top": 1325, "width": 175, "height": 100
            }
            self.weapon_area_2 = {
                "left": 1755, "top": 1245, "width": 175, "height": 100
            }
            self.posture_area_1 = {
                "left": 870, "top": 1308, "width": 5, "height": 5
            }
            self.posture_area_2 = {
                "left": 868, "top": 1315, "width": 5, "height": 5
            }
        else:
            # 默认使用2560x1440的绝对位置
            self.resources_dir = os.path.join(resources_base, "25601440")
            self.ui_position = {"x": 1560, "y": 1370}
            self.weapon_area = {
                "left": 1940, "top": 1325, "width": 195, "height": 100
            }
            self.weapon_area_2 = {
                "left": 1940, "top": 1245, "width": 195, "height": 100
            }
            self.posture_area_1 = {
                "left": 962, "top": 1308, "width": 5, "height": 5
            }
            self.posture_area_2 = {
                "left": 960, "top": 1315, "width": 5, "height": 5
            }
    
    def get_ui_position(self):
        """获取UI位置
        
        Returns:
            dict: UI位置字典
        """
        return self.ui_position
    
    def get_weapon_area(self, slot=1):
        """获取武器识别区域
        
        Args:
            slot: 武器槽位，1或2
            
        Returns:
            dict: 武器识别区域字典
        """
        if slot == 2:
            return self.weapon_area_2
        return self.weapon_area
    
    def get_posture_area(self, index=1):
        """获取姿势检测区域
        
        Args:
            index: 检测区域索引，1或2
            
        Returns:
            dict: 姿势检测区域字典
        """
        if index == 2:
            return self.posture_area_2
        return self.posture_area_1
    
    def get_resources_dir(self):
        """获取资源目录
        
        Returns:
            str: 资源目录路径
        """
        return self.resources_dir
    
   
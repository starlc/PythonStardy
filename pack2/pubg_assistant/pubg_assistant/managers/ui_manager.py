#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI管理器模块
负责管理程序的用户界面
"""

import tkinter as tk
import time
import os

class CharacterDisplayApp:
    """字符显示应用类"""
    
    def __init__(self, initial_character, x, y):
        """初始化字符显示应用
        
        Args:
            initial_character: 初始显示字符
            x: 窗口x坐标
            y: 窗口y坐标
        """
        self.root = tk.Tk()
        self.root.title("Character Display")
        
        # 去掉窗口边框
        self.root.overrideredirect(True)
        
        # 设置窗口透明度为50%
        self.root.attributes("-alpha", 0.5)
        
        # 设置窗口置顶
        self.root.attributes("-topmost", True)
        
        # 创建标签并设置背景为浅灰色，字体颜色为深蓝色
        self.label = tk.Label(
            self.root, 
            text=initial_character, 
            font=("Microsoft YaHei", 12), 
            fg="#1e3a8a", 
            bg="#d1d5db", 
            anchor="w", 
            justify="left"
        )
        self.label.pack(fill="both", expand=True)
        
        # 设置窗口位置
        self.root.geometry(f"+{x}+{y}")
        
        # 保持窗口在最前
        self.root.attributes("-topmost", True)
        
        # 初始更新
        self.root.update()
    
    def update_character(self, new_character):
        """更新显示字符
        
        Args:
            new_character: 新的显示字符
        """
        try:
            self.label.config(text=new_character)
            self.root.update_idletasks()
            self.root.update()
        except:
            pass  # 忽略更新失败
    
    def destroy(self):
        """销毁窗口"""
        try:
            self.root.destroy()
        except:
            pass  # 忽略销毁失败

class UIManager:
    """UI管理器类"""
    
    def __init__(self):
        """初始化UI管理器"""
        self.app = None
        self.running = False
    
    def start_display(self, initial_character="启动", x=1560, y=1370):
        """启动显示
        
        Args:
            initial_character: 初始显示字符
            x: 窗口x坐标
            y: 窗口y坐标
        """
        try:
            # 创建显示应用
            self.app = CharacterDisplayApp(initial_character, x, y)
            self.running = True
        except Exception as e:
            print(f"启动UI显示失败: {e}")
            self.running = False
    
    def update_display(self, gun_lock, gun_name, posture, gun_config):
        """更新显示
        
        Args:
            gun_lock: 武器锁定状态，0为未锁定，1为锁定
            gun_name: 武器名称
            posture: 姿势状态，1为站立，其他为蹲下
            gun_config: 武器配置状态，True为裸配，False为满配
        """
        if not self.app or not self.running:
            return
            
        gun_status = "锁" if gun_lock == 1 else "解"
        posture_status = "站" if posture == 1 else "蹲"
        full_status = "满" if  gun_config else "裸"
        new_character = f"{gun_status}|{full_status}|{posture_status}|{gun_name}"
        
        try:
            self.app.update_character(new_character)
        except:
            pass  # 忽略更新失败
    
    def update_display_with_algorithm(self, gun_lock, gun_name, posture, gun_config, use_template):
        """更新显示（带算法指示）
        
        Args:
            gun_lock: 武器锁定状态，0为未锁定，1为锁定
            gun_name: 武器名称
            posture: 姿势状态，1为站立，其他为蹲下
            gun_config: 武器配置状态，True为裸配，False为满配
            use_template: 是否使用模板匹配算法
        """
        if not self.app or not self.running:
            return
            
        gun_status = "锁" if gun_lock == 1 else "解"
        posture_status = "站" if posture == 1 else "蹲"
        full_status = "满" if gun_config else "裸"
        method_status = "" if not use_template  else "|"
        new_character = f"{gun_status}|{full_status}|{posture_status}{method_status}|{gun_name}"
        
        try:
            self.app.update_character(new_character)
        except:
            pass  # 忽略更新失败
    
    def stop_display(self):
        """停止显示界面"""
        try:
            if self.app:
                self.app.destroy()
                self.app = None
            self.running = False
        except:
            pass  # 忽略停止失败 
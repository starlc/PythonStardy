#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI管理器模块
负责管理程序的用户界面
"""

import tkinter as tk
import time
import os
import threading
import queue
from enum import Enum

from pubg_assistant.core.logging import get_logger
from pubg_assistant.core.exceptions import UIError

class CharacterDisplayApp:
    """字符显示应用类"""
    
    def __init__(self, initial_character, x, y, theme="DEFAULT", update_queue=None):
        """初始化字符显示应用
        
        Args:
            initial_character: 初始显示字符
            x: 窗口x坐标
            y: 窗口y坐标
            theme: 主题名称
            update_queue: 更新队列
        """
        self.logger = get_logger("ui_display")
        self.update_queue = update_queue
        self.running = True
        
        try:
            # 尝试找到已存在的Tk根窗口，否则创建一个新的
            try:
                self.root = tk.Toplevel(tk._default_root)
            except:
                # 如果没有找到根窗口，创建一个新的
                import tkinter as _tk
                self._root = _tk.Tk()
                self._root.withdraw()  # 隐藏根窗口
                self.root = tk.Toplevel(self._root)
            
            # 完全按照原始UI设置样式
            self.root.title("PUBG Assistant")
            self.root.overrideredirect(True)  # 无边框
            self.root.attributes('-alpha', 0.5)  # 透明度为50%
            self.root.attributes('-topmost', True)  # 置顶
            
            # 使用原始UI样式
            self.label = tk.Label(
                self.root,
                text=initial_character,
                font=("Microsoft YaHei", 12),  # 使用微软雅黑12号字体
                fg="#1e3a8a",  # 深蓝色文字
                bg="#d1d5db",  # 浅灰色背景
                anchor="w",  # 文字左对齐
                justify="left"  # 多行时左对齐
            )
            self.label.pack(fill="both", expand=True)
            
            # 设置窗口位置
            self.root.geometry(f"+{x}+{y}")
            
            # 初始更新
            self.root.update()
            
            # 添加鼠标拖动功能
            self._add_drag_support()
            
            # 设置周期性检查更新队列
            if self.update_queue:
                self.root.after(100, self._check_update_queue)
            
            self.logger.info(f"UI显示初始化成功，位置({x}, {y})")
        except Exception as e:
            self.logger.error(f"UI显示初始化失败: {str(e)}")
            raise UIError(f"UI显示初始化失败: {str(e)}")
    
    def _add_drag_support(self):
        """添加鼠标拖动支持"""
        self.root.bind("<Button-1>", self._start_drag)
        self.root.bind("<ButtonRelease-1>", self._stop_drag)
        self.root.bind("<B1-Motion>", self._do_drag)
        
        self.label.bind("<Button-1>", self._start_drag)
        self.label.bind("<ButtonRelease-1>", self._stop_drag)
        self.label.bind("<B1-Motion>", self._do_drag)
        
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
    
    def _start_drag(self, event):
        """开始拖动"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["dragging"] = True
    
    def _stop_drag(self, event):
        """停止拖动"""
        self.drag_data["dragging"] = False
    
    def _do_drag(self, event):
        """执行拖动"""
        if not self.drag_data["dragging"]:
            return
            
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        
        self.root.geometry(f"+{x}+{y}")
    
    def _check_update_queue(self):
        """检查更新队列"""
        if not self.running:
            return
            
        try:
            # 非阻塞方式获取更新
            while True:
                try:
                    new_character = self.update_queue.get_nowait()
                    self.label.config(text=new_character)
                    self.update_queue.task_done()
                except queue.Empty:
                    break
        except Exception as e:
            self.logger.error(f"处理UI更新队列失败: {str(e)}")
        
        # 再次安排检查
        if self.running:
            self.root.after(100, self._check_update_queue)
    
    def update_character(self, new_character):
        """更新显示字符
        
        Args:
            new_character: 新的显示字符
        """
        try:
            if self.update_queue:
                # 将更新放入队列
                self.update_queue.put(new_character)
            else:
                # 直接更新（旧方法，作为备份）
                def _safe_update():
                    try:
                        self.label.config(text=new_character)
                        self.root.update_idletasks()
                    except Exception as e:
                        self.logger.error(f"执行UI更新失败: {str(e)}")
                
                # 如果当前在主线程，直接更新；否则使用 after 方法
                if threading.current_thread() is threading.main_thread():
                    _safe_update()
                else:
                    self.root.after(0, _safe_update)
        except Exception as e:
            self.logger.error(f"更新显示内容失败: {str(e)}")
    
    def destroy(self):
        """销毁窗口"""
        try:
            self.running = False
            if hasattr(self, 'root') and self.root:
                self.root.destroy()
                self.root = None
            if hasattr(self, '_root') and self._root:
                self._root.destroy()
                self._root = None
            self.logger.info("UI显示已关闭")
        except Exception as e:
            self.logger.error(f"销毁UI窗口失败: {str(e)}")

class UIManager:
    """UI管理器类"""
    
    def __init__(self, theme="DEFAULT"):
        """初始化UI管理器
        
        Args:
            theme: 主题名称
        """
        self.app = None
        self.running = False
        self.logger = get_logger("ui_manager")
        
        # 更新队列
        self.update_queue = queue.Queue()
        
        # 状态锁
        self.lock = threading.RLock()
        
        self.logger.info("UI管理器初始化完成")
    
    def start_display(self, initial_character="启动", x=1560, y=1370):
        """启动显示
        
        Args:
            initial_character: 初始显示字符
            x: 窗口x坐标
            y: 窗口y坐标
        """
        with self.lock:
            try:
                if self.running:
                    return
                    
                # 打印控制台消息，确认UI启动
                print(f"UI显示启动中，位置({x}, {y})...")
                
                # 直接在主线程创建UI
                self.app = CharacterDisplayApp(initial_character, x, y, update_queue=self.update_queue)
                self.running = True
                
                # 确认UI已启动
                print("UI显示已启动成功")
                self.logger.info(f"UI显示启动成功: {initial_character}")
            except Exception as e:
                print(f"启动UI显示失败: {str(e)}")
                self.logger.error(f"启动UI显示失败: {str(e)}")
                self.running = False
    
    def update_display(self, gun_lock, gun_name, posture, gun_config):
        """更新显示
        
        Args:
            gun_lock: 武器锁定状态，0为未锁定，1为锁定
            gun_name: 武器名称
            posture: 姿势状态，1为站立，其他为蹲下
            gun_config: 武器配置状态，True为裸配，False为满配
        """
        with self.lock:
            if not self.running or not self.app:
                return
                
            try:
                # 完全按照原始UI格式
                gun_status = "锁" if gun_lock == 1 else "解"
                posture_status = "站" if posture == 1 else "蹲"
                full_status = "满" if gun_config else "裸"
                
                # 完全按照原始UI格式使用|分隔
                new_character = f"{gun_status}|{full_status}|{posture_status}|{gun_name}"
                
                # 使用队列更新
                self.update_queue.put(new_character)
            except Exception as e:
                self.logger.error(f"更新UI显示失败: {str(e)}")
    
    def update_display_with_algorithm(self, gun_lock, gun_name, posture, gun_config, use_template):
        """更新显示（带算法指示）
        
        Args:
            gun_lock: 武器锁定状态，0为未锁定，1为锁定
            gun_name: 武器名称
            posture: 姿势状态，1为站立，其他为蹲下
            gun_config: 武器配置状态，True为裸配，False为满配
            use_template: 是否使用模板匹配算法
        """
        with self.lock:
            if not self.running or not self.app:
                return
                
            try:
                # 完全按照原始UI格式
                gun_status = "锁" if gun_lock == 1 else "解"
                posture_status = "站" if posture == 1 else "蹲"
                full_status = "满" if gun_config else "裸"
                method_status = "" if use_template else "|"
                
                # 按照原始代码完全匹配
                new_character = f"{gun_status}|{full_status}|{posture_status}{method_status}|{gun_name}"
                
                # 使用队列更新
                self.update_queue.put(new_character)
            except Exception as e:
                self.logger.error(f"更新UI显示失败: {str(e)}")
    
    def stop_display(self):
        """停止显示界面"""
        with self.lock:
            try:
                if self.app:
                    self.app.destroy()
                    self.app = None
                    
                # 清空队列
                try:
                    while True:
                        self.update_queue.get_nowait()
                        self.update_queue.task_done()
                except queue.Empty:
                    pass
                    
                self.running = False
                self.logger.info("UI显示已停止")
            except Exception as e:
                self.logger.error(f"停止UI显示失败: {str(e)}")
    
    def is_running(self):
        """检查是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        with self.lock:
            return self.running 
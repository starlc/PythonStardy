#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
输入管理器模块
负责管理键盘和鼠标输入
"""

import threading
from queue import Queue
from pynput import keyboard, mouse
from pynput.mouse import Button

class Action:
    """动作类"""
    
    def __init__(self, action_type, param):
        """初始化动作
        
        Args:
            action_type: 动作类型 True为键盘动作 False为鼠标动作
            param: 动作参数
        """
        self.action_type = action_type
        self.param = param
    
    def get_type(self):
        """获取动作类型
        
        Returns:
            bool: 动作类型
        """
        return self.action_type
    
    def get_param(self):
        """获取动作参数
        
        Returns:
            any: 动作参数
        """
        return self.param

class InputManager:
    """输入管理器类"""
    
    def __init__(self, action_queue=None, posture_monitor=None):
        """初始化输入管理器
        
        Args:
            action_queue: 动作队列
            posture_monitor: 姿势监控器
        """
        self.action_queue = action_queue if action_queue else Queue()
        self.posture_monitor = posture_monitor
        self.keyboard_listener = None
        self.mouse_listener = None
        self.consumer_thread = None
        self.is_running = False
    
    def start(self):
        """启动输入管理器"""
        self.is_running = True
        
        # 启动消费者线程
        self.consumer_thread = threading.Thread(target=self._consumer)
        self.consumer_thread.daemon = True
        self.consumer_thread.start()
        
        # 启动键盘监听器
        self.keyboard_listener = keyboard.Listener(on_release=self._on_key_release)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        
        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
    
    def stop(self):
        """停止输入管理器"""
        self.is_running = False
        
        # 停止键盘监听器
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # 停止鼠标监听器
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        # 清空队列
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
                self.action_queue.task_done()
            except:
                pass
    
    def _consumer(self):
        """消费者线程"""
        while self.is_running:
            try:
                action = self.action_queue.get()
                self._process_action(action)
                self.action_queue.task_done()
            except:
                pass
    
    def _process_action(self, action):
        """处理动作
        
        Args:
            action: 动作对象
        """
        if hasattr(self, 'action_processor') and self.action_processor:
            if action.get_type():
                # 键盘动作
                self.action_processor.handle_keyboard_action(action.get_param())
            else:
                # 鼠标动作
                self.action_processor.handle_mouse_action(action.get_param())
    
    def _on_key_release(self, key):
        """键盘释放事件处理
        
        Args:
            key: 按键对象
            
        Returns:
            bool: True继续监听，False停止监听
        """
        try:
            if key == keyboard.Key.f1:
                # 按下F1 将武器设值为0
                self.action_queue.queue.clear()
                action = Action(True, 0)
                self.action_queue.put(action)
                return True
            
            if key == keyboard.Key.num_lock:
                # 按下numlock 变更numLock状态
                self.action_queue.queue.clear()
                action = Action(True, key)
                self.action_queue.put(action)
                return True
            
            if hasattr(key, 'char') and key.char == '`':
                # 按下~ 锁定武器栏
                self.action_queue.queue.clear()
                action = Action(True, 4)
                self.action_queue.put(action)
                return True
            
            if hasattr(key, 'char') and key.char in ['1', '2']:
                # 按下1或2 切换武器
                key_num = int(key.char)
                self.action_queue.queue.clear()
                action = Action(True, key_num)
                self.action_queue.put(action)
                return True
        except:
            pass
        
        return True
    
    def _on_click(self, x, y, button, pressed):
        """鼠标点击事件处理
        
        Args:
            x: 鼠标x坐标
            y: 鼠标y坐标
            button: 鼠标按键
            pressed: 是否按下
        """
        if Button.x2 == button:
            if self.posture_monitor:
                if pressed:
                    # 按下鼠标侧键X2时开始姿势检测
                    self.posture_monitor.resume()
                else:
                    # 释放鼠标侧键X2时停止姿势检测
                    self.posture_monitor.pause()
    
    def set_action_processor(self, action_processor):
        """设置动作处理器
        
        Args:
            action_processor: 动作处理器
        """
        self.action_processor = action_processor
    
    def set_posture_monitor(self, posture_monitor):
        """设置姿势监控器
        
        Args:
            posture_monitor: 姿势监控器
        """
        self.posture_monitor = posture_monitor
        
    def get_action_queue(self):
        """获取动作队列
        
        Returns:
            Queue: 动作队列
        """
        return self.action_queue 
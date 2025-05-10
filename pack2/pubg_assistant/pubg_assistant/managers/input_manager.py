#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
输入管理器模块
负责管理键盘和鼠标输入
"""

import threading
from queue import Queue, Empty
from pynput import keyboard, mouse
from pynput.mouse import Button
from enum import Enum

from pubg_assistant.core.logging import get_logger
from pubg_assistant.core.exceptions import InputError

class ActionType(Enum):
    """动作类型枚举"""
    KEYBOARD = 1  # 键盘动作
    MOUSE = 2  # 鼠标动作

class Action:
    """动作类"""
    
    def __init__(self, action_type, param):
        """初始化动作
        
        Args:
            action_type: 动作类型，使用ActionType枚举
            param: 动作参数
        """
        self.action_type = action_type
        self.param = param
    
    def get_type(self):
        """获取动作类型
        
        Returns:
            ActionType: 动作类型
        """
        return self.action_type
    
    def get_param(self):
        """获取动作参数
        
        Returns:
            any: 动作参数
        """
        return self.param
    
    def __str__(self):
        """字符串表示
        
        Returns:
            str: 动作的字符串表示
        """
        return f"Action({self.action_type.name}, {self.param})"

class InputManager:
    """输入管理器类"""
    
    # 队列大小和处理超时
    QUEUE_SIZE = 100
    QUEUE_TIMEOUT = 0.1  # 秒
    
    def __init__(self, action_queue=None, posture_monitor=None):
        """初始化输入管理器
        
        Args:
            action_queue: 动作队列
            posture_monitor: 姿势监控器
        """
        self.action_queue = action_queue if action_queue else Queue(maxsize=self.QUEUE_SIZE)
        self.posture_monitor = posture_monitor
        self.action_processor = None
        self.keyboard_listener = None
        self.mouse_listener = None
        self.consumer_thread = None
        self.is_running = False
        self.logger = get_logger("input_manager")
        
        # 状态锁
        self.lock = threading.RLock()
        
        self.logger.info("输入管理器初始化完成")
    
    def start(self):
        """启动输入管理器"""
        with self.lock:
            if self.is_running:
                return
                
            self.is_running = True
            
            # 启动消费者线程
            self.consumer_thread = threading.Thread(target=self._consumer, name="InputConsumerThread")
            self.consumer_thread.daemon = True
            self.consumer_thread.start()
            
            # 启动键盘监听器
            self.keyboard_listener = keyboard.Listener(
                on_release=self._on_key_release,
                name="KeyboardListenerThread"
            )
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
            
            # 启动鼠标监听器
            self.mouse_listener = mouse.Listener(
                on_click=self._on_click,
                name="MouseListenerThread"
            )
            self.mouse_listener.daemon = True
            self.mouse_listener.start()
            
            self.logger.info("输入管理器启动成功")
    
    def stop(self):
        """停止输入管理器"""
        with self.lock:
            if not self.is_running:
                return
                
            self.is_running = False
            
            # 停止键盘监听器
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            
            # 停止鼠标监听器
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            # 清空队列并发送退出信号
            try:
                while not self.action_queue.empty():
                    try:
                        self.action_queue.get_nowait()
                        self.action_queue.task_done()
                    except:
                        pass
            except:
                pass
                
            self.logger.info("输入管理器已停止")
    
    def _consumer(self):
        """消费者线程"""
        self.logger.info("输入消费者线程启动")
        
        while self.is_running:
            try:
                # 带超时的获取，让线程能够正常退出
                try:
                    action = self.action_queue.get(timeout=self.QUEUE_TIMEOUT)
                    self._process_action(action)
                    self.action_queue.task_done()
                except Empty:
                    continue
            except Exception as e:
                self.logger.error(f"处理输入动作失败: {str(e)}")
                
        self.logger.info("输入消费者线程退出")
    
    def _process_action(self, action):
        """处理动作
        
        Args:
            action: 动作对象
        """
        if not hasattr(self, 'action_processor') or not self.action_processor:
            self.logger.warning("未设置动作处理器，无法处理输入")
            return
            
        try:
            if action.get_type() == ActionType.KEYBOARD:
                # 键盘动作
                self.action_processor.handle_keyboard_action(action.get_param())
            elif action.get_type() == ActionType.MOUSE:
                # 鼠标动作
                self.action_processor.handle_mouse_action(action.get_param())
        except Exception as e:
            self.logger.error(f"处理动作失败: {str(e)}")
    
    def _on_key_release(self, key):
        """键盘释放事件处理
        
        Args:
            key: 按键对象
            
        Returns:
            bool: True继续监听，False停止监听
        """
        try:
            # 防止队列过载
            if self.action_queue.qsize() >= self.QUEUE_SIZE - 10:
                self.logger.warning("输入队列接近满载，丢弃部分输入")
                return True
                
            handled = True
            
            if key == keyboard.Key.f1:
                # 按下F1 将武器设值为0
                self._clear_queue_and_add_action(Action(ActionType.KEYBOARD, 0))
            
            elif key == keyboard.Key.f8:
                # 按下F8 切换算法
                self._clear_queue_and_add_action(Action(ActionType.KEYBOARD, 8))
            
            elif key == keyboard.Key.f9:
                # 按下F9 退出程序
                self._clear_queue_and_add_action(Action(ActionType.KEYBOARD, 9))
                
            elif key == keyboard.Key.num_lock:
                # 按下numlock 变更numLock状态
                self._clear_queue_and_add_action(Action(ActionType.KEYBOARD, key))
                
            elif hasattr(key, 'char') and key.char == '`':
                # 按下~ 锁定武器栏
                self._clear_queue_and_add_action(Action(ActionType.KEYBOARD, 4))
                
            elif hasattr(key, 'char') and key.char in ['1', '2']:
                # 按下1或2 切换武器
                key_num = int(key.char)
                self._clear_queue_and_add_action(Action(ActionType.KEYBOARD, key_num))
                
            else:
                handled = False
                
            if handled:
                self.logger.debug(f"处理键盘输入: {key}")
                
        except Exception as e:
            self.logger.error(f"处理键盘输入失败: {str(e)}")
        
        return True  # 继续监听
    
    def _clear_queue_and_add_action(self, action):
        """清空队列并添加动作
        
        Args:
            action: 要添加的动作
        """
        try:
            # 清空现有队列
            while not self.action_queue.empty():
                try:
                    self.action_queue.get_nowait()
                    self.action_queue.task_done()
                except:
                    pass
                    
            # 添加新动作
            self.action_queue.put(action)
        except Exception as e:
            self.logger.error(f"处理队列操作失败: {str(e)}")
    
    def _on_click(self, x, y, button, pressed):
        """鼠标点击事件处理
        
        Args:
            x: 鼠标x坐标
            y: 鼠标y坐标
            button: 鼠标按键
            pressed: 是否按下
        """
        try:
            if Button.x2 == button:
                if self.posture_monitor:
                    if pressed:
                        # 按下鼠标侧键X2时开始姿势检测
                        self.logger.info("开始姿势检测")
                        self.posture_monitor.resume()
                    else:
                        # 释放鼠标侧键X2时停止姿势检测
                        self.logger.info("停止姿势检测")
                        self.posture_monitor.pause()
        except Exception as e:
            self.logger.error(f"处理鼠标输入失败: {str(e)}")
    
    def set_action_processor(self, action_processor):
        """设置动作处理器
        
        Args:
            action_processor: 动作处理器
        """
        with self.lock:
            self.action_processor = action_processor
            self.logger.info("设置动作处理器成功")
    
    def set_posture_monitor(self, posture_monitor):
        """设置姿势监控器
        
        Args:
            posture_monitor: 姿势监控器
        """
        with self.lock:
            self.posture_monitor = posture_monitor
            self.logger.info("设置姿势监控器成功")
    
    def get_action_queue(self):
        """获取动作队列
        
        Returns:
            Queue: 动作队列
        """
        return self.action_queue
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
动作处理器模块
负责处理游戏中的各种动作和操作
"""

import time
import ctypes
import sys
from pynput import keyboard

class ActionProcessor:
    """动作处理器类"""
    
    def __init__(self, image_processor, config_manager, ui_manager):
        """初始化动作处理器
        
        Args:
            image_processor: 图像处理器
            config_manager: 配置管理器
            ui_manager: UI管理器
        """
        self.image_processor = image_processor
        self.config_manager = config_manager
        self.ui_manager = ui_manager
        
        # 状态变量
        self.current_gun = {1: "", 2: ""}  # 当前的武器名
        self.player_posture = 1  # 姿势 1为站 2为蹲 3为趴(暂时不用) 默认1
        self.player_gun = 0  # 当前持有的武器ID
        self.gun_lock = 0  # 武器锁定 0 初始化 1锁定
        self.player_gun_config = True  # 枪械是否满配 false 满配  true 裸配
        
        # 枪械名称列表
        self.gun_list_name = self.config_manager.load_gun_names()
        
        # 检测NumLock状态
        self.player_gun_config = not self._is_numlock_on()
        
        # 退出标志
        self.exit_flag = False
    
    def _is_numlock_on(self):
        """检查NumLock状态
        
        Returns:
            bool: NumLock是否开启
        """
        hll_dll = ctypes.WinDLL("User32.dll")
        vk_numlock = 0x90
        return bool(hll_dll.GetKeyState(vk_numlock) & 1)
    
    def _is_caps_lock_on(self):
        """检查CapsLock状态
        
        Returns:
            bool: CapsLock是否开启
        """
        return bool(ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1)
    
    def _play_sound(self, content):
        """播放语音
        
        Args:
            content: 语音内容
        """
        try:
            import pyttsx3 as pytts
            engine = pytts.Engine()
            engine.setProperty('rate', 220)  # 语速
            engine.setProperty('volume', 0.35)  # 音量
            engine.say(content)
            engine.runAndWait()
            engine.stop()
        except:
            pass
    
    def _update_display(self):
        """更新显示"""
        use_template = self.image_processor.is_using_template_matching()
        self.ui_manager.update_display_with_algorithm(
            self.gun_lock,
            self.get_gun_name(int(self.player_gun)),
            self.player_posture,
            self.player_gun_config,
            use_template
        )
    
    def _save_player_gun_and_sound(self, gun_id, gun_pos):
        """保存武器到配置文件并播报
        
        Args:
            gun_id: 武器ID
            gun_pos: 武器位置
        """
        if self.player_gun != gun_id and gun_id != '':
            self.player_gun = gun_id
            self.current_gun[gun_pos] = gun_id  # 避免重复操作
            self.config_manager.save_config("gun", str(gun_id))
            self._update_display()
            # self._play_sound(self.get_gun_name(int(gun_id)))
    
    def handle_keyboard_action(self, key):
        """处理键盘动作
        
        Args:
            key: 按键
        """
        # 锁定武器栏
        if key == 4:
            self._lock_weapon_bar()
            return True
        
        # 临时关闭宏
        elif key == 0:
            self._close_weapon(key)
            return True
        
        # 切换匹配算法
        elif key == 8:
            self._toggle_algorithm()
            return True
        
        # 退出程序
        elif key == 9:
            self._exit_program()
            return True
        
        # 检测NumLock状态
        elif hasattr(key, 'name') and key.name == 'num_lock':
            self._change_weapon_config_state()
            return True
        
        # 对应1,2切换武器或者识别
        elif key == 1 or key == 2:
            if self.gun_lock == 0:
                self._detect_weapon(key)
            else:
                self._save_player_gun_and_sound(self.current_gun[key], key)
    
    def _lock_weapon_bar(self):
        """锁定/解锁武器栏"""
        self.gun_lock = 1 if self.gun_lock == 0 else 0
        self._update_display()
    
    def _change_weapon_config_state(self):
        """变更武器满配/裸配状态"""
        self.player_gun_config = not self.player_gun_config
        self._update_display()
    
    def _close_weapon(self, key):
        """关闭宏 只能在手持某武器之后按"""
        self.config_manager.save_config("gun", "0")
        self._play_sound("close")
    
    def _detect_weapon(self, gun_pos):
        """检测武器
        
        Args:
            gun_pos: 武器位置
        """
        success, gun_id = self.image_processor.detect_weapon(gun_pos)
        if success:
            self._save_player_gun_and_sound(gun_id, gun_pos)
            print(f"检测到武器: {self.get_gun_name(int(gun_id))}, 位置: {gun_pos}")
    
    def _toggle_algorithm(self):
        """切换匹配算法"""
        use_template = self.image_processor.toggle_matching_algorithm()
        if use_template:
            print("已切换到模板匹配算法")
        else:
            print("已切换到特征点匹配算法")
        self._update_display()
    
    def _exit_program(self):
        """退出程序"""
        print("收到F9退出指令，正在退出程序...")
        self.exit_flag = True
    
    def is_exit_requested(self):
        """检查是否请求退出
        
        Returns:
            bool: 是否请求退出
        """
        return self.exit_flag
    
    def get_gun_name(self, gun_index):
        """获取武器名称
        
        Args:
            gun_index: 武器索引
            
        Returns:
            str: 武器名称
        """
        return self.config_manager.get_gun_name(gun_index, self.gun_list_name)
    
    def check_posture(self):
        """检测姿势并更新状态"""
        new_posture = self.image_processor.detect_posture()
        
        if new_posture != self.player_posture:
            self.player_posture = new_posture
            self.config_manager.save_config("posture", str(self.player_posture))
            self._update_display()
   
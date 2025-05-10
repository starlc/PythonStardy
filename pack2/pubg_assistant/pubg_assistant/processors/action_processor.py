#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
动作处理器模块
负责处理游戏中的各种动作和操作
"""

import time
import ctypes
import sys
import threading
from pynput import keyboard
from enum import Enum, auto

from pubg_assistant.core.logging import get_logger
from pubg_assistant.core.exceptions import InputError

class PostureState(Enum):
    """姿势状态枚举"""
    STANDING = 1  # 站立
    CROUCHING = 2  # 蹲下
    PRONE = 3  # 趴下（暂未实现）

class WeaponLockState(Enum):
    """武器锁定状态枚举"""
    UNLOCKED = 0  # 未锁定
    LOCKED = 1  # 锁定

class WeaponConfigState(Enum):
    """武器配置状态枚举"""
    FULL_CONFIG = False  # 满配
    BARE_CONFIG = True  # 裸配

class ActionProcessor:
    """动作处理器类"""
    
    # 检测间隔
    POSTURE_CHECK_INTERVAL = 0.5  # 姿势检测间隔，秒
    
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
        self.logger = get_logger("action_processor")
        
        # 状态变量
        self.current_gun = {1: "", 2: ""}  # 当前的武器名
        self.player_posture = PostureState.STANDING  # 姿势状态，默认站立
        self.player_gun = 0  # 当前持有的武器ID
        self.gun_lock = WeaponLockState.UNLOCKED  # 武器锁定状态，默认未锁定
        self.player_gun_config = WeaponConfigState.BARE_CONFIG  # 枪械是否满配，默认裸配
        
        # 枪械名称列表
        self.gun_list_name = self.config_manager.load_gun_names()
        
        # 加载配置中的武器和姿势
        self._load_saved_state()
        
        # 检测NumLock状态
        self.player_gun_config = WeaponConfigState.FULL_CONFIG if self._is_numlock_on() else WeaponConfigState.BARE_CONFIG
        
        # 退出标志
        self.exit_flag = False
        
        # 状态锁
        self.state_lock = threading.RLock()
        
        # 上次检测时间
        self.last_posture_check_time = 0
        
        self.logger.info("动作处理器初始化完成")
    
    def _load_saved_state(self):
        """从配置加载保存的状态"""
        try:
            # 加载武器
            gun_id = self.config_manager.load_config("gun")
            if gun_id and gun_id.isdigit():
                self.player_gun = int(gun_id)
                self.logger.info(f"从配置加载武器: {self.get_gun_name(self.player_gun)}")
            
            # 加载姿势
            posture = self.config_manager.load_config("posture")
            if posture and posture.isdigit():
                self.player_posture = PostureState(int(posture)) if int(posture) in [1, 2, 3] else PostureState.STANDING
                self.logger.info(f"从配置加载姿势: {self.player_posture.name}")
        except Exception as e:
            self.logger.error(f"加载保存状态失败: {str(e)}")
    
    def _is_numlock_on(self):
        """检查NumLock状态
        
        Returns:
            bool: NumLock是否开启
        """
        try:
            hll_dll = ctypes.WinDLL("User32.dll")
            vk_numlock = 0x90
            return bool(hll_dll.GetKeyState(vk_numlock) & 1)
        except Exception as e:
            self.logger.error(f"检查NumLock状态失败: {str(e)}")
            return False
    
    def _is_caps_lock_on(self):
        """检查CapsLock状态
        
        Returns:
            bool: CapsLock是否开启
        """
        try:
            return bool(ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1)
        except Exception as e:
            self.logger.error(f"检查CapsLock状态失败: {str(e)}")
            return False
    
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
        except Exception as e:
            self.logger.error(f"播放语音失败: {str(e)}")
    
    def _update_display(self):
        """更新显示"""
        with self.state_lock:
            use_template = self.image_processor.is_using_template_matching()
            posture_value = self.player_posture.value
            gun_lock_value = self.gun_lock.value
            config_value = self.player_gun_config.value
            
            # 获取武器名称前进行类型安全处理
            gun_name = self.get_gun_name(self.player_gun)
            
            self.ui_manager.update_display_with_algorithm(
                gun_lock_value,
                gun_name,
                posture_value,
                config_value,
                use_template
            )
    
    def _save_player_gun_and_sound(self, gun_id, gun_pos):
        """保存武器到配置文件并播报
        
        Args:
            gun_id: 武器ID
            gun_pos: 武器位置
        """
        with self.state_lock:
            if self.player_gun != gun_id and gun_id != '':
                self.player_gun = gun_id
                self.current_gun[gun_pos] = gun_id  # 避免重复操作
                self.config_manager.save_config("gun", str(gun_id))
                self._update_display()
                
                # 播报武器名称
                gun_name = self.get_gun_name(int(gun_id))
                print(f"检测到武器: {gun_name}, 位置: {gun_pos}")  # 直接控制台反馈
                self.logger.info(f"武器设置为: {gun_name}")
                self.logger.info(f"检测到武器: {gun_name}, 位置: {gun_pos}")
                # self._play_sound(gun_name)
    
    def handle_keyboard_action(self, key):
        """处理键盘动作
        
        Args:
            key: 按键
            
        Returns:
            bool: 是否处理了按键
        """
        try:
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
                if self.gun_lock == WeaponLockState.UNLOCKED:
                    self._detect_weapon(key)
                else:
                    self._save_player_gun_and_sound(self.current_gun[key], key)
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"处理键盘动作失败: {str(e)}")
            return False
    
    def handle_mouse_action(self, action):
        """处理鼠标动作
        
        Args:
            action: 动作参数
            
        Returns:
            bool: 是否处理了动作
        """
        # 预留鼠标动作处理
        return False
    
    def _lock_weapon_bar(self):
        """锁定/解锁武器栏"""
        with self.state_lock:
            if self.gun_lock == WeaponLockState.UNLOCKED:
                self.gun_lock = WeaponLockState.LOCKED
                print("武器栏已锁定")  # 直接控制台反馈
            else:
                self.gun_lock = WeaponLockState.UNLOCKED
                print("武器栏已解锁")  # 直接控制台反馈
                
            self.logger.info(f"武器栏状态: {self.gun_lock.name}")
            self._update_display()
    
    def _change_weapon_config_state(self):
        """切换武器配置状态"""
        with self.state_lock:
            if self.player_gun_config == WeaponConfigState.FULL_CONFIG:
                self.player_gun_config = WeaponConfigState.BARE_CONFIG
                print("切换为裸配")  # 直接控制台反馈
            else:
                self.player_gun_config = WeaponConfigState.FULL_CONFIG
                print("切换为满配")  # 直接控制台反馈
                
            self.logger.info(f"武器配置状态: {self.player_gun_config.name}")
            self._update_display()
    
    def _close_weapon(self, key):
        """关闭宏"""
        with self.state_lock:
            self.config_manager.save_config("gun", "0")
            self.player_gun = 0
            self.logger.info("关闭武器宏")
            self._play_sound("close")
            self._update_display()
    
    def _detect_weapon(self, gun_pos):
        """检测武器
        
        Args:
            gun_pos: 武器位置
        """
        with self.state_lock:
            # 只有在未锁定状态下检测武器
            if self.gun_lock == WeaponLockState.LOCKED:
                return
                
            try:
                # 使用图像处理器检测武器
                gun_id, similarity = self.image_processor.detect_weapon(gun_pos)
                
                # 如果相似度超过阈值，保存武器信息
                if similarity >= 10 and gun_id:  # 使用较低的阈值
                    self._save_player_gun_and_sound(gun_id, gun_pos)
            except Exception as e:
                self.logger.error(f"武器检测处理失败: {str(e)}")
    
    def _toggle_algorithm(self):
        """切换匹配算法"""
        with self.state_lock:
            self.image_processor.toggle_matching_method()
            use_template = self.image_processor.is_using_template_matching()
            method_name = "模板匹配" if use_template else "特征匹配"
            print(f"切换为{method_name}算法")  # 直接控制台反馈
            self.logger.info(f"切换为{method_name}算法")
            self._update_display()
    
    def _exit_program(self):
        """退出程序"""
        with self.state_lock:
            print("准备退出程序...")  # 直接控制台反馈
            self.logger.info("收到退出指令，准备退出程序...")
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
        # 确保 gun_index 是整数
        try:
            gun_index_int = int(gun_index)
        except (ValueError, TypeError):
            return str(gun_index)  # 如果无法转换为整数，直接返回原始值的字符串形式
            
        return self.config_manager.get_gun_name(gun_index_int, self.gun_list_name)
    
    def check_posture(self):
        """检测并更新姿势状态
        
        Returns:
            bool: 姿势是否改变
        """
        # 限制检测频率
        current_time = time.time()
        if current_time - self.last_posture_check_time < self.POSTURE_CHECK_INTERVAL:
            return False
            
        self.last_posture_check_time = current_time
        
        try:
            # 检测姿势
            posture = self.image_processor.detect_posture()
            new_posture = PostureState(posture)
            
            with self.state_lock:
                # 判断姿势是否变化
                if new_posture != self.player_posture:
                    self.player_posture = new_posture
                    self.config_manager.save_config("posture", str(posture))
                    self._update_display()
                    
                    posture_name = "站立" if posture == 1 else "蹲下"
                    self.logger.info(f"姿势变更为: {posture_name}")
                    return True
                    
            return False
        except Exception as e:
            self.logger.error(f"检测姿势失败: {str(e)}")
            return False
   
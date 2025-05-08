#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器模块
负责管理配置文件和保存配置
"""

import os
import json
import threading
from typing import Dict, Any

class ConfigManager:
    """配置管理器类，负责管理和持久化配置"""
    
    def __init__(self, config_dir="D:\\pubg\\"):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.lock = threading.Lock()
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
    
    def save_config(self, title, content):
        """保存配置到文件
        
        Args:
            title: 配置项名称
            content: 配置项内容
        """
        with self.lock:
            file_path = os.path.join(self.config_dir, f"{title}.lua")
            field = title
            if title == "gun":
                field = "weaponNo"
            with open(file_path, "w+") as file:
                file.write(f"{field}={content}")
    
    def load_gun_dict(self, dict_path="../resources/dict/gun_dict.json"):
        """加载枪械字典
        
        Args:
            dict_path: 字典文件路径
            
        Returns:
            dict: 枪械字典
        """
        with self.lock:
            try:
                with open(dict_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载枪械字典失败: {e}")
                return {}
    
    def load_gun_names(self, names_path="../resources/dict/gun_arr.json"):
        """加载枪械名称列表
        
        Args:
            names_path: 名称文件路径
            
        Returns:
            list: 枪械名称列表
        """
        with self.lock:
            try:
                with open(names_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载枪械名称列表失败: {e}")
                return []
    
    def get_gun_config_name(self, gun_name, gun_dict=None):
        """获取枪械配置名称
        
        Args:
            gun_name: 枪械名称
            gun_dict: 枪械字典
            
        Returns:
            str: 枪械配置名称
        """
        if gun_dict and gun_name in gun_dict:
            return gun_dict[gun_name]
        return gun_name
    
    def get_gun_name(self, gun_index, gun_name_list=None):
        """根据索引获取枪械名称
        
        Args:
            gun_index: 枪械索引
            gun_name_list: 枪械名称列表
            
        Returns:
            str: 枪械名称
        """
        if not gun_name_list or gun_index <= 0 or gun_index > len(gun_name_list):
            return str(gun_index)
        return gun_name_list[gun_index-1]
    
    
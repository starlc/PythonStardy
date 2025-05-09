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
        
        # 计算资源目录的基础路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.resources_base = os.path.join(base_dir, "resources")
        self.dict_dir = os.path.join(self.resources_base, "dict")
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        # 确保dict目录存在
        os.makedirs(self.dict_dir, exist_ok=True)
    
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
    
    def load_gun_dict(self, dict_path=None):
        """加载枪械字典
        
        Args:
            dict_path: 字典文件路径
            
        Returns:
            dict: 枪械字典
        """
        if dict_path is None:
            dict_path = os.path.join(self.dict_dir, "gun_dict.json")
            
        with self.lock:
            try:
                with open(dict_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载枪械字典失败: {e}")
                # 如果文件不存在，创建一个空的默认字典文件
                if isinstance(e, FileNotFoundError):
                    try:
                        # 确保目录存在
                        os.makedirs(os.path.dirname(dict_path), exist_ok=True)
                        with open(dict_path, 'w') as f:
                            json.dump({}, f)
                        print(f"已创建默认枪械字典文件: {dict_path}")
                    except Exception as write_err:
                        print(f"创建默认枪械字典文件失败: {write_err}")
                return {}
    
    def load_gun_names(self, names_path=None):
        """加载枪械名称列表
        
        Args:
            names_path: 名称文件路径
            
        Returns:
            list: 枪械名称列表
        """
        if names_path is None:
            names_path = os.path.join(self.dict_dir, "gun_arr.json")
            
        with self.lock:
            try:
                with open(names_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载枪械名称列表失败: {e}")
                # 如果文件不存在，创建一个包含默认武器名称的文件
                if isinstance(e, FileNotFoundError):
                    try:
                        # 确保目录存在
                        os.makedirs(os.path.dirname(names_path), exist_ok=True)
                        # 默认武器名称列表，可以根据需要修改
                        default_gun_names = [
                            "空位", "M416", "AKM", "SCAR-L", "M16A4", "G36C", "QBZ",
                            "GROZA", "AUG", "BERYL", "MK47", "UMP45", "VECTOR",
                            "PP-19", "THOMPSON", "MP5K", "UZI", "MINI14", "SKS",
                            "SLR", "QBU", "MK12", "MK14", "KAR98K", "M24", "AWM",
                            "WIN94", "VSS", "M249", "DP-28", "MG3", "未知"
                        ]
                        with open(names_path, 'w') as f:
                            json.dump(default_gun_names, f, ensure_ascii=False)
                        print(f"已创建默认枪械名称列表文件: {names_path}")
                        return default_gun_names
                    except Exception as write_err:
                        print(f"创建默认枪械名称列表文件失败: {write_err}")
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
    
    
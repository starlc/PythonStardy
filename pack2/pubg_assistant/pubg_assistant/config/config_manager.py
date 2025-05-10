#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器模块
负责管理配置文件和保存配置
"""

import os
import json
import threading
from typing import Dict, Any, List, Optional, Union

class ConfigManager:
    """配置管理器类，负责管理和持久化配置"""
    
    def __init__(self, config_dir: str = "D:\\pubg\\"):
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
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.dict_dir, exist_ok=True)
    
    def save_config(self, title: str, content: str) -> None:
        """保存配置到文件
        
        Args:
            title: 配置项名称
            content: 配置项内容
        """
        with self.lock:
            file_path = os.path.join(self.config_dir, f"{title}.lua")
            field = "weaponNo" if title == "gun" else title
            with open(file_path, "w+") as file:
                file.write(f"{field}={content}")
    
    def load_config(self, title: str, default: str = "") -> str:
        """从文件加载配置
        
        Args:
            title: 配置项名称
            default: 默认值
            
        Returns:
            str: 配置项内容
        """
        with self.lock:
            file_path = os.path.join(self.config_dir, f"{title}.lua")
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    # 解析配置内容
                    if "=" in content:
                        return content.split("=", 1)[1].strip()
                    return content.strip()
            except (FileNotFoundError, IOError):
                return default
    
    def load_gun_names(self, names_path: Optional[str] = None) -> List[str]:
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
                # 如果文件不存在，创建默认名称列表
                if isinstance(e, FileNotFoundError):
                    return self._create_default_gun_names(names_path)
                return []
    
    def _create_default_gun_names(self, names_path: str) -> List[str]:
        """创建默认枪械名称列表文件
        
        Args:
            names_path: 名称文件路径
            
        Returns:
            list: 默认枪械名称列表
        """
        # 创建一个简单的默认列表
        default_names = ["未知武器"]
        
        try:
            os.makedirs(os.path.dirname(names_path), exist_ok=True)
            with open(names_path, 'w') as f:
                json.dump(default_names, f, ensure_ascii=False)
            print(f"已创建默认枪械名称列表文件: {names_path}")
            return default_names
        except Exception as write_err:
            print(f"创建默认枪械名称列表文件失败: {write_err}")
            return []
    
    def get_gun_name(self, gun_index: int, gun_name_list: Optional[List[str]] = None) -> str:
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
    
    def save_gun_names(self, gun_names: List[str], names_path: Optional[str] = None) -> bool:
        """保存枪械名称列表
        
        Args:
            gun_names: 枪械名称列表
            names_path: 名称文件路径
            
        Returns:
            bool: 是否保存成功
        """
        if names_path is None:
            names_path = os.path.join(self.dict_dir, "gun_arr.json")
            
        with self.lock:
            try:
                os.makedirs(os.path.dirname(names_path), exist_ok=True)
                with open(names_path, 'w') as f:
                    json.dump(gun_names, f, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"保存枪械名称列表失败: {e}")
                return False
    
    
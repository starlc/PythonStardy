#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志模块
提供程序中使用的日志功能
"""

import os
import logging
import sys
from datetime import datetime

# 日志级别字典
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 默认日志格式
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# 简洁日志格式（用于控制台）
SIMPLE_LOG_FORMAT = '%(message)s'

# 日志实例缓存
_loggers = {}

def get_logger(name='pubg_assistant', level='INFO', log_file=None, file_level=None, console=True, console_level='WARNING'):
    """获取日志器实例
    
    Args:
        name: 日志器名称
        level: 日志级别
        log_file: 日志文件路径，默认为None表示不写文件
        file_level: 文件日志级别，默认与level相同
        console: 是否输出到控制台
        console_level: 控制台日志级别，默认为WARNING，只输出警告及以上级别
        
    Returns:
        logging.Logger: 日志器实例
    """
    global _loggers
    
    if name in _loggers:
        return _loggers[name]
    
    # 创建新的日志器实例
    logger = logging.getLogger(name)
    
    # 设置默认级别
    level = LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 防止日志重复输出
    if not logger.handlers:
        # 添加控制台处理器（仅显示重要信息）
        if console:
            console_level = LOG_LEVELS.get(console_level.upper(), logging.WARNING)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(console_level)  # 仅显示警告以上级别
            # 使用简洁格式
            console_handler.setFormatter(logging.Formatter(SIMPLE_LOG_FORMAT))
            logger.addHandler(console_handler)
        
        # 添加文件处理器（记录详细日志）
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_level = LOG_LEVELS.get(file_level.upper(), level) if file_level else level
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(file_level)
            file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
            logger.addHandler(file_handler)
    
    # 缓存日志器
    _loggers[name] = logger
    return logger

def setup_default_logger(console_level='WARNING'):
    """设置默认日志器，同时输出到控制台和文件
    
    Args:
        console_level: 控制台日志级别，默认为WARNING，只输出警告及以上级别
    
    Returns:
        logging.Logger: 默认日志器实例
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logs_dir = os.path.join(base_dir, "logs")
    
    # 创建日志文件夹
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # 创建日志文件名
    now = datetime.now()
    log_filename = f"pubg_assistant_{now.strftime('%Y%m%d')}.log"
    log_file = os.path.join(logs_dir, log_filename)
    
    # 获取日志器，将日志详细信息写入文件，控制台只显示警告及错误
    return get_logger(
        name='pubg_assistant', 
        level='INFO', 
        log_file=log_file, 
        console_level=console_level
    ) 
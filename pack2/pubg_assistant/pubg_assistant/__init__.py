#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUBG Assistant 包
一个辅助 PUBG 游戏的工具，提供了武器识别、姿势监控等功能。
"""

from pubg_assistant.config.resolution_config import ResolutionConfig
from pubg_assistant.config.config_manager import ConfigManager
from pubg_assistant.managers.ui_manager import UIManager, CharacterDisplayApp
from pubg_assistant.managers.input_manager import InputManager, Action
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.processors.action_processor import ActionProcessor
from pubg_assistant.monitors.posture_monitor import PostureMonitor
from pubg_assistant.core.exceptions import ConfigurationError, ResourceError
from pubg_assistant.core.logging import get_logger

__version__ = '1.1.0' 
__author__ = 'PUBG Assistant Team'
__all__ = [
    'ResolutionConfig',
    'ConfigManager',
    'UIManager',
    'CharacterDisplayApp',
    'InputManager',
    'Action',
    'ImageProcessor',
    'ActionProcessor',
    'PostureMonitor',
    'get_logger'
] 
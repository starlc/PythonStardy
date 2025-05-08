#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUBG Assistant 包
"""

from pubg_assistant.config.resolution_config import ResolutionConfig
from pubg_assistant.config.config_manager import ConfigManager
from pubg_assistant.managers.ui_manager import UIManager, CharacterDisplayApp
from pubg_assistant.managers.input_manager import InputManager, Action
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.processors.action_processor import ActionProcessor
from pubg_assistant.monitors.posture_monitor import PostureMonitor

__version__ = '1.0.0' 
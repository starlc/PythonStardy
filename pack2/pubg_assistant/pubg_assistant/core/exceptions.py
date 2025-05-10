#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
异常处理模块
定义程序中使用的自定义异常类
"""

class PubgAssistantError(Exception):
    """PUBG Assistant 基础异常类"""
    pass

class ConfigurationError(PubgAssistantError):
    """配置相关错误"""
    pass

class ResourceError(PubgAssistantError):
    """资源相关错误"""
    pass

class InputError(PubgAssistantError):
    """输入相关错误"""
    pass

class ImageProcessingError(PubgAssistantError):
    """图像处理相关错误"""
    pass

class UIError(PubgAssistantError):
    """UI相关错误"""
    pass 
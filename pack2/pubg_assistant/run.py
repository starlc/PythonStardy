#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUBG Assistant 启动脚本
"""

import os
import sys
import argparse
from pubg_assistant.main import main

if __name__ == "__main__":
    # 添加当前目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        
    # 启动主程序
    main() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图像处理器模块
负责截图和图像识别
"""

import cv2 as cv
import numpy as np
import os
import time
import threading
from PIL import Image
from datetime import datetime
from mss import mss

class ImageProcessor:
    """图像处理器类，负责截图和图像识别处理"""
    
    # 常量定义
    SIMILARITY_THRESHOLD = 40  # 武器识别相似度阈值
    LOW_SIMILARITY_THRESHOLD = 10  # 低相似度阈值
    MATCH_DISTANCE_THRESHOLD = 60  # 特征点匹配距离阈值
    WHITE_THRESHOLD = 190  # 白色识别阈值
    MAX_MATCHES_TO_SORT = 100  # 排序的最大匹配点数
    
    def __init__(self, resolution_config):
        """初始化图像处理器
        
        Args:
            resolution_config: 分辨率配置
        """
        # 基础属性
        self.resolution_config = resolution_config
        self.global_seq = 1
        self.gun_img_dict = {}
        self.use_template_matching = False
        
        # 路径设置
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.resources_base = os.path.join(base_dir, "resources")
        self.temp_dir = os.path.join(self.resources_base, "temp2313")
        self.posture_temp_dir = os.path.join(self.resources_base, "posturetemp")
        
        # 图像处理器初始化
        self.orb = cv.ORB_create()
        self.bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        
        # 线程本地存储
        self.thread_local = threading.local()
        
        # 初始化武器图像库
        self._initialize_gun_images()
    
    #---------------------------
    # 初始化和资源管理方法
    #---------------------------
    
    def _initialize_gun_images(self):
        """初始化武器图像字典，预先加载和计算特征"""
        resources_dir = self.resolution_config.get_resources_dir()
        for file_name in os.listdir(resources_dir):
            if os.path.splitext(file_name)[1] == '.png':
                gun_id = os.path.splitext(file_name)[0]
                gun_file = os.path.join(resources_dir, file_name)
                img = cv.imread(gun_file, cv.IMREAD_GRAYSCALE)
                self.gun_img_dict[gun_id] = {
                    'image': img,
                    'kp_des': self._compute_features(img)
                }
    
    def _compute_features(self, img):
        """计算图像特征点和描述符
        
        Args:
            img: 图像
            
        Returns:
            tuple: (特征点, 描述符)
        """
        kp, des = self.orb.detectAndCompute(img, None)
        return (kp, des)
    
    def _get_sct(self):
        """获取当前线程的mss实例，确保线程安全
        
        Returns:
            mss实例
        """
        if not hasattr(self.thread_local, 'sct'):
            self.thread_local.sct = mss()
        return self.thread_local.sct
    
    def _get_sequence(self):
        """获取序列号，用于临时文件命名
        
        Returns:
            str: 时间戳加序列号
        """
        now = datetime.now()
        str_date = now.strftime('%Y%m%d%H%M%S')
        str_seq = f"{self.global_seq:04d}"
        self.global_seq = self.global_seq + 1
        return f"{str_date}{str_seq}"
    
    #---------------------------
    # 截图和图像处理基础方法
    #---------------------------
    
    def screenshot(self, box):
        """截取屏幕指定区域
        
        Args:
            box: 截图区域 (left, top, width, height)
            
        Returns:
            shot: 截图对象
        """
        sct = self._get_sct()
        return sct.grab(box)
    
    def save_temp_pic(self, img, path, is_save):
        """保存临时图片，用于调试
        
        Args:
            img: 图片对象
            path: 保存路径
            is_save: 是否保存
            
        Returns:
            bool: 是否成功
        """
        if not is_save:
            return True
            
        img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        save_path = os.path.abspath(path + self._get_sequence())
        img.save(save_path + '.png', format='PNG')
        return True
    
    def extract_gun(self, image):
        """提取图片中的枪，预处理图片增强对比度
        
        Args:
            image: 图片数组
            
        Returns:
            image: 处理后的图片数组
        """
        image[image <= 200] = 0
        return image
    
    def get_rgb(self, box):
        """获取指定区域的RGB值，判断是否为白色
        
        Args:
            box: 截图区域 (left, top, width, height)
            
        Returns:
            bool: 是否为白色
        """
        img = self.screenshot(box)
        save_dir = os.path.join(self.posture_temp_dir, '')
        self.save_temp_pic(img, save_dir, False)
        r, g, b = img.pixel(3, 3)
        
        return r > self.WHITE_THRESHOLD and g > self.WHITE_THRESHOLD and b > self.WHITE_THRESHOLD
    
    #---------------------------
    # 图像匹配算法控制方法
    #---------------------------
    
    def toggle_matching_algorithm(self):
        """切换匹配算法，在特征点匹配和模板匹配间切换
        
        Returns:
            bool: 当前是否使用模板匹配算法
        """
        self.use_template_matching = not self.use_template_matching
        return self.use_template_matching
    
    def is_using_template_matching(self):
        """获取当前使用的匹配算法类型
        
        Returns:
            bool: 当前是否使用模板匹配算法
        """
        return self.use_template_matching
    
    #---------------------------
    # 图像相似度比较方法
    #---------------------------
    
    def template_similarity(self, template, target):
        """使用模板匹配计算图像相似度
        
        Args:
            template: 模板图像
            target: 目标图像
            
        Returns:
            float: 相似度得分
        """
        # 确保两个图像是灰度图
        if len(template.shape) > 2:
            template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        if len(target.shape) > 2:
            target = cv.cvtColor(target, cv.COLOR_BGR2GRAY)
            
        # 调整模板大小以匹配目标图像
        if template.shape != target.shape:
            template = cv.resize(template, (target.shape[1], target.shape[0]))
            
        try:
            # 使用更快的TM_CCORR_NORMED模板匹配方法
            result = cv.matchTemplate(target, template, cv.TM_CCORR_NORMED)
            _, max_val, _, _ = cv.minMaxLoc(result)
            
            # 转换为0-100的相似度
            similarity = max_val * 100
            
            # 根据相似度计算返回点数
            if similarity >= 60:
                return int(similarity / 2)
            elif similarity >= 40:
                return int(similarity / 3)
            else:
                return 0
        except Exception:
            return 0
    
    def image_similarity_opencv(self, gun_data, img2):
        """计算图片相似度，支持特征点匹配和模板匹配两种方式
        
        Args:
            gun_data: 武器图像数据（字典或图像）
            img2: 目标图像
            
        Returns:
            int: 相似度分数
        """
        # 使用模板匹配
        if self.use_template_matching:
            template = gun_data['image'] if isinstance(gun_data, dict) else gun_data
            return self.template_similarity(template, img2)
        
        # 使用特征点匹配
        if isinstance(gun_data, dict):
            kp1, des1 = gun_data['kp_des']
        else:
            kp1, des1 = self.orb.detectAndCompute(gun_data, None)
        
        # 确保目标图像是灰度图
        if len(img2.shape) > 2:
            img2 = cv.cvtColor(img2, cv.COLOR_BGRA2GRAY)
        
        kp2, des2 = self.orb.detectAndCompute(img2, None)
        
        if des1 is None or des2 is None:
            return 0
        
        # 执行特征点匹配
        matches = self.bf.match(des1, des2)
        
        # 只对部分匹配点排序，提高性能
        if len(matches) > self.MAX_MATCHES_TO_SORT:
            matches = sorted(matches, key=lambda x: x.distance)[:self.MAX_MATCHES_TO_SORT]
        else:
            matches = sorted(matches, key=lambda x: x.distance)
        
        # 计算好的匹配点数量
        good_matches = sum(1 for m in matches if m.distance <= self.MATCH_DISTANCE_THRESHOLD)
        return good_matches
    
    #---------------------------
    # 武器检测方法
    #---------------------------
    
    def detect_weapon(self, gun_pos):
        """检测武器，识别武器ID
        
        Args:
            gun_pos: 武器位置，1或2
            
        Returns:
            tuple: (是否检测到武器, 武器ID)
        """
        # 获取武器区域
        weapon_area = self.resolution_config.get_weapon_area(gun_pos)
        box = (weapon_area['left'], weapon_area['top'], 
               weapon_area['left'] + weapon_area['width'], 
               weapon_area['top'] + weapon_area['height'])
        
        # 常用武器ID列表，优先检测
        first_check_gun_ids = ["2", "4", "7", "9", "10", "15", "19", "20", "22", "23"]
        
        # 等待游戏UI稳定
        time.sleep(0.2)
        
        # 尝试识别两次
        for attempt in range(2):
            # 截图并转换为numpy数组
            img = self.screenshot(box)
            arr = np.array(img.pixels, dtype=np.uint8)
            
            # 保存临时图片（调试用）
            save_dir = os.path.join(self.temp_dir, '')
            self.save_temp_pic(img, save_dir, False)
            
            # 相似度比较结果记录
            similarity_dict = {}
            max_similarity = 0
            max_gun_id = ""
            
            # 先检查常用武器
            for gun_id in first_check_gun_ids:
                if gun_id in self.gun_img_dict:
                    result = self.image_similarity_opencv(self.gun_img_dict[gun_id], arr)
                    similarity_dict[gun_id] = result
                    
                    # 高相似度直接返回结果
                    if result >= self.SIMILARITY_THRESHOLD:
                        return True, gun_id
                    
                    # 记录最高相似度
                    if result > max_similarity:
                        max_similarity = result
                        max_gun_id = gun_id
            
            # 检查其他武器
            for gun_id in self.gun_img_dict:
                if gun_id not in first_check_gun_ids:
                    result = self.image_similarity_opencv(self.gun_img_dict[gun_id], arr)
                    similarity_dict[gun_id] = result
                    
                    # 高相似度直接返回结果
                    if result >= self.SIMILARITY_THRESHOLD:
                        return True, gun_id
                    
                    # 记录最高相似度
                    if result > max_similarity:
                        max_similarity = result
                        max_gun_id = gun_id
            
            # 如果有低相似度匹配也返回
            if max_similarity >= self.LOW_SIMILARITY_THRESHOLD:
                return True, max_gun_id
            
            # 第一次尝试未成功，等待后重试
            if attempt == 0:
                time.sleep(0.5)
        
        # 两次识别都失败，返回未识别
        return False, ""
    
    #---------------------------
    # 姿势检测方法
    #---------------------------
    
    def detect_posture(self):
        """检测玩家姿势（站立或蹲下）
        
        Returns:
            int: 姿势 1为站立 99为蹲下
        """
        # 获取姿势检测区域
        area1 = self.resolution_config.get_posture_area(1)
        box1 = (area1['left'], area1['top'], 
                area1['left'] + area1['width'], 
                area1['top'] + area1['height'])
        
        area2 = self.resolution_config.get_posture_area(2)
        box2 = (area2['left'], area2['top'], 
                area2['left'] + area2['width'], 
                area2['top'] + area2['height'])
        
        # 短暂延迟确保UI稳定
        time.sleep(0.03)
        
        # 检测两个点的颜色
        result1 = self.get_rgb(box1)
        result2 = self.get_rgb(box2)
        
        # 两个点都是白色，则为站立
        return 1 if result1 and result2 else 99
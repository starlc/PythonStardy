#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图像处理器模块
负责截图和图像识别
"""

import cv2 as cv
import numpy as np
import os
import json
from PIL import Image
from datetime import datetime
from mss import mss
import threading

class ImageProcessor:
    """图像处理器类"""
    
    def __init__(self, resolution_config):
        """初始化图像处理器
        
        Args:
            resolution_config: 分辨率配置
        """
        self.resolution_config = resolution_config
        self.global_seq = 1
        self.gun_img_dict = {}
        self.use_template_matching = False  # 是否使用模板匹配算法
        
        # 计算资源目录的基础路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.resources_base = os.path.join(base_dir, "resources")
        
        # 临时目录路径
        self.temp_dir = os.path.join(self.resources_base, "temp2313")
        self.posture_temp_dir = os.path.join(self.resources_base, "posturetemp")
        
        # 优化2: 预先创建ORB检测器，避免重复创建
        self.orb = cv.ORB_create()
        self.bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        
        # 线程本地存储，每个线程使用自己的mss实例
        self.thread_local = threading.local()
        
        # 初始化武器图像字典
        self._initialize_gun_images()
    
    def _initialize_gun_images(self):
        """初始化武器图像字典"""
        resources_dir = self.resolution_config.get_resources_dir()
        for file_name in os.listdir(resources_dir):
            if os.path.splitext(file_name)[1] == '.png':
                gun_id = os.path.splitext(file_name)[0]
                gun_file = os.path.join(resources_dir, file_name)
                # 优化3: 提前计算特征点和描述符，避免每次检测时计算
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
        """获取当前线程的mss实例
        
        Returns:
            mss实例
        """
        if not hasattr(self.thread_local, 'sct'):
            self.thread_local.sct = mss()
        return self.thread_local.sct
    
    def screenshot(self, box):
        """截图
        
        Args:
            box: 截图区域 (left, top, width, height)
            
        Returns:
            shot: 截图对象
        """
        # 使用线程本地的mss实例
        sct = self._get_sct()
        shot = sct.grab(box)
        return shot
    
    def save_temp_pic(self, img, path, is_save):
        """保存临时图片
        
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
    
    def _get_sequence(self):
        """获取序列号
        
        Returns:
            str: 序列号
        """
        now = datetime.now()
        str_date = now.strftime('%Y%m%d%H%M%S')
        str_seq = f"{self.global_seq:04d}"
        self.global_seq = self.global_seq + 1
        return f"{str_date}{str_seq}"
    
    def extract_gun(self, image):
        """提取图片中的枪(预处理图片)
        
        Args:
            image: 图片数组
            
        Returns:
            image: 处理后的图片数组
        """
        image[image <= 200] = 0
        return image
    
    def toggle_matching_algorithm(self):
        """切换匹配算法
        
        Returns:
            bool: 当前是否使用模板匹配算法
        """
        self.use_template_matching = not self.use_template_matching
        return self.use_template_matching
    
    def is_using_template_matching(self):
        """获取当前使用的匹配算法
        
        Returns:
            bool: 当前是否使用模板匹配算法
        """
        return self.use_template_matching
    
    def template_similarity(self, template, target):
        """使用模板匹配计算图像相似度
        
        Args:
            template: 模板图像
            target: 目标图像
            
        Returns:
            float: 相似度得分（百分比）
        """
        # 确保两个图像是灰度图
        if len(template.shape) > 2:
            template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        if len(target.shape) > 2:
            target = cv.cvtColor(target, cv.COLOR_BGR2GRAY)
            
        # 调整模板大小以匹配目标图像
        if template.shape != target.shape:
            template = cv.resize(template, (target.shape[1], target.shape[0]))
            
        # 使用OpenCV的模板匹配
        try:
            # 优化5: 对于模板匹配，可以使用TM_CCORR_NORMED，它在某些情况下比TM_CCOEFF_NORMED更快
            result = cv.matchTemplate(target, template, cv.TM_CCORR_NORMED)
            _, max_val, _, _ = cv.minMaxLoc(result)
            # 转换为0-100的相似度
            similarity = max_val * 100
            # 根据相似度计算接近于ORB特征点匹配的点数
            # 40分以上才被认为有效，相当于特征点匹配的40个点
            if similarity >= 60:
                points = int(similarity / 2)
            elif similarity >= 40:
                points = int(similarity / 3)
            else:
                points = 0
                
            return points
        except Exception:
            return 0
    
    def image_similarity_opencv(self, gun_data, img2):
        """图片相似度比较
        
        Args:
            gun_data: 武器图像数据（字典或图像）
            img2: 目标图像
            
        Returns:
            int: 相似度
        """
        # 如果启用了模板匹配，则使用模板匹配算法
        if self.use_template_matching:
            template = gun_data['image'] if isinstance(gun_data, dict) else gun_data
            return self.template_similarity(template, img2)
        
        # 优化6: 使用预计算的特征点和描述符
        if isinstance(gun_data, dict):
            kp1, des1 = gun_data['kp_des']
        else:
            kp1, des1 = self.orb.detectAndCompute(gun_data, None)
        
        # 优化7: 直接将截图转换为灰度图，避免多次转换
        if len(img2.shape) > 2:
            img2 = cv.cvtColor(img2, cv.COLOR_BGRA2GRAY)
        
        kp2, des2 = self.orb.detectAndCompute(img2, None)
        
        if des1 is None or des2 is None:
            return 0
            
        matches = self.bf.match(des1, des2)
        
        # 优化8: 只对前100个匹配进行排序，以加快速度
        if len(matches) > 100:
            matches = sorted(matches, key=lambda x: x.distance)[:100]
        else:
            matches = sorted(matches, key=lambda x: x.distance)
        
        good_matches = 0
        for m in matches:
            if m.distance <= 60:
                good_matches = good_matches + 1
                
        return good_matches
    
    def detect_weapon(self, gun_pos):
        """检测武器
        
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
        
        n = 0
        time_to_sleep = 0.2  # 优化9: 减少初始等待时间
        import time
        time.sleep(time_to_sleep)
        
        while True:
            # 截图
            img = self.screenshot(box)
            # 优化10: 直接将PIL图像转换为numpy数组，避免多次转换
            arr = np.array(img.pixels, dtype=np.uint8)
            
            # 保存临时图片
            # 使用绝对路径
            save_dir = os.path.join(self.temp_dir, '')
            self.save_temp_pic(img, save_dir, False)
            
            # 武器相似度比较
            similarity_dict = {}
            max_similarity = 0
            max_gun_id = ""
            
            # 优化11: 尝试对部分武器进行相似度计算，避免对所有武器进行计算
            first_check_gun_ids = ["2", "4", "7","9", "10", "15", "19", "20", "22", "23"]  # 常用武器ID，根据实际情况调整
            
            # 先检查常用武器
            for gun_id in first_check_gun_ids:
                if gun_id in self.gun_img_dict:
                    result = self.image_similarity_opencv(self.gun_img_dict[gun_id], arr)
                    similarity_dict[gun_id] = result
                    
                    if result >= 40:
                        # 如果相似度大于阈值，返回检测到的武器
                        return True, gun_id
                    
                    if result > max_similarity:
                        max_similarity = result
                        max_gun_id = gun_id
            
            # 如果没有找到常用武器，检查其他武器
            for gun_id in self.gun_img_dict:
                if gun_id not in first_check_gun_ids:
                    result = self.image_similarity_opencv(self.gun_img_dict[gun_id], arr)
                    similarity_dict[gun_id] = result
                    
                    if result >= 40:
                        # 如果相似度大于阈值，返回检测到的武器
                        return True, gun_id
                    
                    if result > max_similarity:
                        max_similarity = result
                        max_gun_id = gun_id
            
            # 如果最大相似度大于10，也认为检测到武器
            if max_similarity >= 10:
                return True, max_gun_id
                
            n = n + 1
            if n >= 2:  # 如果2次还没有识别出来，退出循环
                break
                
            time.sleep(0.5)  # 优化12: 减少重试等待时间
            
        return False, ""
    
    def get_rgb(self, box):
        """获取RGB值
        
        Args:
            box: 截图区域 (left, top, width, height)
            
        Returns:
            bool: 是否为白色
        """
        img = self.screenshot(box)
        # 使用绝对路径
        save_dir = os.path.join(self.posture_temp_dir, '')
        self.save_temp_pic(img, save_dir, False)
        r, g, b = img.pixel(3, 3)
        
        if r > 190 and g > 190 and b > 190:
            return True
        return False
    
    def detect_posture(self):
        """检测姿势
        
        Returns:
            int: 姿势 1为站立 99为蹲下
        """
        import time
        
        # 获取姿势检测区域1
        area1 = self.resolution_config.get_posture_area(1)
        box1 = (area1['left'], area1['top'], 
                area1['left'] + area1['width'], 
                area1['top'] + area1['height'])
        
        # 获取姿势检测区域2
        area2 = self.resolution_config.get_posture_area(2)
        box2 = (area2['left'], area2['top'], 
                area2['left'] + area2['width'], 
                area2['top'] + area2['height'])
        
        # 检测点1
        time.sleep(0.03)  # 优化13: 减少等待时间
        result1 = self.get_rgb(box1)
        
        # 检测点2
        result2 = self.get_rgb(box2)
        
        if result1 and result2:
            return 1  # 站立
        else:
            return 99  # 蹲下
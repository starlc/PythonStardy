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
from functools import lru_cache
import concurrent.futures

from pubg_assistant.core.exceptions import ImageProcessingError
from pubg_assistant.core.logging import get_logger

class ImageProcessor:
    """图像处理器类，负责截图和图像识别处理"""
    
    # 常量定义
    SIMILARITY_THRESHOLD = 40  # 武器识别相似度阈值
    LOW_SIMILARITY_THRESHOLD = 10  # 低相似度阈值
    MATCH_DISTANCE_THRESHOLD = 60  # 特征点匹配距离阈值
    WHITE_THRESHOLD = 190  # 白色识别阈值
    MAX_MATCHES_TO_SORT = 100  # 排序的最大匹配点数
    CACHE_SIZE = 128  # 缓存大小
    MAX_WORKERS = 4  # 最大线程数
    
    def __init__(self, resolution_config, save_temp_images=False):
        """初始化图像处理器
        
        Args:
            resolution_config: 分辨率配置
            save_temp_images: 是否保存临时图片，默认False
        """
        # 基础属性
        self.resolution_config = resolution_config
        self.global_seq = 1
        self.gun_img_dict = {}
        self.use_template_matching = True
        self.save_temp_images = save_temp_images  # 控制是否保存临时图片
        self.logger = get_logger("image_processor")
        
        # 路径设置
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.resources_base = os.path.join(base_dir, "resources")
        self.temp_dir = os.path.join(self.resources_base, "temp2313")
        self.posture_temp_dir = os.path.join(self.resources_base, "posturetemp")
        
        # 确保临时目录存在
        if self.save_temp_images:
            for dir_path in [self.temp_dir, self.posture_temp_dir]:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
        
        # 图像处理器初始化
        self.orb = cv.ORB_create(nfeatures=500)  # 增加特征点数量
        self.bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        
        # 线程本地存储
        self.thread_local = threading.local()
        
        # 线程池
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        
        # 初始化武器图像库
        self._initialize_gun_images()
        
        self.logger.info("图像处理器初始化完成")
    
    #---------------------------
    # 初始化和资源管理方法
    #---------------------------
    
    def _initialize_gun_images(self):
        """初始化武器图像字典，预先加载和计算特征"""
        resources_dir = self.resolution_config.get_resources_dir()
        
        if not os.path.exists(resources_dir):
            self.logger.error(f"资源目录不存在: {resources_dir}")
            raise ImageProcessingError(f"资源目录不存在: {resources_dir}")
            
        image_files = [f for f in os.listdir(resources_dir) if f.endswith('.png')]
        
        if not image_files:
            self.logger.error(f"资源目录中没有找到图像文件: {resources_dir}")
            raise ImageProcessingError(f"资源目录中没有找到图像文件: {resources_dir}")
        
        # 使用并行加载提高性能
        future_to_gun = {}
        for file_name in image_files:
            gun_id = os.path.splitext(file_name)[0]
            gun_file = os.path.join(resources_dir, file_name)
            future = self.executor.submit(self._load_gun_image, gun_id, gun_file)
            future_to_gun[future] = gun_id
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_gun):
            gun_id = future_to_gun[future]
            try:
                gun_data = future.result()
                self.gun_img_dict[gun_id] = gun_data
            except Exception as e:
                self.logger.error(f"加载武器图像失败 {gun_id}: {str(e)}")
        
        self.logger.info(f"已加载 {len(self.gun_img_dict)} 个武器图像模板")
    
    def _load_gun_image(self, gun_id, gun_file):
        """加载武器图像并计算特征
        
        Args:
            gun_id: 武器ID
            gun_file: 武器图像文件路径
            
        Returns:
            dict: 包含图像和特征的字典
        """
        try:
            img = cv.imread(gun_file, cv.IMREAD_GRAYSCALE)
            if img is None:
                raise ImageProcessingError(f"无法读取图像文件: {gun_file}")
            
            # 预处理图像提高对比度
            img = self._preprocess_image(img)
            
            # 计算特征点和描述符
            kp, des = self._compute_features(img)
            
            return {
                'image': img,
                'kp_des': (kp, des)
            }
        except Exception as e:
            self.logger.error(f"加载武器图像失败 {gun_id}: {str(e)}")
            raise
    
    def _preprocess_image(self, img):
        """预处理图像，提高对比度
        
        Args:
            img: 输入图像
            
        Returns:
            处理后的图像
        """
        # 应用自适应直方图均衡化提高对比度
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)
    
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
        self.global_seq = (self.global_seq + 1) % 10000  # 防止无限增长
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
        try:
            sct = self._get_sct()
            return sct.grab(box)
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
            raise ImageProcessingError(f"截图失败: {str(e)}")
    
    def save_temp_pic(self, img, path, is_save):
        """保存临时图片，用于调试
        
        Args:
            img: 图片对象（可能是mss截图或numpy数组）
            path: 保存路径
            is_save: 是否保存
            
        Returns:
            bool: 是否成功
        """
        if not is_save:
            return True
            
        try:
            # 生成唯一的文件名
            save_path = os.path.abspath(path)
            if not save_path.endswith('.png'):
                save_path = save_path + self._get_sequence() + '.png'
                
            # 根据输入图像类型进行不同处理
            if isinstance(img, np.ndarray):
                # 如果是numpy数组，直接保存
                cv.imwrite(save_path, img)
            elif hasattr(img, 'bgra'):
                # 如果是mss截图，先转换为PIL图像
                pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
                pil_img.save(save_path, format='PNG')
            else:
                # 其他情况尝试直接保存
                cv.imwrite(save_path, np.array(img))
                
            return True
        except Exception as e:
            # 不再记录错误日志，避免过多日志输出
            return False
    
    def extract_gun(self, image):
        """提取图片中的枪，预处理图片增强对比度
        
        Args:
            image: 图片数组
            
        Returns:
            image: 处理后的图片数组
        """
        # 应用更高级的图像处理
        # 1. 二值化处理，突出武器轮廓
        _, thresh = cv.threshold(image, 200, 255, cv.THRESH_BINARY)
        
        # 2. 降噪
        kernel = np.ones((3, 3), np.uint8)
        opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=1)
        
        return opening
    
    def get_rgb(self, box):
        """获取指定区域的RGB值，判断是否为白色
        
        Args:
            box: 截图区域 (left, top, width, height)
            
        Returns:
            bool: 是否为白色
        """
        try:
            # 截图
            img = self.screenshot(box)
            
            # 从截图中获取特定点的RGB值
            if hasattr(img, 'pixel'):
                # 如果是mss截图对象
                r, g, b = img.pixel(3, 3)
            else:
                # 如果是numpy数组，转换为RGB格式
                img_array = np.array(img)
                if img_array.shape[2] >= 3:  # 确保有RGB通道
                    b, g, r = img_array[3, 3, :3]  # OpenCV格式为BGR
                else:
                    return False
            
            # 判断是否为白色（亮色）
            return r > self.WHITE_THRESHOLD and g > self.WHITE_THRESHOLD and b > self.WHITE_THRESHOLD
        except Exception as e:
            # 失败时记录到日志，但不打印到控制台
            self.logger.debug(f"获取RGB值失败: {str(e)}")
            return False
    
    #---------------------------
    # 图像匹配算法控制方法
    #---------------------------
    
    def toggle_matching_method(self):
        """切换匹配算法
        
        Returns:
            bool: 是否使用模板匹配
        """
        self.use_template_matching = not self.use_template_matching
        method_name = "模板匹配" if self.use_template_matching else "特征匹配"
        self.logger.info(f"切换到{method_name}算法")
        return self.use_template_matching
    
    def is_using_template_matching(self):
        """检查是否使用模板匹配算法
        
        Returns:
            bool: 是否使用模板匹配
        """
        return self.use_template_matching
    
    #---------------------------
    # 图像相似度比较方法
    #---------------------------
    
    @lru_cache(maxsize=CACHE_SIZE)
    def template_similarity(self, template_id, target_data):
        """使用模板匹配计算图像相似度（带缓存）
        
        Args:
            template_id: 模板ID（用于缓存）
            target_data: 目标图像数据
            
        Returns:
            float: 相似度
        """
        template = self.gun_img_dict.get(template_id)
        if not template:
            return 0
            
        target_array = np.frombuffer(target_data, dtype=np.uint8)
        target = cv.imdecode(target_array, cv.IMREAD_GRAYSCALE)
        
        # 模板匹配
        res = cv.matchTemplate(target, template['image'], cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(res)
        
        # 转换为百分比
        similarity = int(max_val * 100)
        return similarity
    
    def image_similarity_opencv(self, gun_data, kp2, des2):
        """计算两个图像之间的相似度，使用OpenCV特征点匹配
        
        Args:
            gun_data: 武器模板数据
            kp2, des2: 目标图像的特征点和描述符
            
        Returns:
            float: 相似度
        """
        try:
            # 获取模板图像的特征点和描述符
            kp1, des1 = gun_data['kp_des']
            
            # 特征点匹配
            if des1 is None or des2 is None or len(des1) == 0 or len(des2) == 0:
                return 0
                
            matches = self.bf.match(des1, des2)
            
            # 如果没有匹配点，直接返回0
            if len(matches) == 0:
                return 0
                
            # 计算匹配质量
            distances = sorted([m.distance for m in matches])
            
            # 取前N个最佳匹配计算平均距离
            n = min(len(distances), self.MAX_MATCHES_TO_SORT)
            if n == 0:
                return 0
                
            avg_distance = sum(distances[:n]) / n
            
            # 将距离转换为相似度
            max_distance = self.MATCH_DISTANCE_THRESHOLD
            if avg_distance > max_distance:
                similarity = 0
            else:
                similarity = (1 - avg_distance / max_distance) * 100
                
            return similarity
                
        except Exception as e:
            self.logger.error(f"特征点匹配计算失败: {str(e)}")
            return 0
    
    def _match_with_template(self, gray_pic):
        """使用模板匹配算法匹配武器
        
        Args:
            gray_pic: 灰度图像
            
        Returns:
            tuple: (最佳匹配的武器ID, 相似度)
        """
        # 将图像编码为二进制数据（用于缓存）
        _, target_data = cv.imencode('.png', gray_pic)
        target_data_bytes = target_data.tobytes()
        
        # 初始化结果
        max_similarity = 0
        best_match = ""
        
        # 并行处理所有武器模板
        future_to_gun = {}
        for gun_id in self.gun_img_dict:
            future = self.executor.submit(self.template_similarity, gun_id, target_data_bytes)
            future_to_gun[future] = gun_id
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_gun):
            gun_id = future_to_gun[future]
            try:
                similarity = future.result()
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = gun_id
            except Exception as e:
                self.logger.error(f"模板匹配错误 {gun_id}: {str(e)}")
        
        return best_match, max_similarity
    
    def _match_with_features(self, gray_pic):
        """使用特征点匹配算法匹配武器
        
        Args:
            gray_pic: 灰度图像
            
        Returns:
            tuple: (最佳匹配的武器ID, 相似度)
        """
        # 初始化结果
        max_similarity = 0
        best_match = ""
        
        # 计算目标图像的特征
        kp2, des2 = self._compute_features(gray_pic)
        
        # 并行处理所有武器模板
        future_to_gun = {}
        for gun_id, gun_data in self.gun_img_dict.items():
            future = self.executor.submit(self.image_similarity_opencv, gun_data, kp2, des2)
            future_to_gun[future] = gun_id
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_gun):
            gun_id = future_to_gun[future]
            try:
                similarity = future.result()
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = gun_id
            except Exception as e:
                self.logger.error(f"特征匹配错误 {gun_id}: {str(e)}")
        
        return best_match, max_similarity
    
    #---------------------------
    # 武器和姿势检测方法
    #---------------------------
    
    def detect_weapon(self, gun_pos):
        """检测武器
        
        Args:
            gun_pos: 武器位置(1或2)
            
        Returns:
            tuple: (最相似武器ID, 相似度)
        """
        try:
            # 获取武器区域
            weapon_area = self.resolution_config.get_weapon_area(gun_pos)
            
            # 截图
            start_time = time.time()
            shot = self.screenshot(weapon_area)
            gray_pic = cv.cvtColor(np.array(shot), cv.COLOR_RGB2GRAY)
            
            # 预处理提高对比度
            gray_pic = self._preprocess_image(gray_pic)
            
            # 保存临时图片（如果需要）
            gun_temp_file = os.path.join(self.temp_dir, f"gun{gun_pos}.png")
            self.save_temp_pic(gray_pic, gun_temp_file, self.save_temp_images)
            
            # 根据选择的算法进行匹配
            if self.use_template_matching:
                # 使用模板匹配算法
                best_match, similarity = self._match_with_template(gray_pic)
            else:
                # 使用特征点匹配算法
                best_match, similarity = self._match_with_features(gray_pic)
            
            # 计算处理时间
            process_time = (time.time() - start_time) * 1000  # 毫秒
            
            # 根据相似度阈值记录日志
            if similarity >= self.SIMILARITY_THRESHOLD:
                self.logger.info(f"成功识别武器: {best_match}, 相似度: {similarity:.0f}%, 处理时间: {process_time:.1f}毫秒")
            elif similarity >= self.LOW_SIMILARITY_THRESHOLD:
                self.logger.info(f"低可信度识别武器: {best_match}, 相似度: {similarity:.0f}%, 处理时间: {process_time:.1f}毫秒")
            else:
                self.logger.warning(f"未能识别武器, 最高相似度: {similarity:.0f}%, 处理时间: {process_time:.1f}毫秒")
            
            return best_match, similarity
            
        except Exception as e:
            self.logger.error(f"武器识别失败: {str(e)}")
            return "", 0
    
    def detect_posture(self):
        """检测姿势
        
        Returns:
            int: 姿势状态，1为站立，2为蹲下
        """
        try:
            # 获取姿势检测区域
            area1 = self.resolution_config.get_posture_area(1)
            area2 = self.resolution_config.get_posture_area(2)
            
            # 检测两个区域是否为白色
            is_white1 = self.get_rgb(area1)
            is_white2 = self.get_rgb(area2)
            
            # 根据检测结果确定姿势，并输出到控制台
            if is_white1 and is_white2:
                return 1  # 站立
            else:
                return 2  # 蹲下
                
        except Exception as e:
            self.logger.error(f"姿势检测失败: {str(e)}")
            return 1  # 失败时默认为站立
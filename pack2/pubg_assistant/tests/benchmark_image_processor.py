#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ImageProcessor类基准测试
测试图像处理性能和识别准确性
"""

import os
import sys
import time
import cv2 as cv
import numpy as np
from datetime import datetime
import argparse

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.config.resolution_config import ResolutionConfig

class ImageProcessorBenchmark:
    """ImageProcessor类基准测试"""
    
    def __init__(self, resolution_config=None, resources_base=None):
        """初始化基准测试
        
        Args:
            resolution_config: 分辨率配置，如果为None则使用默认配置
            resources_base: 资源目录基础路径，如果为None则使用默认路径
        """
        # 获取项目根目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 设置资源目录
        self.resources_base = resources_base or os.path.join(self.base_dir, "resources")
        self.template_dir = os.path.join(self.resources_base, "25601440")
        self.temp_dir = os.path.join(self.resources_base, "temp2313")
        
        # 创建分辨率配置
        self.resolution_config = resolution_config or ResolutionConfig(2560, 1440)
        
        # 创建图像处理器
        self.image_processor = ImageProcessor(self.resolution_config)
        
        # 确保测试资源存在
        self._ensure_resources()
    
    def _ensure_resources(self):
        """确保测试资源存在"""
        # 检查模板目录
        if not os.path.exists(self.template_dir):
            print(f"警告: 模板目录不存在: {self.template_dir}")
            print("某些测试可能无法运行")
        
        # 检查临时目录
        if not os.path.exists(self.temp_dir):
            print(f"警告: 临时目录不存在: {self.temp_dir}")
            print("某些测试可能无法运行")
    
    def run_all_benchmarks(self, output_file=None):
        """运行所有基准测试
        
        Args:
            output_file: 输出结果文件路径，如果为None则只打印到控制台
        """
        print("=" * 60)
        print("开始 ImageProcessor 基准测试")
        print("=" * 60)
        
        # 记录测试开始时间
        start_time = time.time()
        
        # 准备输出文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# ImageProcessor 基准测试结果\n\n")
                f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 运行各项基准测试
        results = {}
        
        # 1. 初始化性能测试
        print("\n## 初始化性能测试")
        init_result = self.benchmark_initialization()
        results['initialization'] = init_result
        
        # 2. 截图性能测试
        print("\n## 截图性能测试")
        screenshot_result = self.benchmark_screenshot()
        results['screenshot'] = screenshot_result
        
        # 3. 特征点匹配性能测试
        print("\n## 特征点匹配性能测试")
        feature_matching_result = self.benchmark_feature_matching()
        results['feature_matching'] = feature_matching_result
        
        # 4. 模板匹配性能测试
        print("\n## 模板匹配性能测试")
        template_matching_result = self.benchmark_template_matching()
        results['template_matching'] = template_matching_result
        
        # 5. 武器检测性能测试
        print("\n## 武器检测性能测试")
        weapon_detection_result = self.benchmark_weapon_detection()
        results['weapon_detection'] = weapon_detection_result
        
        # 6. 姿势检测性能测试
        print("\n## 姿势检测性能测试")
        posture_detection_result = self.benchmark_posture_detection()
        results['posture_detection'] = posture_detection_result
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 显示测试汇总
        print("\n" + "=" * 60)
        print(f"ImageProcessor 基准测试完成，总耗时: {total_time:.2f}秒")
        print("=" * 60)
        
        # 保存测试结果到文件
        if output_file:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n## 测试汇总\n\n")
                f.write(f"- 总耗时: {total_time:.2f}秒\n\n")
                
                # 生成汇总表格
                f.write("| 测试项目 | 平均耗时(毫秒) | 最小耗时(毫秒) | 最大耗时(毫秒) | 次数 | 备注 |\n")
                f.write("|----------|---------------|---------------|---------------|------|------|\n")
                
                for test_name, result in results.items():
                    if isinstance(result, dict) and 'avg_time' in result:
                        f.write(f"| {test_name} | {result['avg_time'] * 1000:.2f} | {result['min_time'] * 1000:.2f} | {result['max_time'] * 1000:.2f} | {result['iterations']} | {result.get('notes', '')} |\n")
                    elif isinstance(result, dict):
                        notes = ', '.join([f"{k}: {v}" for k, v in result.items() if k != 'notes'])
                        f.write(f"| {test_name} | - | - | - | - | {notes} |\n")
                    else:
                        f.write(f"| {test_name} | - | - | - | - | {result} |\n")
            
            print(f"测试结果已保存到: {output_file}")
        
        return results
    
    def benchmark_initialization(self, iterations=5):
        """测试ImageProcessor初始化性能
        
        Args:
            iterations: 重复测试次数
            
        Returns:
            dict: 性能测试结果
        """
        print(f"测试ImageProcessor初始化性能 ({iterations}次)...")
        
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            # 每次使用新的实例进行测试
            processor = ImageProcessor(self.resolution_config)
            end_time = time.time()
            
            elapsed = end_time - start_time
            times.append(elapsed)
            print(f"  第{i+1}次: {elapsed:.4f}秒")
        
        # 计算统计数据
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"初始化平均耗时: {avg_time:.4f}秒")
        
        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'iterations': iterations,
            'notes': '包含武器图像库加载时间'
        }
    
    def benchmark_screenshot(self, iterations=100):
        """测试截图性能
        
        Args:
            iterations: 重复测试次数
            
        Returns:
            dict: 性能测试结果
        """
        print(f"测试截图性能 ({iterations}次)...")
        
        # 使用一个典型的截图区域
        box = (0, 0, 100, 100)  # 小区域以加快测试速度
        
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            # 执行截图
            self.image_processor.screenshot(box)
            end_time = time.time()
            
            elapsed = end_time - start_time
            times.append(elapsed)
            
            if i % 20 == 0:
                print(f"  进度: {i}/{iterations}")
        
        # 计算统计数据
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"截图平均耗时: {avg_time:.4f}秒")
        
        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'iterations': iterations,
            'notes': f'测试区域大小: {box[2]}x{box[3]}'
        }
    
    def benchmark_feature_matching(self, iterations=20):
        """测试特征点匹配性能
        
        Args:
            iterations: 重复测试次数
            
        Returns:
            dict: 性能测试结果
        """
        print(f"测试特征点匹配性能 ({iterations}次)...")
        
        # 准备测试数据
        test_samples = []
        for gun_id, gun_data in self.image_processor.gun_img_dict.items():
            if isinstance(gun_data, dict) and 'image' in gun_data:
                test_samples.append((gun_id, gun_data))
                if len(test_samples) >= 5:  # 只使用前5个样本
                    break
        
        if not test_samples:
            return "无法进行测试，缺少测试样本"
        
        # 确保模板匹配模式关闭
        self.image_processor.use_template_matching = False
        
        times = []
        
        for i in range(iterations):
            # 随机选择两个样本进行匹配测试
            if len(test_samples) >= 2:
                sample1 = test_samples[i % len(test_samples)]
                sample2 = test_samples[(i + 1) % len(test_samples)]
                
                start_time = time.time()
                # 执行特征点匹配
                self.image_processor.image_similarity_opencv(sample1[1], sample2[1]['image'])
                end_time = time.time()
                
                elapsed = end_time - start_time
                times.append(elapsed)
                
                if i % 5 == 0:
                    print(f"  进度: {i}/{iterations}")
        
        # 计算统计数据
        avg_time = sum(times) / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        
        print(f"特征点匹配平均耗时: {avg_time:.4f}秒")
        
        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'iterations': len(times),
            'notes': '特征点匹配使用ORB算法'
        }
    
    def benchmark_template_matching(self, iterations=20):
        """测试模板匹配性能
        
        Args:
            iterations: 重复测试次数
            
        Returns:
            dict: 性能测试结果
        """
        print(f"测试模板匹配性能 ({iterations}次)...")
        
        # 准备测试数据
        test_samples = []
        for gun_id, gun_data in self.image_processor.gun_img_dict.items():
            if isinstance(gun_data, dict) and 'image' in gun_data:
                test_samples.append((gun_id, gun_data))
                if len(test_samples) >= 5:  # 只使用前5个样本
                    break
        
        if not test_samples:
            return "无法进行测试，缺少测试样本"
        
        # 确保模板匹配模式开启
        original_mode = self.image_processor.use_template_matching
        self.image_processor.use_template_matching = True
        
        times = []
        
        for i in range(iterations):
            # 随机选择两个样本进行匹配测试
            if len(test_samples) >= 2:
                sample1 = test_samples[i % len(test_samples)]
                sample2 = test_samples[(i + 1) % len(test_samples)]
                
                start_time = time.time()
                # 执行模板匹配
                self.image_processor.image_similarity_opencv(sample1[1], sample2[1]['image'])
                end_time = time.time()
                
                elapsed = end_time - start_time
                times.append(elapsed)
                
                if i % 5 == 0:
                    print(f"  进度: {i}/{iterations}")
        
        # 还原模板匹配模式
        self.image_processor.use_template_matching = original_mode
        
        # 计算统计数据
        avg_time = sum(times) / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        
        print(f"模板匹配平均耗时: {avg_time:.4f}秒")
        
        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'iterations': len(times),
            'notes': '使用TM_CCORR_NORMED匹配方法'
        }
    
    def benchmark_weapon_detection(self, iterations=5):
        """测试武器检测性能
        
        Args:
            iterations: 重复测试次数
            
        Returns:
            dict: 性能测试结果
        """
        print(f"测试武器检测性能 ({iterations}次)...")
        print("注意: 此测试需要实际游戏画面或模拟画面，可能不会返回有效结果")
        
        # 测试gun_pos=1和gun_pos=2两种情况
        results = {}
        for gun_pos in [1, 2]:
            print(f"测试武器位置 {gun_pos}:")
            times = []
            detected_count = 0
            
            for i in range(iterations):
                start_time = time.time()
                # 执行武器检测
                detected, gun_id = self.image_processor.detect_weapon(gun_pos)
                end_time = time.time()
                
                elapsed = end_time - start_time
                times.append(elapsed)
                
                if detected:
                    detected_count += 1
                    print(f"  第{i+1}次: {elapsed:.4f}秒, 检测到武器: {gun_id}")
                else:
                    print(f"  第{i+1}次: {elapsed:.4f}秒, 未检测到武器")
            
            # 计算统计数据
            avg_time = sum(times) / len(times) if times else 0
            min_time = min(times) if times else 0
            max_time = max(times) if times else 0
            detection_rate = detected_count / iterations if iterations > 0 else 0
            
            print(f"武器位置{gun_pos}检测平均耗时: {avg_time:.4f}秒, 检测率: {detection_rate:.0%}")
            
            results[f'gun_pos_{gun_pos}'] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'iterations': iterations,
                'detection_rate': detection_rate,
                'notes': f'武器位置{gun_pos}'
            }
        
        return results
    
    def benchmark_posture_detection(self, iterations=10):
        """测试姿势检测性能
        
        Args:
            iterations: 重复测试次数
            
        Returns:
            dict: 性能测试结果
        """
        print(f"测试姿势检测性能 ({iterations}次)...")
        print("注意: 此测试需要实际游戏画面或模拟画面，可能不会返回准确结果")
        
        times = []
        posture_results = []
        
        for i in range(iterations):
            start_time = time.time()
            # 执行姿势检测
            posture = self.image_processor.detect_posture()
            end_time = time.time()
            
            elapsed = end_time - start_time
            times.append(elapsed)
            posture_results.append(posture)
            
            posture_name = "站立" if posture == 1 else "蹲下" if posture == 99 else f"未知({posture})"
            print(f"  第{i+1}次: {elapsed:.4f}秒, 检测结果: {posture_name}")
        
        # 计算统计数据
        avg_time = sum(times) / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        
        # 分析姿势检测结果
        standing_count = posture_results.count(1)
        crouching_count = posture_results.count(99)
        other_count = iterations - standing_count - crouching_count
        
        print(f"姿势检测平均耗时: {avg_time:.4f}秒")
        print(f"检测结果统计: 站立 {standing_count}次, 蹲下 {crouching_count}次, 其他 {other_count}次")
        
        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'iterations': iterations,
            'standing_count': standing_count,
            'crouching_count': crouching_count,
            'other_count': other_count,
            'notes': f'站立:{standing_count}, 蹲下:{crouching_count}, 其他:{other_count}'
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ImageProcessor基准测试工具')
    parser.add_argument('--output', type=str, default='benchmark_results.md', help='输出结果文件名')
    parser.add_argument('--resolution', type=str, default='2560x1440', help='分辨率设置，格式为widthxheight')
    args = parser.parse_args()
    
    # 解析分辨率
    try:
        width, height = map(int, args.resolution.lower().split('x'))
    except:
        print(f"无效的分辨率格式: {args.resolution}，使用默认值 2560x1440")
        width, height = 2560, 1440
    
    # 获取项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(base_dir, 'tests', args.output)
    
    # 创建分辨率配置
    resolution_config = ResolutionConfig(width, height)
    
    # 创建并运行基准测试
    benchmark = ImageProcessorBenchmark(resolution_config)
    benchmark.run_all_benchmarks(output_file)

if __name__ == "__main__":
    main() 
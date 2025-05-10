#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模板匹配性能
比较temp2313目录下图片与25601440目录下模板的匹配情况
"""

import os
import sys
import cv2 as cv
import numpy as np
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.config.resolution_config import ResolutionConfig
import argparse

def test_template_matching(template_dir, temp_dir, target_file=None, output_file=None):
    """测试临时目录中的截图与模板的匹配度
    
    Args:
        template_dir: 模板图片所在目录
        temp_dir: 临时截图所在目录
        target_file: 可选，指定只匹配特定文件名
        output_file: 可选，指定输出结果文件
    """
    # 创建分辨率配置，用于初始化图像处理器
    resolution_config = ResolutionConfig(2560, 1440)
    # 为了测试目的，修改资源目录路径
    resolution_config.resources_dir = template_dir
    
    processor = ImageProcessor(resolution_config)
    # 手动加载模板图片，而不是使用ImageProcessor中的初始化方法
    gun_list, gun_img_dict = load_gun_images(template_dir)
    if not gun_list:
        print(f"未找到模板目录或目录为空: {template_dir}")
        return
    
    # 获取临时目录中的所有图片
    temp_files = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # 如果指定了目标文件名，则只处理该文件
                if target_file and file != target_file:
                    continue
                temp_files.append(os.path.join(root, file))
    
    if not temp_files:
        if target_file:
            print(f"在临时目录中未找到指定文件: {target_file}")
        else:
            print(f"临时目录中没有找到图片: {temp_dir}")
        return
    
    print(f"\n找到临时图片 {len(temp_files)} 个{f'(目标文件: {target_file})' if target_file else ''}，开始匹配测试...")
    print(f"模板目录: {template_dir}")
    print(f"临时图片目录: {temp_dir}")
    print("-" * 60)
    
    # 准备输出文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 模板匹配测试结果\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"模板目录: {template_dir}\n")
            f.write(f"临时图片目录: {temp_dir}\n\n")
    
    # 统计结果
    all_results = []
    
    # 对每个临时图片进行测试
    for temp_file in temp_files:
        filename = os.path.basename(temp_file)
        print(f"\n图片: {filename}")
        
        # 读取临时图片
        img = cv.imread(temp_file)
        if img is None:
            print(f"无法读取图片: {temp_file}")
            continue
            
        # 转换为灰度图
        if len(img.shape) == 3:
            gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        else:
            gray_img = img
        
        # 测试与每个模板的匹配度
        results = []
        for gun_id in gun_list:
            # 获取模板图像
            template_data = gun_img_dict[gun_id]
            
            # 处理不同格式的模板数据
            if isinstance(template_data, dict) and 'image' in template_data:
                template_img = template_data['image']
            elif hasattr(template_data, 'shape'): 
                template_img = template_data
            else:
                print(f"警告: 无法解析武器ID {gun_id} 的模板数据，跳过此模板")
                continue
            
            # 计算相似度
            similarity = calculate_similarity(template_img, gray_img)
            results.append((gun_id, similarity))
        
        # 按相似度从高到低排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 输出最匹配的模板（前5个）
        print(f"{'武器ID':<10} {'相似度':<10}")
        print("-" * 20)
        for gun_id, similarity in results[:5]:
            print(f"{gun_id:<10} {similarity:.2f}%")
            
        # 突出显示最佳匹配结果
        if results:
            best_match = results[0]
            print(f"\n最佳匹配结果: 武器ID {best_match[0]}, 相似度 {best_match[1]:.2f}%")
            
            # 匹配度评级
            if best_match[1] >= 80:
                rating = "极佳 (非常可能是正确识别)"
                print(f"匹配评级: {rating}")
            elif best_match[1] >= 60:
                rating = "良好 (可能是正确识别)"
                print(f"匹配评级: {rating}")
            elif best_match[1] >= 40:
                rating = "一般 (识别结果可靠性较低)"
                print(f"匹配评级: {rating}")
            else:
                rating = "较差 (识别结果不可靠)"
                print(f"匹配评级: {rating}")
                
            # 保存结果
            all_results.append({
                'file': filename,
                'best_match': best_match[0],
                'similarity': best_match[1],
                'rating': rating,
                'top5': results[:5]
            })
        
        print("-" * 60)
        
        # 保存单个图片的匹配结果
        if output_file and results:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"## 图片: {filename}\n\n")
                f.write(f"最佳匹配结果: 武器ID {best_match[0]}, 相似度 {best_match[1]:.2f}%\n")
                f.write(f"匹配评级: {rating}\n\n")
                f.write(f"前五匹配结果:\n\n")
                f.write(f"| 武器ID | 相似度 |\n")
                f.write(f"|--------|--------|\n")
                for gun_id, similarity in results[:5]:
                    f.write(f"| {gun_id} | {similarity:.2f}% |\n")
                f.write("\n" + "-" * 40 + "\n\n")
    
    # 保存汇总结果
    if output_file and all_results:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n# 汇总结果\n\n")
            f.write(f"共测试 {len(all_results)} 个图片\n\n")
            f.write(f"| 图片文件 | 最佳匹配 | 相似度 | 匹配评级 |\n")
            f.write(f"|----------|----------|--------|----------|\n")
            for result in all_results:
                f.write(f"| {result['file']} | {result['best_match']} | {result['similarity']:.2f}% | {result['rating']} |\n")
    
    print(f"\n测试完成，共测试 {len(all_results)} 个图片")
    if output_file:
        print(f"测试结果已保存到: {output_file}")

def load_gun_images(template_dir):
    """加载模板图片
    
    Args:
        template_dir: 模板图片所在目录
        
    Returns:
        tuple: (枪械ID列表, 枪械图像字典)
    """
    gun_list = []
    gun_img_dict = {}
    
    if not os.path.exists(template_dir):
        return gun_list, gun_img_dict
    
    for file_name in os.listdir(template_dir):
        if file_name.lower().endswith('.png'):
            gun_id = os.path.splitext(file_name)[0]
            gun_file = os.path.join(template_dir, file_name)
            gun_img_dict[gun_id] = cv.imread(gun_file, cv.IMREAD_GRAYSCALE)
            gun_list.append(gun_id)
    
    return gun_list, gun_img_dict
        
def calculate_similarity(template, target):
    """计算两个图像的相似度
    
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
        result = cv.matchTemplate(target, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(result)
        return max_val * 100  # 转换为百分比
    except Exception as e:
        print(f"模板匹配出错: {e}")
        return 0

def main():
    """主函数"""
    try:
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='测试模板匹配功能')
        parser.add_argument('--file', type=str, help='指定要匹配的文件名')
        parser.add_argument('--output', type=str, default='match_results.md', help='指定输出结果文件名')
        args = parser.parse_args()
        
        # 设置目录路径
        template_dir = os.path.join(base_dir, 'resources', '25601440')
        temp_dir = os.path.join(base_dir, 'resources', 'temp2313')
        output_file = os.path.join(base_dir, 'tests', args.output)
        
        # 检查目录是否存在
        if not os.path.exists(template_dir):
            print(f"错误: 模板目录不存在: {template_dir}")
            print("请确认您的项目结构是否正确")
            return
            
        if not os.path.exists(temp_dir):
            print(f"错误: 临时图片目录不存在: {temp_dir}")
            print("请确认您的项目结构是否正确")
            return
        
        # 测试模板匹配
        print("=== 测试临时截图与模板的匹配度 ===")
        test_template_matching(template_dir, temp_dir, args.file, output_file)
        
    except Exception as e:
        import traceback
        print(f"程序执行出错: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 
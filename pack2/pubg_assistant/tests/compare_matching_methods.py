#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
比较两种图像匹配方法
1. 测试test_template_matching.py中的calculate_similarity方法
2. 测试ImageProcessor中的图像匹配方法
3. 对比两种方法的结果
"""

import os
import sys
import cv2 as cv
import numpy as np
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# 导入测试模块和图像处理器
from tests.test_template_matching import calculate_similarity, load_gun_images
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.config.resolution_config import ResolutionConfig

def compare_matching_methods(template_dir, temp_dir, target_file=None, output_file=None, toggle_algorithm=False):
    """比较两种图像匹配方法
    
    Args:
        template_dir: 模板图片所在目录
        temp_dir: 临时截图所在目录
        target_file: 可选，指定只匹配特定文件名
        output_file: 可选，指定输出结果文件
        toggle_algorithm: 是否切换为模板匹配算法
    """
    print(f"\n开始比较两种图像匹配方法...")
    print(f"模板目录: {template_dir}")
    print(f"临时图片目录: {temp_dir}")
    print("-" * 80)
    
    # 1. 加载test_template_matching中的方法
    gun_list, gun_img_dict = load_gun_images(template_dir)
    if not gun_list:
        print(f"未找到模板目录或目录为空: {template_dir}")
        return
    
    # 2. 初始化ImageProcessor
    resolution_config = ResolutionConfig(2560, 1440)
    resolution_config.resources_dir = template_dir  # 重写资源目录
    image_processor = ImageProcessor(resolution_config)
    
    # 如果需要切换算法，则切换为模板匹配算法
    if toggle_algorithm:
        image_processor.toggle_matching_algorithm()
        print(f"ImageProcessor已切换为{'模板匹配' if image_processor.is_using_template_matching() else 'ORB特征点匹配'}算法")
    else:
        print(f"ImageProcessor当前使用{'模板匹配' if image_processor.is_using_template_matching() else 'ORB特征点匹配'}算法")
    
    # 3. 获取临时目录中的所有图片
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
    
    print(f"找到临时图片 {len(temp_files)} 个{f'(目标文件: {target_file})' if target_file else ''}")
    
    # 准备输出文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 图像匹配方法比较结果\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"模板目录: {template_dir}\n")
            f.write(f"临时图片目录: {temp_dir}\n")
            f.write(f"ImageProcessor算法: {'模板匹配' if image_processor.is_using_template_matching() else 'ORB特征点匹配'}\n\n")
    
    # 统计结果
    all_results = []
    
    # 对每个临时图片进行测试
    for temp_file in temp_files:
        filename = os.path.basename(temp_file)
        print(f"\n图片: {filename}")
        print("-" * 80)
        
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
        
        # 使用两种方法测试与每个模板的匹配度
        template_results = []  # test_template_matching的结果
        processor_results = []  # ImageProcessor的结果
        
        for gun_id in gun_list:
            # 获取模板图像
            template_img = gun_img_dict[gun_id]
            
            # 使用test_template_matching的方法计算相似度
            template_similarity = calculate_similarity(template_img, gray_img)
            template_results.append((gun_id, template_similarity))
            
            # 使用ImageProcessor的方法计算相似度
            processor_similarity = image_processor.image_similarity_opencv(template_img, gray_img)
            # 如果是原始算法(ORB)，返回值是特征点数量，将其转换为0-100的相似度
            if not image_processor.is_using_template_matching():
                # 特征点匹配数量转换为相似度百分比 (以40点为基准100%)
                normalized_similarity = min(100, processor_similarity * 2.5)
            else:
                # 模板匹配已经是0-100的相似度
                normalized_similarity = processor_similarity
            processor_results.append((gun_id, processor_similarity, normalized_similarity))
        
        # 按相似度从高到低排序
        template_results.sort(key=lambda x: x[1], reverse=True)
        processor_results.sort(key=lambda x: x[1], reverse=True)
        
        # 输出最匹配的模板（前5个）
        print("test_template_matching方法结果:")
        print(f"{'武器ID':<10} {'相似度':<10}")
        print("-" * 20)
        for gun_id, similarity in template_results[:5]:
            print(f"{gun_id:<10} {similarity:.2f}%")
            
        print("\nImageProcessor方法结果:")
        print(f"{'武器ID':<10} {'匹配值':<10} {'换算相似度':<10}")
        print("-" * 30)
        for gun_id, raw_similarity, normalized_similarity in processor_results[:5]:
            print(f"{gun_id:<10} {raw_similarity:<10.0f} {normalized_similarity:.2f}%")
            
        # 突出显示最佳匹配结果
        if template_results and processor_results:
            template_best = template_results[0]
            processor_best = processor_results[0]
            
            print("\n最佳匹配比较:")
            print(f"test_template_matching: 武器ID {template_best[0]}, 相似度 {template_best[1]:.2f}%")
            print(f"ImageProcessor: 武器ID {processor_best[0]}, 相似度 {processor_best[2]:.2f}%")
            
            # 结果是否一致
            is_same = template_best[0] == processor_best[0]
            print(f"两种方法结果一致: {'是' if is_same else '否'}")
            
            # 保存结果
            result_entry = {
                'file': filename,
                'template_best': template_best[0],
                'template_similarity': template_best[1],
                'processor_best': processor_best[0],
                'processor_raw_similarity': processor_best[1],
                'processor_normalized_similarity': processor_best[2],
                'is_same': is_same
            }
            all_results.append(result_entry)
        
        print("-" * 80)
        
        # 保存单个图片的匹配结果
        if output_file and template_results and processor_results:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"## 图片: {filename}\n\n")
                f.write(f"### test_template_matching方法结果\n\n")
                f.write(f"| 武器ID | 相似度 |\n")
                f.write(f"|--------|--------|\n")
                for gun_id, similarity in template_results[:5]:
                    f.write(f"| {gun_id} | {similarity:.2f}% |\n")
                    
                f.write(f"\n### ImageProcessor方法结果\n\n")
                f.write(f"| 武器ID | 匹配值 | 换算相似度 |\n")
                f.write(f"|--------|--------|------------|\n")
                for gun_id, raw_similarity, normalized_similarity in processor_results[:5]:
                    f.write(f"| {gun_id} | {raw_similarity:.0f} | {normalized_similarity:.2f}% |\n")
                    
                f.write(f"\n### 比较结果\n\n")
                f.write(f"- test_template_matching: 武器ID {template_best[0]}, 相似度 {template_best[1]:.2f}%\n")
                f.write(f"- ImageProcessor: 武器ID {processor_best[0]}, 相似度 {processor_best[2]:.2f}%\n")
                f.write(f"- 两种方法结果一致: {'是' if is_same else '否'}\n\n")
                f.write("-" * 40 + "\n\n")
    
    # 保存汇总结果
    if output_file and all_results:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n# 汇总结果\n\n")
            f.write(f"共测试 {len(all_results)} 个图片\n\n")
            
            # 计算一致率
            same_count = sum(1 for result in all_results if result['is_same'])
            consistency_rate = (same_count / len(all_results)) * 100
            f.write(f"两种方法结果一致率: {consistency_rate:.2f}%\n\n")
            
            f.write(f"| 图片文件 | test_template_matching | 相似度 | ImageProcessor | 相似度 | 结果一致 |\n")
            f.write(f"|----------|------------------------|--------|----------------|--------|----------|\n")
            for result in all_results:
                f.write(f"| {result['file']} | {result['template_best']} | {result['template_similarity']:.2f}% | {result['processor_best']} | {result['processor_normalized_similarity']:.2f}% | {'✓' if result['is_same'] else '✗'} |\n")
    
    # 计算统计数据
    if all_results:
        same_count = sum(1 for result in all_results if result['is_same'])
        consistency_rate = (same_count / len(all_results)) * 100
        
        # 打印统计结果
        print("\n统计结果:")
        print(f"共测试 {len(all_results)} 个图片")
        print(f"两种方法结果一致: {same_count} 个图片")
        print(f"两种方法结果一致率: {consistency_rate:.2f}%")
        
        # 如果有不一致的结果，单独列出
        if same_count < len(all_results):
            print("\n不一致的结果:")
            print(f"{'图片文件':<20} {'test_template_matching':<20} {'ImageProcessor':<20}")
            print("-" * 60)
            for result in all_results:
                if not result['is_same']:
                    print(f"{result['file']:<20} {result['template_best']:<20} {result['processor_best']:<20}")
    
    print(f"\n测试完成，共测试 {len(all_results)} 个图片")
    if output_file:
        print(f"测试结果已保存到: {output_file}")

def main():
    """主函数"""
    try:
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='比较两种图像匹配方法')
        parser.add_argument('--file', type=str, help='指定要匹配的文件名')
        parser.add_argument('--output', type=str, default='comparison_results.md', help='指定输出结果文件名')
        parser.add_argument('--toggle', action='store_true', help='切换为模板匹配算法')
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
        
        # 比较两种匹配方法
        print("=== 比较两种图像匹配方法 ===")
        compare_matching_methods(template_dir, temp_dir, args.file, output_file, args.toggle)
        
    except Exception as e:
        import traceback
        print(f"程序执行出错: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 
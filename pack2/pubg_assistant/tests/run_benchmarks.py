#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUBG Assistant 基准测试运行器
运行所有模块的基准测试并生成汇总报告
"""

import os
import sys
import time
import argparse
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入各基准测试模块
from tests.benchmark_image_processor import ImageProcessorBenchmark
from tests.benchmark_action_processor import ActionProcessorBenchmark

def run_all_benchmarks(args):
    """运行所有基准测试
    
    Args:
        args: 命令行参数
    """
    print("=" * 80)
    print("开始 PUBG Assistant 基准测试")
    print("=" * 80)
    
    # 记录测试开始时间
    start_time = time.time()
    test_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 创建输出目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'tests', 'benchmark_results')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 解析分辨率
    try:
        width, height = map(int, args.resolution.lower().split('x'))
    except:
        print(f"无效的分辨率格式: {args.resolution}，使用默认值 2560x1440")
        width, height = 2560, 1440
    
    # 准备汇总报告文件
    summary_file = os.path.join(output_dir, f'benchmark_summary_{test_time}.md')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# PUBG Assistant 基准测试汇总报告\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"分辨率设置: {width}x{height}\n\n")
    
    # 获取要运行的测试模块
    modules_to_test = []
    if args.all or args.image:
        modules_to_test.append('image')
    if args.all or args.action:
        modules_to_test.append('action')
    
    if not modules_to_test:
        print("错误: 未指定要测试的模块。请使用 --all 或指定具体模块。")
        return
    
    print(f"将测试以下模块: {', '.join(modules_to_test)}")
    
    # 测试结果
    all_results = {}
    
    # 1. 测试图像处理器
    if 'image' in modules_to_test:
        print("\n\n" + "=" * 60)
        print("测试图像处理器(ImageProcessor)")
        print("=" * 60)
        
        image_output_file = os.path.join(output_dir, f'image_processor_{test_time}.md')
        image_benchmark = ImageProcessorBenchmark(None)
        image_results = image_benchmark.run_all_benchmarks(image_output_file)
        all_results['image_processor'] = image_results
        
        print(f"图像处理器测试完成，结果保存到: {os.path.basename(image_output_file)}")
    
    # 2. 测试动作处理器
    if 'action' in modules_to_test:
        print("\n\n" + "=" * 60)
        print("测试动作处理器(ActionProcessor)")
        print("=" * 60)
        
        action_output_file = os.path.join(output_dir, f'action_processor_{test_time}.md')
        action_benchmark = ActionProcessorBenchmark(None)
        action_results = action_benchmark.run_all_benchmarks(action_output_file)
        all_results['action_processor'] = action_results
        
        print(f"动作处理器测试完成，结果保存到: {os.path.basename(action_output_file)}")
    
    # 计算总耗时
    total_time = time.time() - start_time
    
    # 生成汇总报告
    with open(summary_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## 测试汇总\n\n")
        f.write(f"- 总耗时: {total_time:.2f}秒\n")
        f.write(f"- 测试的模块: {', '.join(modules_to_test)}\n\n")
        
        # 添加各模块的关键性能指标
        for module_name, results in all_results.items():
            f.write(f"### {module_name} 性能指标\n\n")
            
            # 生成汇总表格
            f.write("| 测试项目 | 平均耗时(毫秒) | 最小耗时(毫秒) | 最大耗时(毫秒) | 次数 | 备注 |\n")
            f.write("|----------|---------------|---------------|---------------|------|------|\n")
            
            for test_name, result in results.items():
                if isinstance(result, dict) and 'avg_time' in result:
                    f.write(f"| {test_name} | {result['avg_time'] * 1000:.2f} | {result['min_time'] * 1000:.2f} | {result['max_time'] * 1000:.2f} | {result['iterations']} | {result.get('notes', '')} |\n")
            
            f.write("\n")
    
    print("\n" + "=" * 80)
    print(f"所有基准测试完成，总耗时: {total_time:.2f}秒")
    print(f"汇总报告已保存到: {summary_file}")
    print("=" * 80)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PUBG Assistant 基准测试运行器')
    
    # 测试模块选择参数
    module_group = parser.add_argument_group('测试模块选择')
    module_group.add_argument('--all', action='store_true', help='测试所有模块')
    module_group.add_argument('--image', action='store_true', help='测试图像处理器')
    module_group.add_argument('--action', action='store_true', help='测试动作处理器')
    
    # 测试配置参数
    config_group = parser.add_argument_group('测试配置')
    config_group.add_argument('--resolution', type=str, default='2560x1440', help='分辨率设置，格式为widthxheight')
    
    args = parser.parse_args()
    
    run_all_benchmarks(args)

if __name__ == "__main__":
    main() 
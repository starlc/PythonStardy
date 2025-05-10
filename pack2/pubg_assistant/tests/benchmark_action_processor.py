#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ActionProcessor类基准测试
测试动作处理性能和响应时间
"""

import os
import sys
import time
from datetime import datetime
import argparse

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pubg_assistant.processors.image_processor import ImageProcessor
from pubg_assistant.processors.action_processor import ActionProcessor
from pubg_assistant.config.resolution_config import ResolutionConfig
from pubg_assistant.config.config_manager import ConfigManager
from pubg_assistant.managers.ui_manager import UIManager

# 创建一个模拟版的UIManager，用于测试
class MockUIManager:
    """用于测试的UI管理器模拟类"""
    
    def __init__(self):
        """初始化模拟UI管理器"""
        self.running = False
        self.last_update = None
    
    def start_display(self, initial_character="启动", x=1560, y=1370):
        """启动显示（模拟）
        
        Args:
            initial_character: 初始显示字符
            x: 窗口x坐标
            y: 窗口y坐标
        """
        self.running = True
    
    def update_display(self, gun_lock, gun_name, posture, gun_config):
        """更新显示（模拟）
        
        Args:
            gun_lock: 武器锁定状态，0为未锁定，1为锁定
            gun_name: 武器名称
            posture: 姿势状态，1为站立，其他为蹲下
            gun_config: 武器配置状态，True为裸配，False为满配
        """
        self.last_update = {
            'gun_lock': gun_lock,
            'gun_name': gun_name,
            'posture': posture,
            'gun_config': gun_config
        }
    
    def update_display_with_algorithm(self, gun_lock, gun_name, posture, gun_config, use_template):
        """更新显示（带算法指示）（模拟）
        
        Args:
            gun_lock: 武器锁定状态，0为未锁定，1为锁定
            gun_name: 武器名称
            posture: 姿势状态，1为站立，其他为蹲下
            gun_config: 武器配置状态，True为裸配，False为满配
            use_template: 是否使用模板匹配算法
        """
        self.last_update = {
            'gun_lock': gun_lock,
            'gun_name': gun_name,
            'posture': posture,
            'gun_config': gun_config,
            'use_template': use_template
        }
    
    def stop_display(self):
        """停止显示界面（模拟）"""
        self.running = False

# 创建一个模拟版的ImageProcessor类，用于测试
class MockImageProcessor:
    """用于测试的图像处理器模拟类"""
    
    def __init__(self, resolution_config):
        """初始化模拟图像处理器
        
        Args:
            resolution_config: 分辨率配置
        """
        self.resolution_config = resolution_config
        self._use_template = False
        self.last_detected_weapon = "1"  # 默认武器ID
        self.last_detected_posture = 1   # 默认姿势
    
    def detect_weapon(self, gun_pos):
        """模拟武器检测
        
        Args:
            gun_pos: 武器位置
        
        Returns:
            (bool, str): (是否成功, 武器ID)
        """
        # 模拟成功检测武器，返回ID为1-5的随机武器
        weapon_id = str((gun_pos % 5) + 1)
        self.last_detected_weapon = weapon_id
        return True, weapon_id
    
    def detect_posture(self):
        """模拟姿势检测
        
        Returns:
            int: 姿势 1为站立 99为蹲下
        """
        # 随机返回站立(1)或蹲下(99)，但更偏向返回与上次检测不同的结果
        new_posture = 99 if self.last_detected_posture == 1 else 1
        self.last_detected_posture = new_posture
        return new_posture
    
    def toggle_matching_algorithm(self):
        """切换匹配算法
        
        Returns:
            bool: 是否使用模板匹配
        """
        self._use_template = not self._use_template
        return self._use_template
    
    def is_using_template_matching(self):
        """检查是否使用模板匹配
        
        Returns:
            bool: 是否使用模板匹配
        """
        return self._use_template

class ActionProcessorBenchmark:
    """ActionProcessor类基准测试"""
    
    def __init__(self, resolution_config=None):
        """初始化基准测试
        
        Args:
            resolution_config: 分辨率配置，如果为None则使用默认配置
        """
        # 获取项目根目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 创建分辨率配置
        self.resolution_config = resolution_config or ResolutionConfig(2560, 1440)
        
        # 创建配置管理器
        self.config_manager = ConfigManager()
        
        # 创建UI管理器 (使用模拟版，不会真正显示UI)
        self.ui_manager = MockUIManager()
        
        # 创建图像处理器 (使用模拟版，不会真正处理图像)
        self.image_processor = MockImageProcessor(self.resolution_config)
        
        # 创建动作处理器
        self.action_processor = ActionProcessor(
            self.image_processor,
            self.config_manager,
            self.ui_manager
        )
    
    def run_all_benchmarks(self, output_file=None):
        """运行所有基准测试
        
        Args:
            output_file: 输出结果文件路径，如果为None则只打印到控制台
        """
        print("=" * 60)
        print("开始 ActionProcessor 基准测试")
        print("=" * 60)
        
        # 记录测试开始时间
        start_time = time.time()
        
        # 准备输出文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# ActionProcessor 基准测试结果\n\n")
                f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 运行各项基准测试
        results = {}
        
        # 1. 武器切换测试
        print("\n## 武器切换测试")
        weapon_switch_result = self.benchmark_weapon_switch()
        results['weapon_switch'] = weapon_switch_result
        
        # 2. 姿势检测测试
        print("\n## 姿势检测测试")
        posture_check_result = self.benchmark_posture_check()
        results['posture_check'] = posture_check_result
        
        # 3. UI更新测试
        print("\n## UI更新测试")
        ui_update_result = self.benchmark_ui_update()
        results['ui_update'] = ui_update_result
        
        # 4. 键盘处理测试
        print("\n## 键盘处理测试")
        keyboard_handling_result = self.benchmark_keyboard_handling()
        results['keyboard_handling'] = keyboard_handling_result
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 显示测试汇总
        print("\n" + "=" * 60)
        print(f"ActionProcessor 基准测试完成，总耗时: {total_time:.2f}秒")
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
    
    def benchmark_weapon_switch(self, iterations=100):
        """武器切换性能测试
        
        测试武器切换功能的性能
        
        Args:
            iterations: 测试迭代次数
        
        Returns:
            包含测试结果的字典
        """
        print(f"执行武器切换性能测试，迭代次数: {iterations}")
        
        # 测试不同武器间的切换
        weapon_ids = ["1", "2", "3", "4", "5"]  # 武器ID
        times = []
        min_time = float('inf')
        max_time = 0
        success_count = 0
        
        for i in range(iterations):
            # 随机选择两个不同的武器
            current_weapon_id = weapon_ids[i % len(weapon_ids)]
            weapon_pos = (i % 2) + 1  # 在位置1和2之间交替
            
            # 模拟当前武器状态
            self.action_processor.current_gun[weapon_pos] = current_weapon_id
            
            # 测量切换武器的时间
            start_time = time.time()
            
            # 执行武器切换
            try:
                self.action_processor._save_player_gun_and_sound(current_weapon_id, weapon_pos)
                success = True
                success_count += 1
            except Exception as e:
                success = False
                print(f"  错误: {e}")
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if success:
                times.append(elapsed)
                min_time = min(min_time, elapsed)
                max_time = max(max_time, elapsed)
            
            if i % 10 == 0 or i == iterations - 1:
                print(f"  进度: {i+1}/{iterations}")
        
        # 计算平均时间
        avg_time = sum(times) / len(times) if times else 0
        success_rate = (success_count / iterations) * 100
        
        result = {
            'avg_time': avg_time,
            'min_time': min_time if min_time != float('inf') else 0,
            'max_time': max_time,
            'iterations': iterations,
            'success_rate': f"{success_rate:.2f}%",
            'notes': f"成功率: {success_rate:.2f}%"
        }
        
        print(f"  平均耗时: {avg_time * 1000:.2f}ms")
        print(f"  最小耗时: {result['min_time'] * 1000:.2f}ms")
        print(f"  最大耗时: {max_time * 1000:.2f}ms")
        print(f"  成功率: {success_rate:.2f}%")
        
        return result
    
    def benchmark_posture_check(self, iterations=100):
        """姿势检测性能测试
        
        测试姿势检测功能的性能
        
        Args:
            iterations: 测试迭代次数
        
        Returns:
            包含测试结果的字典
        """
        print(f"执行姿势检测性能测试，迭代次数: {iterations}")
        
        # 测试姿势检测
        postures = [1, 2]  # 1为站立，2为蹲下/趴下
        times = []
        min_time = float('inf')
        max_time = 0
        success_count = 0
        
        for i in range(iterations):
            # 随机选择一个姿势
            current_posture = postures[i % len(postures)]
            
            # 模拟当前姿势
            self.action_processor.player_posture = current_posture
            
            # 测量检测姿势的时间
            start_time = time.time()
            
            # 执行姿势检测
            try:
                self.action_processor.check_posture()
                success = True
                success_count += 1
            except Exception as e:
                success = False
                print(f"  错误: {e}")
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if success:
                times.append(elapsed)
                min_time = min(min_time, elapsed)
                max_time = max(max_time, elapsed)
            
            if i % 10 == 0 or i == iterations - 1:
                print(f"  进度: {i+1}/{iterations}")
        
        # 计算平均时间
        avg_time = sum(times) / len(times) if times else 0
        success_rate = (success_count / iterations) * 100
        
        result = {
            'avg_time': avg_time,
            'min_time': min_time if min_time != float('inf') else 0,
            'max_time': max_time,
            'iterations': iterations,
            'success_rate': f"{success_rate:.2f}%",
            'notes': f"成功率: {success_rate:.2f}%"
        }
        
        print(f"  平均耗时: {avg_time * 1000:.2f}ms")
        print(f"  最小耗时: {result['min_time'] * 1000:.2f}ms")
        print(f"  最大耗时: {max_time * 1000:.2f}ms")
        print(f"  成功率: {success_rate:.2f}%")
        
        return result
    
    def benchmark_ui_update(self, iterations=50):
        """UI更新性能测试
        
        测试UI更新功能的性能
        
        Args:
            iterations: 测试迭代次数
        
        Returns:
            包含测试结果的字典
        """
        print(f"执行UI更新性能测试，迭代次数: {iterations}")
        
        # 测试UI更新
        weapons = ["M416", "AKM", "SCAR-L", "M16A4", "UMP45"]
        postures = [1, 2]  # 1为站立，2为蹲下/趴下
        gun_locks = [0, 1]  # 0为未锁定，1为锁定
        gun_configs = [True, False]  # True为裸配，False为满配
        times = []
        min_time = float('inf')
        max_time = 0
        success_count = 0
        
        for i in range(iterations):
            # 随机选择参数
            gun_lock = gun_locks[i % len(gun_locks)]
            gun_name = weapons[i % len(weapons)]
            gun_id = i % 20 + 1  # 模拟武器ID
            posture = postures[i % len(postures)]
            gun_config = gun_configs[i % len(gun_configs)]
            
            # 设置ActionProcessor的状态
            self.action_processor.gun_lock = gun_lock
            self.action_processor.player_gun = gun_id
            self.action_processor.player_posture = posture
            self.action_processor.player_gun_config = gun_config
            
            # 测量UI更新的时间
            start_time = time.time()
            
            # 执行UI更新
            try:
                self.action_processor._update_display()
                success = True
                success_count += 1
            except Exception as e:
                success = False
                print(f"  错误: {e}")
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if success:
                times.append(elapsed)
                min_time = min(min_time, elapsed)
                max_time = max(max_time, elapsed)
            
            if i % 10 == 0 or i == iterations - 1:
                print(f"  进度: {i+1}/{iterations}")
        
        # 计算平均时间
        avg_time = sum(times) / len(times) if times else 0
        success_rate = (success_count / iterations) * 100
        
        result = {
            'avg_time': avg_time,
            'min_time': min_time if min_time != float('inf') else 0,
            'max_time': max_time,
            'iterations': iterations,
            'success_rate': f"{success_rate:.2f}%",
            'notes': f"成功率: {success_rate:.2f}%"
        }
        
        print(f"  平均耗时: {avg_time * 1000:.2f}ms")
        print(f"  最小耗时: {result['min_time'] * 1000:.2f}ms")
        print(f"  最大耗时: {max_time * 1000:.2f}ms")
        print(f"  成功率: {success_rate:.2f}%")
        
        return result
    
    def benchmark_keyboard_handling(self, iterations=50):
        """键盘处理性能测试
        
        测试键盘处理功能的性能
        
        Args:
            iterations: 测试迭代次数
        
        Returns:
            包含测试结果的字典
        """
        print(f"执行键盘处理性能测试，迭代次数: {iterations}")
        
        # 模拟键盘事件，使用数字代表不同的按键
        # 1, 2: 武器切换, 4: 锁定武器, 8: 切换算法, 0: 关闭宏
        keys = [1, 2, 4, 8, 0]
        times = []
        min_time = float('inf')
        max_time = 0
        success_count = 0
        
        for i in range(iterations):
            # 随机选择一个按键
            key = keys[i % len(keys)]
            
            # 测量键盘处理的时间
            start_time = time.time()
            
            # 执行键盘处理
            try:
                # 调用键盘处理方法
                self.action_processor.handle_keyboard_action(key)
                success = True
                success_count += 1
            except Exception as e:
                success = False
                print(f"  错误: {e}")
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if success:
                times.append(elapsed)
                min_time = min(min_time, elapsed)
                max_time = max(max_time, elapsed)
            
            if i % 10 == 0 or i == iterations - 1:
                print(f"  进度: {i+1}/{iterations}")
        
        # 计算平均时间
        avg_time = sum(times) / len(times) if times else 0
        success_rate = (success_count / iterations) * 100
        
        result = {
            'avg_time': avg_time,
            'min_time': min_time if min_time != float('inf') else 0,
            'max_time': max_time,
            'iterations': iterations,
            'success_rate': f"{success_rate:.2f}%",
            'notes': f"成功率: {success_rate:.2f}%"
        }
        
        print(f"  平均耗时: {avg_time * 1000:.2f}ms")
        print(f"  最小耗时: {result['min_time'] * 1000:.2f}ms")
        print(f"  最大耗时: {max_time * 1000:.2f}ms")
        print(f"  成功率: {success_rate:.2f}%")
        
        return result

def main():
    """主函数"""
    try:
        # 创建参数解析器
        parser = argparse.ArgumentParser(description='ActionProcessor基准测试')
        parser.add_argument('--output', '-o', type=str, default=None,
                            help='输出结果保存的文件路径，默认为benchmark_action_processor_结果.md')
        parser.add_argument('--resolution', '-r', type=str, default='2560x1440',
                            help='测试分辨率，格式为"宽x高"，例如"2560x1440"')
        
        # 解析命令行参数
        args = parser.parse_args()
        
        # 设置默认输出文件名
        if args.output is None:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 创建输出目录
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'benchmark_results')
            os.makedirs(output_dir, exist_ok=True)
            args.output = os.path.join(output_dir, f'benchmark_action_processor_{current_time}.md')
        
        # 解析分辨率配置
        try:
            width, height = map(int, args.resolution.lower().split('x'))
            resolution_config = ResolutionConfig(width, height)
        except ValueError:
            print(f"错误: 无效的分辨率格式 '{args.resolution}'。请使用 '宽x高' 格式，例如 '2560x1440'。")
            return 1
        
        print(f"使用分辨率: {width}x{height}")
        
        # 创建基准测试实例
        benchmark = ActionProcessorBenchmark(resolution_config)
        
        # 运行所有测试
        results = benchmark.run_all_benchmarks(args.output)
        
        print(f"\n测试完成，结果已保存到: {args.output}")
        
        # 检查是否有失败的测试
        has_failures = False
        for test_name, result in results.items():
            if isinstance(result, dict) and 'success_rate' in result:
                success_rate = float(result['success_rate'].rstrip('%'))
                if success_rate < 100:
                    print(f"警告: {test_name} 测试成功率低于100%: {success_rate}%")
                    has_failures = True
        
        return 1 if has_failures else 0
    
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
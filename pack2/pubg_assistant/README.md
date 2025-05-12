# PUBG Assistant

PUBG Assistant 是一个辅助工具，提供了武器识别、姿势监控等功能。最新版本包含多项性能优化和稳定性改进。

## 项目结构

```
pubg_assistant/
├── pubg_assistant/          # 主包
│   ├── __init__.py
│   ├── main.py              # 主程序入口
│   ├── config/              # 配置模块
│   │   ├── __init__.py
│   │   ├── resolution_config.py  # 分辨率配置
│   │   └── config_manager.py     # 配置管理器
│   ├── managers/            # 管理器模块
│   │   ├── __init__.py
│   │   ├── input_manager.py      # 输入管理器
│   │   └── ui_manager.py         # UI管理器
│   ├── processors/          # 处理器模块
│   │   ├── __init__.py
│   │   ├── action_processor.py   # 动作处理器
│   │   └── image_processor.py    # 图像处理器
│   ├── core/                # 核心功能模块
│   │   ├── __init__.py
│   │   └── logging.py            # 日志管理
│   └── monitors/            # 监控器模块
│       ├── __init__.py
│       └── posture_monitor.py    # 姿势监控器
├── resources/               # 资源文件
│   ├── 23131440/                 # 2313x1440分辨率武器图像模板
│   ├── 25601440/                 # 2560x1440分辨率武器图像模板
│   ├── dict/                     # 配置字典文件
│   │   └── gun_arr.json          # 武器名称列表
│   ├── temp2313/                 # 截图临时文件
│   └── posturetemp/              # 姿势检测临时文件
├── tests/                   # 测试文件
│   ├── __init__.py
│   ├── benchmark_action_processor.py  # 动作处理器基准测试
│   ├── benchmark_image_processor.py   # 图像处理器基准测试
│   ├── compare_matching_methods.py    # 匹配方法比较
│   ├── run_benchmarks.py              # 基准测试运行脚本
│   ├── test_template_matching.py      # 模板匹配测试
│   └── test_image_black_detection.py  # 图像黑色检测测试
├── logs/                    # 日志文件目录
├── run.py                   # 程序启动脚本
├── run.bat                  # Windows启动批处理文件
└── README.md                # 本文件
```

## 功能特性

- **武器识别**：自动识别游戏中的武器类型
- **姿势检测**：检测玩家当前的姿势（站立/蹲下）
- **状态显示**：实时显示当前武器、姿势和配置状态
- **键盘快捷键**：支持多种快捷键操作
- **多分辨率支持**：支持2560x1440和2313x1440等多种分辨率
- **性能优化**：优化的图像处理算法，支持特征点匹配和模板匹配
- **基准测试**：完整的基准测试套件，用于性能评估
- **日志管理**：优化的日志系统，支持不同级别的日志输出
- **退出优化**：改进的退出流程，确保资源正确释放
- **临时图片管理**：可控制临时图片保存，减少磁盘I/O

## 系统要求

- Windows 10或更高版本
- Python 3.7或更高版本
- 至少4GB内存
- 支持的游戏分辨率：2560x1440, 2313x1440

## 安装

1. 克隆或下载本仓库
2. 安装依赖:

```bash
# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 快速启动

直接运行批处理文件：

```
run.bat
```

或者使用Python运行：

```bash
python run.py
```

### 命令行参数

程序支持以下命令行参数：

```bash
# 启用调试模式（详细日志输出）
python run.py --debug

# 指定分辨率
python run.py --resolution 2560x1440

# 保存临时图片（用于调试）
python run.py --save-temp

# 组合使用
python run.py --debug --resolution 2313x1440 --save-temp
```

### 运行基准测试

```bash
cd tests
run_benchmarks.bat
```

或者使用Python直接运行：

```bash
# 运行所有测试
python tests/run_benchmarks.py --all --resolution 2560x1440

# 只测试图像处理器
python tests/run_benchmarks.py --image --resolution 2560x1440

# 只测试动作处理器
python tests/run_benchmarks.py --action --resolution 2560x1440
```

### 比较匹配方法

```bash
cd tests
run_comparison.bat
```

### 快捷键说明

- `1`：切换/识别第一个武器槽
- `2`：切换/识别第二个武器槽
- `` ` ``（反引号）：锁定/解锁武器栏
- `0`：关闭宏
- `8`：切换匹配算法（特征点匹配/模板匹配）
- `9`：退出程序
- `NumLock`：切换武器配置状态（满配/裸配）

## 主要模块

### 配置模块

- **ResolutionConfig**：管理不同分辨率下的配置参数
  - 支持多种预定义分辨率（2560x1440, 2313x1440）
  - 自动选择合适的资源路径
  - 配置UI位置、武器识别区域和姿势检测区域

- **ConfigManager**：管理配置文件
  - 保存和加载配置
  - 管理武器名称列表
  - 支持配置持久化

### 处理器模块

- **ImageProcessor**：图像处理器
  - 支持特征点匹配和模板匹配两种算法
  - 武器识别
  - 姿势检测
  - 截图功能
  - 可选的临时图片保存功能

- **ActionProcessor**：动作处理器
  - 处理用户操作
  - 管理武器状态
  - 更新UI显示
  - 优化的退出流程

### 管理器模块

- **InputManager**：处理键盘和鼠标输入
  - 监听按键
  - 分发动作事件
  - 线程安全的退出机制
  - 优化的队列处理

- **UIManager**：管理用户界面
  - 显示当前状态
  - 更新显示内容
  - 优化的窗口创建和销毁

### 监控器模块

- **PostureMonitor**：监控玩家姿势
  - 定期检测姿势变化
  - 适应不同的游戏场景
  - 守护线程设计，确保主线程退出时自动退出
  - 改进的线程停止机制

### 核心模块

- **Logging**：日志管理
  - 可配置的日志级别
  - 分离的控制台和文件日志
  - 优化的日志格式

## 配置文件

程序使用以下配置文件：

- `gun_arr.json`：武器名称列表
- `gun.lua`：当前武器配置
- `posture.lua`：当前姿势配置

## 性能优化

最新版本包含以下性能优化：

1. **日志系统优化**
   - 降低控制台日志级别，减少I/O操作
   - 保留详细文件日志，便于后期分析
   - 添加直接控制台输出，提供关键事件反馈

2. **图像处理优化**
   - 可选的临时图片保存，减少磁盘写入
   - 优化特征点匹配和模板匹配算法
   - 改进姿势检测算法，提高准确性

3. **线程管理优化**
   - 守护线程设计，确保程序干净退出
   - 线程安全的队列处理
   - 超时参数，避免线程阻塞

4. **资源管理优化**
   - 改进的资源加载和释放流程
   - 优化窗口创建和销毁顺序
   - 安全的事件绑定和解除

可以通过以下方式进一步优化性能：

1. 调整匹配算法（特征点匹配/模板匹配）
2. 运行基准测试确定最佳配置
3. 根据具体硬件调整分辨率设置
4. 控制临时图片保存（仅在调试时启用）

## 故障排除

如果遇到问题：

1. 检查日志输出（位于logs目录）
2. 验证资源文件是否存在
3. 确认配置目录权限
4. 运行基准测试检查系统性能
5. 尝试使用`--debug`参数启动，获取更详细的日志
6. 如果出现图像识别问题，尝试使用`--save-temp`参数保存临时图片进行分析

## 开发

要设置开发环境:

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。 
@echo off
title PUBG Assistant v1.1.0
echo =========================================
echo         PUBG Assistant v1.1.0
echo         绝地求生游戏助手
echo =========================================
echo 正在初始化环境...

:: 检查Python环境
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到Python，请确保已安装Python并添加到PATH环境变量中。
    pause
    exit /b
)

:: 获取Python版本
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo 检测到Python版本: %PYTHON_VERSION%

:: 检查依赖
echo 检查依赖库...
python -c "import mss, cv2, numpy, pynput, PIL, pyttsx3" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [警告] 部分依赖库缺失，尝试安装...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [错误] 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b
    )
    echo 依赖安装完成！
) else (
    echo 依赖检查通过！
)

:: 运行程序
echo =========================================
echo 启动PUBG Assistant...
echo =========================================
python run.py %*

:: 如果异常退出，显示提示
if %ERRORLEVEL% neq 0 (
    echo.
    echo [错误] 程序异常退出，错误代码: %ERRORLEVEL%
    echo 请检查日志文件获取更多信息
    pause
) 
@echo off
echo PUBG Assistant 图像处理工具
echo ============================

rem 检查Python是否已安装
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH中。
    pause
    exit /b 1
)

rem 检查依赖库是否已安装
python -c "import cv2, numpy, matplotlib" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 警告: 可能缺少必要的依赖库。
    echo 请确保已安装以下依赖:
    echo - OpenCV (cv2)
    echo - NumPy
    echo - Matplotlib
    echo - mss (用于截图功能)
    
    echo.
    echo 是否要尝试安装这些依赖? (Y/N)
    set /p install=
    
    if /i "%install%"=="Y" (
        echo 正在安装依赖...
        python -m pip install opencv-python numpy matplotlib mss
    ) else (
        echo 已取消安装依赖。工具可能无法正常工作。
    )
)

rem 执行工具
if "%~1"=="" (
    echo.
    echo 用法: %~nx0 [命令] [参数...]
    echo.
    echo 可用命令:
    echo   grayscale         - 将图像转换为灰度图
    echo   threshold         - 对图像应用阈值处理
    echo   batch_threshold   - 批量对目录中的图像应用阈值处理
    echo   analyze           - 分析图像中的黑色区域
    echo   batch_analyze     - 批量分析目录中图像的黑色区域
    echo   match             - 匹配两个图像
    echo   multi             - 测试多个模板与目标图像的匹配
    echo   compare           - 比较不同匹配方法的效果
    echo   screenshot        - 使用截图测试模板匹配
    echo   enhance           - 增强图像
    echo.
    echo 使用 %~nx0 [命令] -h 获取特定命令的帮助。
    echo.
    
    rem 在没有参数的情况下，提供交互式选择
    echo 请选择要执行的命令:
    echo 1) grayscale        - 将图像转换为灰度图
    echo 2) threshold        - 对图像应用阈值处理
    echo 3) analyze          - 分析图像中的黑色区域
    echo 4) match            - 匹配两个图像
    echo 5) screenshot       - 使用截图测试模板匹配
    echo 6) enhance          - 增强图像
    echo 0) 退出
    
    set /p choice=请输入选择 (0-6): 
    
    if "%choice%"=="1" (
        set /p input=输入图像路径: 
        set /p output=输出图像路径 (可选，按Enter跳过): 
        
        if "%output%"=="" (
            python pubg_assistant\tools_runner.py grayscale "%input%"
        ) else (
            python pubg_assistant\tools_runner.py grayscale "%input%" -o "%output%"
        )
    ) else if "%choice%"=="2" (
        set /p input=输入图像路径: 
        set /p threshold=阈值 (0-255，可选，按Enter使用默认值200): 
        set /p output=输出图像路径 (可选，按Enter跳过): 
        
        set cmd=python pubg_assistant\tools_runner.py threshold "%input%"
        
        if not "%threshold%"=="" (
            set cmd=%cmd% -t %threshold%
        )
        
        if not "%output%"=="" (
            set cmd=%cmd% -o "%output%"
        )
        
        %cmd%
    ) else if "%choice%"=="3" (
        set /p input=输入图像路径: 
        set /p threshold=黑色区域阈值 (0-255，可选，按Enter使用默认值10): 
        set /p save=是否保存分析结果 (y/n，默认n): 
        set /p visualize=是否显示分析结果 (y/n，默认n): 
        
        set cmd=python pubg_assistant\tools_runner.py analyze "%input%"
        
        if not "%threshold%"=="" (
            set cmd=%cmd% -t %threshold%
        )
        
        if /i "%save%"=="y" (
            set cmd=%cmd% -s
        )
        
        if /i "%visualize%"=="y" (
            set cmd=%cmd% -v
        )
        
        %cmd%
    ) else if "%choice%"=="4" (
        set /p template=模板图像路径: 
        set /p target=目标图像路径: 
        set /p method=匹配方法 (original/template/enhanced/black_region，默认enhanced): 
        set /p show=是否显示匹配结果 (y/n，默认n): 
        set /p save=是否保存匹配结果 (y/n，默认n): 
        
        set cmd=python pubg_assistant\tools_runner.py match "%template%" "%target%"
        
        if not "%method%"=="" (
            set cmd=%cmd% -m %method%
        )
        
        if /i "%show%"=="y" (
            set cmd=%cmd% -s
        )
        
        if /i "%save%"=="y" (
            set cmd=%cmd% -v
        )
        
        %cmd%
    ) else if "%choice%"=="5" (
        set /p template=模板图像路径: 
        set /p coords=截图区域坐标 (left top width height，可选，按Enter截取全屏): 
        set /p save=是否保存截图 (y/n，默认n): 
        
        set cmd=python pubg_assistant\tools_runner.py screenshot "%template%"
        
        if not "%coords%"=="" (
            set cmd=%cmd% %coords%
        )
        
        if /i "%save%"=="y" (
            set cmd=%cmd% -s
        )
        
        %cmd%
    ) else if "%choice%"=="6" (
        set /p input=输入图像路径: 
        set /p output=输出图像路径 (可选，按Enter跳过): 
        
        set cmd=python pubg_assistant\tools_runner.py enhance "%input%"
        
        if not "%output%"=="" (
            set cmd=%cmd% -o "%output%"
        )
        
        %cmd%
    ) else if "%choice%"=="0" (
        echo 已退出。
        exit /b 0
    ) else (
        echo 无效的选择!
        pause
        exit /b 1
    )
) else (
    rem 传递所有参数给Python脚本
    python pubg_assistant\tools_runner.py %*
)

pause 
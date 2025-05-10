@echo off
REM PUBG Assistant Benchmark Test Script

echo PUBG Assistant Benchmark Test
echo ============================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

REM Set Python environment
set PYTHONPATH=%PROJECT_DIR%;%PYTHONPATH%

echo Select tests to run:
echo 1. All tests
echo 2. Image Processor tests only
echo 3. Action Processor tests only
echo.

set /p TEST_CHOICE="Enter your choice (1-3): "

echo.
echo Select resolution:
echo 1. 2560x1440 (default)
echo 2. 2313x1440
echo 3. Custom
echo.

set /p RES_CHOICE="Enter your choice (1-3): "

if "%RES_CHOICE%"=="2" (
    set RESOLUTION=2313x1440
) else if "%RES_CHOICE%"=="3" (
    set /p RESOLUTION="Enter custom resolution (format: widthxheight, e.g. 1920x1080): "
) else (
    set RESOLUTION=2560x1440
)

echo.
echo Starting tests with resolution: %RESOLUTION%
echo.

if "%TEST_CHOICE%"=="2" (
    python %SCRIPT_DIR%run_benchmarks.py --image --resolution %RESOLUTION%
) else if "%TEST_CHOICE%"=="3" (
    python %SCRIPT_DIR%run_benchmarks.py --action --resolution %RESOLUTION%
) else (
    python %SCRIPT_DIR%run_benchmarks.py --all --resolution %RESOLUTION%
)

echo.
echo Tests completed. Please check the results in tests\benchmark_results directory.
echo.

pause 
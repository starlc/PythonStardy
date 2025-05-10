@echo off
echo Running matching method comparison test for a single image...

REM Set path variables
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..
set FILENAME=%1

REM Check if filename parameter is provided
if "%FILENAME%"=="" (
    echo Error: No filename provided
    echo Usage: compare_single_file.bat image_filename
    echo Example: compare_single_file.bat test_image.png
    exit /b
)

REM Switch to project root directory
cd %PROJECT_DIR%

REM Run comparison with default ORB feature matching algorithm
echo.
echo === Running comparison with ORB algorithm for %FILENAME% ===
python %SCRIPT_DIR%\compare_matching_methods.py --file %FILENAME% --output comparison_single_orb.md
echo.

REM Run comparison with template matching algorithm
echo.
echo === Running comparison with template matching algorithm for %FILENAME% ===
python %SCRIPT_DIR%\compare_matching_methods.py --file %FILENAME% --toggle --output comparison_single_template.md
echo.

echo Test completed! Results have been saved to the tests directory
pause 
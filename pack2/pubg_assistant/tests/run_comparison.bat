@echo off
echo Running image matching method comparison test...

REM Set path variables
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

REM Switch to project root directory
cd %PROJECT_DIR%

REM Run comparison with default ORB feature matching algorithm
echo.
echo === Running comparison with default ORB feature matching algorithm ===
python %SCRIPT_DIR%\compare_matching_methods.py --output comparison_orb.md
echo.

REM Run comparison with template matching algorithm
echo.
echo === Running comparison with template matching algorithm ===
python %SCRIPT_DIR%\compare_matching_methods.py --toggle --output comparison_template.md
echo.

echo Test completed! Results have been saved to the tests directory
pause 
@echo off
REM Batch file to run the cuboid volume calculator
REM Make sure Python is installed and in your PATH

cd /d "%~dp0"
echo Running Molecular Cuboid Volume Calculator...
echo.

REM Try to run with python, if that fails try python3
python calculate_cuboid_volume.py
if errorlevel 1 (
    echo Python not found in PATH. Trying python3...
    python3 calculate_cuboid_volume.py
)

if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in your system PATH.
    echo Please install Python from https://www.python.org/
    echo.
    echo Required package: numpy
    echo Install with: pip install numpy
    echo.
    pause
)

echo.
echo Script completed! Check cuboid_volumes.csv for results.
pause


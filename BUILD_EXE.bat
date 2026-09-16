@echo off
REM SONY Credentials - Build Executable for Windows
REM This script builds SONY_Credentials.exe

echo.
echo ========================================
echo  SONY Credentials - Building EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12 or newer from python.org
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Building executable...
echo This may take 2-3 minutes...
echo.

python build_exe.py
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo  BUILD COMPLETE!
echo ========================================
echo.
echo Your executable is in: dist\SONY_Credentials.exe
echo.
echo Next steps:
echo   1. Test the executable: dist\SONY_Credentials.exe
echo   2. Copy to deployment location
echo   3. Distribute to staff
echo.
pause

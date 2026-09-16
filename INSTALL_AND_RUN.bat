@echo off
REM SONY Credentials - Simple Installation & Launch
REM This script installs dependencies and runs the app directly
REM No exe building required!

echo.
echo ========================================
echo  SONY Credentials - Installation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo.
    echo Please install Python from: https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version

echo.
echo Step 1: Installing dependencies...
echo This may take 1-2 minutes on first run...
echo.

pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Starting SONY Credentials...
echo.
echo The application will open in your browser.
echo Press Ctrl+C in this window to stop the server.
echo.

timeout /t 2

REM Start the Flask app
python app.py

@echo off
REM Zeyta AI Web Application - Quick Start Script for Windows
REM This script installs all dependencies and starts the server

echo ========================================
echo   Zeyta AI Web Application
echo   Quick Start Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python version...
python --version

echo.
echo [2/3] Installing dependencies...
echo This may take 5-15 minutes depending on your internet speed.
echo Large packages like PyTorch will be downloaded...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install.
    echo The server will attempt to install missing packages on startup.
    echo.
)

echo.
echo [3/3] Starting Zeyta AI Web Server...
echo.

REM ============================================================================
REM SYSTEM INTEGRITY CHECK
REM ============================================================================
echo 🔍 Checking system integrity...

REM 1. Ensure Critical Directories Exist
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads
if not exist "chat_logs" mkdir chat_logs
if not exist "agent_screenshots" mkdir agent_screenshots
if not exist "debug_files" mkdir debug_files
if not exist "models\piper" mkdir models\piper

REM 2. Check for Chatterbox Python 3.11 Venv
if not exist "venv_chatterbox" (
    echo ⚠️  Chatterbox venv (Python 3.11) not found!
    echo    Initializing smart setup script...
    
    REM Call the smart setup script (Python)
    python setup\smart_setup.py
    
    if errorlevel 1 (
        echo ❌ Failed to create Chatterbox venv.
    ) else (
        echo ✅ Chatterbox venv created successfully.
    )
) else (
    echo ✅ Chatterbox venv found.
)
echo.

echo The server will open on https://localhost:5000
echo (Accept the self-signed certificate warning in your browser)
echo Press Ctrl+C to stop the server
echo.

REM Add cuDNN to PATH for GPU acceleration
set "CUDNN_PATH=C:\Users\Rayan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\nvidia\cudnn\bin"
set "PATH=%CUDNN_PATH%;%PATH%"
echo ✅ cuDNN added to PATH for GPU support
echo.

python web_app.py

pause

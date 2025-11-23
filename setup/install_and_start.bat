@echo off
REM Zeyta AI - Python 3.12 Compatible Installation Script
echo ========================================
echo   Zeyta AI - Dependency Installer
echo   Python 3.12+ Compatible
echo ========================================
echo.

REM Check Python version
python --version
echo.

echo [Step 1/4] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade build tools
    pause
    exit /b 1
)
echo ✅ Build tools upgraded
echo.

echo [Step 2/4] Installing core packages...
python -m pip install flask flask-cors flask-socketio werkzeug python-socketio
if errorlevel 1 (
    echo ⚠️  Warning: Some web framework packages failed
)
echo.

echo [Step 3/4] Installing PyTorch (this may take 5-10 minutes)...
echo Downloading ~2GB, please be patient...
python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
if errorlevel 1 (
    echo Trying CPU-only version...
    python -m pip install torch torchaudio
)
echo.

echo [Step 4/4] Installing AI packages...
python -m pip install numpy>=1.26.0 scipy>=1.11.4
python -m pip install transformers sounddevice soundfile
python -m pip install faster-whisper webrtcvad

REM Try to install chatterbox-tts (may fail, but optional)
echo.
echo Installing TTS (optional, may fail)...
python -m pip install chatterbox-tts
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Starting Zeyta AI Web Server...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python web_app.py

pause

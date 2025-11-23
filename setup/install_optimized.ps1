# Installation script for optimized TTS with PyTorch nightly
# Supports RTX 50-series GPUs (Blackwell architecture)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Optimized TTS Installation Script" -ForegroundColor Cyan
Write-Host "RTX 50-Series GPU Support" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip, setuptools, and wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

# Uninstall existing PyTorch (if any)
Write-Host ""
Write-Host "Removing existing PyTorch installations..." -ForegroundColor Yellow
pip uninstall -y torch torchvision torchaudio

# Install PyTorch nightly with CUDA 12.4 support
Write-Host ""
Write-Host "Installing PyTorch nightly with CUDA 12.4 (RTX 50-series support)..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124

# Install Triton for torch.compile
Write-Host ""
Write-Host "Installing Triton for torch.compile optimizations..." -ForegroundColor Yellow
pip install triton

# Install other dependencies
Write-Host ""
Write-Host "Installing other dependencies..." -ForegroundColor Yellow
pip install psutil numpy scipy sounddevice soundfile librosa transformers
pip install flask flask-cors flask-socketio werkzeug
pip install faster-whisper webrtcvad
pip install requests pillow pyautogui pywin32
pip install python-socketio

# Install TTS engines
Write-Host ""
Write-Host "Installing TTS engines..." -ForegroundColor Yellow
pip install pyttsx3

# Try to install Chatterbox (may have compatibility issues)
Write-Host ""
Write-Host "Attempting to install Chatterbox TTS..." -ForegroundColor Yellow
Write-Host "(Note: Chatterbox may have NumPy version conflicts)" -ForegroundColor Gray
pip install chatterbox-tts
if ($LASTEXITCODE -ne 0) {
    Write-Host "Chatterbox installation failed - you may need to install in a separate venv" -ForegroundColor Red
}

# Try to install Piper
Write-Host ""
Write-Host "Attempting to install Piper TTS..." -ForegroundColor Yellow
pip install piper-tts
if ($LASTEXITCODE -ne 0) {
    Write-Host "Piper installation failed - trying alternative..." -ForegroundColor Yellow
    pip install piper
}

# Verify PyTorch installation
Write-Host ""
Write-Host "Verifying PyTorch installation..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To test the optimized TTS:" -ForegroundColor Cyan
    Write-Host "  python tts_test_optimized.py" -ForegroundColor White
    Write-Host ""
    Write-Host "To see optimizer capabilities:" -ForegroundColor Cyan
    Write-Host "  python tts_optimizer_advanced.py" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Installation completed with warnings" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "PyTorch verification failed. Check errors above." -ForegroundColor Yellow
}

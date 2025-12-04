# Zeyta AI Web Application - PowerShell Start Script
# This script ensures cuDNN is in PATH for GPU acceleration
# NumPy 1.26.4 is used for binary compatibility

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Zeyta AI Web Application" -ForegroundColor Cyan
Write-Host "   Starting with GPU Support" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# FORCE DISCRETE GPU USAGE (NVIDIA RTX 5070 Ti)
$env:CUDA_VISIBLE_DEVICES = "0"
$env:OLLAMA_NUM_GPU = "1"
$env:OLLAMA_GPU_LAYERS = "99"  # Force ALL layers to GPU
$env:CUDA_DEVICE_ORDER = "PCI_BUS_ID"
Write-Host "🎮 GPU Configuration:" -ForegroundColor Magenta
Write-Host "   CUDA_VISIBLE_DEVICES = $env:CUDA_VISIBLE_DEVICES" -ForegroundColor White
Write-Host "   OLLAMA_NUM_GPU = $env:OLLAMA_NUM_GPU" -ForegroundColor White
Write-Host "   OLLAMA_GPU_LAYERS = $env:OLLAMA_GPU_LAYERS (force all layers)" -ForegroundColor White
Write-Host "   Forcing NVIDIA RTX 5070 Ti (discrete GPU)" -ForegroundColor Green
Write-Host ""

# Add cuDNN to PATH
$cudnnPath = "C:\Users\Rayan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\nvidia\cudnn\bin"
$env:PATH = "$cudnnPath;$env:PATH"
Write-Host "✅ cuDNN added to PATH for GPU acceleration" -ForegroundColor Green
Write-Host ""

# Check if cuDNN DLLs exist
if (Test-Path "$cudnnPath\cudnn_ops64_9.dll") {
    Write-Host "✅ cuDNN DLLs found - GPU acceleration enabled" -ForegroundColor Green
} else {
    Write-Host "⚠️  cuDNN DLLs not found - will use CPU mode" -ForegroundColor Yellow
    Write-Host "   Run: pip install nvidia-cudnn-cu12" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# SYSTEM INTEGRITY CHECK
# ============================================================================
Write-Host "🔍 Checking system integrity..." -ForegroundColor Cyan

# 1. Ensure Critical Directories Exist
$criticalDirs = @("models", "uploads", "chat_logs", "agent_screenshots", "debug_files", "models/piper")
foreach ($dir in $criticalDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✅ Created missing directory: $dir" -ForegroundColor Green
    }
}

# 2. Check for Chatterbox Python 3.11 Venv (Required for TTS)
$venvPath = ".\venv_chatterbox"
if (-not (Test-Path $venvPath)) {
    Write-Host "⚠️  Chatterbox venv (Python 3.11) not found!" -ForegroundColor Yellow
    Write-Host "   Initializing setup script..." -ForegroundColor Gray
    
    if (Test-Path ".\setup\setup_chatterbox.ps1") {
        # Run the setup script
        & ".\setup\setup_chatterbox.ps1"
        
        if ($LASTEXITCODE -eq 0) {
             Write-Host "✅ Chatterbox venv created successfully." -ForegroundColor Green
        } else {
             Write-Host "❌ Failed to create Chatterbox venv." -ForegroundColor Red
             # We don't exit here, as the main app might still run without TTS
        }
    } else {
        Write-Host "❌ Error: setup_chatterbox.ps1 not found in .\setup\" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Chatterbox venv found." -ForegroundColor Green
}
Write-Host ""

# Start the web server
Write-Host "🚀 Starting web server..." -ForegroundColor Cyan
Write-Host "   Server will be available at: https://localhost:5000" -ForegroundColor White
Write-Host "   (Accept the self-signed certificate warning in your browser)" -ForegroundColor Gray
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor White
Write-Host ""

# Use the correct Python path
$pythonPath = "C:/Users/Rayan/AppData/Local/Microsoft/WindowsApps/python3.11.exe"
& $pythonPath web_app.py

Write-Host ""
Write-Host "Server stopped. Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

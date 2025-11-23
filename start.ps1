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

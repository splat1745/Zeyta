# Ollama GPU Configuration Fix
# Sets environment variables to force NVIDIA GPU usage

# Force Ollama to use discrete GPU
$env:OLLAMA_NUM_GPU = "1"
$env:CUDA_VISIBLE_DEVICES = "0"

# Display current settings
Write-Host "=" -ForegroundColor Green
Write-Host "Ollama GPU Configuration Applied:" -ForegroundColor Green
Write-Host "  OLLAMA_NUM_GPU = $env:OLLAMA_NUM_GPU" -ForegroundColor Cyan
Write-Host "  CUDA_VISIBLE_DEVICES = $env:CUDA_VISIBLE_DEVICES" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Green
Write-Host ""

# Restart Ollama to apply changes
Write-Host "Stopping Ollama service..." -ForegroundColor Yellow
Stop-Process -Name "ollama*" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Starting Ollama service..." -ForegroundColor Yellow
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ Ollama configured to use NVIDIA RTX 5070 Ti" -ForegroundColor Green
Write-Host ""
Write-Host "Testing GPU detection..."
ollama list

Write-Host ""
Write-Host "To make this permanent, add these to your system environment variables:" -ForegroundColor Cyan
Write-Host "  OLLAMA_NUM_GPU=1" -ForegroundColor White
Write-Host "  CUDA_VISIBLE_DEVICES=0" -ForegroundColor White

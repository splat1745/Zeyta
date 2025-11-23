# Fix Ollama GPU Configuration - Force RTX 5070 Ti Usage
# This script configures Ollama service to use discrete GPU

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ollama GPU Configuration Fix" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Stop Ollama service
Write-Host "[1/5] Stopping Ollama service..." -ForegroundColor Yellow
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Set system environment variables for Ollama
Write-Host "[2/5] Setting system environment variables..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable("CUDA_VISIBLE_DEVICES", "0", [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_GPU", "1", [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("OLLAMA_GPU_LAYERS", "99", [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("CUDA_DEVICE_ORDER", "PCI_BUS_ID", [System.EnvironmentVariableTarget]::User)

Write-Host "   ✓ CUDA_VISIBLE_DEVICES = 0" -ForegroundColor Green
Write-Host "   ✓ OLLAMA_NUM_GPU = 1" -ForegroundColor Green
Write-Host "   ✓ OLLAMA_GPU_LAYERS = 99" -ForegroundColor Green
Write-Host "   ✓ CUDA_DEVICE_ORDER = PCI_BUS_ID" -ForegroundColor Green

# Set current session environment variables
Write-Host "`n[3/5] Setting session environment variables..." -ForegroundColor Yellow
$env:CUDA_VISIBLE_DEVICES = "0"
$env:OLLAMA_NUM_GPU = "1"
$env:OLLAMA_GPU_LAYERS = "99"
$env:CUDA_DEVICE_ORDER = "PCI_BUS_ID"

# Restart Ollama with correct environment
Write-Host "`n[4/5] Starting Ollama with GPU configuration..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 5

# Test Ollama connection
Write-Host "`n[5/5] Testing Ollama connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Ollama is running and accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Could not connect to Ollama" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Configuration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run this script: .\fix_ollama_gpu.ps1" -ForegroundColor White
Write-Host "2. Close and reopen PowerShell" -ForegroundColor White
Write-Host "3. Run start.ps1 to launch the app" -ForegroundColor White
Write-Host "4. Test with: nvidia-smi (should show VRAM usage when model runs)" -ForegroundColor White

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

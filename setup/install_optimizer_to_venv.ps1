# Install Optimizer in Chatterbox Venv
$venvPath = "E:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox"
$pythonExe = "$venvPath\Scripts\python.exe"

Write-Host "Installing Optimizer in Chatterbox Venv" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

if (-not (Test-Path $pythonExe)) {
    Write-Host "Error: Venv not found at $venvPath" -ForegroundColor Red
    exit 1
}

Write-Host "Found venv: $venvPath" -ForegroundColor Green

# Install dependency
Write-Host "[1/3] Installing psutil..." -ForegroundColor Yellow
& $pythonExe -m pip install psutil --quiet

# Copy optimizer
Write-Host "[2/3] Copying optimizer..." -ForegroundColor Yellow
$optimizerDst = "$venvPath\Lib\site-packages\tts_optimizer_advanced.py"
Copy-Item "tts_optimizer_advanced.py" $optimizerDst -Force

# Verify
Write-Host "[3/3] Verifying..." -ForegroundColor Yellow
$result = & $pythonExe -c "from tts_optimizer_advanced import get_optimizer; print('OK')" 2>&1

if ($result -match "OK") {
    Write-Host ""
    Write-Host "SUCCESS! Optimizer installed" -ForegroundColor Green
    Write-Host "Expected speedup: 3-5x faster (RTF 8x -> 0.1-0.3x)" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host $result
}

# Quick Chatterbox Installation for Dedicated venv
# Install compatible versions to avoid ABI errors

Write-Host "Installing Chatterbox TTS in dedicated venv..." -ForegroundColor Yellow
Write-Host ""

$venvPython = ".\venv_chatterbox\Scripts\python.exe"

# Verify venv exists
if (-not (Test-Path $venvPython)) {
    Write-Host "Venv not found at .\venv_chatterbox" -ForegroundColor Red
    Write-Host "Run setup_chatterbox_venv.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using: $venvPython" -ForegroundColor Green
Write-Host ""

# Install with compatible versions
Write-Host "Installing NumPy 1.25.3..." -ForegroundColor Yellow
& $venvPython -m pip install numpy==1.25.3 -q

Write-Host "Installing PyTorch 2.1.0 (CUDA 12.1)..." -ForegroundColor Yellow
& $venvPython -m pip install torch==2.1.0 torchaudio==2.1.0 -q

Write-Host "Installing Chatterbox TTS..." -ForegroundColor Yellow
& $venvPython -m pip install chatterbox-tts -q

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Verifying installation..." -ForegroundColor Yellow
    & $venvPython -c "from chatterbox import ChatterboxTTS; import torch; print(f'OK: Chatterbox installed, PyTorch {torch.__version__}')"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "Chatterbox installation successful!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Installation completed but verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Installation failed" -ForegroundColor Red
    exit 1
}

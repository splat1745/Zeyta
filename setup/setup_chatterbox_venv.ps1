# Setup dedicated Chatterbox virtual environment with compatible dependencies
# This isolates Chatterbox from main venv to avoid version conflicts

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Chatterbox Virtual Environment Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$venvPath = "venv_chatterbox"
$pythonPath = ".\$venvPath\Scripts\python.exe"

# Check if venv already exists
if (Test-Path $venvPath) {
    Write-Host "Using existing venv at $venvPath" -ForegroundColor Green
} else {
    Write-Host "Creating new venv at $venvPath..." -ForegroundColor Yellow
    python -m venv $venvPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Venv created successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to create venv" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Activating venv and upgrading pip..." -ForegroundColor Yellow
& $pythonPath -m pip install --upgrade pip setuptools wheel

Write-Host ""
Write-Host "Installing PyTorch (CUDA 12.1 compatible)..." -ForegroundColor Yellow
& $pythonPath -m pip install torch==2.1.0+cu121 torchaudio==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121

Write-Host ""
Write-Host "Installing Chatterbox TTS..." -ForegroundColor Yellow
& $pythonPath -m pip install chatterbox-tts

Write-Host ""
Write-Host "Installing audio dependencies..." -ForegroundColor Yellow
& $pythonPath -m pip install numpy soundfile librosa

Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow
& $pythonPath -c "
import torch
from chatterbox import ChatterboxTTS
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'Chatterbox: OK')
"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Chatterbox venv setup complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To use Chatterbox:" -ForegroundColor Cyan
    Write-Host "  Set environment variable: `$env:CHATTERBOX_PYTHON='$(Resolve-Path $pythonPath)'" -ForegroundColor White
    Write-Host "  Or set permanently in PowerShell profile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Python path: $(Resolve-Path $pythonPath)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Chatterbox venv setup failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit 1
}

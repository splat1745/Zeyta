<#
PowerShell helper: create a venv and install Chatterbox + optional PyTorch. 
Usage:
  .\setup_chatterbox.ps1 [-VenvPath <path>] [-InstallTorch]

Notes:
  - This script assumes you have a working Python 3.12+ installed on PATH
  - If you want to install a specific PyTorch CUDA build, use -InstallTorch to attempt a cu128 nightly install
  - If you prefer a different location, pass -VenvPath like `-VenvPath .\.venv_chatterbox`
#>

param(
    [string]$VenvPath = ".\venv_chatterbox",
    [switch]$InstallTorch
)

$ErrorActionPreference = 'Stop'

Write-Host "Setting up venv at $VenvPath..."
$fullPath = (Resolve-Path -Path $VenvPath -ErrorAction SilentlyContinue)
if (-Not $fullPath) {
    python -m venv $VenvPath
    $fullPath = (Resolve-Path -Path $VenvPath)
}
$venvPython = Join-Path -Path $fullPath -ChildPath 'Scripts\python.exe'

Write-Host "Upgrading pip and common packages in venv..."
& $venvPython -m pip install --upgrade pip setuptools wheel

if ($InstallTorch) {
    Write-Host "Installing PyTorch nightly cu128 (you may want to change this based on your CUDA setup)..."
    Write-Host "This will install torch 2.7+ with CUDA 12.8 support for RTX 50-series GPUs"
    & $venvPython -m pip install --pre --extra-index-url https://download.pytorch.org/whl/nightly/cu128 torch torchvision torchaudio --upgrade
}
else {
    Write-Host "Skipping PyTorch install (use -InstallTorch to install nightly cu128)"
    Write-Host "If torch is not installed, chatterbox-tts may fail or use CPU-only torch"
}

Write-Host "Installing chatterbox-tts, soundfile, and numpy in venv..."
& $venvPython -m pip install chatterbox-tts soundfile numpy

# Verify installation
$ok = $false
try {
    $out = & $venvPython -c "import importlib, torch; print('PYTHON=',__import__('sys').executable); print('Torch', torch.__version__, 'CUDA', torch.cuda.is_available()); print('CHATTERBOX', importlib.util.find_spec('chatterbox') is not None)"
    Write-Host $out
    $ok = $true
} catch {
    Write-Host "Installation succeeded but quick import check failed: $_" -ForegroundColor Yellow
}

# Set CHATTERBOX_PYTHON env var persistently for the current user
$venvPythonFull = (Resolve-Path -Path $venvPython).Path
Write-Host "Setting CHATTERBOX_PYTHON to $venvPythonFull"
setx CHATTERBOX_PYTHON $venvPythonFull
Write-Host "NOTE: You may need to close and reopen PowerShell / VSCode to pick up the new environment variable."

if ($ok) {
    Write-Host "Setup finished. You can now run the main web app with the system python or in the main environment and subprocess chatterbox will use the venv." -ForegroundColor Green
} else {
    Write-Host "Setup finished but import checks failed — please check logs above for import errors and re-run the script with -InstallTorch if needed." -ForegroundColor Yellow
}

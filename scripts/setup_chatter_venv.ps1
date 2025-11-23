# PowerShell script to create a venv for Chatterbox TTS compatible with CUDA and a specific torch version.
# Usage:
#   .\setup_chatter_venv.ps1 -path 'E:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox' -torchVersion '2.1.0' -cuda 'cu128'
param(
    [string]$path = "venv_chatterbox",
    [string]$torchVersion = "2.1.0",
    [string]$cuda = "cu128"
)

Write-Host "Creating Python venv at $path"
python -m venv $path
& "$path\Scripts\Activate.ps1"

Write-Host "Upgrading pip and wheel"
python -m pip install --upgrade pip setuptools wheel

Write-Host "Installing Torch $torchVersion for CUDA $cuda - will use the official pytorch index"
$indexUrl = "https://download.pytorch.org/whl/$cuda"
python -m pip install --index-url $indexUrl -f $indexUrl "torch==$torchVersion" "torchaudio==$torchVersion"

Write-Host "Installing Chatterbox and a compatible numpy" 
# Numpy pinned to a known range; you can adjust if needed
python -m pip install numpy==1.25.3
python -m pip install chatterbox-tts

Write-Host 'Setup complete. To use, run:'
Write-Host "  & '$path\Scripts\Activate.ps1'"
Write-Host "Then set CHATTERBOX_PYTHON to your venv python path:"
Write-Host "  setx CHATTERBOX_PYTHON \"$($PWD.Path)\\$path\\Scripts\\python.exe\""
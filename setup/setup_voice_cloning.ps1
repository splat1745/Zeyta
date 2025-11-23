# =============================================================================
# Voice Cloning Setup - Plug and Play
# =============================================================================
# Automatically configures the voice cloning system for Chatterbox TTS
# Requires: Python 3.11+, venv_chatterbox, ShinobuResolve.wav
# =============================================================================

# Color output
function Write-Status { Write-Host "[*] $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }
function Write-Warn { Write-Host "[WARN] $args" -ForegroundColor Yellow }
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Blue }

Write-Host ""
Write-Host "=========================================================================="
Write-Host "         VOICE CLONING WITH CHATTERBOX - PLUG AND PLAY SETUP"
Write-Host "=========================================================================="
Write-Host ""

# Find Python 3.11
Write-Status "Searching for Python 3.11..."
$Python311 = $null
$SearchPaths = @(
    "C:\Users\Rayan\AppData\Local\Microsoft\WindowsApps\python3.11.exe",
    "C:\Users\Rayan\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files (x86)\Python311\python.exe"
)

foreach ($path in $SearchPaths) {
    if (Test-Path $path) {
        Write-Success "Found Python 3.11 at: $path"
        $Python311 = $path
        break
    }
}

if (-not $Python311) {
    Write-Error "Could not find Python 3.11. Please install Python 3.11 and try again."
    exit 1
}

# Verify Python 3.11 version
$version = & $Python311 --version 2>&1
Write-Success "Python version: $version"

# Check for venv_chatterbox
Write-Status "Searching for venv_chatterbox..."
$venvPath = $null
$SearchDirs = @(
    "$PSScriptRoot\venv_chatterbox",
    "$PSScriptRoot\..\venv_chatterbox",
    "$PSScriptRoot\..\..\venv_chatterbox"
)

foreach ($dir in $SearchDirs) {
    $fullPath = Resolve-Path $dir -ErrorAction SilentlyContinue
    if ($null -ne $fullPath) {
        if (Test-Path "$fullPath\Scripts\python.exe") {
            Write-Success "Found venv_chatterbox at: $fullPath"
            $venvPath = $fullPath
            break
        }
    }
}

if (-not $venvPath) {
    Write-Warn "venv_chatterbox not found. Creating new venv..."
    $venvPath = "$PSScriptRoot\venv_chatterbox"
    & $Python311 -m venv $venvPath
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Created venv at: $venvPath"
    } else {
        Write-Error "Failed to create venv"
        exit 1
    }
}

# Install dependencies in venv
Write-Status "Installing dependencies in venv..."
$venvPython = "$venvPath\Scripts\python.exe"

# Upgrade pip first
Write-Info "Upgrading pip..."
& $venvPython -m pip install --upgrade pip -q
if ($LASTEXITCODE -ne 0) {
    Write-Warn "pip upgrade had issues, continuing..."
}

# Install PyTorch CUDA 12.8 nightly
Write-Info "Installing PyTorch CUDA 12.8 nightly (this may take a few minutes)..."
& $venvPython -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 -q
if ($LASTEXITCODE -eq 0) {
    Write-Success "PyTorch installed"
} else {
    Write-Error "Failed to install PyTorch"
    exit 1
}

# Install Chatterbox TTS
Write-Info "Installing Chatterbox TTS..."
& $venvPython -m pip install chatterbox-tts soundfile scipy -q
if ($LASTEXITCODE -eq 0) {
    Write-Success "Chatterbox TTS installed"
} else {
    Write-Warn "Chatterbox TTS installation may have had issues"
}

# Verify Chatterbox is installed
Write-Status "Verifying Chatterbox installation..."
& $venvPython -c "import chatterbox; print('Chatterbox version:', getattr(chatterbox, '__version__', 'unknown'))" 2>&1 | Select-Object -Last 1 | ForEach-Object {
    if ($_ -match "Chatterbox") {
        Write-Success $_
    } else {
        Write-Warn "Chatterbox verification inconclusive"
    }
}

# Check for reference audio
Write-Status "Searching for ShinobuResolve.wav reference audio..."
$audioFiles = @(
    "$PSScriptRoot\ShinobuResolve.wav",
    "$PSScriptRoot\uploads\ShinobuResolve.wav"
)

$audioFound = $false
foreach ($audio in $audioFiles) {
    if (Test-Path $audio) {
        Write-Success "Found reference audio: $audio"
        $audioFound = $true
        break
    }
}

if (-not $audioFound) {
    Write-Warn "ShinobuResolve.wav not found in expected locations"
    Write-Info "Please ensure ShinobuResolve.wav is in $PSScriptRoot or $PSScriptRoot\uploads"
}

# Display summary
Write-Host ""
Write-Host "=========================================================================="
Write-Host "                         SETUP COMPLETE"
Write-Host "=========================================================================="
Write-Host ""
Write-Success "Python 3.11: $Python311"
Write-Success "venv path: $venvPath"
Write-Success "venv Python: $venvPython"

Write-Host ""
Write-Info "To run voice cloning test:"
Write-Host ""
Write-Host "    # Option 1: Automatic (recommended)"
Write-Host "    python voice_clone_test.py"
Write-Host ""
Write-Host "    # Option 2: Direct with Python 3.11"
Write-Host "    $Python311 voice_clone_test.py"
Write-Host ""

Write-Host "=========================================================================="
Write-Host ""

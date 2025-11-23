#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick test runner using the venv_chatterbox Python interpreter directly
    
.DESCRIPTION
    This bypasses the system Python 3.11 (which has CPU-only torch 2.6) and runs
    the TTS optimizer tests using the venv_chatterbox Python (which has CUDA torch nightly).
    
.PARAMETER Ref
    Path to reference audio file for voice cloning (default: uploads/ShinobuResolve.wav)
    
.PARAMETER Runs
    Number of benchmark runs per test (default: 5)
    
.EXAMPLE
    .\run_tts_test_venv.ps1
    .\run_tts_test_venv.ps1 -Ref "uploads/ShinobuResolve.wav" -Runs 3
#>

param(
    [string]$Ref = "uploads\ShinobuResolve.wav",
    [int]$Runs = 5
)

$venvPython = ".\venv_chatterbox\Scripts\python.exe"

if (-Not (Test-Path $venvPython)) {
    Write-Host "venv_chatterbox not found. Run setup_chatterbox.ps1 first:" -ForegroundColor Red
    Write-Host "  .\setup_chatterbox.ps1 -InstallTorch" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using venv python: $venvPython" -ForegroundColor Green
Write-Host "Reference audio: $Ref"
Write-Host "Runs per test: $Runs"
Write-Host ""

# Run test_tts_optimizations.py directly with the venv python
& $venvPython test_tts_optimizations.py --ref $Ref --runs $Runs

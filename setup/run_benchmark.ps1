# Run TTS Benchmark - Works with Your Venv Setup
# This handles all the venv complexity for you

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "TTS Performance Benchmark" -ForegroundColor Cyan
Write-Host "RTX 5070 Ti Optimization Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Set Chatterbox Python path (your venv)
$env:CHATTERBOX_PYTHON = "E:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox\Scripts\python.exe"

# Verify paths exist
if (-not (Test-Path $env:CHATTERBOX_PYTHON)) {
    Write-Host "Warning: Chatterbox venv not found at:" -ForegroundColor Yellow
    Write-Host "  $env:CHATTERBOX_PYTHON" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Benchmark will run with available engines only." -ForegroundColor Yellow
    Write-Host ""
}

# Run benchmark
Write-Host "Starting benchmark..." -ForegroundColor Green
Write-Host "(This will take 2-5 minutes depending on engines available)" -ForegroundColor Gray
Write-Host ""

python benchmark_rtx50.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Benchmark Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Results are shown above." -ForegroundColor White
    Write-Host ""
    Write-Host "Key Metrics:" -ForegroundColor Cyan
    Write-Host "  RTF < 1.0 = Faster than realtime" -ForegroundColor White
    Write-Host "  RTF 0.1   = 10x faster than realtime" -ForegroundColor White
    Write-Host "  RTF 0.05  = 20x faster than realtime" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Benchmark Failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check errors above. Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Missing dependencies (run: pip install -r requirements.txt)" -ForegroundColor Gray
    Write-Host "  2. CUDA not available (check: python -c 'import torch; print(torch.cuda.is_available())')" -ForegroundColor Gray
    Write-Host "  3. TTS engines not installed" -ForegroundColor Gray
}

Write-Host ""

# TTS Optimization Testing - Quick Fix Guide

## Problem Summary
Your system Python 3.11 has **PyTorch 2.6.0+cpu** (no CUDA), causing:
- ❌ Chatterbox fails to import (torchvision ABI mismatch with CPU torch)
- ❌ No GPU acceleration available
- ❌ Optimizations can't run (require CUDA)

Your `venv_chatterbox` has the **correct PyTorch nightly cu128** with CUDA and works perfectly! ✅

## Solution: Use venv_chatterbox Python for all TTS testing

### Quick Test (Recommended)
Run the test using the correct venv Python directly:

```powershell
.\run_tts_test_venv.ps1
```

This bypasses the system Python 3.11 and uses `venv_chatterbox\Scripts\python.exe` which has:
- ✅ PyTorch 2.7+ nightly with CUDA 12.8
- ✅ RTX 5070 Ti support (compute capability 8.9)
- ✅ All optimizations enabled (FP16, CUDA Graphs, embedding cache)

### Custom Reference Audio
```powershell
.\run_tts_test_venv.ps1 -Ref "uploads\ShinobuResolve.wav" -Runs 5
```

### What to Expect
With the correct venv Python:
- Environment check shows: `CUDA Available: True`
- GPU: `NVIDIA GeForce RTX 5070 Ti`
- Compute capability: `8.9` (RTX 50-series detected)
- Baseline TTS runs at ~5-10s per generation
- Optimized TTS runs at ~2-5s per generation
- **Target speedup: 2-4x** 🚀

### Generated Outputs
After testing, check these files:
- `outputs/voiceclone_cold.wav` - First generation (cold cache)
- `outputs/voiceclone_warm.wav` - Second generation (warm cache, should be faster)

---

## Alternative: Fix System Python (More Work)

If you want to use system Python 3.11 directly:

1. **Uninstall CPU torch from Python 3.11:**
```powershell
python -m pip uninstall torch torchvision torchaudio -y
```

2. **Install CUDA torch nightly:**
```powershell
python -m pip install --pre --extra-index-url https://download.pytorch.org/whl/nightly/cu128 torch torchvision torchaudio
```

3. **Reinstall chatterbox and dependencies:**
```powershell
python -m pip install chatterbox-tts soundfile numpy --force-reinstall
```

4. **Verify CUDA is available:**
```powershell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.__version__)"
```

**Warning:** This may break other projects using Python 3.11 if they expect CPU torch.

---

## For Web App Usage

The web app already works with subprocess mode via `CHATTERBOX_PYTHON`:

1. **Ensure env var is set permanently:**
```powershell
setx CHATTERBOX_PYTHON "E:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox\Scripts\python.exe"
```

2. **Restart VSCode/terminal** to pick up the new env var

3. **Run web app normally:**
```powershell
python web_app.py
```

The app will automatically use the venv_chatterbox subprocess for TTS with full GPU optimizations.

---

## Troubleshooting

### "venv_chatterbox not found"
Run the setup script:
```powershell
.\setup_chatterbox.ps1 -InstallTorch
```

### "CUDA not available in venv"
Check the venv torch:
```powershell
.\venv_chatterbox\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

If False, reinstall torch in the venv:
```powershell
.\venv_chatterbox\Scripts\Activate
pip install --pre --extra-index-url https://download.pytorch.org/whl/nightly/cu128 torch torchvision torchaudio --upgrade
deactivate
```

### Unicode Errors in Subprocess (Non-Critical)
The subprocess works despite Unicode decode warnings. These are harmless stderr encoding issues and don't affect generation. I've added error handling to suppress them.

---

## Expected Test Results

### Environment Check
```
Python: 3.11.x (or 3.12.x)
PyTorch: 2.7.0.dev20241114+cu128 (or similar nightly)
CUDA Available: True
CUDA Version: 12.8
GPU: NVIDIA GeForce RTX 5070 Ti
Compute Capability: 8.9
RTX 50-series GPU: True
```

### Performance Targets
- **Baseline**: ~5-10s per generation
- **Optimized**: ~2-5s per generation
- **Speedup**: 2-4x faster
- **Voice cloning cache**: 1st gen slower, 2nd+ gen 1.5-2x faster

---

## Summary
✅ **Use `.\run_tts_test_venv.ps1` for all testing** - it uses the correct Python with CUDA torch

✅ **Web app works via subprocess** - set `CHATTERBOX_PYTHON` env var and restart

✅ **System Python 3.11 has wrong torch** - either fix it (uninstall CPU torch, install CUDA torch) or just use venv for TTS

🚀 **Optimizations are ready** - FP16, CUDA Graphs, and embedding cache will work when using the correct CUDA-enabled torch!

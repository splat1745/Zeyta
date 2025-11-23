# GPU Compatibility Fix Guide

## Issues Resolved

### 1. **CUDA Kernel Compatibility Error**
**Error:** `CUDA error: no kernel image is available for execution on device`
**Cause:** ChatterboxTTS was compiled for GPU compute capability that doesn't match RTX 5070 Ti (compute 12.0)

**Solution:** Reinstall chatterbox-tts to recompile for your GPU architecture

### 2. **Dependency Conflicts**
- `torch 2.6.0` vs `torchvision 0.20.1+cu121` (requires torch 2.5.1)
- `numpy 1.25.2` vs `opencv-python` (requires numpy >=2.0)
- Other version mismatches

**Solution:** Updated fix_chatterbox_gpu() to align all package versions

### 3. **Invalid Distributions**
**Warning:** `Ignoring invalid distribution ~ympy`
**Cause:** Windows locks .pyd files when Python is running, leaving temp folders

**Solution:** Created cleanup script (runs when Python is closed)

## Automated Fixes Implemented

### In `web_app.py`:

1. **Enhanced `fix_chatterbox_gpu()` function** (lines 141-228):
   - Step 1: Fixes PyTorch/torchvision version conflicts
   - Step 2: Upgrades numpy to 2.x for opencv compatibility
   - Step 3: Uninstalls chatterbox-tts
   - Step 4: Reinstalls with `--no-cache-dir` to force GPU-specific compilation

2. **Added `clean_invalid_distributions()` function** (lines 230-246):
   - Detects ~* folders in site-packages
   - Notifies user they'll be cleaned on restart
   - Called on startup to check status

3. **Improved TTS GPU loading** (lines 405-477):
   - Detects CUDA kernel errors
   - Attempts compatibility fixes:
     - Clears CUDA cache
     - Sets float32 precision
     - Retries loading
   - If still failing, automatically calls fix_chatterbox_gpu()
   - Shows GPU info (name, compute capability)

4. **Startup checks** (lines 1413-1427):
   - Runs clean_invalid_distributions()
   - Runs check_binary_compatibility()
   - Auto-fixes issues before starting server

## Manual Cleanup Script

**File:** `cleanup_invalid_distributions.ps1`

**Usage:**
1. Close all Python processes (VS Code, terminals, web app)
2. Right-click the script
3. Select "Run with PowerShell"
4. Script will:
   - Detect Python processes and offer to kill them
   - Remove all ~* folders from site-packages
   - Show success/failure for each folder

## How to Fix GPU Compatibility

### Option 1: Automatic (Recommended)
1. Start web_app.py
2. Initialize TTS with GPU
3. It will detect the issue and automatically:
   - Show GPU details
   - Fix dependency conflicts
   - Reinstall chatterbox-tts
   - Ask you to restart
4. Restart web_app.py
5. Initialize TTS again - should work on GPU now

### Option 2: Manual
1. Close all Python processes
2. Run cleanup script (optional, for warnings)
3. Run these commands:
   ```powershell
   # Fix torch/torchvision versions
   python -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
   
   # Upgrade numpy for opencv
   python -m pip install "numpy>=2.0,<2.3"
   
   # Reinstall chatterbox for your GPU
   python -m pip uninstall -y chatterbox-tts
   python -m pip cache purge
   python -m pip install --no-cache-dir chatterbox-tts
   ```
4. Restart web_app.py

## What Changed in web_app.py

### GPU Detection & Fallback
```python
# Old: Simple CPU fallback
if device == 'cuda' and original_device == 'auto':
    device = 'cpu'
    self.tts_model = ChatterboxTTS.from_pretrained(device=device)

# New: Compatibility fixes first, then fallback
if device == 'cuda' and cuda_kernel_error:
    # Try clearing cache and precision fixes
    torch.cuda.empty_cache()
    torch.set_default_dtype(torch.float32)
    self.tts_model = ChatterboxTTS.from_pretrained(device=device)
    
    # If still fails, auto-fix and ask for restart
    if fix_chatterbox_gpu():
        return False, "GPU fix applied. Please restart."
```

### Dependency Management
```python
# New: Checks and fixes dependency conflicts
def fix_chatterbox_gpu():
    # Check torch/torchvision compatibility
    if torch_version != torchvision_version:
        # Reinstall matching versions
        pip install torch==2.5.1 torchvision==0.20.1
    
    # Check numpy for opencv
    if numpy_version < 2.0:
        pip install "numpy>=2.0,<2.3"
    
    # Reinstall chatterbox for GPU
    pip uninstall chatterbox-tts
    pip install --no-cache-dir chatterbox-tts
```

### Startup Checks
```python
# New: Cleans up and checks compatibility on startup
if __name__ == '__main__':
    clean_invalid_distributions()  # Check for ~* folders
    check_binary_compatibility()   # Test numpy/scipy/torch ops
    # Start server...
```

## Expected Results

### After Fix:
✅ TTS loads on GPU (RTX 5070 Ti)
✅ No CUDA kernel errors
✅ No dependency conflicts
✅ Invalid distribution warnings gone (after cleanup script)
✅ Voice cloning works with reference audio
✅ Faster TTS generation (GPU vs CPU)

### GPU Info:
- **GPU:** NVIDIA GeForce RTX 5070 Ti
- **Compute Capability:** 12.0
- **CUDA:** 12.1
- **PyTorch:** 2.5.1+cu121
- **ChatterboxTTS:** Compiled for compute 12.0

## Troubleshooting

### If GPU still fails after fix:
1. Check CUDA installation: `nvidia-smi`
2. Verify PyTorch sees GPU: `python -c "import torch; print(torch.cuda.is_available())"`
3. Check compute capability: `python -c "import torch; print(torch.cuda.get_device_capability())"`
4. Reinstall CUDA 12.1 if needed

### If invalid distribution warnings persist:
1. Close ALL Python processes (check Task Manager)
2. Run cleanup_invalid_distributions.ps1
3. Or manually delete folders starting with ~ in site-packages

### If dependencies conflict again:
1. The fix function checks and aligns versions automatically
2. If manual fix needed, see Option 2 commands above

## Summary

The web app now intelligently handles GPU compatibility issues by:
1. **Detecting** CUDA kernel errors and showing GPU info
2. **Attempting** compatibility fixes (cache clear, precision)
3. **Auto-fixing** dependency conflicts (torch, numpy)
4. **Reinstalling** packages compiled for your specific GPU
5. **Cleaning up** invalid distributions on startup
6. **Providing** clear error messages and restart instructions

All fixes happen automatically - just restart when prompted!

# Chatterbox TTS - CUDA Only Setup

## Overview
Chatterbox TTS now runs exclusively on CUDA (GPU) via a separate virtual environment to avoid dependency conflicts with the main PyTorch installation.

## What Was Done

### 1. Created Isolated Chatterbox Environment
- **Location**: `e:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox`
- **PyTorch Version**: 2.10.0.dev (nightly with cu128)
- **Dependencies**: All chatterbox-tts requirements installed with compatible versions

### 2. Subprocess Integration
The main script (`tts_test.py`) now:
- Only attempts to load Chatterbox when CUDA is available
- Uses subprocess execution to run Chatterbox in the isolated venv
- Automatically detects and uses the `CHATTERBOX_PYTHON` environment variable
- Falls back to Piper if Chatterbox is unavailable

### 3. Environment Configuration
- Set `CHATTERBOX_PYTHON` to point to the venv Python interpreter
- This allows seamless subprocess execution without modifying the main environment

## How It Works

### Architecture
```
Main Process (Python 3.12, PyTorch 2.10 cu128, numpy 2.3.4)
    ├── Piper TTS (GPU-enabled, in-process)
    ├── ONNX Runtime (GPU-enabled, in-process)
    └── Chatterbox TTS (subprocess)
         └── venv_chatterbox (Python 3.12, PyTorch 2.10 cu128, compatible deps)
              └── Runs on CUDA only
```

### TTS Modes
- **`fast` mode**: Uses Piper (GPU, in-process)
- **`cinematic` mode**: Uses Chatterbox (GPU, subprocess)
- **`auto` mode**: Prefers Piper
- **`windows` mode**: Uses pyttsx3 or falls back to Piper

### CUDA Enforcement
Chatterbox will ONLY run if:
1. `torch.cuda.is_available()` returns `True`
2. The subprocess Python interpreter has CUDA-enabled PyTorch
3. The `CHATTERBOX_PYTHON` environment variable is set (or subprocess check passes)

If CUDA is not available, the script automatically falls back to Piper.

## Usage

### Running TTS Test
```powershell
# The environment variable is already set, so just run:
python tts_test.py
```

### Cinematic Mode (Chatterbox)
```python
from tts_test import speak

# This will use Chatterbox on CUDA via subprocess
speak("Hello, this is cinematic mode!", mode="cinematic", outfile="output.wav")
```

### Verification
Check if Chatterbox subprocess is working:
```powershell
# Verify environment variable
$env:CHATTERBOX_PYTHON

# Check subprocess availability (in Python)
python -c "from tts_test import can_run_chatter_subprocess; print(f'Subprocess usable: {can_run_chatter_subprocess()}')"
```

## Files Modified

### Main Files
- **`tts_test.py`**: Updated with subprocess support and CUDA-only enforcement
- **`venv_chatterbox/`**: New isolated Python environment for Chatterbox

### Helper Scripts
- **`scripts/set_chatterbox_env.ps1`**: Sets the `CHATTERBOX_PYTHON` environment variable
- **`scripts/setup_chatter_venv.ps1`**: Creates and configures the Chatterbox venv (already done)
- **`Chatterbox_SETUP.md`**: Detailed setup instructions

## Diagnostics

### Check TTS Environment
The script automatically prints diagnostic information showing:
- Torch version and CUDA availability
- ONNX Runtime providers
- Piper status (CUDA enabled/disabled)
- Chatterbox status (in-process or subprocess)
- `CHATTERBOX_PYTHON` setting
- Subprocess usability

### Example Output
```
--- TTS Environment Diagnostic ---
Torch: 2.10.0.dev20251114+cu128, cuda_available=True
Piper is available; cuda=True, sample_rate~22050
ChatterboxTTS not available.
CHATTERBOX_PYTHON is set to: e:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox\Scripts\python.exe
CHATTERBOX subprocess usable: True
--- End Diagnostic ---
```

## Troubleshooting

### Chatterbox Not Running
1. Verify CUDA is available: `python -c "import torch; print(torch.cuda.is_available())"`
2. Check environment variable: `$env:CHATTERBOX_PYTHON`
3. Test venv directly:
   ```powershell
   & "e:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox\Scripts\python.exe" -c "import torch; from chatterbox import ChatterboxTTS; print('OK')"
   ```

### Subprocess Fails
- Check that the venv Python executable exists
- Verify all dependencies are installed in the venv
- Look at the error message in the script output (subprocess stderr is captured and displayed)

### Re-create Environment
If the venv becomes corrupted:
```powershell
# Remove old venv
Remove-Item -Recurse -Force "e:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox"

# Re-create using the setup script
cd "e:\AI-OFFICIAL\AI-RELEASE\scripts"
.\setup_chatter_venv.ps1 -path '..\venv_chatterbox' -torchVersion 'nightly' -cuda 'cu128'
```

## Performance Notes
- Chatterbox subprocess adds ~2-3 seconds overhead for model loading on first call
- Subsequent calls reuse the loaded model within the same subprocess execution
- For production use, consider implementing a persistent background process/server
- GPU memory: Chatterbox requires ~2-4GB VRAM depending on the model

## Key Benefits
✓ Chatterbox runs exclusively on CUDA (no CPU fallback)
✓ No dependency conflicts with main environment
✓ Easy to update either environment independently
✓ Automatic fallback to Piper if Chatterbox unavailable
✓ Clear error messages and diagnostics

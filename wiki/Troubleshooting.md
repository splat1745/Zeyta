# 🔧 Troubleshooting Guide

Solutions to common problems and issues when running Zeyta.

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Model Loading Problems](#model-loading-problems)
- [Memory & Performance Issues](#memory--performance-issues)
- [Audio Problems](#audio-problems)
- [Configuration Errors](#configuration-errors)
- [Runtime Errors](#runtime-errors)
- [Platform-Specific Issues](#platform-specific-issues)

---

## 🔍 Quick Diagnostics

### Run System Check

```bash
# Check Python version
python --version  # Should be 3.11+

# Check CUDA availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check installed packages
pip list | grep -E "torch|transformers|whisper|gradio"

# Test imports
python -c "
from transformers import pipeline
from faster_whisper import WhisperModel
print('✅ All imports successful')
"
```

### Common Quick Fixes

```bash
# 1. Reinstall requirements
pip install -r requirements.txt --force-reinstall

# 2. Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 3. Clear GPU memory
python -c "import torch; torch.cuda.empty_cache()"

# 4. Reset configuration
cp config.example.py config.py
```

---

## 📦 Installation Issues

### Problem: `ModuleNotFoundError`

**Error:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solutions:**

```bash
# Solution 1: Install missing package
pip install transformers

# Solution 2: Reinstall all requirements
pip install -r requirements.txt

# Solution 3: Check virtual environment is activated
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Verify after:
pip list | grep transformers
```

### Problem: PyTorch Installation

**Error:**
```
No module named 'torch'
```

**Solutions:**

```bash
# For GPU (CUDA 12.1):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For GPU (CUDA 11.8):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CPU only:
pip install torch torchvision torchaudio

# Verify:
python -c "import torch; print(torch.__version__)"
```

### Problem: FFmpeg Not Found

**Error:**
```
FileNotFoundError: FFmpeg not found
```

**Solutions:**

**Windows:**
```bash
# Option 1: Chocolatey
choco install ffmpeg

# Option 2: Download from ffmpeg.org
# Extract and add to PATH
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg

# Verify:
ffmpeg -version
```

**macOS:**
```bash
brew install ffmpeg

# Verify:
ffmpeg -version
```

### Problem: Gradio Installation

**Error:**
```
No module named 'gradio'
```

**Solution:**
```bash
pip install gradio

# Or with specific version:
pip install gradio>=4.0.0
```

---

## 🧠 Model Loading Problems

### Problem: Model Download Fails

**Error:**
```
OSError: Unable to load model from 'meta-llama/Llama-2-7b-chat-hf'
```

**Solutions:**

```python
# Solution 1: Check internet connection
ping huggingface.co

# Solution 2: Set custom cache directory
import os
os.environ['HF_HOME'] = '/path/with/more/space'

# Solution 3: Download manually
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    cache_dir="/custom/cache"
)

# Solution 4: Use local model
LLM_MODEL_ID = "/path/to/local/model"
```

### Problem: Model Access Denied

**Error:**
```
403 Client Error: Forbidden
```

**Solutions:**

```bash
# Solution 1: Login to Hugging Face
pip install huggingface-hub
huggingface-cli login

# Enter your token from: https://huggingface.co/settings/tokens

# Solution 2: Request model access
# Some models (e.g., Llama) require accepting terms on Hugging Face
```

### Problem: Model Version Mismatch

**Error:**
```
ValueError: Tokenizer class cannot be found
```

**Solutions:**

```bash
# Solution 1: Update transformers
pip install --upgrade transformers

# Solution 2: Clear cache and reload
rm -rf ~/.cache/huggingface/
python  # Fresh Python session

# Solution 3: Specify revision
from transformers import pipeline
pipe = pipeline("text-generation", model="model-name", revision="main")
```

---

## 💾 Memory & Performance Issues

### Problem: CUDA Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory. Tried to allocate X.XX GiB
```

**Solutions:**

**Immediate Fixes:**
```bash
# 1. Clear GPU memory
python -c "import torch; torch.cuda.empty_cache()"

# 2. Kill other GPU processes
nvidia-smi
kill -9 <process_id>
```

**Configuration Fixes:**
```python
# In config.py

# Solution 1: Use smaller models
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"  # Instead of 7B
STT_MODEL_SIZE = "base"  # Instead of large-v3

# Solution 2: Use quantization
STT_COMPUTE_TYPE = "int8"  # Instead of float16

# Solution 3: Reduce generation length
GENERATION_ARGS = {
    "max_new_tokens": 256,  # Instead of 2048
}

# Solution 4: Use half precision
torch_dtype=torch.float16

# Solution 5: CPU offloading
device_map="auto"  # Automatically manage memory
```

**Check VRAM Usage:**
```bash
# Monitor GPU memory
watch -n 1 nvidia-smi

# Or in Python:
import torch
print(f"Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"Reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

### Problem: Slow Inference

**Symptoms:**
- Responses take 30+ seconds
- UI freezes during generation
- High CPU usage

**Solutions:**

```python
# In config.py

# 1. Enable GPU
# Check CUDA:
python -c "import torch; print(torch.cuda.is_available())"

# 2. Use smaller models
LLM_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
STT_MODEL_SIZE = "tiny"

# 3. Reduce generation parameters
GENERATION_ARGS = {
    "max_new_tokens": 256,
    "do_sample": False,  # Greedy decoding (faster)
}

# 4. Use float16
torch_dtype=torch.float16

# 5. Disable memory search (if enabled)
ENABLE_HISTORY_SEARCH = False
```

### Problem: High RAM Usage

**Solutions:**

```python
# 1. Close other applications

# 2. Use smaller models
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

# 3. Limit conversation history
# In context manager, keep only recent messages
MAX_HISTORY_MESSAGES = 20

# 4. Clear conversation logs periodically
import os
import shutil
shutil.rmtree("chat_logs/old")

# 5. Use streaming inference (advanced)
for chunk in model.generate_stream():
    process(chunk)
```

---

## 🎤 Audio Problems

### Problem: Microphone Not Detected

**Error:**
```
OSError: No input device found
```

**Solutions:**

**Check Permissions:**
```bash
# Windows:
# Settings → Privacy → Microphone → Allow apps

# Linux:
# Check PulseAudio/ALSA
pactl list sources

# macOS:
# System Preferences → Security & Privacy → Microphone
```

**Test Microphone:**
```python
import sounddevice as sd
print(sd.query_devices())

# Test recording
duration = 3  # seconds
fs = 16000
recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
print("Recording successful!")
```

**Select Specific Device:**
```python
# In stt.py or config
import sounddevice as sd
devices = sd.query_devices()
print(devices)  # Find your device index

# Use specific device
sd.default.device = 1  # Your microphone index
```

### Problem: STT Not Transcribing

**Symptoms:**
- Microphone lights up but no text appears
- Returns empty string
- Times out

**Solutions:**

```python
# Solution 1: Check VAD sensitivity
# In IO/stt.py
vad = webrtcvad.Vad(1)  # Try different levels: 0-3

# Solution 2: Increase timeout
timeout = 30  # Increase from default

# Solution 3: Test STT directly
from faster_whisper import WhisperModel
model = WhisperModel("base")
segments, info = model.transcribe("test_audio.wav")
for segment in segments:
    print(segment.text)

# Solution 4: Check audio format
# Whisper needs 16kHz mono
import soundfile as sf
data, samplerate = sf.read("audio.wav")
print(f"Sample rate: {samplerate}, Channels: {len(data.shape)}")
```

### Problem: TTS Not Speaking

**Symptoms:**
- Text response shown but no audio
- Error in TTS module
- Audio file not created

**Solutions:**

```python
# Solution 1: Check TTS backend
# In config.py
TTS_BACKEND = "piper"  # Try fallback first

# Solution 2: Test TTS directly
from IO import tts
tts.initialize_tts()
tts.speak("This is a test")

# Solution 3: Check audio output device
import sounddevice as sd
print(sd.query_devices())  # Find output device

# Solution 4: Verify Piper files exist
import os
piper_exe = "piper/piper.exe"  # Windows
piper_model = "piper/en_US-hfc_female-medium.onnx"
print(f"Piper exe exists: {os.path.exists(piper_exe)}")
print(f"Piper model exists: {os.path.exists(piper_model)}")
```

### Problem: ChatterboxTTS Fails

**Error:**
```
Failed to initialize Coqui TTS
```

**Solutions:**

```bash
# Solution 1: Install chatterbox-tts
pip install chatterbox-tts

# Solution 2: Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Solution 3: Fall back to CPU
# In config.py
COQUI_DEVICE = "cpu"

# Solution 4: Use Piper instead
TTS_BACKEND = "piper"

# Solution 5: Check reference audio
import os
ref_path = "your_reference.wav"
print(f"Reference exists: {os.path.exists(ref_path)}")

# Solution 6: Verify audio format
# Reference should be WAV, 48kHz, mono
ffmpeg -i input.mp3 -ar 48000 -ac 1 reference.wav
```

---

## ⚙️ Configuration Errors

### Problem: `config.py` Not Found

**Error:**
```
ModuleNotFoundError: No module named 'config'
```

**Solution:**
```bash
# Create config from example
cp config.example.py config.py

# Edit with your settings
nano config.py
```

### Problem: Invalid Configuration

**Error:**
```
AttributeError: module 'config' has no attribute 'LLM_MODEL_ID'
```

**Solutions:**

```python
# Solution 1: Check config.py has all required fields
# Compare with config.example.py

required_fields = [
    'LLM_MODEL_ID',
    'STT_MODEL_SIZE',
    'TTS_BACKEND',
    'SYSTEM_PROMPT',
    'GENERATION_ARGS',
]

import config
for field in required_fields:
    if not hasattr(config, field):
        print(f"Missing: {field}")

# Solution 2: Reset to example
cp config.example.py config.py

# Solution 3: Check syntax errors
python -m py_compile config.py
```

### Problem: Model Path Invalid

**Error:**
```
OSError: Model not found at path
```

**Solutions:**

```python
# Solution 1: Use Hugging Face model ID (not path)
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"  # ✅
# NOT: LLM_MODEL_ID = "/wrong/path"  # ❌

# Solution 2: For local models, use absolute path
import os
model_path = os.path.abspath("/path/to/model")
LLM_MODEL_ID = model_path

# Verify path exists
print(f"Model exists: {os.path.exists(model_path)}")
```

---

## 🐛 Runtime Errors

### Problem: Application Crashes on Startup

**Error:**
```
Segmentation fault (core dumped)
```

**Solutions:**

```bash
# Solution 1: Check Python version
python --version  # Must be 3.11+

# Solution 2: Reinstall PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio

# Solution 3: Check CUDA compatibility
nvidia-smi  # Note CUDA version
# Install matching PyTorch version

# Solution 4: Run with debug info
python -u main.py 2>&1 | tee debug.log

# Solution 5: Check for conflicting packages
pip check
```

### Problem: Gradio App Won't Start

**Error:**
```
OSError: Cannot find empty port in range
```

**Solutions:**

```python
# Solution 1: Specify different port
# In app.py
app.launch(server_port=7861)  # Try different port

# Solution 2: Kill existing process
# Windows:
netstat -ano | findstr :7860
taskkill /PID <pid> /F

# Linux/macOS:
lsof -ti:7860 | xargs kill -9

# Solution 3: Use random port
app.launch(server_port=0)  # Random available port
```

### Problem: Import Errors at Runtime

**Error:**
```
ImportError: cannot import name 'function' from 'module'
```

**Solutions:**

```bash
# Solution 1: Check package versions
pip show transformers
pip show torch

# Solution 2: Upgrade packages
pip install --upgrade transformers torch

# Solution 3: Downgrade if needed
pip install transformers==4.36.0

# Solution 4: Check dependencies
pip install -r requirements.txt --upgrade
```

---

## 💻 Platform-Specific Issues

### Windows Issues

**Problem: DLL Load Failed**

```bash
# Solution: Install Visual C++ Redistributable
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Solution: Update Windows
# Check for Windows updates
```

**Problem: Path Too Long**

```bash
# Enable long paths
# Run as Administrator in PowerShell:
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

**Problem: Antivirus Blocking**

```bash
# Add Python and Zeyta directory to antivirus exclusions
# Windows Defender:
# Settings → Update & Security → Windows Security → 
# Virus & threat protection → Exclusions
```

### Linux Issues

**Problem: Permission Denied**

```bash
# Solution: Fix permissions
chmod +x main.py
chmod +x app.py

# Or run with python
python main.py
```

**Problem: Audio Permissions**

```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Reload groups
newgrp audio

# Verify
groups | grep audio
```

**Problem: Missing Libraries**

```bash
# Install development headers
sudo apt install python3-dev
sudo apt install portaudio19-dev  # For audio
sudo apt install libsndfile1-dev  # For soundfile
```

### macOS Issues

**Problem: Microphone Permission**

```bash
# Grant microphone access:
# System Preferences → Security & Privacy → 
# Privacy → Microphone → Add Terminal/Python
```

**Problem: SSL Certificate Error**

```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command

# Or manually:
pip install --upgrade certifi
```

**Problem: M1/M2 Chip Issues**

```bash
# Use ARM-compatible PyTorch
pip install torch torchvision torchaudio

# If issues persist, try:
arch -arm64 pip install torch torchvision torchaudio
```

---

## 🆘 Getting More Help

### Collect Diagnostic Information

```bash
# Run this script to collect info for bug reports
cat > diagnostics.sh << 'EOF'
#!/bin/bash
echo "=== System Info ==="
uname -a
python --version
pip --version

echo -e "\n=== GPU Info ==="
nvidia-smi || echo "No NVIDIA GPU"

echo -e "\n=== Python Packages ==="
pip list | grep -E "torch|transformers|whisper|gradio"

echo -e "\n=== CUDA Check ==="
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')" || echo "PyTorch not installed"

echo -e "\n=== Disk Space ==="
df -h .

echo -e "\n=== Memory ==="
free -h || vm_stat
EOF

chmod +x diagnostics.sh
./diagnostics.sh > diagnostics.txt
```

### Where to Get Help

1. **GitHub Issues**: [relfayoumi/Zeyta/issues](https://github.com/relfayoumi/Zeyta/issues)
2. **Documentation**: [Zeyta Wiki](Home.md)
3. **Community**: Check discussions on GitHub

### Creating a Good Bug Report

Include:
- ✅ Clear description of the problem
- ✅ Steps to reproduce
- ✅ Expected vs actual behavior
- ✅ Error messages (full stack trace)
- ✅ System information (from diagnostics)
- ✅ Configuration (sanitize sensitive info)

---

## 📚 Related Documentation

- [Getting Started](Getting-Started.md) - Installation guide
- [Configuration](Configuration.md) - Setup options
- [FAQ](FAQ.md) - Common questions

---

<div align="center">

**[⬆️ Back to Top](#-troubleshooting-guide)** | **[🏠 Home](Home.md)** | **[Next: FAQ →](FAQ.md)**

</div>

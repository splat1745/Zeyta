# 🚀 Getting Started with Zeyta

Welcome! This guide will help you install and run Zeyta in just a few minutes.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Zeyta](#running-zeyta)
- [First Conversation](#first-conversation)
- [Next Steps](#next-steps)

---

## 📦 Prerequisites

Before installing Zeyta, make sure you have:

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.11+ | Main runtime environment |
| **pip** | Latest | Package manager |
| **FFmpeg** | Latest | Audio processing |
| **Git** | Any | Clone the repository |

### Hardware Requirements

**Minimum:**
- 8 GB RAM
- 10 GB disk space
- Multi-core CPU

**Recommended:**
- 16 GB+ RAM
- 20 GB+ disk space
- NVIDIA GPU with 8GB+ VRAM
- CUDA 12.1+

### Checking Your System

```bash
# Check Python version
python --version  # Should be 3.11 or higher

# Check pip
pip --version

# Check if CUDA is available (optional but recommended)
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

---

## 💾 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/relfayoumi/Zeyta.git
cd Zeyta
```

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment keeps Zeyta's dependencies isolated:

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
```

This will install:
- 🧠 Transformers (for LLM)
- 🎤 Faster-Whisper (for STT)
- 🔊 ChatterboxTTS (for voice cloning)
- 🖥️ Gradio (for web interface)
- And more...

### Step 4: Install PyTorch with CUDA (Optional, for GPU)

If you have an NVIDIA GPU, install PyTorch with CUDA support for much faster performance:

**For CUDA 12.1:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**For CUDA 11.8:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**CPU Only (slower, but works on any system):**
```bash
pip install torch torchvision torchaudio
```

### Step 5: Install Optional Components

**For Document Support (recommended):**
```bash
pip install PyPDF2 python-docx
```

**For Standalone Window Mode (recommended):**
```bash
pip install pywebview

# Platform-specific enhancements:
# Windows: pip install pywebview[cef]
# Linux: pip install pywebview[qt]
# macOS: pip install pywebview[qt]
```

### Step 6: Install FFmpeg

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and add to PATH
3. Or use Chocolatey: `choco install ffmpeg`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

---

## ⚙️ Configuration

### Step 1: Create Configuration File

```bash
cp config.example.py config.py
```

### Step 2: Edit Configuration

Open `config.py` in your favorite text editor and customize:

**🧠 LLM Model (Required)**
```python
# Choose a model based on your hardware
LLM_MODEL_ID = "chuanli11/Llama-3.2-3B-Instruct-uncensored"

# For stronger hardware:
# LLM_MODEL_ID = "meta-llama/Llama-2-7b-chat-hf"

# For lighter hardware:
# LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
```

**🎤 Speech-to-Text Settings**
```python
# Choose model size based on speed vs accuracy
STT_MODEL_SIZE = "base"  # Options: "tiny", "base", "small", "medium", "large-v3"
STT_COMPUTE_TYPE = "float16"  # "float16" (GPU), "int8" (lighter), "float32" (CPU)
```

**🔊 Text-to-Speech Settings**
```python
# Choose your TTS backend
TTS_BACKEND = "coqui"  # "coqui" (voice cloning) or "piper" (faster, no cloning)

# For voice cloning (requires reference audio file)
COQUI_REFERENCE_WAV = "path/to/your/reference_voice.wav"
COQUI_DEVICE = "cuda"  # "cuda" or "cpu"
```

**💬 Conversation Settings**
```python
SYSTEM_PROMPT = """You are a helpful, friendly AI assistant named Zeyta. 
You provide clear, concise answers and maintain context throughout conversations."""

INITIAL_GREETING = "Hello! I'm Zeyta, your AI assistant. How can I help you today?"
```

**⚡ Generation Parameters**
```python
GENERATION_ARGS = {
    "max_new_tokens": 512,     # Maximum response length
    "temperature": 0.7,        # Creativity (0.1-2.0)
    "top_p": 0.95,            # Nucleus sampling
    "repetition_penalty": 1.3, # Avoid repetition
}
```

### Configuration Presets

**💻 For Low-End Systems:**
```python
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
STT_MODEL_SIZE = "tiny"
STT_COMPUTE_TYPE = "int8"
TTS_BACKEND = "piper"
GENERATION_ARGS = {
    "max_new_tokens": 256,
    "temperature": 0.7,
    "top_p": 0.95,
}
```

**🚀 For High-End Systems (GPU):**
```python
LLM_MODEL_ID = "meta-llama/Llama-2-13b-chat-hf"
STT_MODEL_SIZE = "large-v3"
STT_COMPUTE_TYPE = "float16"
TTS_BACKEND = "coqui"
GENERATION_ARGS = {
    "max_new_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.95,
}
```

---

## 🎮 Running Zeyta

Zeyta offers multiple ways to run based on your preference:

### Option 1: Desktop Application (Recommended)

The best user experience with a native window interface:

```bash
python app.py
```

**Features:**
- ✨ Modern, clean interface
- 🎤 Voice input/output
- 📁 File upload support
- ⚙️ Real-time configuration
- 💬 Chat history

**First Time Running:**
The app will check for dependencies and show their status:

```
============================================================
🚀 Starting Zeyta AI Assistant
============================================================

📦 Checking dependencies...
✅ Faster-Whisper available
✅ Transformers available
✅ ChatterboxTTS available
✅ CUDA available - NVIDIA GeForce RTX 3090

============================================================
🖥️  Launching application in standalone window...
============================================================
```

### Option 2: Command-Line Assistant

For voice-based conversations in the terminal:

```bash
python main.py
```

**Features:**
- 🎤 Voice input via microphone
- 🔊 Voice output
- 📝 Conversation history
- 💾 Auto-saves conversations

### Option 3: Testing Applications

**Integrated Testing App:**
```bash
python testing/integrated_app.py
```
Best for development and testing individual components.

**Standalone Testing App:**
```bash
python testing/standalone_app.py
```
Terminal-based testing interface.

---

## 💬 First Conversation

### Using the Desktop App

1. **Initialize Models** (first time only):
   - Click "🧠 Initialize LLM" and wait for the model to load
   - Click "🎤 Initialize STT" if using voice input
   - Click "🔊 Initialize TTS" if using voice output

2. **Choose Your Pipeline**:
   - **Text Chat Only** - Type messages
   - **Voice to Text** - Speak, get text responses
   - **Voice to Voice** - Full voice conversation
   - **Text to Voice** - Type, get voice responses

3. **Start Chatting**:
   - Type in the message box or use voice input
   - Click "Send 📤" or press Enter
   - Wait for AI response

**Example Conversation:**
```
You: Hello! What can you help me with?

Zeyta: Hello! I'm Zeyta, your AI assistant. I can help you with:
- Answering questions on various topics
- Document analysis and discussion
- Problem-solving and brainstorming
- General conversation and assistance
What would you like to know?
```

### Using the CLI

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Wait for the greeting:**
   ```
   [Zeyta starts listening via microphone]
   Zeyta: "Hello! I'm Zeyta. How can I help you today?"
   ```

3. **Speak your question:**
   ```
   You: [Speaking] "What's the weather like today?"
   [Zeyta transcribes your speech]
   Zeyta: [Speaking] "I don't have real-time weather data..."
   ```

4. **Exit the conversation:**
   Say "goodbye", "exit", or "quit"

---

## 📊 Verifying Your Setup

### Check GPU Acceleration

```python
import torch
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")
```

**Expected output (with GPU):**
```
CUDA Available: True
GPU: NVIDIA GeForce RTX 3090
CUDA Version: 12.1
```

### Test Individual Components

**Test STT:**
```bash
python testing/test_stt.py
```

**Test TTS:**
```bash
python testing/test_tts_clean.py
```

**Test LLM:**
```python
from transformers import pipeline
pipe = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct")
print(pipe("Hello, AI!", max_new_tokens=50))
```

---

## 🎯 Next Steps

Now that you're set up, explore more features:

1. 📚 **[Basic Concepts](Basic-Concepts.md)** - Understand how Zeyta works
2. ⚙️ **[Configuration Guide](Configuration.md)** - Fine-tune for your needs
3. 🎭 **[Voice Cloning](Advanced-Features.md#voice-cloning)** - Personalize TTS
4. 🔍 **[Memory & Context](Advanced-Features.md#memory-search)** - Leverage conversation history
5. 🎨 **[Pipeline Modes](Pipeline-Modes.md)** - Master different interaction modes

---

## 🆘 Troubleshooting Quick Fixes

### Common Issues

**"CUDA Out of Memory"**
```python
# In config.py, reduce model sizes:
STT_MODEL_SIZE = "base"  # instead of "large-v3"
STT_COMPUTE_TYPE = "int8"  # instead of "float16"
```

**"Import Error: No module named..."**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**"Model download is slow"**
```bash
# Set Hugging Face cache directory
export HF_HOME="/path/to/large/storage"
```

**"Microphone not working"**
```bash
# Test microphone access
python -m sounddevice

# Check permissions in your OS settings
```

For more solutions, see [Troubleshooting Guide](Troubleshooting.md).

---

## 🎓 Learning Path

**Beginner:**
1. ✅ Complete this guide
2. 📖 Read [Basic Concepts](Basic-Concepts.md)
3. 🎮 Try different [Pipeline Modes](Pipeline-Modes.md)

**Intermediate:**
1. ⚙️ Explore [Configuration Options](Configuration.md)
2. 🏗️ Study [Architecture](Architecture.md)
3. 🧪 Run [Testing Tools](Testing.md)

**Advanced:**
1. 💻 Review [Code Structure](Code-Structure.md)
2. 🔧 Extend with [Integration Examples](Integration-Examples.md)
3. 🤝 Read [Contributing Guide](Contributing.md)

---

<div align="center">

**[⬆️ Back to Top](#-getting-started-with-zeyta)** | **[🏠 Home](Home.md)** | **[Next: Basic Concepts →](Basic-Concepts.md)**

</div>

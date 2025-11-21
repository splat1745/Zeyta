# ⚙️ Configuration Guide

Complete guide to configuring Zeyta for your specific needs and hardware.

## 📋 Table of Contents

- [Configuration Overview](#configuration-overview)
- [Model Configuration](#model-configuration)
- [STT Configuration](#stt-configuration)
- [TTS Configuration](#tts-configuration)
- [Conversation Settings](#conversation-settings)
- [Performance Tuning](#performance-tuning)
- [Configuration Presets](#configuration-presets)
- [Advanced Options](#advanced-options)

---

## 📄 Configuration Overview

Zeyta uses a single configuration file: **`config.py`**

### Creating Your Configuration

```bash
# Copy the example configuration
cp config.example.py config.py

# Edit with your preferred editor
nano config.py
# or
code config.py
```

**Important Notes:**
- ✅ `config.py` is git-ignored (your settings stay private)
- ✅ `config.example.py` contains all available options with documentation
- ✅ Changes take effect after restarting the application

---

## 🧠 Model Configuration

### LLM (Language Model) Settings

```python
# Main LLM model identifier from Hugging Face
LLM_MODEL_ID = "chuanli11/Llama-3.2-3B-Instruct-uncensored"
```

### Choosing the Right Model

| Model | Size | VRAM | Speed | Quality | Best For |
|-------|------|------|-------|---------|----------|
| **Phi-3-mini** | 2-3GB | 4GB | 🚀🚀🚀 | ⭐⭐⭐ | Low-end systems |
| **Llama-3.2-3B** | 3-4GB | 6GB | 🚀🚀 | ⭐⭐⭐⭐ | Balanced |
| **Llama-2-7B** | 7-8GB | 12GB | 🚀 | ⭐⭐⭐⭐⭐ | High quality |
| **Llama-2-13B** | 13-14GB | 20GB | 🐌 | ⭐⭐⭐⭐⭐⭐ | Best quality |

### Popular Model Options

**Lightweight Models (2-4GB VRAM):**
```python
# Microsoft Phi-3 Mini (3.8B parameters)
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

# TinyLlama (1.1B parameters) - Very fast
LLM_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Phi-2 (2.7B parameters)
LLM_MODEL_ID = "microsoft/phi-2"
```

**Balanced Models (6-8GB VRAM):**
```python
# Llama 3.2 (3B parameters) - Recommended
LLM_MODEL_ID = "chuanli11/Llama-3.2-3B-Instruct-uncensored"

# Mistral 7B
LLM_MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

# Zephyr 7B
LLM_MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"
```

**High-Performance Models (12GB+ VRAM):**
```python
# Llama 2 7B Chat
LLM_MODEL_ID = "meta-llama/Llama-2-7b-chat-hf"

# Llama 2 13B Chat
LLM_MODEL_ID = "meta-llama/Llama-2-13b-chat-hf"

# CodeLlama 13B (for coding tasks)
LLM_MODEL_ID = "codellama/CodeLlama-13b-Instruct-hf"
```

### Model Selection Guide

**Choose based on:**

🎯 **Task Type:**
- General chat → Llama, Mistral, Zephyr
- Coding help → CodeLlama, Phi-3
- Lightweight → TinyLlama, Phi-2

💻 **Hardware:**
- 8GB VRAM → Phi-3, TinyLlama
- 12GB VRAM → Llama-3.2-3B, Mistral-7B
- 16GB VRAM → Llama-2-7B
- 24GB+ VRAM → Llama-2-13B or larger

⚡ **Performance:**
- Fast responses → Smaller models (1-3B)
- Best quality → Larger models (7-13B)

---

## 🎤 STT Configuration

### Whisper Model Settings

```python
# Model size: "tiny", "base", "small", "medium", "large-v3"
STT_MODEL_SIZE = "base"

# Compute type: "float16", "int8", "float32"
STT_COMPUTE_TYPE = "float16"
```

### STT Model Comparison

| Size | Speed | Accuracy | VRAM | CPU RAM | Use Case |
|------|-------|----------|------|---------|----------|
| **tiny** | 🚀🚀🚀 | ⭐⭐ | ~1GB | ~1GB | Testing, demos |
| **base** | 🚀🚀 | ⭐⭐⭐ | ~1GB | ~1GB | General use |
| **small** | 🚀 | ⭐⭐⭐⭐ | ~2GB | ~2GB | Good accuracy |
| **medium** | 🐌 | ⭐⭐⭐⭐⭐ | ~5GB | ~5GB | High accuracy |
| **large-v3** | 🐌🐌 | ⭐⭐⭐⭐⭐⭐ | ~10GB | ~10GB | Best accuracy |

### Compute Type Comparison

```python
# float16 - Best for GPUs with CUDA
STT_COMPUTE_TYPE = "float16"
# Pros: Fast, accurate, low VRAM
# Cons: Requires GPU with FP16 support

# int8 - Good for lower VRAM
STT_COMPUTE_TYPE = "int8"
# Pros: 50% less VRAM, still fast
# Cons: Slight accuracy loss

# float32 - Best for CPUs
STT_COMPUTE_TYPE = "float32"
# Pros: Best accuracy, works anywhere
# Cons: Slower, more memory
```

### Recommended STT Configurations

**Fast & Lightweight:**
```python
STT_MODEL_SIZE = "tiny"
STT_COMPUTE_TYPE = "int8"
# ~500MB VRAM, very fast
```

**Balanced:**
```python
STT_MODEL_SIZE = "base"
STT_COMPUTE_TYPE = "float16"
# ~1GB VRAM, good accuracy
```

**High Accuracy:**
```python
STT_MODEL_SIZE = "medium"
STT_COMPUTE_TYPE = "float16"
# ~5GB VRAM, excellent accuracy
```

**Best Quality:**
```python
STT_MODEL_SIZE = "large-v3"
STT_COMPUTE_TYPE = "float16"
# ~10GB VRAM, best possible accuracy
```

---

## 🔊 TTS Configuration

### Backend Selection

```python
# Choose TTS backend
TTS_BACKEND = "coqui"  # or "piper"
```

### Backend Comparison

| Feature | Coqui (ChatterboxTTS) | Piper |
|---------|----------------------|-------|
| **Quality** | ⭐⭐⭐⭐⭐ Natural | ⭐⭐⭐ Robotic |
| **Speed** | 🐌 Slower | 🚀 Very fast |
| **Voice Cloning** | ✅ Yes | ❌ No |
| **VRAM** | ~2-4GB | ~500MB |
| **Languages** | 17+ | 40+ |
| **Setup** | Complex | Simple |

### Coqui TTS Settings

```python
TTS_BACKEND = "coqui"

# Model to use
COQUI_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

# Reference audio for voice cloning (WAV file, 5-10 seconds)
COQUI_REFERENCE_WAV = "path/to/reference_voice.wav"

# Device: "cuda" or "cpu"
COQUI_DEVICE = "cuda"

# Language code
COQUI_LANGUAGE = "en"  # "en", "es", "fr", "de", "it", "pt", etc.
```

### Voice Cloning Setup

**1. Record Reference Audio:**
```bash
# Requirements for good reference:
✅ 5-10 seconds of speech
✅ Clear, no background noise
✅ 48kHz or 44.1kHz sample rate
✅ Single speaker
✅ Natural speaking style
```

**2. Prepare Audio File:**
```bash
# Convert to proper format using FFmpeg
ffmpeg -i input.mp3 -ar 48000 -ac 1 -c:a pcm_s16le reference.wav

# Or use the provided utility
python utils/resample_references.py --input input.mp3 --output reference.wav
```

**3. Configure:**
```python
COQUI_REFERENCE_WAV = "IO/AudioRef_48kHz/your_voice.wav"
```

### Piper TTS Settings

```python
TTS_BACKEND = "piper"

# Piper uses pre-configured models in piper/ directory
# No additional configuration needed
```

---

## 💬 Conversation Settings

### System Prompt

The system prompt defines your AI's personality and behavior:

```python
SYSTEM_PROMPT = """
You are Zeyta, a helpful and friendly AI assistant.

Key traits:
- Professional yet approachable
- Clear and concise in responses
- Patient with follow-up questions
- Honest about limitations

Guidelines:
- Provide accurate information
- If unsure, say so
- Stay on topic unless user changes subject
- Be respectful and inclusive
"""
```

### Example System Prompts

**Casual Friend:**
```python
SYSTEM_PROMPT = """
You're Zeyta, a friendly AI buddy! 
Be casual, fun, and conversational. 
Use emojis occasionally and keep things light. 
Help out but don't be too formal about it! 😊
"""
```

**Professional Assistant:**
```python
SYSTEM_PROMPT = """
You are Zeyta, a professional AI assistant.
Provide clear, accurate, and well-structured information.
Maintain a formal and respectful tone.
Focus on efficiency and precision.
"""
```

**Technical Expert:**
```python
SYSTEM_PROMPT = """
You are Zeyta, an AI specialized in technical topics.
Provide detailed technical explanations with examples.
Use code snippets and technical terminology appropriately.
Be thorough and precise in technical discussions.
"""
```

**Teacher/Tutor:**
```python
SYSTEM_PROMPT = """
You are Zeyta, an AI tutor.
Explain concepts clearly with examples.
Break down complex topics into simple steps.
Encourage learning with positive reinforcement.
Check understanding with follow-up questions.
"""
```

### Greeting & Exit Configuration

```python
# Initial greeting
INITIAL_GREETING = "Hello! How can I help you today?"

# Words that trigger exit
EXIT_PHRASES = ["exit", "quit", "goodbye", "bye"]

# Farewell message
FAREWELL_MESSAGE = "Goodbye! Have a great day!"
```

### Memory & History Settings

```python
# Directory for saving conversations
CHAT_LOG_DIR = "chat_logs"

# Load past conversations on startup (legacy mode)
INTEGRATE_PAST_LOGS = False  # Set to True to merge old chats

# Maximum results for memory search
CHAT_QUERY_MAX_RESULTS = 5

# Enable automatic memory search
ENABLE_HISTORY_SEARCH = True  # Detects "remember" queries
```

---

## ⚡ Performance Tuning

### Generation Parameters

Control how the AI generates responses:

```python
GENERATION_ARGS = {
    "max_new_tokens": 512,        # Maximum response length
    "do_sample": True,            # Enable sampling (vs greedy)
    "temperature": 0.7,           # Randomness (0.1-2.0)
    "top_p": 0.95,               # Nucleus sampling threshold
    "repetition_penalty": 1.3,    # Avoid repetition (1.0-2.0)
}
```

### Parameter Explanations

**max_new_tokens:**
```python
max_new_tokens: 256   # Short responses (1-2 paragraphs)
max_new_tokens: 512   # Medium responses (2-4 paragraphs)
max_new_tokens: 1024  # Long responses (4-6 paragraphs)
max_new_tokens: 2048  # Very long (6-10 paragraphs)
max_new_tokens: 4096  # Maximum (articles, stories)
```

**temperature:**
```python
temperature: 0.1-0.3  # Very focused, deterministic
temperature: 0.5-0.7  # Balanced (recommended)
temperature: 0.8-1.0  # Creative, varied
temperature: 1.1-2.0  # Very creative, unpredictable
```

**top_p (nucleus sampling):**
```python
top_p: 0.9   # Conservative, focused
top_p: 0.95  # Balanced (recommended)
top_p: 0.99  # More variety
top_p: 1.0   # Maximum variety
```

**repetition_penalty:**
```python
repetition_penalty: 1.0   # No penalty
repetition_penalty: 1.1   # Light penalty
repetition_penalty: 1.3   # Moderate (recommended)
repetition_penalty: 1.5   # Strong penalty
repetition_penalty: 2.0   # Very strong
```

### Initial Greeting Parameters

Separate parameters for the first response:

```python
INITIAL_GEN_ARGS = {
    "max_new_tokens": 256,        # Shorter greeting
    "do_sample": True,
    "temperature": 0.5,           # More focused
    "top_p": 0.95,
    "repetition_penalty": 1.2,
}
```

---

## 🎛️ Configuration Presets

### Low-End System (4-8GB VRAM)

```python
# config.py - Low-end preset

# LLM
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

# STT
STT_MODEL_SIZE = "tiny"
STT_COMPUTE_TYPE = "int8"

# TTS
TTS_BACKEND = "piper"  # Faster, less VRAM

# Generation
GENERATION_ARGS = {
    "max_new_tokens": 256,
    "temperature": 0.7,
    "top_p": 0.95,
    "repetition_penalty": 1.3,
}
```

### Mid-Range System (8-12GB VRAM)

```python
# config.py - Mid-range preset

# LLM
LLM_MODEL_ID = "chuanli11/Llama-3.2-3B-Instruct-uncensored"

# STT
STT_MODEL_SIZE = "base"
STT_COMPUTE_TYPE = "float16"

# TTS
TTS_BACKEND = "coqui"
COQUI_DEVICE = "cuda"
COQUI_REFERENCE_WAV = "your_reference.wav"

# Generation
GENERATION_ARGS = {
    "max_new_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.95,
    "repetition_penalty": 1.3,
}
```

### High-End System (16GB+ VRAM)

```python
# config.py - High-end preset

# LLM
LLM_MODEL_ID = "meta-llama/Llama-2-13b-chat-hf"

# STT
STT_MODEL_SIZE = "large-v3"
STT_COMPUTE_TYPE = "float16"

# TTS
TTS_BACKEND = "coqui"
COQUI_DEVICE = "cuda"
COQUI_REFERENCE_WAV = "your_reference.wav"

# Generation
GENERATION_ARGS = {
    "max_new_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.95,
    "repetition_penalty": 1.3,
}
```

### CPU-Only Configuration

```python
# config.py - CPU-only preset

# LLM - Lightweight model
LLM_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# STT
STT_MODEL_SIZE = "tiny"
STT_COMPUTE_TYPE = "float32"  # Better for CPU

# TTS
TTS_BACKEND = "piper"  # Much faster on CPU

# Generation - Conservative
GENERATION_ARGS = {
    "max_new_tokens": 256,
    "temperature": 0.7,
    "top_p": 0.95,
    "repetition_penalty": 1.3,
}
```

---

## 🔧 Advanced Options

### Custom Model Paths

```python
# Use local model instead of downloading
LLM_MODEL_ID = "/path/to/local/model"

# Or Hugging Face cache location
import os
os.environ["HF_HOME"] = "/custom/cache/directory"
```

### Memory Management

```python
# In your code or config
import torch

# Clear GPU cache periodically
torch.cuda.empty_cache()

# Set memory allocation strategy
torch.cuda.set_per_process_memory_fraction(0.8)  # Use 80% max
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in config
DEBUG_MODE = True
VERBOSE_LOGGING = True
```

### Custom Paths

```python
# Custom directories
CHAT_LOG_DIR = "/custom/path/to/logs"
OUTPUT_DIR = "/custom/path/to/outputs"
CACHE_DIR = "/custom/path/to/cache"
```

---

## 🔍 Configuration Validation

### Testing Your Configuration

```python
# test_config.py
from config import *

print(f"LLM Model: {LLM_MODEL_ID}")
print(f"STT Model: {STT_MODEL_SIZE}")
print(f"TTS Backend: {TTS_BACKEND}")
print(f"Generation max tokens: {GENERATION_ARGS['max_new_tokens']}")
```

### Common Issues

**Issue: Model doesn't load**
```python
# Solution: Check model ID is correct
# Try loading manually:
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(LLM_MODEL_ID)
```

**Issue: Out of memory**
```python
# Solution: Reduce model sizes or use quantization
STT_COMPUTE_TYPE = "int8"  # Instead of float16
# Or use smaller model
LLM_MODEL_ID = "smaller-model-id"
```

**Issue: TTS not working**
```python
# Solution: Check backend and reference file
if TTS_BACKEND == "coqui":
    assert Path(COQUI_REFERENCE_WAV).exists()
```

---

## 📚 Next Steps

- [Performance Tips](Performance-Tips.md) - Optimize for your hardware
- [Pipeline Modes](Pipeline-Modes.md) - Choose interaction style
- [Advanced Features](Advanced-Features.md) - Voice cloning, memory, etc.

---

<div align="center">

**[⬆️ Back to Top](#-configuration-guide)** | **[🏠 Home](Home.md)** | **[Next: Pipeline Modes →](Pipeline-Modes.md)**

</div>

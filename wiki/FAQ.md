# ❓ Frequently Asked Questions (FAQ)

Quick answers to common questions about Zeyta.

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Privacy & Security](#privacy--security)
- [Performance & Hardware](#performance--hardware)
- [Features & Capabilities](#features--capabilities)
- [Models & Configuration](#models--configuration)
- [Troubleshooting](#troubleshooting)
- [Development & Contributing](#development--contributing)

---

## 🌐 General Questions

### What is Zeyta?

Zeyta is a local, privacy-first AI assistant that runs entirely on your computer. It combines:
- Large Language Models (LLMs) for intelligent responses
- Speech-to-Text (Whisper) for voice input
- Text-to-Speech (ChatterboxTTS/Piper) for voice output
- Conversation memory for context awareness

**Key advantage:** Everything runs locally - no cloud services, no data sharing, complete privacy.

### Is Zeyta free?

Yes! Zeyta is completely free and open-source. There are no subscriptions, API fees, or hidden costs.

**Costs you might have:**
- ✅ Electricity (running your computer)
- ✅ Initial download (models can be large, 2-20GB)
- ❌ No cloud API costs
- ❌ No subscriptions

### Do I need an internet connection?

**Setup phase:** Yes, to download models and dependencies.

**After setup:** No, Zeyta runs completely offline.

```
Internet Needed:
✅ Initial installation (pip install)
✅ Downloading AI models (first run)
✅ Updates and new models

Internet NOT Needed:
❌ Running conversations
❌ Voice interactions
❌ Daily use
```

### What platforms does Zeyta support?

| Platform | Support | Notes |
|----------|---------|-------|
| **Windows** | ✅ Full | Windows 10+ |
| **Linux** | ✅ Full | Ubuntu 20.04+, most distros |
| **macOS** | ✅ Full | macOS 10.15+, M1/M2 supported |

### How is Zeyta different from ChatGPT/Alexa/Siri?

| Feature | Zeyta | ChatGPT/Alexa/Siri |
|---------|-------|-------------------|
| **Privacy** | 100% local | Cloud-based |
| **Internet** | Optional after setup | Required |
| **Cost** | Free | Subscription/API costs |
| **Customization** | Full control | Limited |
| **Voice** | Custom cloning | Generic |
| **Data** | Stays on your PC | Sent to servers |
| **Speed** | Depends on your hardware | Network dependent |

---

## 🔒 Privacy & Security

### Is my data really private?

**Yes!** Here's why:

```
Your Data Flow:
You → Your Computer → Your Storage
      ↑
      └─ Never leaves your machine

No cloud services
No external APIs
No telemetry
No analytics
No data collection
```

**What's stored locally:**
- Conversation logs (in `chat_logs/`)
- AI models (in Hugging Face cache)
- Configuration (`config.py`)
- Generated audio (temporary)

**What's NOT stored:**
- Nothing is sent to external servers
- No user tracking
- No analytics
- No remote logging

### Can others access my conversations?

**Physical access:** If someone has access to your computer, they could read your conversation logs.

**Protection measures:**
```bash
# 1. Encrypt your hard drive (recommended)
# Windows: BitLocker
# Linux: LUKS
# macOS: FileVault

# 2. Use strong system passwords

# 3. Secure chat_logs directory
chmod 700 chat_logs/  # Linux/macOS

# 4. Delete old conversations periodically
rm -rf chat_logs/old/
```

### Are the AI models safe?

**Models are from trusted sources:**
- Hugging Face (primary source)
- Official model creators (Meta, Microsoft, etc.)

**Security best practices:**
```python
# Verify model source before downloading
# Check model card on Hugging Face
# Review model usage and licenses
```

### Does Zeyta collect any data?

**No.** Zeyta does not:
- ❌ Collect usage statistics
- ❌ Send telemetry
- ❌ Track you
- ❌ Report errors remotely
- ❌ Have analytics
- ❌ Connect to external services (except model download)

---

## 💻 Performance & Hardware

### What are the minimum requirements?

**Absolute Minimum (CPU-only):**
- Python 3.11+
- 8 GB RAM
- 10 GB storage
- Multi-core CPU

**Works but slow:** ~30-60s per response

**Recommended (with GPU):**
- Python 3.11+
- 16 GB RAM
- 20 GB storage
- NVIDIA GPU with 8GB+ VRAM
- CUDA 12.1+

**Much faster:** ~2-10s per response

### Do I need a GPU?

**Short answer:** No, but it's highly recommended.

**Comparison:**

| Hardware | Speed | Experience |
|----------|-------|------------|
| **CPU only** | 🐌 Very slow | Frustrating for real-time |
| **Budget GPU (6GB)** | 🚀 Fast | Good for most models |
| **Good GPU (12GB)** | 🚀🚀 Very fast | Excellent experience |
| **High-end GPU (24GB+)** | 🚀🚀🚀 Instant | Best possible |

**CPU optimization tips:**
```python
# Use lightweight models
LLM_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
STT_MODEL_SIZE = "tiny"
TTS_BACKEND = "piper"
```

### How much VRAM do I need?

**Model VRAM requirements:**

| Model Size | Minimum VRAM | Recommended | Example Models |
|------------|--------------|-------------|----------------|
| **1-3B** | 4GB | 6GB | Phi-3, TinyLlama |
| **7B** | 8GB | 12GB | Llama-2-7B, Mistral |
| **13B** | 16GB | 20GB | Llama-2-13B |
| **70B+** | 40GB+ | 80GB+ | Not recommended |

**Total VRAM calculation:**
```
Total = LLM + STT + TTS + Overhead

Example (comfortable setup):
LLM (7B): ~8GB
STT (base): ~1GB
TTS (coqui): ~2GB
Overhead: ~1GB
Total: ~12GB VRAM
```

### Can I use Apple Silicon (M1/M2)?

**Yes!** Zeyta works on Apple Silicon.

```bash
# Install ARM-compatible packages
pip install torch torchvision torchaudio

# For best performance, use MPS backend
device = "mps"  # Metal Performance Shaders

# Note: Some features may be CPU-only
```

**Performance:** M1/M2 chips have unified memory and perform well for AI tasks.

### Why is Zeyta slow on my system?

**Common causes:**

1. **CPU-only mode**
   ```python
   # Check:
   import torch
   print(torch.cuda.is_available())  # Should be True
   ```

2. **Large models**
   ```python
   # Use smaller models:
   LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
   ```

3. **High generation length**
   ```python
   # Reduce:
   GENERATION_ARGS = {"max_new_tokens": 256}
   ```

4. **Memory issues**
   ```bash
   # Check VRAM:
   nvidia-smi
   ```

See [Performance Tips](Performance-Tips.md) for optimization.

---

## ✨ Features & Capabilities

### Can Zeyta access the internet?

**No, by default.** Zeyta has no built-in internet access.

**Why:** For privacy and security.

**Can I add it?** Yes, through custom integrations:
```python
# integrations/web_search.py (you would create this)
import requests

def search_web(query):
    # Your implementation
    pass
```

### Does Zeyta support multiple languages?

**STT (Speech-to-Text):**
- ✅ Yes! Whisper supports 90+ languages
- Auto-detects language by default

**LLM (Responses):**
- Depends on the model
- Most models support English well
- Multi-lingual models available (Llama, BLOOM)

**TTS (Text-to-Speech):**
- ChatterboxTTS: 17+ languages
- Piper: 40+ languages

```python
# Configure language
COQUI_LANGUAGE = "es"  # Spanish
# or "fr", "de", "it", "pt", etc.
```

### Can Zeyta remember past conversations?

**Yes!** Zeyta has two levels of memory:

**1. Short-term (current session):**
- Automatically remembers current conversation
- Uses context for responses

**2. Long-term (past sessions):**
```python
# Enable in config.py
ENABLE_HISTORY_SEARCH = True

# Ask about past conversations:
"What did I say about Python last week?"
"Do you remember my favorite color?"
```

See [Advanced Features](Advanced-Features.md) for details.

### Can I customize Zeyta's personality?

**Yes!** Edit the system prompt:

```python
# In config.py
SYSTEM_PROMPT = """
You are Zeyta, a [your personality here].

Key traits:
- [trait 1]
- [trait 2]
- [trait 3]

Guidelines:
- [guideline 1]
- [guideline 2]
"""
```

**Examples:** See [Configuration Guide](Configuration.md#system-prompt).

### Can Zeyta control my computer?

**Not by default.** Zeyta is sandboxed for security.

**Can I add it?** Yes, via integrations:
```python
# integrations/pc_control.py
# Carefully add system control features

# ⚠️ Security warning:
# Be cautious with system control!
```

Available integrations:
- `browser.py` - Browser control
- `pc_control.py` - System commands
- `smart_home.py` - IoT devices

### Does Zeyta support image input?

**Partial support.** Currently:
- ❌ No image understanding by default
- ✅ `vision.py` module exists for future support
- ✅ Can be extended with vision models

**Future support:** Vision capabilities planned.

---

## ⚙️ Models & Configuration

### Which LLM model should I use?

**Depends on your hardware:**

| GPU VRAM | Recommended Model | Size |
|----------|------------------|------|
| **4-6GB** | microsoft/Phi-3-mini-4k-instruct | 3.8B |
| **8-12GB** | chuanli11/Llama-3.2-3B-Instruct | 3B |
| **12-16GB** | meta-llama/Llama-2-7b-chat-hf | 7B |
| **20GB+** | meta-llama/Llama-2-13b-chat-hf | 13B |

**For specific tasks:**
- **Coding:** codellama/CodeLlama-7b-Instruct-hf
- **Fast:** TinyLlama/TinyLlama-1.1B-Chat-v1.0
- **General:** mistralai/Mistral-7B-Instruct-v0.2

### Can I use ChatGPT or GPT-4?

**Not directly.** Those are cloud services requiring API access.

**Alternative:**
```python
# Use open-source alternatives:
LLM_MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"  # Similar quality
LLM_MODEL_ID = "meta-llama/Llama-2-13b-chat-hf"  # Strong performance
```

### How do I change the voice?

**Option 1: Voice Cloning (ChatterboxTTS)**
```python
# 1. Record 5-10 seconds of target voice
# 2. Convert to WAV (48kHz)
ffmpeg -i input.mp3 -ar 48000 -ac 1 reference.wav

# 3. Configure:
TTS_BACKEND = "coqui"
COQUI_REFERENCE_WAV = "path/to/reference.wav"
```

**Option 2: Different Piper Voice**
```bash
# Download different Piper models
# Place in piper/ directory
# Update model path in tts.py
```

### Can I run multiple models simultaneously?

**Technically yes, but not recommended:**
```python
# Would require significant VRAM
LLM (7B): 8GB
+ Another LLM: 8GB
+ STT: 1GB
+ TTS: 2GB
= 19GB total VRAM
```

**Better approach:** Switch models as needed.

### Where are models stored?

**Hugging Face cache:**
```bash
# Default location:
~/.cache/huggingface/  # Linux/macOS
C:\Users\<username>\.cache\huggingface\  # Windows

# Custom location:
export HF_HOME="/custom/path"
```

**Conversation logs:**
```bash
# In project directory:
Zeyta/chat_logs/
```

**Generated audio:**
```bash
# Temporary files:
Zeyta/testing/outputs/
Zeyta/output.wav  # Piper output
```

---

## 🔧 Troubleshooting

### Zeyta won't start. What should I do?

**Quick checks:**

1. **Python version:**
   ```bash
   python --version  # Must be 3.11+
   ```

2. **Virtual environment:**
   ```bash
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate  # Windows
   ```

3. **Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration:**
   ```bash
   cp config.example.py config.py
   ```

See [Troubleshooting Guide](Troubleshooting.md) for detailed help.

### Why does it keep saying "CUDA out of memory"?

**Solutions:**

```python
# 1. Use smaller models
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
STT_MODEL_SIZE = "base"

# 2. Use quantization
STT_COMPUTE_TYPE = "int8"

# 3. Reduce generation length
GENERATION_ARGS = {"max_new_tokens": 256}

# 4. Close other GPU applications
```

### The voice doesn't sound natural. Help?

**For better TTS quality:**

```python
# Use ChatterboxTTS (not Piper)
TTS_BACKEND = "coqui"

# Use high-quality reference audio:
# - 5-10 seconds
# - Clear recording
# - No background noise
# - 48kHz sample rate
COQUI_REFERENCE_WAV = "high_quality_reference.wav"

# If still issues, try recording new reference
```

### How do I reset everything?

**Complete reset:**

```bash
# 1. Remove cache
rm -rf ~/.cache/huggingface/

# 2. Remove conversation logs
rm -rf chat_logs/

# 3. Reset configuration
cp config.example.py config.py

# 4. Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 5. Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +

# 6. Restart
python app.py
```

---

## 👥 Development & Contributing

### Can I contribute to Zeyta?

**Yes! Contributions are welcome!**

See [Contributing Guide](Contributing.md) for:
- How to contribute
- Code standards
- Development setup
- Pull request process

### How can I add custom features?

**Several extension points:**

1. **Custom integrations:**
   ```python
   # integrations/my_feature.py
   def my_custom_function():
       pass
   ```

2. **Custom TTS backend:**
   ```python
   # IO/my_tts.py
   ```

3. **Custom prompts:**
   ```python
   # config.py
   SYSTEM_PROMPT = "..."
   ```

4. **Custom tools:**
   ```python
   # utils/my_tool.py
   ```

### Where can I get help?

1. **Documentation:** This wiki
2. **Issues:** [GitHub Issues](https://github.com/relfayoumi/Zeyta/issues)
3. **Discussions:** GitHub Discussions
4. **Troubleshooting:** [Troubleshooting Guide](Troubleshooting.md)

### Is there a community?

Check the GitHub repository for:
- Issue discussions
- Pull requests
- Community contributions
- Feature requests

---

## 💡 Tips & Tricks

### How can I make responses faster?

```python
# Lighter models
LLM_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
STT_MODEL_SIZE = "tiny"
TTS_BACKEND = "piper"

# Shorter responses
GENERATION_ARGS = {"max_new_tokens": 256}

# Greedy decoding
GENERATION_ARGS = {"do_sample": False}

# Disable memory search
ENABLE_HISTORY_SEARCH = False
```

### How can I make responses better quality?

```python
# Larger models
LLM_MODEL_ID = "meta-llama/Llama-2-13b-chat-hf"
STT_MODEL_SIZE = "large-v3"
TTS_BACKEND = "coqui"

# Longer context
GENERATION_ARGS = {"max_new_tokens": 2048}

# Better system prompt
SYSTEM_PROMPT = """Detailed personality and guidelines..."""
```

### Can I use Zeyta for specific domains?

**Yes! Customize the system prompt:**

```python
# For coding assistant:
SYSTEM_PROMPT = """You are an expert programmer..."""

# For medical information:
SYSTEM_PROMPT = """You are a medical information assistant...
(Disclaimer: Not for diagnosis)"""

# For creative writing:
SYSTEM_PROMPT = """You are a creative writing assistant..."""
```

---

## 📚 More Resources

- [Getting Started](Getting-Started.md) - Setup guide
- [Configuration](Configuration.md) - All settings
- [Pipeline Modes](Pipeline-Modes.md) - Interaction modes
- [Troubleshooting](Troubleshooting.md) - Problem solving
- [Performance Tips](Performance-Tips.md) - Optimization

---

<div align="center">

**[⬆️ Back to Top](#-frequently-asked-questions-faq)** | **[🏠 Home](Home.md)**

**Have more questions? [Open an issue](https://github.com/relfayoumi/Zeyta/issues)!**

</div>

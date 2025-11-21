# 🎭 Advanced Features

Explore Zeyta's powerful advanced capabilities: voice cloning, memory search, and more.

## 📋 Table of Contents

- [Voice Cloning](#voice-cloning)
- [Memory & History Search](#memory--history-search)
- [Custom Integrations](#custom-integrations)
- [Advanced Configuration](#advanced-configuration)
- [Performance Optimization](#performance-optimization)

---

## 🎤 Voice Cloning

Create a custom voice for Zeyta using ChatterboxTTS voice cloning.

### What is Voice Cloning?

Voice cloning allows Zeyta to speak in any voice by learning from a short audio sample (5-10 seconds). The AI analyzes the voice characteristics and recreates them for new speech.

```
Reference Audio (5-10s) → Voice Cloning Model → Custom Voice
    "Hello, this is         Analyzes pitch,          Zeyta speaks
     my voice"              tone, style              in your voice!
```

### Requirements

**Hardware:**
- NVIDIA GPU with 4GB+ VRAM
- CUDA support

**Software:**
- ChatterboxTTS installed: `pip install chatterbox-tts`
- FFmpeg for audio processing

**Audio Sample:**
- 5-10 seconds of clear speech
- WAV format, 48kHz sample rate
- Single speaker
- Minimal background noise
- Natural speaking style

### Step-by-Step Setup

#### 1. Record Reference Audio

**Recording Tips:**

```
✅ DO:
- Speak naturally and clearly
- Use your normal speaking pace
- Record in a quiet environment
- Position mic 6-12 inches away
- Keep consistent volume
- Record 5-10 seconds

❌ DON'T:
- Shout or whisper
- Record with background noise
- Use compressed audio (MP3 low quality)
- Have multiple speakers
- Use music or sound effects
```

**Recording Tools:**

```bash
# Windows: Use Voice Recorder app
# macOS: Use QuickTime Player
# Linux: Use Audacity or arecord

# Command line recording (Linux/macOS):
arecord -f cd -d 10 reference.wav

# Or use Python:
python -c "
import sounddevice as sd
import soundfile as sf
duration = 10  # seconds
fs = 48000
recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
sf.write('reference.wav', recording, fs)
print('Recording saved!')
"
```

#### 2. Convert to Proper Format

Reference audio must be **WAV, 48kHz, mono**.

```bash
# Using FFmpeg (recommended):
ffmpeg -i input.mp3 -ar 48000 -ac 1 -c:a pcm_s16le reference.wav

# Check format:
ffmpeg -i reference.wav

# Should show:
# Stream #0:0: Audio: pcm_s16le, 48000 Hz, 1 channels, s16, 768 kb/s
```

**Using Zeyta's Utility:**

```bash
# Zeyta includes a resampling utility
python utils/resample_references.py --input input.mp3 --output reference.wav

# Batch process multiple files
python utils/resample_references.py --input-dir audio/ --output-dir IO/AudioRef_48kHz/
```

#### 3. Configure Zeyta

Edit `config.py`:

```python
# Enable ChatterboxTTS backend
TTS_BACKEND = "coqui"

# Specify reference audio path
COQUI_REFERENCE_WAV = "IO/AudioRef_48kHz/my_voice.wav"

# Use GPU for faster synthesis
COQUI_DEVICE = "cuda"

# Set language
COQUI_LANGUAGE = "en"  # English

# Model (default is XTTS v2)
COQUI_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
```

#### 4. Test Voice Cloning

```python
# Test synthesis
python testing/test_tts_clean.py \
    --ref-dir IO/AudioRef_48kHz \
    --text "This is a test of voice cloning" \
    --expressive \
    --temperature 0.75
```

**Expected Output:**
```
Loading ChatterboxTTS...
Using reference: my_voice.wav
Synthesizing: "This is a test of voice cloning"
Audio saved to: testing/outputs/test_output.wav
✅ Success!
```

### Voice Cloning Quality

**Factors Affecting Quality:**

| Factor | Impact | Recommendation |
|--------|--------|----------------|
| **Reference Length** | ⭐⭐⭐ | 5-10 seconds optimal |
| **Audio Quality** | ⭐⭐⭐⭐⭐ | 48kHz, clear recording |
| **Background Noise** | ⭐⭐⭐⭐ | Silent environment |
| **Speaking Style** | ⭐⭐⭐ | Natural, consistent |
| **Temperature** | ⭐⭐ | 0.65-0.85 range |

**Temperature Settings:**

```python
# In coqui_backend.py or testing script
temperature = 0.65  # More stable, less expressive
temperature = 0.75  # Balanced (recommended)
temperature = 0.85  # More expressive, less stable
temperature = 0.95  # Very expressive, may be unstable
```

### Advanced Voice Cloning

**Multiple Reference Files:**

```python
# Use multiple samples for better quality
COQUI_REFERENCE_WAV = [
    "IO/AudioRef_48kHz/voice1.wav",
    "IO/AudioRef_48kHz/voice2.wav",
    "IO/AudioRef_48kHz/voice3.wav",
]

# ChatterboxTTS will blend characteristics
```

**Language-Specific Cloning:**

```python
# Clone voice for specific language
COQUI_LANGUAGE = "es"  # Spanish
COQUI_REFERENCE_WAV = "spanish_voice.wav"

# Supported languages:
# en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh, ja, ko, hi
```

**Fine-Tuning Parameters:**

```python
# In IO/coqui_backend.py (advanced)
synthesis_kwargs = {
    "temperature": 0.75,
    "length_penalty": 1.0,
    "repetition_penalty": 5.0,
    "top_k": 50,
    "top_p": 0.85,
}
```

### Troubleshooting Voice Cloning

**Issue: Voice sounds robotic**

```python
# Solutions:
# 1. Use higher quality reference
ffmpeg -i input.mp3 -ar 48000 -ac 1 -c:a pcm_s16le reference.wav

# 2. Increase temperature
temperature = 0.85

# 3. Use longer reference (8-10 seconds)

# 4. Record in quieter environment
```

**Issue: Voice doesn't match reference**

```python
# Solutions:
# 1. Ensure reference is 48kHz
ffmpeg -i reference.wav

# 2. Use multiple reference files
COQUI_REFERENCE_WAV = ["ref1.wav", "ref2.wav", "ref3.wav"]

# 3. Verify GPU is being used
import torch
print(torch.cuda.is_available())

# 4. Try different reference sections
# Extract clear 10-second segment
```

**Issue: Synthesis is slow**

```python
# Solutions:
# 1. Ensure GPU is enabled
COQUI_DEVICE = "cuda"

# 2. Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# 3. Reduce text length
# Split long text into sentences

# 4. Use Piper as fallback for speed
TTS_BACKEND = "piper"  # Much faster, but no cloning
```

---

## 💭 Memory & History Search

Zeyta can remember and search past conversations using semantic search.

### How Memory Works

```
┌─────────────────────────────────────────┐
│  Short-Term Memory                      │
│  (Current Session)                      │
│                                         │
│  Current conversation in RAM            │
│  Cleared when session ends              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Long-Term Memory                       │
│  (Past Sessions)                        │
│                                         │
│  Saved to: chat_logs/*.json             │
│  Searchable across all past chats       │
└─────────────────────────────────────────┘
```

### Enabling Memory Search

```python
# In config.py
ENABLE_HISTORY_SEARCH = True
CHAT_QUERY_MAX_RESULTS = 5
CHAT_LOG_DIR = "chat_logs"
```

### Using Memory Search

**Memory Query Keywords:**

Zeyta detects these phrases as memory queries:

```python
# Detection keywords
"remember"
"recall"
"said"
"mentioned"
"talked about"
"discussed"
"told you"
"what did i"
"do you remember"
```

**Example Queries:**

```
✅ Memory queries (will search):
"What did I say about Python?"
"Do you remember my favorite color?"
"What did we discuss yesterday?"
"Recall our conversation about AI"

❌ Regular queries (won't search):
"Tell me about Python"
"What's your favorite color?"
"Let's discuss AI"
```

### How Memory Search Works

**Process:**

```
1. User: "What did I say about Python?"
   ↓
2. Detect memory query (contains "what did i")
   ↓
3. Load all past conversation logs
   ↓
4. Search for mentions of "Python"
   ↓
5. Rank by relevance and recency
   ↓
6. Format top 5 results
   ↓
7. Inject into LLM context:
   [MEMORY RECALL]
   Past conversation (2024-01-15):
   User: "I love Python for data science"
   Assistant: "Python is great for that!"
   ↓
8. Generate response with context
   ↓
9. Response: "Based on our past conversation,
              you mentioned loving Python..."
```

### Memory Search Examples

**Example 1: Simple Recall**

```
Session 1 (Jan 15):
You: "My name is Alex"
Zeyta: "Nice to meet you, Alex!"

Session 2 (Jan 16):
You: "Do you remember my name?"
Zeyta: [Searches past] "Yes! Based on our previous conversation 
       on January 15th, your name is Alex."
```

**Example 2: Topic Recall**

```
Session 1 (Jan 10):
You: "I'm learning Python for machine learning"
Zeyta: "That's great! Python has excellent ML libraries..."

Session 2 (Jan 15):
You: "What programming language was I learning?"
Zeyta: [Searches past] "According to our conversation on 
       January 10th, you mentioned learning Python for 
       machine learning."
```

**Example 3: Preference Recall**

```
Session 1:
You: "My favorite color is blue"
Zeyta: "Blue is a wonderful color!"

Later session:
You: "What's my favorite color?"
Zeyta: [Searches past] "You told me your favorite color is blue!"
```

### Advanced Memory Features

**Custom Search Implementation:**

```python
# core/context.py (customize search logic)

def search_and_format_memories(self, query, limit=5):
    """
    Custom semantic search implementation
    """
    # Load past logs
    logs = self.load_past_logs()
    
    # Simple keyword search (current)
    results = []
    for log in logs:
        for message in log:
            if query.lower() in message['content'].lower():
                results.append(message)
    
    # Future: Semantic embeddings search
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer('all-MiniLM-L6-v2')
    # embeddings = model.encode(contents)
    # similarity = cosine_similarity(query_embedding, embeddings)
    
    return self.format_results(results[:limit])
```

**Memory Management:**

```python
# Limit memory search to recent conversations
MEMORY_SEARCH_DAYS = 30  # Only search last 30 days

# Limit number of past logs loaded
MAX_PAST_LOGS = 100

# Clear old conversations
import os
import time
from datetime import datetime, timedelta

def clean_old_logs(days=90):
    """Remove logs older than N days"""
    cutoff = datetime.now() - timedelta(days=days)
    for filename in os.listdir("chat_logs"):
        filepath = os.path.join("chat_logs", filename)
        mtime = os.path.getmtime(filepath)
        if datetime.fromtimestamp(mtime) < cutoff:
            os.remove(filepath)
            print(f"Deleted: {filename}")
```

### Privacy & Memory

**What's Stored:**

```json
// chat_logs/chat_2024-01-15_10-30-45.json
[
  {
    "role": "system",
    "content": "You are a helpful assistant"
  },
  {
    "role": "user",
    "content": "What is Python?"
  },
  {
    "role": "assistant",
    "content": "Python is a programming language..."
  }
]
```

**Managing Privacy:**

```bash
# View stored conversations
ls -lh chat_logs/

# Delete specific conversation
rm chat_logs/chat_2024-01-15_10-30-45.json

# Delete all conversations
rm -rf chat_logs/*

# Disable memory altogether
# In config.py:
ENABLE_HISTORY_SEARCH = False
INTEGRATE_PAST_LOGS = False
```

---

## 🔌 Custom Integrations

Extend Zeyta with custom integrations for browser control, system commands, IoT, and more.

### Available Integrations

**Location:** `integrations/` directory

**Current Integrations:**

1. **browser.py** - Web browser control
2. **pc_control.py** - System commands
3. **smart_home.py** - IoT device control

### Creating Custom Integration

**Template:**

```python
# integrations/my_integration.py

import logging

def setup():
    """
    Initialize integration
    Called once at startup
    """
    logging.info("My integration initialized")
    # Setup code here

def handle_command(command: str) -> str:
    """
    Process integration-specific commands
    
    Args:
        command: User command or query
    
    Returns:
        Result string or None if not handled
    """
    if "my trigger" in command.lower():
        # Your logic here
        return "Command executed successfully"
    
    return None  # Not handled by this integration

def cleanup():
    """
    Cleanup on shutdown
    """
    logging.info("My integration cleaned up")
```

**Using the Integration:**

```python
# In main.py or controller.py
from integrations import my_integration

# Initialize
my_integration.setup()

# In conversation loop
result = my_integration.handle_command(user_input)
if result:
    # Integration handled the command
    tts.speak(result)
else:
    # Pass to LLM
    response = brain.generate_response(...)
```

### Example: Weather Integration

```python
# integrations/weather.py

import requests

API_KEY = "your_api_key"

def setup():
    """Initialize weather API"""
    # Verify API key, etc.
    pass

def handle_command(command: str) -> str:
    """Handle weather queries"""
    if "weather" not in command.lower():
        return None
    
    # Extract location (simple example)
    # In production, use NLP or regex
    location = "New York"  # Default
    
    # Call weather API
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": API_KEY, "units": "metric"}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        
        return f"The weather in {location} is {description} with a temperature of {temp}°C"
    
    except Exception as e:
        return f"Sorry, I couldn't fetch weather data: {e}"
```

### Integration Best Practices

**Security:**

```python
# ⚠️ NEVER execute arbitrary system commands directly
# ❌ Bad:
os.system(user_input)  # Dangerous!

# ✅ Good:
ALLOWED_COMMANDS = ["open browser", "check system", "list files"]
if user_input in ALLOWED_COMMANDS:
    execute_safe_command(user_input)
```

**Error Handling:**

```python
def handle_command(command: str) -> str:
    try:
        # Your logic
        return result
    except Exception as e:
        logging.error(f"Integration error: {e}")
        return f"Sorry, there was an error: {e}"
```

**Testing:**

```python
# Test your integration standalone
if __name__ == "__main__":
    setup()
    result = handle_command("test command")
    print(result)
```

---

## ⚡ Advanced Configuration

### Dynamic Configuration

```python
# config.py - Advanced patterns

# Environment-based configuration
import os

if os.getenv("ZEYTA_ENV") == "production":
    LLM_MODEL_ID = "meta-llama/Llama-2-13b-chat-hf"
    STT_MODEL_SIZE = "large-v3"
else:
    LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
    STT_MODEL_SIZE = "base"

# Hardware-based configuration
import torch

if torch.cuda.is_available():
    vram = torch.cuda.get_device_properties(0).total_memory / 1e9
    if vram >= 20:
        LLM_MODEL_ID = "meta-llama/Llama-2-13b-chat-hf"
    elif vram >= 12:
        LLM_MODEL_ID = "meta-llama/Llama-2-7b-chat-hf"
    else:
        LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
```

### Custom Prompts by Context

```python
# Different prompts for different tasks
PROMPT_CODING = """You are an expert programmer..."""
PROMPT_CREATIVE = """You are a creative writing assistant..."""
PROMPT_FORMAL = """You are a professional assistant..."""

# Switch dynamically
current_prompt = PROMPT_CODING
context = ContextManager(current_prompt)
```

### Multi-Model Setup

```python
# Use different models for different tasks
CODING_MODEL = "codellama/CodeLlama-7b-Instruct-hf"
GENERAL_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# Load based on query type
if "code" in user_query:
    model = load_model(CODING_MODEL)
else:
    model = load_model(GENERAL_MODEL)
```

---

## 📚 Next Steps

- [IO Modules](IO-Modules.md) - Deep dive into STT/TTS
- [API Reference](API-Reference.md) - Complete API docs
- [Performance Tips](Performance-Tips.md) - Optimize further

---

<div align="center">

**[⬆️ Back to Top](#-advanced-features)** | **[🏠 Home](Home.md)** | **[Next: API Reference →](API-Reference.md)**

</div>

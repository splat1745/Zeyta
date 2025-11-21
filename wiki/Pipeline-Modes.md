# 🎮 Pipeline Modes Guide

Master the different ways you can interact with Zeyta for various use cases.

## 📋 Table of Contents

- [What are Pipeline Modes?](#what-are-pipeline-modes)
- [Mode Comparison](#mode-comparison)
- [Text Chat Only](#text-chat-only)
- [Voice to Text](#voice-to-text)
- [Voice to Voice](#voice-to-voice)
- [Text to Voice](#text-to-voice)
- [Choosing the Right Mode](#choosing-the-right-mode)
- [Switching Between Modes](#switching-between-modes)

---

## 🤔 What are Pipeline Modes?

Pipeline modes determine how Zeyta processes your input and delivers responses. Each mode uses different combinations of components:

- 🎤 **STT** (Speech-to-Text) - Converts voice to text
- 🧠 **LLM** (Language Model) - Processes and generates responses
- 🔊 **TTS** (Text-to-Speech) - Converts text to voice

```
                    Pipeline Modes
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   Text Only        Voice Input       Voice Output
   💬 → 🧠 → 💬    🎤 → 💬 → 🧠    💬 → 🧠 → 🔊
```

---

## 📊 Mode Comparison

| Mode | Input | Output | Components | Speed | Use Case |
|------|-------|--------|------------|-------|----------|
| **Text Chat Only** | Typing | Text | LLM | ⚡⚡⚡ | Quiet environments, coding |
| **Voice to Text** | Voice | Text | STT + LLM | ⚡⚡ | Hands-free input, reading |
| **Voice to Voice** | Voice | Voice | STT + LLM + TTS | ⚡ | Natural conversation |
| **Text to Voice** | Typing | Voice | LLM + TTS | ⚡⚡ | Multitasking, accessibility |

---

## 💬 Text Chat Only

### Overview

The fastest and most straightforward mode - just type and read responses.

```
User Types: "What's the weather?"
     ↓
   LLM processes
     ↓
Display: "I don't have access to real-time weather..."
```

### When to Use

✅ **Best For:**
- Quiet environments (library, office)
- Code discussions with syntax highlighting
- Detailed technical explanations
- When you need to copy/paste responses
- Quick lookups and searches

❌ **Not Ideal For:**
- Hands-free situations
- While driving (unsafe)
- When multitasking

### Using Text Chat Mode

**In Desktop App:**
1. Select "Text Chat Only" in pipeline selector
2. Type in the message box
3. Press Enter or click "Send 📤"
4. Read response in chat window

**Example Conversation:**
```
You: Explain how Zeyta's memory works

Zeyta: Zeyta's memory system has two layers:

1. Short-term memory: Your current conversation session
2. Long-term memory: Past conversations saved to disk

When you ask about something from the past, Zeyta:
- Detects your memory query
- Searches past conversation logs
- Injects relevant context into the LLM
- Generates an informed response

This allows Zeyta to reference things discussed hours or days ago!
```

### Performance Tips

```python
# In config.py - Optimize for text speed
GENERATION_ARGS = {
    "max_new_tokens": 512,     # Shorter responses load faster
    "temperature": 0.7,        
    "do_sample": True,
}
```

### Advantages

- ⚡ **Fastest** - No audio processing overhead
- 📋 **Easy to copy** - Text responses can be copied/pasted
- 🔍 **Better for code** - Syntax highlighting, formatting
- 💾 **Lower resource use** - Only LLM needed
- 📝 **Easier to review** - Scroll back through history

---

## 🎤→💬 Voice to Text

### Overview

Speak naturally and read text responses - best of both worlds for input.

```
User Speaks: "What's the weather?"
     ↓
  STT transcribes
     ↓
   LLM processes
     ↓
Display: "I don't have access to real-time weather..."
```

### When to Use

✅ **Best For:**
- Hands-free input
- Faster than typing
- Accessibility (typing difficulties)
- When you want to review responses carefully
- Long questions or descriptions

❌ **Not Ideal For:**
- Noisy environments
- Need for silent operation
- Multiple speakers nearby

### Using Voice to Text Mode

**In Desktop App:**
1. Select "Voice to Text" in pipeline selector
2. Initialize STT model (first time only)
3. Click microphone button or upload audio file
4. Speak your question
5. Read text response

**Example Conversation:**
```
[You speak into microphone]
"Hey Zeyta, can you explain the difference between 
LLM temperature and top-p sampling?"

[Transcribed] ✓
"Hey Zeyta, can you explain the difference between 
LLM temperature and top-p sampling?"

[Zeyta responds in text]
"Great question! Both control randomness, but differently:

Temperature (0.1-2.0):
- Controls overall randomness
- Lower = more focused/predictable
- Higher = more creative/varied

Top-p (0.0-1.0):
- Nucleus sampling threshold
- Considers only top probability tokens
- 0.95 means use tokens comprising top 95%

Use temperature for creativity, top-p for coherence!"
```

### STT Configuration

```python
# In config.py
STT_MODEL_SIZE = "base"      # Good balance
STT_COMPUTE_TYPE = "float16"  # GPU acceleration

# For better accuracy (more VRAM):
STT_MODEL_SIZE = "large-v3"

# For faster processing (less accurate):
STT_MODEL_SIZE = "tiny"
```

### Audio Input Tips

**📝 For Best Recognition:**
- Speak clearly and at normal pace
- Use a good quality microphone
- Minimize background noise
- Position mic 6-12 inches from mouth
- Speak in complete sentences

**Common Issues:**
```
Problem: "Zeyta misunderstands me"
Solution: 
- Use larger STT model (medium/large-v3)
- Check microphone quality
- Reduce background noise
- Speak more clearly/slowly

Problem: "Processing is slow"
Solution:
- Use smaller STT model (tiny/base)
- Enable GPU acceleration
- Use int8 compute type
```

### Advantages

- 🎤 **Hands-free input** - Type-free operation
- ⚡ **Faster than typing** - Speak naturally
- 📖 **Read at your pace** - Review responses carefully
- 🔍 **Easy to reference** - Text stays on screen
- ♿ **Accessible** - Helps those with typing difficulties

---

## 🎤→🔊 Voice to Voice

### Overview

The most natural mode - full voice conversation like talking to a person.

```
User Speaks: "What's the weather?"
     ↓
  STT transcribes
     ↓
   LLM processes
     ↓
  TTS synthesizes
     ↓
Speaker plays: "I don't have access to real-time weather..."
```

### When to Use

✅ **Best For:**
- Natural conversation experience
- Hands-free operation
- Multitasking (cooking, exercising)
- Accessibility (vision impairment)
- Learning through listening
- Car use (with proper setup)

❌ **Not Ideal For:**
- Quiet environments (library)
- When others are present
- Complex technical content
- Need to review/copy responses

### Using Voice to Voice Mode

**In Desktop App:**
1. Select "Voice to Voice" in pipeline selector
2. Initialize STT model
3. Initialize TTS model
4. Click microphone and speak
5. Listen to voice response

**Example Conversation:**
```
[You speak]
"Hey Zeyta, tell me a fun fact about space"

[Zeyta speaks back]
"Here's a fascinating space fact! A day on Venus is longer 
than its year. Venus takes about 243 Earth days to complete 
one rotation, but only 225 Earth days to orbit the Sun. 
This means a Venusian day is longer than a Venusian year!"
```

### Voice Configuration

**STT Settings:**
```python
# Recommended for voice conversation
STT_MODEL_SIZE = "base"       # Fast enough for real-time
STT_COMPUTE_TYPE = "float16"  # GPU acceleration
```

**TTS Settings:**
```python
# For natural voice (recommended)
TTS_BACKEND = "coqui"
COQUI_DEVICE = "cuda"
COQUI_REFERENCE_WAV = "your_voice.wav"

# For faster response (less natural)
TTS_BACKEND = "piper"
```

### Voice Cloning

Make Zeyta speak in your chosen voice:

**Setup Steps:**
1. Record 5-10 seconds of clear speech
2. Convert to 48kHz WAV format
3. Configure reference path:
   ```python
   COQUI_REFERENCE_WAV = "IO/AudioRef_48kHz/custom_voice.wav"
   ```
4. Restart Zeyta

**Recording Tips:**
- 📢 Speak naturally, not too fast or slow
- 🔇 Record in quiet environment
- 🎤 Use good quality microphone
- 📏 5-10 seconds is ideal
- ✅ Avoid background noise

### Advantages

- 🗣️ **Most natural** - Like talking to a person
- 👐 **Completely hands-free** - No typing or reading needed
- 🏃 **Multitask-friendly** - Do other things while talking
- ♿ **Most accessible** - Great for vision impairment
- 🎭 **Voice customization** - Clone any voice

### Performance Notes

⚠️ **Slowest Mode** - All three components in sequence
- STT: ~0.5-2s (depending on model)
- LLM: ~2-10s (depending on model and length)
- TTS: ~1-5s (depending on backend and length)
- **Total: ~4-17s per interaction**

**Speed Optimization:**
```python
# Fast configuration
STT_MODEL_SIZE = "base"
LLM_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
TTS_BACKEND = "piper"
GENERATION_ARGS = {"max_new_tokens": 256}
# Total: ~2-5s per interaction
```

---

## 💬→🔊 Text to Voice

### Overview

Type your questions but listen to responses - great for multitasking.

```
User Types: "What's the weather?"
     ↓
   LLM processes
     ↓
  TTS synthesizes
     ↓
Speaker plays: "I don't have access to real-time weather..."
```

### When to Use

✅ **Best For:**
- Multitasking (listen while doing other work)
- Precise questions (type exactly what you mean)
- Learning through listening
- Accessibility (hearing responses)
- Long responses (easier to listen)

❌ **Not Ideal For:**
- Need to reference responses
- Quiet environments
- Complex technical content
- When others are present

### Using Text to Voice Mode

**In Desktop App:**
1. Select "Text to Voice" in pipeline selector
2. Initialize TTS model
3. Type your message
4. Press Enter or click "Send 📤"
5. Listen to voice response

**Example Conversation:**
```
[You type]
"Explain how neural networks learn"

[Zeyta speaks]
"Neural networks learn through a process called backpropagation.
Here's how it works: First, the network makes a prediction. 
Then, it calculates how wrong that prediction was. Finally, 
it adjusts its internal weights to make better predictions next time.
This process repeats thousands of times until the network becomes accurate!"
```

### Configuration

```python
# For best quality voice
TTS_BACKEND = "coqui"
COQUI_DEVICE = "cuda"
COQUI_REFERENCE_WAV = "your_reference.wav"

# For faster response
TTS_BACKEND = "piper"

# Adjust response length for listening
GENERATION_ARGS = {
    "max_new_tokens": 512,  # Good for audio
}
```

### Advantages

- ⌨️ **Precise input** - Type exactly what you mean
- 👂 **Listen while working** - Multitask effectively
- 🎧 **Easy on eyes** - No need to read responses
- ♿ **Accessible** - Helps those with reading difficulties
- ⚡ **Faster than voice-to-voice** - No STT processing

---

## 🎯 Choosing the Right Mode

### Decision Tree

```
Need voice input?
├─ No → Need voice output?
│       ├─ No → TEXT CHAT ONLY 💬
│       └─ Yes → TEXT TO VOICE 💬→🔊
└─ Yes → Need voice output?
        ├─ No → VOICE TO TEXT 🎤→💬
        └─ Yes → VOICE TO VOICE 🎤→🔊
```

### Use Case Matrix

| Situation | Recommended Mode | Why |
|-----------|-----------------|-----|
| Working on code | Text Chat Only | Copy/paste, formatting |
| Cooking dinner | Voice to Voice | Hands-free, can listen |
| In library | Text Chat Only | Silent operation |
| Driving* | Voice to Voice | Completely hands-free |
| Learning tutorial | Text to Voice | Listen while following |
| Quick question | Text Chat Only | Fastest response |
| Accessibility | Voice to Voice | Full audio interaction |

*⚠️ Always prioritize safe driving!

### Performance Comparison

```
Speed (fastest to slowest):
1. Text Chat Only      ⚡⚡⚡ (~2-5s)
2. Text to Voice       ⚡⚡   (~3-8s)
3. Voice to Text       ⚡⚡   (~3-8s)
4. Voice to Voice      ⚡     (~4-17s)

Resource Usage (lightest to heaviest):
1. Text Chat Only      💾    (LLM only)
2. Voice to Text       💾💾  (LLM + STT)
3. Text to Voice       💾💾  (LLM + TTS)
4. Voice to Voice      💾💾💾 (All three)
```

---

## 🔄 Switching Between Modes

### In the Desktop App

**Runtime Switching:**
1. Simply select a different mode from dropdown
2. No need to reinitialize (if models already loaded)
3. Switch as often as needed

**Example Workflow:**
```
Morning: Voice to Voice while making coffee
  ↓
Work: Text Chat Only for coding help
  ↓
Lunch: Voice to Text for quick questions
  ↓
Evening: Text to Voice for learning content
```

### Dynamic Mode Selection

```python
# Programmatic mode selection (for advanced users)
def select_mode(environment, task):
    if environment == "quiet" and task == "coding":
        return "text_only"
    elif environment == "noisy":
        return "text_only"  # Voice unreliable
    elif task == "multitasking":
        return "voice_to_voice"
    else:
        return "text_only"  # Default
```

### Best Practices

**📱 Start Simple:**
- Begin with Text Chat Only
- Add voice features as needed
- Don't use all features just because they exist

**⚙️ Optimize per Task:**
- Use fastest mode for quick lookups
- Use voice modes when hands-free matters
- Use text modes for complex topics

**💪 Build Muscle Memory:**
- Stick with one mode for similar tasks
- Switch modes based on environment
- Develop preferences over time

---

## 🎓 Advanced Tips

### Combining Modes with Files

**Upload Document + Text:**
```
1. Upload PDF file
2. Type: "Summarize this document"
3. Get text response with key points
```

**Upload Document + Voice:**
```
1. Upload PDF file
2. Speak: "What are the main conclusions?"
3. Listen to voice summary
```

### Customizing Each Mode

**Text Mode - Fast Responses:**
```python
GENERATION_ARGS = {
    "max_new_tokens": 256,   # Short and quick
    "temperature": 0.5,      # Focused
}
```

**Voice Mode - Natural Conversation:**
```python
GENERATION_ARGS = {
    "max_new_tokens": 512,   # More complete
    "temperature": 0.7,      # More varied
}
```

### Troubleshooting Modes

**Voice Input Not Working:**
```bash
# Test microphone
python -m sounddevice

# Check permissions
# Windows: Settings → Privacy → Microphone
# Linux: Check ALSA/PulseAudio
# macOS: System Preferences → Security → Microphone
```

**Voice Output Not Working:**
```python
# Verify TTS initialization
from IO import tts
tts.initialize_tts()
tts.speak("Test message")
```

---

## 📚 Next Steps

- [Advanced Features](Advanced-Features.md) - Voice cloning, memory search
- [Configuration](Configuration.md) - Fine-tune each component
- [Performance Tips](Performance-Tips.md) - Optimize for your hardware

---

<div align="center">

**[⬆️ Back to Top](#-pipeline-modes-guide)** | **[🏠 Home](Home.md)** | **[Next: Advanced Features →](Advanced-Features.md)**

</div>

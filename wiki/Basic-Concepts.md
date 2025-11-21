# 📚 Basic Concepts

Understanding Zeyta's core concepts will help you use it more effectively and customize it to your needs.

## 📋 Table of Contents

- [What is Zeyta?](#what-is-zeyta)
- [Core Components](#core-components)
- [How Zeyta Works](#how-zeyta-works)
- [Key Terminology](#key-terminology)
- [Data Flow](#data-flow)
- [Privacy & Security](#privacy--security)

---

## 🤔 What is Zeyta?

Zeyta is a **local AI assistant** that runs entirely on your computer. Unlike cloud-based assistants, Zeyta:

| Traditional AI | Zeyta |
|----------------|-------|
| ☁️ Runs in the cloud | 🏠 Runs on your machine |
| 📤 Sends your data to servers | 🔒 Keeps all data local |
| 💳 Often requires subscription | 🆓 Completely free |
| 🌐 Needs internet | ⚡ Works offline (after setup) |
| 🎭 Generic voice | 🎤 Custom voice cloning |

### Why Local AI?

**🔒 Privacy:** Your conversations never leave your computer.

**⚡ Speed:** No network latency for requests.

**💰 Cost:** No API fees or subscriptions.

**🎨 Customization:** Full control over models and behavior.

---

## 🧩 Core Components

Zeyta is built from several independent modules that work together:

### 1. 🧠 Brain (LLM)

The "thinking" part of Zeyta that generates intelligent responses.

**What it does:**
- Understands your questions
- Generates responses based on context
- Maintains personality and behavior

**Technology:**
- Hugging Face Transformers
- Models like Llama, Phi, GPT variants
- Runs on GPU or CPU

**Example models:**
```python
# Lightweight (2-4GB VRAM)
"microsoft/Phi-3-mini-4k-instruct"

# Balanced (6-8GB VRAM)
"chuanli11/Llama-3.2-3B-Instruct-uncensored"

# Powerful (12-16GB VRAM)
"meta-llama/Llama-2-13b-chat-hf"
```

### 2. 🎤 Ears (STT - Speech-to-Text)

Converts your voice into text that the brain can understand.

**What it does:**
- Listens to microphone input
- Detects when you're speaking (VAD - Voice Activity Detection)
- Transcribes speech to text

**Technology:**
- OpenAI Whisper via faster-whisper
- Multiple model sizes (tiny → large-v3)
- GPU or CPU inference

**Model sizes:**
| Size | Speed | Accuracy | VRAM |
|------|-------|----------|------|
| tiny | 🚀🚀🚀 | ⭐⭐ | ~1GB |
| base | 🚀🚀 | ⭐⭐⭐ | ~1GB |
| small | 🚀 | ⭐⭐⭐⭐ | ~2GB |
| medium | 🐌 | ⭐⭐⭐⭐⭐ | ~5GB |
| large-v3 | 🐌🐌 | ⭐⭐⭐⭐⭐⭐ | ~10GB |

### 3. 🔊 Voice (TTS - Text-to-Speech)

Converts text responses into natural-sounding speech.

**What it does:**
- Converts AI text responses to audio
- Can clone specific voices
- Supports multiple languages

**Technology:**
- ChatterboxTTS (voice cloning)
- Piper TTS (fast, fallback)
- Real-time synthesis

**Backends:**
```python
# ChatterboxTTS - High quality, voice cloning
TTS_BACKEND = "coqui"  
# Pros: Natural voice, cloning support
# Cons: Slower, more VRAM

# Piper - Fast, simple
TTS_BACKEND = "piper"
# Pros: Very fast, low resources
# Cons: Less natural, no cloning
```

### 4. 💭 Memory (Context Manager)

Remembers your conversation and maintains context.

**What it does:**
- Stores conversation history
- Searches past conversations
- Provides context to the brain
- Saves/loads chat logs

**Features:**
- Short-term memory (current session)
- Long-term memory (saved conversations)
- Semantic search (find relevant past info)
- Memory queries ("What did I say about...")

### 5. 🎮 Controller

Orchestrates all components and manages the conversation flow.

**What it does:**
- Coordinates input → processing → output
- Manages conversation loop
- Handles initialization
- Controls pipeline modes

---

## 🔄 How Zeyta Works

### Simple Flow

```
1. 🎤 You speak or type
   ↓
2. 📝 Input is converted to text (if voice)
   ↓
3. 🧠 Brain processes with context
   ↓
4. 💬 Response is generated
   ↓
5. 🔊 Response is spoken (if voice mode)
   ↓
6. 💾 Conversation is remembered
```

### Detailed Flow

```
┌─────────────────────────────────────────────────────────┐
│  USER INPUT                                             │
│  🎤 Voice Input    💬 Text Input    📄 File Upload      │
└────────────┬────────────┬────────────┬─────────────────┘
             │            │            │
             ▼            │            ▼
      ┌──────────┐        │     ┌──────────────┐
      │   STT    │        │     │ File Extractor│
      │ (Whisper)│        │     │  PDF/DOCX/TXT │
      └────┬─────┘        │     └──────┬───────┘
           │              │            │
           └──────────────┴────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │    Context Manager           │
           │  • Current conversation      │
           │  • Past conversations        │
           │  • Memory search             │
           └──────────┬───────────────────┘
                      │
                      ▼
           ┌──────────────────────────────┐
           │    Brain (LLM)               │
           │  • Understand input          │
           │  • Generate response         │
           │  • Use context               │
           └──────────┬───────────────────┘
                      │
                      ▼
           ┌──────────────────────────────┐
           │    Response Router           │
           │  (Based on pipeline mode)    │
           └──────────┬───────────────────┘
                      │
           ┌──────────┴───────────┐
           │                      │
           ▼                      ▼
    ┌──────────┐          ┌──────────┐
    │   Text   │          │   TTS    │
    │  Output  │          │ (Voice)  │
    └──────────┘          └──────────┘
```

---

## 📖 Key Terminology

### Models & AI

**LLM (Large Language Model)**
- The AI "brain" that generates text
- Examples: Llama, GPT, Phi
- Measured in parameters (3B, 7B, 13B)

**Inference**
- Running the model to get a response
- Can be on CPU (slow) or GPU (fast)

**Context Window**
- How much conversation history the AI can "remember"
- Measured in tokens (typically 2k-32k)

**Temperature**
- Controls randomness (0.0 = deterministic, 2.0 = creative)
- Lower = more focused, Higher = more diverse

**Tokens**
- Pieces of text the AI processes
- ~1 token ≈ 0.75 words
- Used to measure model input/output

### Voice Processing

**STT (Speech-to-Text)**
- Converting voice to text
- Also called ASR (Automatic Speech Recognition)

**TTS (Text-to-Speech)**
- Converting text to voice
- Also called speech synthesis

**VAD (Voice Activity Detection)**
- Detecting when someone is speaking
- Helps reduce processing of silence

**Sample Rate**
- Audio quality measurement (e.g., 16kHz, 48kHz)
- Higher = better quality but larger files

**Voice Cloning**
- Creating a synthetic voice from reference audio
- Requires 5-10 seconds of reference speech

### Memory & Context

**Context**
- Information available to the AI
- Includes current and past conversation

**Conversation History**
- Record of past messages in current session

**Chat Log**
- Saved conversation stored on disk

**Memory Search**
- Finding relevant past conversations
- Uses semantic similarity

### Processing

**Pipeline**
- The flow of data through components
- Different modes: Text-only, Voice-to-Voice, etc.

**Batch Processing**
- Processing multiple inputs together
- More efficient than one-by-one

**Streaming**
- Processing data as it arrives
- Reduces latency for long responses

---

## 🌊 Data Flow

### Text-Only Pipeline

```
Input: "What's the capital of France?"
  ↓
Context Manager: Add to history
  ↓
Brain (LLM): Process with context
  ↓
Output: "The capital of France is Paris."
  ↓
Context Manager: Add response to history
```

### Voice-to-Voice Pipeline

```
Input: [Voice recording of question]
  ↓
STT (Whisper): Convert to text
  ↓ "What's the capital of France?"
  ↓
Context Manager: Add to history
  ↓
Brain (LLM): Process with context
  ↓ "The capital of France is Paris."
  ↓
TTS (ChatterboxTTS): Convert to speech
  ↓ [Audio output]
  ↓
Context Manager: Add response to history
```

### Document + Chat Pipeline

```
File Upload: document.pdf
  ↓
File Extractor: Extract text content
  ↓ "Document contains information about..."
  ↓
Combine with user question
  ↓
Context Manager: Add to history
  ↓
Brain (LLM): Process document + question
  ↓
Output: Answer based on document
```

---

## 🔒 Privacy & Security

### Where Your Data Goes

```
┌─────────────────────────────────────────┐
│   Your Computer (Local Only)            │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Your Conversations & Files     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  AI Models (Local Storage)      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Processing (CPU/GPU)           │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘

        ❌ No Internet Connection Required
        ❌ No Cloud Services
        ❌ No Data Uploading
        ✅ 100% Private
```

### What Data is Stored

**Locally Stored:**
- Conversation history (in `chat_logs/` directory)
- Configuration settings (`config.py`)
- Downloaded AI models (Hugging Face cache)
- Generated audio files (temporary)

**Not Stored:**
- No telemetry or analytics
- No user tracking
- No remote logging

**You Control:**
- Where data is stored
- How long to keep conversations
- When to delete history

### Security Considerations

**✅ Advantages:**
- No data breaches (data never leaves your PC)
- No unauthorized access to conversations
- No third-party data sharing

**⚠️ Be Aware:**
- Physical access to your computer = access to data
- Conversation logs are saved as plaintext JSON
- Models are downloaded from Hugging Face (verify sources)

**🔐 Best Practices:**
- Encrypt your hard drive
- Use strong system passwords
- Review conversation logs periodically
- Keep your system updated

---

## 🎯 Understanding Pipeline Modes

Zeyta supports multiple ways to interact:

### 1. **Text Chat Only** 💬
```
Type → Brain → Text Response
```
- Fastest mode
- No audio processing
- Best for quiet environments

### 2. **Voice to Text** 🎤→💬
```
Voice → STT → Brain → Text Response
```
- Speak naturally
- Read responses
- Good for accessibility

### 3. **Voice to Voice** 🎤→🔊
```
Voice → STT → Brain → TTS → Voice Response
```
- Full voice interaction
- Most natural experience
- Slowest (most processing)

### 4. **Text to Voice** 💬→🔊
```
Type → Brain → TTS → Voice Response
```
- Type your questions
- Listen to responses
- Good for multitasking

See [Pipeline Modes](Pipeline-Modes.md) for detailed usage.

---

## 🧪 Practical Example

Let's trace a complete conversation:

**User:** "Remember my favorite color is blue."

1. **STT:** Converts voice to text
2. **Context Manager:** Stores "favorite color is blue"
3. **Brain:** Acknowledges and generates response
4. **TTS:** Speaks "I'll remember that your favorite color is blue."
5. **Context Manager:** Saves entire exchange

Later...

**User:** "What's my favorite color?"

1. **STT:** Converts voice to text
2. **Context Manager:** 
   - Detects memory query
   - Searches past conversations
   - Finds "favorite color is blue"
   - Provides context to Brain
3. **Brain:** Uses context to answer
4. **TTS:** Speaks "Your favorite color is blue."

This demonstrates:
- ✅ Voice processing (STT/TTS)
- ✅ Context retention
- ✅ Memory search
- ✅ Intelligent response generation

---

## 🎓 Key Takeaways

After reading this guide, you should understand:

✅ **Components:** Brain, Ears, Voice, Memory, Controller

✅ **Flow:** Input → Processing → Output

✅ **Privacy:** Everything stays on your computer

✅ **Modes:** Different ways to interact

✅ **Terminology:** LLM, STT, TTS, Context, etc.

---

## 🚀 Next Steps

Now that you understand the basics:

1. **Try It Out:** Experiment with different pipeline modes
2. **Customize:** Adjust configuration for your needs
3. **Learn More:** 
   - [Configuration Guide](Configuration.md) - Fine-tune settings
   - [Pipeline Modes](Pipeline-Modes.md) - Master interaction modes
   - [Architecture](Architecture.md) - Deep technical dive

---

<div align="center">

**[⬆️ Back to Top](#-basic-concepts)** | **[🏠 Home](Home.md)** | **[Next: Configuration →](Configuration.md)**

</div>

# 🏗️ Architecture Overview

A comprehensive deep dive into Zeyta's architecture, design patterns, and technical implementation.

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Design Principles](#design-principles)
- [Component Architecture](#component-architecture)
- [Data Flow Architecture](#data-flow-architecture)
- [Module Dependencies](#module-dependencies)
- [Performance Architecture](#performance-architecture)
- [Extensibility](#extensibility)

---

## 🎯 System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                         │
│  ┌──────────────────┐    ┌──────────────────┐                 │
│  │    app.py        │    │    main.py       │                 │
│  │  (Gradio GUI)    │    │  (CLI Voice)     │                 │
│  └────────┬─────────┘    └────────┬─────────┘                 │
└───────────┼──────────────────────┼────────────────────────────┘
            │                      │
┌───────────┼──────────────────────┼────────────────────────────┐
│           │    CONTROLLER LAYER  │                            │
│           ▼                      ▼                            │
│  ┌────────────────────────────────────────────────┐          │
│  │           core/controller.py                    │          │
│  │  • Orchestrates conversation flow               │          │
│  │  • Manages component lifecycle                  │          │
│  │  • Handles chat log persistence                 │          │
│  └────────────────────────────────────────────────┘          │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────┼────────────────────────────────────┐
│         CORE LOGIC LAYER  │                                    │
│                           │                                    │
│  ┌────────────────┐  ┌───┴──────────┐  ┌─────────────────┐   │
│  │ core/brain.py  │  │ core/context │  │ core/memory.py  │   │
│  │               │  │   .py        │  │                 │   │
│  │ • LLM Loading  │  │ • History    │  │ • Semantic      │   │
│  │ • Generation   │  │   Management │  │   Search        │   │
│  │ • Memory Query │  │ • Context    │  │ • Past          │   │
│  │   Integration  │  │   Building   │  │   Retrieval     │   │
│  └────────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────────────┬───────────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────────┐
│         IO LAYER          │                                    │
│                           │                                    │
│  ┌───────────┐  ┌─────────┴──────┐  ┌──────────────────┐     │
│  │  IO/stt.py│  │   IO/tts.py    │  │  IO/vision.py   │     │
│  │           │  │                │  │                  │     │
│  │ • Whisper │  │ • ChatterboxTTS│  │ • Future vision  │     │
│  │   STT     │  │ • Piper TTS    │  │   capabilities   │     │
│  │ • VAD     │  │ • Voice Clone  │  │                  │     │
│  │ • Audio   │  │ • Synthesis    │  │                  │     │
│  └───────────┘  └────────────────┘  └──────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │          IO/coqui_backend.py                         │     │
│  │  • Voice cloning implementation                      │     │
│  │  • Reference audio processing                        │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────────┐
│       UTILITY LAYER        │                                   │
│                           │                                    │
│  ┌─────────────┐  ┌───────┴────────┐  ┌─────────────────┐    │
│  │ utils/      │  │ utils/         │  │ utils/          │    │
│  │ logger.py   │  │ profiler.py    │  │ tools.py        │    │
│  │             │  │                │  │                 │    │
│  │ • Logging   │  │ • Performance  │  │ • Helper        │    │
│  │   Setup     │  │   Monitoring   │  │   Functions     │    │
│  └─────────────┘  └────────────────┘  └─────────────────┘    │
└────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────────┐
│      INTEGRATION LAYER     │                                   │
│                           │                                    │
│  ┌────────────┐  ┌────────┴───────┐  ┌────────────────┐      │
│  │integration/│  │ integration/   │  │ integration/   │      │
│  │browser.py  │  │ pc_control.py  │  │smart_home.py   │      │
│  │            │  │                │  │                │      │
│  │ • Web      │  │ • System       │  │ • IoT          │      │
│  │   Control  │  │   Control      │  │   Control      │      │
│  └────────────┘  └────────────────┘  └────────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

---

## 💡 Design Principles

### 1. **Modularity**

Each component is independent and replaceable:

```python
# Easy to swap implementations
if TTS_BACKEND == "coqui":
    from IO import coqui_backend
else:
    # Fallback to Piper
    use_piper_tts()
```

**Benefits:**
- ✅ Easy to test individual components
- ✅ Can replace/upgrade modules independently
- ✅ Reduces coupling between components
- ✅ Simplifies debugging

### 2. **Local-First**

All processing happens on your machine:

```python
# No external API calls
pipe = pipeline(
    "text-generation",
    model=LLM_MODEL_ID,
    device_map="auto",  # Uses local GPU/CPU
)
```

**Benefits:**
- 🔒 Complete privacy
- ⚡ No network latency
- 💰 No API costs
- 🌐 Works offline

### 3. **Performance Optimization**

Leverages GPU acceleration and efficient algorithms:

```python
# GPU optimization
torch_dtype=torch.float16  # Half precision for speed
device_map="auto"          # Automatic GPU utilization

# Memory efficiency
compute_type="int8"        # Quantization for lower VRAM
```

**Benefits:**
- ⚡ Fast inference
- 💾 Lower memory usage
- 🔋 Efficient resource use

### 4. **Extensibility**

Easy to add new features:

```python
# Simple integration pattern
from integrations import browser
from integrations import smart_home

# Add custom integration
from integrations import my_custom_feature
```

**Benefits:**
- 🔧 Easy to customize
- 📦 Plugin-friendly architecture
- 🚀 Rapid development

---

## 🧩 Component Architecture

### Core: Brain Module

**File:** `core/brain.py`

**Responsibilities:**
- Load and manage LLM
- Generate text responses
- Integrate memory search
- Handle generation parameters

**Key Classes:**

```python
class Brain:
    def __init__(self, context_manager=None):
        self.pipe = self._load_model()
        self.context_manager = context_manager
    
    def _load_model(self):
        """Loads transformer pipeline"""
        
    def generate_response(self, messages, initial=False):
        """Generates AI response with context"""
```

**Architecture Pattern:** Singleton-like (one brain instance per app)

**Dependencies:**
- `transformers` (Hugging Face)
- `torch` (PyTorch)
- `config` (settings)
- `core.context` (conversation history)

### Core: Context Manager

**File:** `core/context.py`

**Responsibilities:**
- Maintain conversation history
- Build context for LLM
- Manage message formatting
- Integrate with memory search

**Key Classes:**

```python
class ContextManager:
    def __init__(self, system_prompt):
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def add_message(self, role, content):
        """Add message to history"""
    
    def get_history(self):
        """Return formatted history for LLM"""
    
    def detect_memory_query(self, text):
        """Detect if user is asking about past conversations"""
    
    def search_and_format_memories(self, query, limit=5):
        """Search past conversations and format for injection"""
```

**Architecture Pattern:** State Manager

**State Management:**
```python
# Short-term memory (current session)
self.messages = [...]

# Long-term memory (via ChatLogManager)
past_logs = chat_log_manager.load_logs()
```

### IO: Speech-to-Text

**File:** `IO/stt.py`

**Responsibilities:**
- Initialize Whisper model
- Capture microphone audio
- Detect voice activity (VAD)
- Transcribe speech

**Key Functions:**

```python
def initialize_stt():
    """Load Whisper model"""
    global stt_model
    stt_model = WhisperModel(
        STT_MODEL_SIZE,
        device="auto",
        compute_type=STT_COMPUTE_TYPE
    )

def listen_and_transcribe(timeout=None):
    """
    Listen via microphone and transcribe
    Returns: (text, audio_array)
    """
```

**Architecture Pattern:** Stateful Service

**Processing Pipeline:**
```
Audio Input → VAD → Buffering → Whisper → Text Output
```

**Optimization:**
- Pre-buffering to capture first word
- Chunk-based processing
- VAD to reduce false triggers

### IO: Text-to-Speech

**File:** `IO/tts.py`

**Responsibilities:**
- Initialize TTS backend
- Synthesize speech
- Handle voice cloning
- Manage audio playback

**Key Functions:**

```python
def initialize_tts():
    """Initialize selected TTS backend"""
    if TTS_BACKEND == "coqui":
        _coqui_ready = coqui_backend.initialize_coqui()
    # Validate Piper as fallback

def speak(text):
    """Convert text to speech and play"""
    sanitized = _sanitize(text)
    if _coqui_ready:
        _speak_coqui(sanitized)
    else:
        _speak_piper(sanitized)
```

**Architecture Pattern:** Strategy Pattern (switchable backends)

**Backend Selection:**
```python
# Runtime backend switching
if TTS_BACKEND == "coqui" and coqui_available:
    use_coqui()
else:
    use_piper()  # Fallback
```

### Core: Controller

**File:** `core/controller.py`

**Responsibilities:**
- Orchestrate conversation loop
- Manage component initialization
- Handle chat log persistence
- Process user input/output

**Key Functions:**

```python
def conversation_loop():
    """
    Main control loop:
    1. Initialize all components
    2. Load past conversations (optional)
    3. Generate initial greeting
    4. Loop: Listen → Think → Speak
    5. Save conversation on exit
    """
```

**Architecture Pattern:** Coordinator/Orchestrator

**Flow Control:**
```
Initialize → Load History → Greeting → Loop → Save → Exit
```

---

## 🌊 Data Flow Architecture

### Request-Response Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                               │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. INPUT PROCESSING                                         │
│    • STT: Voice → Text (if voice input)                     │
│    • File Extractor: File → Text (if file upload)          │
│    • Direct Text: Pass through                              │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CONTEXT BUILDING                                         │
│    • Add user message to history                            │
│    • Detect memory queries                                  │
│    • Search past conversations if needed                    │
│    • Build message array for LLM                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. LLM PROCESSING                                           │
│    • Format messages (system + history + user)              │
│    • Apply generation parameters                            │
│    • Run inference (GPU/CPU)                                │
│    • Generate response text                                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. RESPONSE ROUTING                                         │
│    • Check pipeline configuration                           │
│    • Route to appropriate output                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────────┬─────────────────┐
             ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Text Only   │  │  TTS + Text  │  │  TTS Only    │
    └──────────────┘  └──────────────┘  └──────────────┘
             │                 │                 │
             └─────────────────┴─────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. CONTEXT UPDATE                                           │
│    • Add assistant response to history                      │
│    • Update conversation log                                │
│    • Prepare for next interaction                           │
└─────────────────────────────────────────────────────────────┘
```

### Memory Search Flow

```
User Query: "What did I say about Python?"
    │
    ▼
┌──────────────────────────────────────┐
│ Detect Memory Query                  │
│ Keywords: "what did I", "remember"   │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Load Past Conversation Logs          │
│ From: chat_logs/*.json               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Semantic Search                      │
│ Find relevant messages about "Python"│
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Format Memory Context                │
│ [MEMORY RECALL]                      │
│ Past conversation: ...               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Inject into LLM Context              │
│ System + Memory + Current Query      │
└──────────┬───────────────────────────┘
           │
           ▼
    Generate Response
```

---

## 📦 Module Dependencies

### Dependency Graph

```
main.py / app.py
    │
    ├─→ core/controller.py
    │       │
    │       ├─→ core/brain.py
    │       │       │
    │       │       ├─→ transformers
    │       │       ├─→ torch
    │       │       └─→ config
    │       │
    │       ├─→ core/context.py
    │       │       │
    │       │       └─→ config
    │       │
    │       ├─→ IO/stt.py
    │       │       │
    │       │       ├─→ faster_whisper
    │       │       ├─→ sounddevice
    │       │       ├─→ webrtcvad
    │       │       └─→ config
    │       │
    │       └─→ IO/tts.py
    │               │
    │               ├─→ IO/coqui_backend.py
    │               │       │
    │               │       ├─→ chatterbox-tts
    │               │       └─→ config
    │               │
    │               └─→ config
    │
    └─→ utils/logger.py
```

### External Dependencies

**Core AI:**
- `torch` - PyTorch deep learning framework
- `transformers` - Hugging Face models
- `faster-whisper` - Optimized Whisper STT
- `chatterbox-tts` - Voice cloning TTS

**Audio Processing:**
- `sounddevice` - Audio I/O
- `webrtcvad` - Voice activity detection
- `soundfile` - Audio file handling
- `librosa` - Audio processing utilities

**UI & Integration:**
- `gradio` - Web UI framework
- `pywebview` - Desktop window mode

**Utilities:**
- `numpy` - Numerical operations
- `scipy` - Scientific computing

---

## ⚡ Performance Architecture

### GPU Acceleration

```python
# Automatic GPU utilization
device_map="auto"  # Auto-distributes model across available devices

# Memory optimization
torch_dtype=torch.float16  # Half precision (2x memory saving)
compute_type="int8"        # 8-bit quantization (4x memory saving)
```

### Memory Management

```python
# Streaming inference
for segment in stt_model.transcribe(audio, beam_size=5):
    process_segment(segment)  # Process as we go

# Cleanup
torch.cuda.empty_cache()  # Free GPU memory
del large_object           # Explicit cleanup
```

### Caching Strategy

```
Hugging Face Cache
    ├─ models/              (Downloaded models)
    ├─ tokenizers/          (Tokenizer data)
    └─ transformers/        (Model configs)

Local Cache
    ├─ chat_logs/           (Conversation history)
    └─ testing/outputs/     (Generated audio)
```

---

## 🔧 Extensibility

### Adding New Integrations

```python
# integrations/my_integration.py

def setup():
    """Initialize integration"""
    pass

def handle_command(command: str):
    """Process integration-specific commands"""
    pass

# In main code:
from integrations import my_integration
my_integration.setup()
```

### Custom TTS Backend

```python
# IO/my_tts_backend.py

def initialize():
    """Setup your TTS"""
    pass

def synthesize(text: str) -> Path:
    """Generate audio, return path"""
    pass

# In tts.py:
if TTS_BACKEND == "my_custom":
    from IO import my_tts_backend
```

### Custom Memory Storage

```python
# core/custom_storage.py

class CustomStorage:
    def save_conversation(self, messages):
        # Your storage logic (database, cloud, etc.)
        pass
    
    def load_conversations(self):
        # Your retrieval logic
        pass
```

---

## 🎯 Architecture Best Practices

### 1. **Separation of Concerns**
- Each module has one clear responsibility
- Components don't know about each other's internals

### 2. **Dependency Injection**
```python
# Good: Inject dependencies
brain = Brain(context_manager=context)

# Avoid: Hard-coded dependencies
```

### 3. **Configuration Management**
```python
# All settings in config.py
from config import LLM_MODEL_ID, STT_MODEL_SIZE

# Not scattered throughout code
```

### 4. **Error Handling**
```python
try:
    result = component.process()
except ComponentError as e:
    logging.error(f"Component failed: {e}")
    use_fallback()
```

---

## 📚 Further Reading

- [Core Modules Documentation](Core-Modules.md)
- [IO Modules Documentation](IO-Modules.md)
- [Performance Tips](Performance-Tips.md)
- [API Reference](API-Reference.md)

---

<div align="center">

**[⬆️ Back to Top](#-architecture-overview)** | **[🏠 Home](Home.md)** | **[Next: Core Modules →](Core-Modules.md)**

</div>

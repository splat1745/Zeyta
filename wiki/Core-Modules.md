# 🧠 Core Modules Documentation

Deep dive into Zeyta's core components: Brain, Controller, and Context Manager.

## 📋 Table of Contents

- [Overview](#overview)
- [Brain Module](#brain-module)
- [Controller Module](#controller-module)
- [Context Manager](#context-manager)
- [Integration & Flow](#integration--flow)

---

## 🎯 Overview

Zeyta's core is built on three primary modules that handle the intelligence and conversation management:

```
┌─────────────────────────────────────────────┐
│              CORE MODULES                   │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Brain   │  │Controller│  │ Context  │ │
│  │          │  │          │  │ Manager  │ │
│  │ • LLM    │  │ • Loop   │  │ • History│ │
│  │ • Gen    │  │ • Init   │  │ • Memory │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────┘
```

---

## 🧠 Brain Module

**File:** `core/brain.py`

The Brain is responsible for loading and running the Large Language Model (LLM).

### Class: `Brain`

```python
class Brain:
    """
    Handles loading the Language Model and generating text responses.
    """
    def __init__(self, context_manager=None):
        self.pipe = self._load_model()
        self.context_manager = context_manager
```

### Methods

#### `_load_model()`

Initializes the text-generation pipeline.

```python
def _load_model(self):
    """Loads the text-generation pipeline."""
    pipe = pipeline(
        "text-generation",
        model=LLM_MODEL_ID,
        device_map="auto",       # Automatic GPU/CPU distribution
        return_full_text=False,  # Return only new text
        torch_dtype=torch.float16  # Half precision for speed
    )
    return pipe
```

**Key Features:**
- ✅ Automatic device mapping (GPU/CPU)
- ✅ Half-precision for efficiency
- ✅ Error handling and logging

**Configuration:**
```python
# From config.py
LLM_MODEL_ID = "chuanli11/Llama-3.2-3B-Instruct-uncensored"
```

#### `generate_response(messages, initial=False)`

Generates AI responses based on conversation history.

```python
def generate_response(self, messages, initial=False):
    """
    Generates a response from the LLM.
    
    Args:
        messages: List of conversation messages
        initial: Whether this is the initial greeting
    
    Returns:
        Generated text response
    """
```

**Process:**

1. **Check Memory Queries** (if enabled):
   ```python
   if ENABLE_HISTORY_SEARCH and self.context_manager:
       if self.context_manager.detect_memory_query(user_input):
           memories = self.context_manager.search_and_format_memories(...)
           # Inject memories into context
   ```

2. **Select Generation Args**:
   ```python
   gen_args = INITIAL_GEN_ARGS if initial else GENERATION_ARGS
   ```

3. **Generate Response**:
   ```python
   output = self.pipe(messages, **gen_args)
   response = output[0]['generated_text']
   ```

**Example Usage:**

```python
from core.brain import Brain
from core.context import ContextManager

# Initialize
context = ContextManager("You are a helpful assistant")
brain = Brain(context_manager=context)

# Add user message
context.add_message("user", "What is AI?")

# Generate response
response = brain.generate_response(context.get_history())
print(response)  # "AI, or Artificial Intelligence, is..."

# Add response to history
context.add_message("assistant", response)
```

### Memory Integration

The Brain integrates with memory search:

```python
# When user asks about past conversations
User: "What did I say about Python?"

Brain detects memory query
  ↓
Searches past conversations
  ↓
Finds relevant messages
  ↓
Injects into context:
  [MEMORY RECALL]
  Past conversation: "I love Python for its simplicity..."
  ↓
Generates informed response
```

### Generation Parameters

```python
GENERATION_ARGS = {
    "max_new_tokens": 512,        # Response length
    "do_sample": True,            # Enable sampling
    "temperature": 0.7,           # Creativity level
    "top_p": 0.95,               # Nucleus sampling
    "repetition_penalty": 1.3,    # Avoid repetition
}

INITIAL_GEN_ARGS = {
    "max_new_tokens": 256,        # Shorter greeting
    "temperature": 0.5,           # More focused
    # ... other params
}
```

### Error Handling

```python
try:
    output = self.pipe(messages, **gen_args)
except Exception as e:
    logging.error(f"Generation failed: {e}")
    return "I'm having trouble thinking right now. Please try again."
```

---

## 🎮 Controller Module

**File:** `core/controller.py`

The Controller orchestrates the entire conversation flow.

### Class: `ChatLogManager`

Manages saving and loading conversation logs.

```python
class ChatLogManager:
    def __init__(self, log_dir):
        self.log_dir = log_dir
    
    def load_logs(self):
        """Loads all past conversation logs."""
        # Returns list of past conversations
    
    def save_log(self, conversation_history):
        """Saves current conversation to JSON file."""
        # Saves to chat_logs/chat_YYYY-MM-DD_HH-MM-SS.json
```

**File Format:**
```json
[
  {
    "role": "system",
    "content": "You are a helpful assistant."
  },
  {
    "role": "user",
    "content": "Hello!"
  },
  {
    "role": "assistant",
    "content": "Hi! How can I help you?"
  }
]
```

### Function: `conversation_loop()`

The main conversation orchestrator.

```python
def conversation_loop():
    """
    Main control loop for the assistant.
    Orchestrates listening, thinking, and speaking.
    """
```

**Flow:**

```
┌─────────────────────────────────────┐
│ 1. INITIALIZATION                   │
│    • Create ContextManager          │
│    • Create Brain                   │
│    • Initialize STT                 │
│    • Initialize TTS                 │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 2. LOAD PAST CONVERSATIONS          │
│    (Optional, if INTEGRATE_PAST_LOGS)│
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 3. INITIAL GREETING                 │
│    • Add INITIAL_GREETING to context│
│    • Generate response               │
│    • Speak response                  │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 4. MAIN CONVERSATION LOOP           │
│    ┌─────────────────────────────┐  │
│    │ Listen (STT)                │  │
│    │         ↓                   │  │
│    │ Check for exit phrase       │  │
│    │         ↓                   │  │
│    │ Add to context              │  │
│    │         ↓                   │  │
│    │ Generate response (Brain)   │  │
│    │         ↓                   │  │
│    │ Add response to context     │  │
│    │         ↓                   │  │
│    │ Speak (TTS)                 │  │
│    │         ↓                   │  │
│    │ Repeat                      │  │
│    └─────────────────────────────┘  │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 5. SAVE & EXIT                      │
│    • Save conversation log          │
│    • Speak farewell                 │
│    • Clean exit                     │
└─────────────────────────────────────┘
```

**Code Structure:**

```python
def conversation_loop():
    chat_log_manager = ChatLogManager(CHAT_LOG_DIR)
    
    try:
        # === Initialization ===
        context = ContextManager(SYSTEM_PROMPT)
        brain = Brain(context_manager=context)
        stt.initialize_stt()
        tts.initialize_tts()
        
        # === Load Past Logs ===
        if INTEGRATE_PAST_LOGS:
            past_logs = chat_log_manager.load_logs()
            for conversation in past_logs:
                for msg in conversation:
                    context.add_message(msg["role"], msg["content"])
        
        # === Initial Greeting ===
        context.add_message("user", INITIAL_GREETING)
        response = brain.generate_response(
            context.get_history(), 
            initial=True
        )
        context.add_message("assistant", response)
        tts.speak(response)
        
        # === Main Loop ===
        while True:
            # Listen
            text, audio = stt.listen_and_transcribe()
            
            if not text:
                continue
            
            # Check exit
            if any(phrase in text.lower() for phrase in EXIT_PHRASES):
                tts.speak(FAREWELL_MESSAGE)
                break
            
            # Process
            context.add_message("user", text)
            response = brain.generate_response(context.get_history())
            context.add_message("assistant", response)
            tts.speak(response)
        
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    finally:
        # === Save ===
        if context:
            chat_log_manager.save_log(context.get_history())
```

### Configuration

```python
# From config.py
SYSTEM_PROMPT = "You are a helpful assistant"
INITIAL_GREETING = "Hello! How can I help you?"
EXIT_PHRASES = ["exit", "quit", "goodbye"]
FAREWELL_MESSAGE = "Goodbye! Have a great day!"
CHAT_LOG_DIR = "chat_logs"
INTEGRATE_PAST_LOGS = False
```

---

## 💭 Context Manager

**File:** `core/context.py`

Manages conversation history and memory search.

### Class: `ContextManager`

```python
class ContextManager:
    """
    Manages conversation history and context.
    """
    def __init__(self, system_prompt):
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
```

### Methods

#### `add_message(role, content)`

Adds a message to conversation history.

```python
def add_message(self, role, content):
    """
    Add a message to the conversation history.
    
    Args:
        role: "system", "user", or "assistant"
        content: Message text
    """
    self.messages.append({
        "role": role,
        "content": content
    })
```

**Example:**
```python
context = ContextManager("You are helpful")
context.add_message("user", "What is AI?")
context.add_message("assistant", "AI stands for...")
```

#### `get_history()`

Returns formatted conversation history for LLM.

```python
def get_history(self):
    """
    Get conversation history in format suitable for LLM.
    
    Returns:
        List of message dictionaries
    """
    return self.messages
```

**Output Format:**
```python
[
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI stands for..."},
    {"role": "user", "content": "Tell me more"},
]
```

#### `detect_memory_query(text)`

Detects if user is asking about past conversations.

```python
def detect_memory_query(self, text):
    """
    Detect if user is querying past conversations.
    
    Args:
        text: User input
    
    Returns:
        Boolean - True if memory query detected
    """
    memory_keywords = [
        "remember", "recall", "said", "mentioned",
        "talked about", "discussed", "told you",
        "what did i", "do you remember"
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in memory_keywords)
```

**Examples:**
```python
context.detect_memory_query("What did I say about Python?")  # True
context.detect_memory_query("Do you remember my name?")      # True
context.detect_memory_query("Tell me about AI")              # False
```

#### `search_and_format_memories(query, limit=5)`

Searches past conversations and formats for LLM injection.

```python
def search_and_format_memories(self, query, limit=5):
    """
    Search past conversations for relevant context.
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        Formatted string of relevant past messages
    """
    # Load past logs
    # Perform semantic search
    # Format results
    # Return formatted string
```

**Process:**

```
1. Load all past conversation logs
   ↓
2. Search for relevant messages
   (keyword matching or semantic search)
   ↓
3. Rank by relevance
   ↓
4. Take top N results
   ↓
5. Format for injection:
   [MEMORY RECALL]
   Past conversation (2024-01-15):
   User: "I love Python"
   Assistant: "That's great!..."
   ↓
6. Return formatted string
```

**Example Output:**
```
[MEMORY RECALL]

Relevant past conversation (2024-01-15 10:30):
User: "My favorite programming language is Python"
Assistant: "Python is excellent for beginners and experts alike!"

Relevant past conversation (2024-01-14 15:20):
User: "I'm learning Python for data science"
Assistant: "Great choice! Python has excellent libraries like pandas..."

Use the above context to answer the user's current question.
```

### Memory Search Flow

```
User: "What's my favorite language?"
         ↓
detect_memory_query() → True
         ↓
search_and_format_memories("favorite language")
         ↓
     [Search past logs]
         ↓
   [Find: "favorite ... Python"]
         ↓
    [Format memory context]
         ↓
[Inject into LLM messages]
         ↓
    [Generate response]
         ↓
Response: "Based on our past conversation,
          your favorite language is Python!"
```

### Configuration

```python
# From config.py
ENABLE_HISTORY_SEARCH = True
CHAT_QUERY_MAX_RESULTS = 5
CHAT_LOG_DIR = "chat_logs"
```

---

## 🔄 Integration & Flow

### How Components Work Together

```python
# Example: Complete conversation flow

# 1. Initialize all components
context = ContextManager(SYSTEM_PROMPT)
brain = Brain(context_manager=context)

# 2. User input
user_input = "What did I say about Python yesterday?"

# 3. Add to context
context.add_message("user", user_input)

# 4. Brain detects memory query
messages = context.get_history()
# Brain automatically:
# - Calls context.detect_memory_query()
# - Calls context.search_and_format_memories()
# - Injects memory into messages

# 5. Generate response
response = brain.generate_response(messages)

# 6. Add response to context
context.add_message("assistant", response)

# 7. Continue conversation...
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│                  User Input                         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Context Manager                        │
│  • Add message to history                           │
│  • Detect if memory query                           │
│  • Search past conversations (if needed)            │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ messages (with memory context)
                       │
┌──────────────────────▼──────────────────────────────┐
│                    Brain                            │
│  • Receive messages array                           │
│  • Select generation parameters                     │
│  • Run LLM inference                                │
│  • Generate response text                           │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ response
                       │
┌──────────────────────▼──────────────────────────────┐
│              Context Manager                        │
│  • Add assistant response to history                │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               Controller                            │
│  • Coordinate next action (speak, save, etc.)       │
└─────────────────────────────────────────────────────┘
```

### State Management

**Context State:**
```python
# Current conversation (in memory)
context.messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    # ... continues
]
```

**Persistent State:**
```bash
# Saved to disk
chat_logs/
├── chat_2024-01-15_10-30-45.json
├── chat_2024-01-14_15-20-33.json
└── ...
```

### Threading & Async (Future)

Currently synchronous, but designed for async:

```python
# Future async support
async def conversation_loop():
    async for text in stt.listen_async():
        response = await brain.generate_async(messages)
        await tts.speak_async(response)
```

---

## 📚 Next Steps

- [IO Modules](IO-Modules.md) - STT, TTS, Vision components
- [Advanced Features](Advanced-Features.md) - Memory, voice cloning
- [API Reference](API-Reference.md) - Complete API documentation

---

<div align="center">

**[⬆️ Back to Top](#-core-modules-documentation)** | **[🏠 Home](Home.md)** | **[Next: IO Modules →](IO-Modules.md)**

</div>

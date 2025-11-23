# config.py - Template Configuration
# Copy this file and customize it for your own use

# --- Model Configurations ---
# LLM model for the brain
LLM_MODEL_ID = "chuanli11/Llama-3.2-3B-Instruct-uncensored"  # Or your preferred model

# STT (Whisper) model settings
STT_MODEL_SIZE = "large-v3"  # Options: "tiny", "base", "small", "medium", "large-v3"
STT_COMPUTE_TYPE = "float16"  # "float16", "int8", "float32"

# --- TTS Configuration ---
# Default TTS output settings
TTS_RATE = 175
TTS_VOLUME = 1.0

# Backend selection: "chatterbox", "piper", or "windows"
TTS_BACKEND = "chatterbox"

# Device preference for GPU‑capable backends (chatterbox/piper)
# "auto" = prefer CUDA when available (recommended),
# "cuda" = force GPU, "cpu" = force CPU
TTS_DEVICE = "auto"

# Piper-specific settings (used when TTS_BACKEND == "piper")
# Voice example: "en_US-lessac-high"; see Piper docs/voices
PIPER_MODEL = "en_US-lessac-high"
PIPER_SPEAKER_ID = 0

# Chatterbox-specific preferences
# Whether we are allowed to automatically reinstall a tuned PyTorch stack
# for RTX 50‑series cards (CUDA 12.2, PyTorch 2.1.0+cu122)
ALLOW_TORCH_REINSTALL = True

# --- Conversation Settings ---
SYSTEM_PROMPT = """
You are an AI assistant.
"""
INITIAL_GREETING = "Hello! How can I help you today?"
EXIT_PHRASES = ["exit", "quit", "goodbye"]
FAREWELL_MESSAGE = "Goodbye! Have a great day!"

# Chat log configuration
CHAT_LOG_DIR = "chat_logs"
INTEGRATE_PAST_LOGS = False  # if True, old chats are merged into context
CHAT_QUERY_MAX_RESULTS = 5   # used if implementing search / query features
ENABLE_HISTORY_SEARCH = True  # if True, enables automatic memory search on keywords

# --- Pipeline Generation Arguments ---
GENERATION_ARGS = {
    "max_new_tokens": 4096,
    "do_sample": True,
    "temperature": 0.6,
    "top_p": 0.95,
    "repetition_penalty": 1.3,
}

INITIAL_GEN_ARGS = {
    "max_new_tokens": 256,
    "do_sample": True,
    "temperature": 0.5,
    "top_p": 0.95,
    "repetition_penalty": 1.2,
}
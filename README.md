# Zeyta AI Web Playground

A fully self-contained, locally-hosted web application providing comprehensive AI capabilities including Text-to-Speech, Speech-to-Text, Large Language Model chat, Autonomous Agent Mode, and a Visual Pipeline Builder.

## ✨ Features

### 🗣️ **Text-to-Speech (TTS)**
- High-quality speech synthesis using ChatterboxTTS
- **RTX 50-Series Optimization**: FP16 precision, CUDA Graphs, and embedding caching for lightning-fast generation
- Voice cloning with reference audio support
- Adjustable parameters (temperature, exaggeration, CFG weight)

### 🎤 **Speech-to-Text (STT)**
- Accurate transcription using Faster-Whisper
- Support for audio file upload
- Live microphone recording and transcription
- Multiple language support
- Configurable model sizes (tiny to large-v3-turbo)

### 💬 **AI Chat & Web Search**
- Context-aware conversations powered by Ollama
- **Web Search Plugin**: Real-time internet browsing via DuckDuckGo to answer current events
- **Calculator Plugin**: Solves math problems accurately
- **Vision Plugin**: Analyzes screenshots and images
- Chat history management

### 🤖 **Autonomous Agent Mode**
- **Screen Analysis**: The AI can "see" your screen and understand UI elements
- **Auto-Execution**: Performs multi-step tasks (clicking, typing, navigating) autonomously
- **Task Planning**: Breaks down complex goals into actionable steps
- **Permission System**: Granular control over what the agent can do (mouse, keyboard, file system)

### 🧩 **Visual Pipeline Builder**
- Drag-and-drop interface to create custom AI workflows
- Connect blocks: Mic → STT → LLM → TTS → Audio Output
- **Mobile-Friendly**: Responsive design that adapts layout (vertical on PC, horizontal on mobile)
- Real-time execution logging

### ⚙️ **System Management**
- **Smart Self-Healing Setup**: Automatically detects missing environments, creates virtual environments, and resolves dependency conflicts (e.g., fixing broken pip installs).
- **System Integrity Checks**: Verifies critical folders and files on every startup.
- Real-time system status monitoring (CPU, RAM, GPU VRAM)
- GPU/CPU detection with automatic fallback
- Model configuration display

## 🚀 Quick Start

### ⚠️ Prerequisite: Download Models
**Cloning the repository is not enough!** You must ensure the AI models are available:
1.  **Install Ollama**: Download from [ollama.com](https://ollama.com).
2.  **Pull a Chat Model**: Run `ollama pull llama3` (or `mistral`, `gemma`, etc.) in your terminal.
3.  **First Run Downloads**: The app will download TTS and STT models on the first launch automatically. Ensure you have a stable internet connection.

### Option 1: Simple Run (Recommended)
```powershell
# Run the application as it will install dependencies automatically (may not be enough - Double check!)
.\start.ps1
# OR
.\start.bat
```

### Option 2: Manual Installation
```powershell
# Install dependencies first
pip install -r requirements.txt

# Run the application
python web_app.py
```

Then open your browser to: **https://localhost:5000**

> **Note:** You will see a "Not Secure" warning because the app uses a self-signed certificate. This is required for microphone access. Click "Advanced" -> "Proceed to localhost (unsafe)" to continue.

## 📋 Requirements

### System Requirements
- **Python**: 3.11 (Voice cloning TTS uses 3.11 strictly)
- **RAM**: 16GB minimum (32GB recommended for Agent Mode or smarter models)
- **GPU**: NVIDIA GPU with CUDA support (RTX 3060 or better recommended; RTX 50-series optimized)
- **Storage**: 20GB free space for models

### Python Dependencies
All dependencies are automatically installed on first run:
- Flask (web framework)
- PyTorch & TorchAudio (deep learning)
- ChatterboxTTS (text-to-speech)
- Faster-Whisper (speech-to-text)
- Ollama (LLM backend)
- DuckDuckGo Search (web browsing)
- PyAutoGUI & Pillow (screen interaction)
- SoundDevice & SoundFile (audio processing)

## 📁 Project Structure

```
AI-RELEASE/
├── web_app.py          # Main Flask application with auto-dependency management
├── agent.py            # Autonomous agent logic (screen analysis, task execution)
├── tts_optimizer.py    # RTX 50-series specific optimizations
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── start.ps1           # PowerShell startup script (with integrity checks)
├── start.bat           # Batch startup script (with integrity checks)
├── setup/
│   ├── smart_setup.py  # Self-healing dependency installer
│   └── ...
├── templates/          # HTML templates
│   ├── index.html      # Home page
│   ├── tts.html        # Text-to-Speech page
│   ├── stt.html        # Speech-to-Text page
│   ├── chat.html       # AI Chat page
│   ├── agent.html      # Agent Mode page
│   ├── pipeline.html   # Visual Pipeline Builder
│   └── ...
├── static/             # Static assets (CSS, JS)
├── uploads/            # Uploaded files (auto-created)
└── outputs/            # Generated audio files (auto-created)
```

## 🎯 Usage Guide

### 1. **Home Page**
- View system status
- Quick navigation to all features
- Real-time model status updates

### 2. **Text-to-Speech**
1. Click "Initialize TTS" to load the model
2. Enter text in the text box
3. (Optional) Upload reference audio for voice cloning
4. Click "Generate Speech"

### 3. **Speech-to-Text**
1. Click "Initialize STT" and choose model size (Turbo recommended)
2. Upload a file or use "Live Recording" to transcribe speech

### 4. **AI Chat**
1. Click "Initialize LLM" to connect to Ollama
2. Enable plugins like **Web Search** or **Vision**
3. Ask questions about current events or math problems
4. The AI will use tools to provide accurate answers

### 5. **Agent Mode** (still in beta)
1. Click "Initialize Agent"
2. Select an Ollama model (e.g., LLaVA or Qwen-VL for vision)
3. Type a task: "Open Notepad and write a poem about AI"
4. Watch as the agent takes control of your mouse and keyboard to complete the task
5. **Emergency Stop**: Click "Cancel Task" at any time

### 6. **Pipeline Builder**
1. Drag blocks from the sidebar (Mic, STT, LLM, TTS, Speaker)
2. Connect them to form a chain
3. Click "Run Pipeline" to execute the flow step-by-step
4. Great for testing custom interactions without coding

## 🔧 Configuration

### Model Settings

#### TTS Configuration
- **Device**: Auto-detected (GPU if available, else CPU)
- **RTX 50-Series**: Automatically enables FP16 and CUDA Graphs if detected

#### STT Configuration
- **Model Size**: tiny, base, small, medium, large-v3, large-v3-turbo
- **Compute Type**: Auto, float16 (GPU), int8 (CPU)

#### LLM Configuration
- **Provider**: Ollama (local), OpenAI, Anthropic
- **Model**: Select from installed Ollama models

## 🔒 Security Notes

**This application is designed for LOCAL USE ONLY**
- **Agent Mode**: Grants the AI control over your mouse and keyboard. Use with caution and monitor execution.
- **Web Server**: Runs on all network interfaces (0.0.0.0) by default for local network access.
- **No Authentication**: Do not expose to the public internet.

## 📜 License

Copyright © 2025 Zeyta AI. All rights reserved.

---

**Made with ❤️ for easy AI interaction**

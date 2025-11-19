# Zeyta — AI Assistant with Voice

A modular, local-first voice-based AI assistant powered by local LLMs, speech-to-text (Whisper/faster-whisper), and optimized text-to-speech with voice cloning support.

Table of contents
- Features
- Architecture & Project Structure
- Setup & Installation
- Configuration
- Running
- Troubleshooting
- Development & Contributing
- License & Credits

## Features

- 🎙️ Voice Interaction: Speech-to-text using Whisper / faster-whisper and text-to-speech with voice cloning
- 🧠 Local LLM: Run on your hardware using Hugging Face Transformers
- 🎭 Voice Cloning: Multi-reference voice cloning via ChatterboxTTS
- ⚡ GPU Optimized: CUDA acceleration, memory pinning, and streaming
- 📝 Conversation History: Maintains context across sessions
- 🎯 Customizable Personality: Configure AI behavior via prompts
- 🛠️ Standalone & testing apps: Terminal-based testing interfaces and an optional GUI app

## Architecture

Zeyta is organized modularly to separate concerns and make maintenance easier. Components are split into core logic, IO handlers, integrations, and testing tools.

## Project structure (overview)

```
zeyta/
├── main.py                 # Main voice assistant entry point
├── app.py                  # Standalone window / desktop app entry (optional)
├── config.example.py       # Template configuration
├── config.py               # (gitignored) Actual configuration - create from example
├── requirements.txt        # Python dependencies
├── core/                   # Core logic
│   ├── brain.py            # LLM interaction
│   ├── context.py          # Conversation history management
│   └── controller.py       # Main orchestration loop
├── IO/                     # Input/Output handlers
│   ├── stt.py              # Speech-to-Text (Whisper / faster-whisper)
│   ├── tts.py              # Text-to-Speech (Coqui / Piper)
│   ├── coqui_backend.py    # Voice cloning backend (ChatterboxTTS)
│   ├── mic_stream.py       # Microphone streaming utilities
│   └── vision.py           # Vision capabilities (future)
├── integrations/           # Third-party integration modules (browser, smart home, etc.)
├── utils/                  # Helper utilities (logger, profiler, tools)
├── testing/                # Testing tools and apps
│   ├── standalone_app.py
│   ├── integrated_app.py
│   ├── test_tts_clean.py
│   └── tts_server.py
├── testing/outputs/        # Generated audio files during tests
├── piper/                  # Optional Piper TTS backend files
└── docs/                   # Documentation (APP_GUIDE, ARCHITECTURE, etc.)
```

## Prerequisites

- Python 3.11+
- FFmpeg installed on your system (for audio handling)
- CUDA-capable NVIDIA GPU recommended for best performance (8GB+ VRAM recommended)
- Optional: PyWebView for standalone window mode

## Installation

1. Clone the repository
```bash
git clone https://github.com/relfayoumi/Zeyta.git
cd Zeyta
```

2. Create and activate a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. (Optional) Install PyTorch with CUDA (example for CUDA 12.1)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Configuration

1. Copy the example configuration:
```bash
cp config.example.py config.py
```
2. Edit `config.py`:
- Set `LLM_MODEL_ID` to a Hugging Face model suitable for your hardware.
- Adjust `STT_MODEL_SIZE` (tiny, base, small, medium, large-v3).
- Choose `TTS_BACKEND`: `"coqui"` (voice cloning) or `"piper"` (fallback).
- Set `COQUI_REFERENCE_WAV` path for voice cloning reference files.
- Set `SYSTEM_PROMPT`, `GENERATION_ARGS`, and other options to tune behavior.

Note: `config.py` is intentionally excluded from git and stores personal settings.

## Running

- Run the interactive AI assistant (recommended):
```bash
python app.py
```

- Run the command-line assistant:
```bash
python main.py
```

- Run the integrated testing GUI (for model testing and development):
```bash
python testing/integrated_app.py
```

- Standalone terminal testing app:
```bash
python testing/standalone_app.py
```

- Test TTS optimization and voice cloning:
```bash
python testing/test_tts_clean.py --ref-dir IO/AudioRef_48kHz --expressive --temperature 0.75
```

- Run persistent TTS server:
```bash
python testing/tts_server.py
```

## Capabilities & Pipelines

Configurable pipelines include:
- Text Chat Only (LLM)
- Voice to Text (STT → LLM)
- Voice to Voice (STT → LLM → TTS)
- Text to Voice (LLM → TTS)

## Troubleshooting

- Import errors for faster-whisper:
```bash
pip install faster-whisper
```
- Import errors for chatterbox:
```bash
pip install chatterbox-tts
```
- CUDA Out of Memory:
  - Reduce model sizes in `config.py`
  - Use `STT_COMPUTE_TYPE = "int8"`
  - Close other GPU apps
  - Use smaller LLM models
- Audio issues:
  - Check microphone permissions
  - Verify `config.py` TTS backend setting
  - Inspect `testing/outputs/` for generated audio files

## Performance Tips

1. Use a GPU for inference when possible.
2. Balance model size vs. speed—smaller models are faster with lower quality.
3. Tune generation args (temperature, top-p, max tokens).
4. Use 5–10 second reference clips for voice cloning.
5. Memory pinning and CUDA optimizations are used where available.

## Development & Contributing

Project philosophy:
- Modular design — each component is independent and testable.
- Local-first — runs on your hardware, no cloud dependencies.
- Optimized — GPU acceleration, efficient memory usage.
- Customizable — extensive configuration options.

Contributing:
1. Fork the repo
2. Create a feature branch
3. Implement and test your changes (use the standalone testing app)
4. Submit a pull request

## Documentation

See docs/ for more details:
- docs/APP_GUIDE.md
- docs/ARCHITECTURE.md
- docs/FEATURE_SHOWCASE.md
- docs/QUICK_REFERENCE.md
- docs/USAGE_EXAMPLES.md

## License

See the LICENSE file for details. Check individual dependency licenses for any external libraries used.

## Credits

Built with:
- Transformers (Hugging Face) — LLM inference
- Faster-Whisper — STT
- ChatterboxTTS — Voice cloning
- Piper TTS — Fast fallback TTS

---

This project emphasizes local, privacy-first AI assistance: all processing occurs on your hardware.

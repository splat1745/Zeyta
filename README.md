# Zeyta - AI Assistant with Voice# Zeyta - AI Assistant with Voice



A modular voice-based AI assistant powered by local language models, speech-to-text, and optimized text-to-speech with voice cloning capabilities.A modular voice-based AI assistant powered by local language models, speech-to-text, and optimized text-to-speech with voice cloning capabilities.



## Features## Features



- 🎙️ **Voice Interaction**: Speech-to-text using Whisper and text-to-speech with voice cloning

- 🧠 **Local LLM**: Runs on your hardware using transformers

- 🎭 **Voice Cloning**: Multi-reference voice cloning using ChatterboxTTS

- ⚡ **GPU Optimized**: CUDA acceleration, memory pinning, and streaming

- 📝 **Conversation History**: Maintains context across sessions

- 🎯 **Customizable Personality**: Configure your AI's behavior via prompts

- 🛠️ **Standalone Testing App**: Terminal-based interactive testing interface

## Architecture

## Project Structure

The project is organized into a modular structure to separate concerns and improve maintainability.

```

zeyta/- **`main.py`**: The main entry point of the application

├── main.py                 # Main voice assistant entry point- **`config.py`**: Contains all constants, model IDs, and configuration settings

├── config.py               # Configuration (create from config.example.py)- **`core/`**: The core logic of the assistant

├── config.example.py       # Template configuration  - `brain.py`: Handles interaction with the Large Language Model (LLM)

├── requirements.txt        # Python dependencies  - `context.py`: Manages the conversation history

│  - `controller.py`: The main loop that orchestrates the flow between I/O and the brain

├── core/                   # Core logic- **`io/`**: Handles all input and output operations

│   ├── brain.py           # LLM interaction  - `stt.py`: Speech-to-Text using faster-whisper

│   ├── context.py         # Conversation history management  - `tts.py`: Text-to-Speech using Coqui/Piper

│   └── controller.py      # Main orchestration loop  - `coqui_backend.py`: Voice cloning backend

│- **`integrations/`**: Modules for controlling third-party systems (placeholders)

├── IO/                     # Input/Output handlers- **`utils/`**: Helper scripts for logging, tools, and profiling

│   ├── stt.py             # Speech-to-Text (Whisper)- **`testing/`**: TTS optimization scripts

│   ├── tts.py             # Text-to-Speech (Coqui/Piper)  - `test_tts_clean.py`: Standalone TTS testing with optimizations

│   ├── coqui_backend.py   # Voice cloning backend  - `tts_server.py`: Persistent TTS server mode

│   ├── mic_stream.py      # Microphone streaming  - `integrated_app.py`: Web-based testing interface for all components

│   └── vision.py          # Vision capabilities (future)- **`tests/`**: Unit tests for the modules

│

├── testing/                # Testing tools## Setup

│   ├── standalone_app.py  # Interactive terminal testing app

│   ├── test_tts_clean.py  # TTS optimization testing### 1. Prerequisites

│   ├── tts_server.py      # Persistent TTS server mode

│   └── outputs/           # Generated audio files- Python 3.11+

│- CUDA-capable GPU (recommended for optimal performance)

├── integrations/           # Third-party integrations- FFmpeg installed on your system

│   ├── browser.py         # Browser control

│   ├── pc_control.py      # PC automation### 2. Installation

│   └── smart_home.py      # Smart home integration

│```bash

├── utils/                  # Helper utilities# Clone the repository

│   ├── logger.py          # Logging configurationgit clone https://github.com/relfayoumi/Zeyta.git

│   ├── profiler.py        # Performance profilingcd Zeyta

│   └── tools.py           # Utility functions

│# Create virtual environment

└── piper/                  # Piper TTS backend (fallback)python -m venv .venv

    ├── piper.exe          # Piper executable.venv\Scripts\activate  # Windows

    └── *.onnx             # Voice models# source .venv/bin/activate  # Linux/Mac

```

# Install PyTorch with CUDA support

## Quick Startpip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121



### 1. Setup Environment# Install dependencies

pip install -r requirements.txt

```bash```

# Create virtual environment

python -m venv .venv### 3. Configuration



# Activate (Windows)```bash

.venv\Scripts\activate# Copy the example config

cp config.example.py config.py

# Activate (Linux/Mac)

source .venv/bin/activate# Edit config.py with your preferences:

# - Set your AI's personality in SYSTEM_PROMPT

# Install dependencies# - Configure TTS backend (coqui or piper)

pip install -r requirements.txt# - Set reference voice file path (for voice cloning)

```# - Adjust model sizes based on your hardware

```

### 2. Configure Settings

### 4. Running

```bash
# Run the interactive AI assistant app (recommended for daily use)
python app.py

# Or run the voice assistant (command-line)
python main.py

# Edit config.py with your preferences:

# - LLM model selection# Or test TTS independently

# Or launch the integrated testing app (for model testing)
python testing/integrated_app.py
```

## 🚀 AI Assistant Application

We provide a user-friendly application for daily use that runs in **its own standalone window**:

```bash
python app.py
```

**Features:**
- 🖥️ **Standalone Window**: Runs as a native desktop application (no browser needed)
- 💬 **Chat Interface**: Clean, intuitive chat window
- 📎 **File Upload**: Upload and discuss documents (TXT, PDF, DOCX, MD)
- 🔧 **Pipeline Configuration**: Choose your processing mode:
  - Text Chat Only (LLM)
  - Voice to Text (STT → LLM)
  - Voice to Voice (STT → LLM → TTS)
  - Text to Voice (LLM → TTS)
- 🎤 **Voice Input/Output**: Full voice conversation support

**Installation for standalone window mode:**
```bash
pip install pywebview
```

See [`docs/APP_GUIDE.md`](docs/APP_GUIDE.md) for detailed documentation.

## 🧪 Integrated Testing App

For model testing and development:

python testing/integrated_app.py

**Main Voice Assistant:**```

```bash

python main.py## 🧪 Integrated Testing App

```

The testing app provides:
- 🗣️ **TTS Testing**: Test ChatterboxTTS models with voice cloning
- 🎤 **STT Testing**: Test Whisper models with microphone support
- 💬 **LLM Chat**: Interactive text-to-text chat interface
- 🔄 **Full Pipeline**: Test complete STT → LLM → TTS workflow

```bash

python testing/standalone_app.pypython testing/integrated_app.py

```



The standalone app provides an interactive terminal menu to test:The app provides:

- 🗣️ **TTS Testing**: Test ChatterboxTTS models with voice cloning

- 🎤 **STT Testing**: Test Whisper models with microphone support

- 💬 **LLM Chat**: Interactive text-to-text chat interface

- 🔄 **Full Pipeline**: Test complete STT → LLM → TTS workflow



## Configuration OptionsSee [`testing/INTEGRATED_APP.md`](testing/INTEGRATED_APP.md) for detailed documentation.



Edit `config.py` to customize:## TTS Optimization Features



### LLM SettingsThe testing suite includes advanced optimizations:

- `LLM_MODEL_ID`: Hugging Face model ID

- `GENERATION_ARGS`: Temperature, top_p, max tokens, etc.- ✅ **Reference Filtering**: Automatically filters audio files >11 seconds

- `SYSTEM_PROMPT`: AI personality and behavior- ✅ **GPU Optimizations**: CUDA streams, pinned memory, disabled gradients

- ✅ **Multi-threading**: Parallel reference loading

### STT Settings- ✅ **Caching**: Reference audio caching for faster subsequent runs

- `STT_MODEL_SIZE`: Whisper model size (tiny, base, small, medium, large-v3)- ✅ **Benchmark Mode**: Consistent performance testing

- `STT_COMPUTE_TYPE`: Precision (float16, int8, float32)- ✅ **Server Mode**: Zero-reload persistent model hosting



### TTS SettingsSee `testing/FIXES_APPLIED.md` for detailed optimization documentation.

- `TTS_BACKEND`: "coqui" (voice cloning) or "piper" (fallback)

- `COQUI_MODEL_NAME`: Voice cloning model## Voice Cloning Setup

- `COQUI_REFERENCE_WAV`: Reference audio for voice cloning

- `COQUI_DEVICE`: "cuda" or "cpu"1. Record reference audio samples (5-10 seconds each)

2. Place them in `IO/AudioRef_48kHz/` directory

### Conversation Settings3. Use `--blend-voices` flag for multi-reference cloning

- `CHAT_LOG_DIR`: Directory for conversation logs4. See `QUALITY_GUIDE.md` for recording tips

- `EXIT_PHRASES`: Words to end conversation

- `FAREWELL_MESSAGE`: Goodbye message## Performance



## GPU Requirements- **Model Loading**: ~10s (first run), ~0s (in-memory cache)

- **TTS Generation**: ~8-10s per sentence (GPU)

For best performance:- **Server Mode**: Zero reload overhead between generations

- **NVIDIA GPU** with CUDA support

- **8GB+ VRAM** recommended for large models## Documentation

- **CUDA Toolkit** installed

- `QUALITY_GUIDE.md` - Voice recording quality guidelines

The system auto-detects and uses GPU when available. CPU fallback is supported but slower.- `testing/CACHING_INVESTIGATION.md` - Caching implementation details

- `testing/MODEL_CACHING_STATUS.md` - Model serialization limitations

## Testing Features- `testing/FIXES_APPLIED.md` - Complete optimization summary



### Standalone Testing App## Contributing

Interactive terminal interface for testing all components:

Contributions are welcome! Please feel free to submit pull requests or open issues.

```bash

python testing/standalone_app.py## License

```

This project is open source. Please check individual dependencies for their licenses.

Features:

- Color-coded terminal output## Credits

- No browser required

- Lazy model loading (only load what you need)- Uses [ChatterboxTTS](https://github.com/resemble-ai/chatterbox) for voice cloning

- Persistent chat history during session- Powered by [Whisper](https://github.com/openai/whisper) for speech recognition

- System information display- LLM support via [Transformers](https://github.com/huggingface/transformers)

```

### TTS Optimization Testing

Test and benchmark TTS with various settings:

```bash
python testing/test_tts_clean.py --ref-dir IO/AudioRef_48kHz --expressive --temperature 0.75
```

### TTS Server Mode

Run TTS as a persistent server:

```bash
python testing/tts_server.py
```

## Troubleshooting

### Import Errors

If you get `faster-whisper` import errors:
```bash
pip install faster-whisper
```

If you get `chatterbox` import errors:
```bash
pip install chatterbox-tts
```

### CUDA Out of Memory

- Reduce model size in config
- Use `STT_COMPUTE_TYPE = "int8"` for lower memory usage
- Close other GPU applications
- Use smaller LLM models

### Audio Issues

- Ensure microphone permissions are granted
- Check `config.py` TTS backend settings
- Test with standalone app first
- Verify audio files in `testing/outputs/`

## Development

### Project Philosophy

- **Modular Design**: Each component is independent and testable
- **Local-First**: Runs entirely on your hardware, no cloud dependencies
- **Optimized**: GPU acceleration, efficient memory usage, streaming
- **Customizable**: Extensive configuration options

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with standalone app
5. Submit a pull request

## Security

- `config.py` is excluded from git (contains personal settings)
- Use `config.example.py` as a template
- Conversation logs stored locally in `chat_logs/`
- No data sent to external servers

## Performance Tips

1. **Use GPU**: Dramatically faster inference
2. **Optimize Model Size**: Balance quality vs. speed
3. **Tune Generation Args**: Lower temperature/tokens for faster responses
4. **Voice Cloning**: Use 5-10 second reference audio
5. **Memory Pinning**: Enabled automatically for CUDA

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[APP_GUIDE.md](docs/APP_GUIDE.md)** - Complete user guide for the web application
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design
- **[FEATURE_SHOWCASE.md](docs/FEATURE_SHOWCASE.md)** - Feature overview and examples
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Quick reference guide
- **[USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md)** - Usage scenarios and examples

Additional resources:
- **[examples/](examples/)** - Demo scripts and examples
- **[testing/](testing/)** - Testing tools and utilities

## License

See LICENSE file for details.

## Credits

Built with:
- [Transformers](https://huggingface.co/transformers) - LLM inference
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - STT
- [Coqui TTS](https://github.com/coqui-ai/TTS) / [ChatterboxTTS](https://github.com/resemble-ai/chatterbox) - Voice cloning
- [Piper TTS](https://github.com/rhasspy/piper) - Fallback TTS

---

**Note**: This project is focused on local, privacy-first AI assistance. All processing happens on your hardware.



# 🌟 Welcome to Zeyta Wiki

<div align="center">

![Zeyta Logo](images/zeyta-banner.png)

**A modular, local-first voice-based AI assistant powered by local LLMs**

[Getting Started](Getting-Started.md) • [Architecture](Architecture.md) • [Configuration](Configuration.md) • [API Reference](API-Reference.md)

</div>

---

## 📖 What is Zeyta?

Zeyta is a powerful, privacy-first AI assistant that runs entirely on your hardware. It combines:
- 🧠 **Local LLM** - AI that thinks and responds using models running on your machine
- 🎤 **Speech Recognition** - Whisper-based speech-to-text conversion
- 🔊 **Voice Synthesis** - High-quality text-to-speech with voice cloning capabilities
- 💬 **Conversation Memory** - Context-aware conversations that remember past interactions
- 🔧 **Modular Design** - Easy to customize and extend

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **🎙️ Voice Interaction** | Natural voice conversations using Whisper STT and ChatterboxTTS |
| **🧠 Local LLM** | Complete privacy - all processing on your hardware |
| **🎭 Voice Cloning** | Multi-reference voice cloning for personalized TTS |
| **⚡ GPU Optimized** | CUDA acceleration for fast inference |
| **📝 Conversation History** | Maintains context across sessions |
| **🎯 Customizable** | Extensive configuration options |
| **🛠️ Multiple Interfaces** | CLI, GUI, and desktop app modes |

## 📚 Wiki Navigation

### For Beginners 👶

1. **[Getting Started](Getting-Started.md)** - Install and run Zeyta in 5 minutes
2. **[Basic Concepts](Basic-Concepts.md)** - Understanding the core ideas
3. **[Configuration Guide](Configuration.md)** - Setting up your preferences
4. **[Pipeline Modes](Pipeline-Modes.md)** - Choose how you want to interact

### For Advanced Users 🚀

1. **[Architecture Overview](Architecture.md)** - Deep dive into system design
2. **[Core Modules](Core-Modules.md)** - Brain, Controller, Context management
3. **[IO Modules](IO-Modules.md)** - STT, TTS, and Vision components
4. **[Advanced Features](Advanced-Features.md)** - Voice cloning, memory search
5. **[API Reference](API-Reference.md)** - Complete API documentation

### For Developers 💻

1. **[Contributing Guide](Contributing.md)** - How to contribute to Zeyta
2. **[Code Structure](Code-Structure.md)** - Understanding the codebase
3. **[Testing Guide](Testing.md)** - Running and writing tests
4. **[Integration Examples](Integration-Examples.md)** - Extend Zeyta's capabilities

### Support & Resources 🆘

1. **[Troubleshooting](Troubleshooting.md)** - Common issues and solutions
2. **[FAQ](FAQ.md)** - Frequently asked questions
3. **[Performance Tips](Performance-Tips.md)** - Optimize for your hardware
4. **[Changelog](Changelog.md)** - What's new in each version

## 🎨 Visual Overview

```
┌─────────────────────────────────────────────────────────┐
│                    🎤 User Input                        │
│              (Voice, Text, or Documents)                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              📝 Input Processing Layer                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│   │   STT    │  │   Text   │  │   File   │            │
│   │ Whisper  │  │  Direct  │  │ Extractor│            │
│   └──────────┘  └──────────┘  └──────────┘            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              🧠 AI Processing Core                      │
│   ┌─────────────────────────────────────────┐          │
│   │         Context Manager                 │          │
│   │    (Conversation History & Memory)      │          │
│   └──────────────────┬──────────────────────┘          │
│                      │                                  │
│   ┌──────────────────▼──────────────────────┐          │
│   │         LLM Brain (Transformers)        │          │
│   │      (Llama, GPT, or Custom Model)      │          │
│   └──────────────────┬──────────────────────┘          │
└──────────────────────┼──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              🔊 Output Generation Layer                 │
│   ┌──────────┐              ┌──────────┐               │
│   │   Text   │              │   TTS    │               │
│   │  Display │              │ Chatter/ │               │
│   │          │              │  Piper   │               │
│   └──────────┘              └──────────┘               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    💬 AI Response                       │
│              (Text, Voice, or Both)                     │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/relfayoumi/Zeyta.git
cd Zeyta

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure (copy and edit)
cp config.example.py config.py
nano config.py

# 4. Run the assistant
python app.py
```

👉 **[Complete Installation Guide →](Getting-Started.md)**

## 🌐 Project Links

- **GitHub Repository**: [relfayoumi/Zeyta](https://github.com/relfayoumi/Zeyta)
- **Documentation**: [docs/](../docs/)
- **Issue Tracker**: [GitHub Issues](https://github.com/relfayoumi/Zeyta/issues)

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.11 or higher
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **CPU**: Multi-core processor (Intel i5/AMD Ryzen 5 or better)

### Recommended Requirements
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for optimal performance)
- **CUDA**: 12.1 or higher (for GPU acceleration)
- **RAM**: 16 GB or more
- **Storage**: 20 GB+ free space (for models)

## 💡 Understanding Zeyta's Philosophy

Zeyta is built on three core principles:

1. **🔒 Privacy First** - All processing happens locally on your machine. No data leaves your computer.

2. **🧩 Modular Design** - Each component is independent and can be customized or replaced.

3. **⚡ Performance Optimized** - GPU acceleration, efficient memory usage, and streaming support.

## 📖 Documentation Structure

This wiki is organized to help both beginners and advanced users:

- **Conceptual Guides** - Understand what Zeyta does and how it works
- **Tutorials** - Step-by-step instructions for common tasks
- **How-To Guides** - Solutions for specific problems
- **Reference** - Technical specifications and API documentation

## 🤝 Contributing

Zeyta is an open-source project and welcomes contributions! See our [Contributing Guide](Contributing.md) to get started.

## 📄 License

See the [LICENSE](../LICENSE) file for details.

---

<div align="center">

**[⬆️ Back to Top](#-welcome-to-zeyta-wiki)**

Made with ❤️ by the Zeyta community

</div>

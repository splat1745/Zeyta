# Zeyta AI Web Application 🤖

A fully self-contained, locally-hosted web application providing comprehensive AI capabilities including Text-to-Speech, Speech-to-Text, and Large Language Model chat functionality.

## ✨ Features

### 🗣️ **Text-to-Speech (TTS)**
- High-quality speech synthesis using ChatterboxTTS
- Voice cloning with reference audio support
- Adjustable parameters (temperature, exaggeration, CFG weight)
- Multiple voice samples support

### 🎤 **Speech-to-Text (STT)**
- Accurate transcription using Whisper
- Support for audio file upload
- Live microphone recording and transcription
- Multiple language support
- Configurable model sizes (tiny to large-v3)

### 💬 **AI Chat**
- Context-aware conversations
- Powered by advanced LLM
- Chat history management
- Real-time responses

### 🔄 **Full Pipeline**
- Complete end-to-end workflow
- Audio → Transcription → AI Response → Speech
- Automated processing
- Visual step tracking

### ⚙️ **System Management**
- Automatic dependency installation
- Real-time system status monitoring
- GPU/CPU detection
- Model configuration display

## 🚀 Quick Start

### Option 1: Simple Run (Recommended)
```powershell
# Just run the application - it will install dependencies automatically
python web_app.py
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
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended for large models)
- **Storage**: 10GB free space for models
- **GPU**: Optional (CUDA-capable for faster processing)

### Python Dependencies
All dependencies are automatically installed on first run:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- Flask-SocketIO (real-time communication)
- PyTorch & TorchAudio (deep learning)
- ChatterboxTTS (text-to-speech)
- Faster-Whisper (speech-to-text)
- Transformers (AI models)
- SoundDevice & SoundFile (audio processing)
- WebRTCVAD (voice activity detection)

## 📁 Project Structure

```
AI-RELEASE/
├── web_app.py          # Main Flask application with auto-dependency management
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/         # HTML templates
│   ├── index.html     # Home page
│   ├── tts.html       # Text-to-Speech page
│   ├── stt.html       # Speech-to-Text page
│   ├── chat.html      # AI Chat page
│   ├── pipeline.html  # Full Pipeline page
│   └── system.html    # System Information page
├── static/            # Static assets
│   ├── style.css      # Main stylesheet
│   ├── app.js         # Common functions
│   ├── tts.js         # TTS functionality
│   ├── stt.js         # STT functionality
│   ├── chat.js        # Chat functionality
│   ├── pipeline.js    # Pipeline functionality
│   └── system.js      # System info functionality
├── uploads/           # Uploaded files (auto-created)
└── outputs/           # Generated audio files (auto-created)
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
4. Adjust advanced settings if desired
5. Click "Generate Speech"
6. Listen to and download the result

### 3. **Speech-to-Text**
1. Click "Initialize STT" and choose model size
2. **For File Transcription:**
   - Switch to "Transcribe File" tab
   - Upload an audio file
   - Click "Transcribe"
3. **For Live Recording:**
   - Switch to "Live Recording" tab
   - Click "Start Recording"
   - Speak into your microphone
   - Click "Stop Recording" when done

### 4. **AI Chat**
1. Click "Initialize LLM" to load the language model
2. Type your message in the chat box
3. Press Enter or click "Send"
4. View AI responses in real-time
5. Use "Clear History" to start fresh

### 5. **Full Pipeline**
1. Click "Initialize All Models" (this may take a few minutes)
2. Upload an audio file containing a question or statement
3. Click "Run Complete Pipeline"
4. Watch as the system:
   - Transcribes your audio
   - Generates an AI response
   - Converts the response to speech
5. Download the final audio output

### 6. **System Information**
- View hardware status (GPU/CPU)
- Check model loading status
- See configuration details
- Monitor dependencies
- Track output files

## 🔧 Configuration

### Model Settings

#### TTS Configuration
- **Device**: Auto-detected (GPU if available, else CPU)
- **Temperature**: Controls randomness (0.0 - 1.0)
- **Exaggeration**: Voice expressiveness (0.0 - 1.0)
- **CFG Weight**: Classifier-free guidance (0.0 - 1.0)

#### STT Configuration
- **Model Size**: tiny, base, small, medium, large-v3
  - `tiny`: Fastest, least accurate
  - `base`: Good balance (recommended)
  - `medium`: High accuracy
  - `large-v3`: Best accuracy, slower
- **Device**: Auto, CUDA (GPU), or CPU
- **Compute Type**: Auto, float16 (GPU), int8 (CPU)

#### LLM Configuration
- Uses your existing Brain and ContextManager from core/
- System prompt loaded from config.py if available

## 🛠️ Troubleshooting

### Dependency Installation Issues

**Problem**: Package fails to install
```powershell
# Manual installation with verbose output
pip install <package-name> --verbose
```

**Problem**: Missing Visual C++ compiler (Windows)
- Install "Build Tools for Visual Studio"
- Choose "Desktop development with C++"
- Download: https://visualstudio.microsoft.com/downloads/

### Model Loading Issues

**Problem**: Out of memory
- Use smaller model sizes (tiny/base for STT)
- Close other applications
- Force CPU mode if GPU memory is insufficient

**Problem**: Models download slowly
- Models are downloaded on first use
- Be patient during first initialization
- Check internet connection

### Audio Issues

**Problem**: Microphone not detected
```powershell
# Install/reinstall sounddevice
pip install --upgrade --force-reinstall sounddevice
```

**Problem**: Generated audio won't play
- Check browser console for errors
- Try downloading and playing locally
- Verify output file exists in outputs/ folder

### Server Issues

**Problem**: Port 5000 already in use
```python
# Edit web_app.py, change last line to:
socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
```

**Problem**: CORS errors
- Already configured with Flask-CORS
- Check browser console for specific errors
- Ensure you're accessing via https://localhost:5000

## 🔒 Security Notes

**This application is designed for LOCAL USE ONLY**
- Do not expose to the internet without proper security measures
- No authentication system included
- File uploads have size limits but minimal validation
- Runs on all network interfaces (0.0.0.0) by default

For production deployment:
- Add authentication (Flask-Login, OAuth)
- Implement rate limiting
- Add input validation and sanitization
- Use HTTPS
- Restrict host to 127.0.0.1
- Add CSRF protection

## 📊 Performance Tips

### For Faster Processing:
1. **Use GPU**: Ensure CUDA is installed and available
2. **Smaller Models**: Use base/small for STT instead of large
3. **Batch Processing**: Process multiple files together
4. **Close Unnecessary Apps**: Free up RAM and GPU memory

### For Better Quality:
1. **Larger Models**: Use medium/large-v3 for STT
2. **High-Quality Audio**: Use lossless formats (WAV, FLAC)
3. **Good Microphone**: For live recording
4. **Quiet Environment**: Reduce background noise

## 📝 File Management

### Automatic Cleanup
- Old uploaded files are automatically deleted after 24 hours
- Generated audio files are kept indefinitely
- Manual cleanup: Delete files from `uploads/` and `outputs/` folders

### Output Files
- TTS outputs: `outputs/tts_<timestamp>.wav`
- All audio: 24kHz WAV format
- Download directly from the web interface

## 🆘 Support

### Common Issues

1. **"Model not loaded" error**
   - Click the initialize button for that specific model
   - Wait for confirmation message
   - Check System page to verify loading

2. **Slow performance**
   - First run downloads models (several GB)
   - Subsequent runs are faster
   - GPU significantly speeds up processing

3. **Browser compatibility**
   - Recommended: Chrome, Edge, Firefox (latest versions)
   - Safari: May have WebRTC issues with live recording

### Getting Help

Check these locations for errors:
1. Browser console (F12)
2. Terminal/PowerShell running the server
3. System Information page in the app

## 🎓 Advanced Usage

### Using with Existing Core Modules
The application integrates with your existing `core/` directory:
- `core/brain.py` - LLM interface
- `core/context.py` - Context management
- `config.py` - System prompts and settings

### Customization
- **Styling**: Edit `static/style.css`
- **Functionality**: Modify JavaScript files in `static/`
- **Templates**: Update HTML in `templates/`
- **API**: Extend routes in `web_app.py`

## 📜 License

Copyright © 2025 Zeyta AI. All rights reserved.

---

**Made with ❤️ for easy AI interaction**

For questions, issues, or feature requests, check the troubleshooting section or review the browser console and server logs for detailed error messages.

#!/bin/bash

# Zeyta AI Web Application - Dependency Installation Script
# This can be run separately to avoid memory issues during startup

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Zeyta AI Dependencies Installation${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed or not in PATH.${NC}"
    exit 1
fi

# Create main venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${CYAN}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        echo "Trying to install venv package..."
        sudo apt-get update
        sudo apt-get install -y python3.12-venv python3-full
        python3 -m venv venv
    fi
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${GREEN}Virtual environment already exists.${NC}"
fi

# Activate venv
source venv/bin/activate
echo -e "${CYAN}Using Python: $(which python)${NC}"

# Upgrade pip first
echo -e "${CYAN}Upgrading pip, setuptools, and wheel...${NC}"
python -m pip install --upgrade pip setuptools wheel --quiet

# Install PyTorch and audio libraries first
echo -e "${CYAN}Installing PyTorch (CUDA 12.8) and audio libraries...${NC}"
python -m pip install --index-url https://download.pytorch.org/whl/nightly/cu128 \
    torch>=2.10.0.dev \
    torchaudio>=2.10.0.dev \
    torchvision>=0.25.0.dev \
    --quiet

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}PyTorch installation had warnings. Continuing...${NC}"
fi

# Install transformers and other dependencies
echo -e "${CYAN}Installing transformers and utilities...${NC}"
python -m pip install \
    transformers>=4.35.0 \
    numpy>=1.24.0,<2.0 \
    scipy>=1.11.4 \
    --quiet

# Install TTS/STT dependencies  
echo -e "${CYAN}Installing audio processing libraries...${NC}"
python -m pip install \
    sounddevice>=0.4.6 \
    soundfile>=0.12.1 \
    librosa>=0.10.0 \
    faster-whisper>=1.0.0 \
    webrtcvad>=2.0.10 \
    --quiet

# Install web framework and utilities
echo -e "${CYAN}Installing web framework and utilities...${NC}"
python -m pip install \
    flask>=3.0.0 \
    flask-cors>=4.0.0 \
    flask-socketio>=5.3.0 \
    werkzeug>=3.0.0 \
    python-socketio>=5.10.0 \
    psutil>=5.9.0 \
    requests>=2.31.0 \
    pillow>=10.0.0 \
    pyautogui>=0.9.54 \
    --quiet

# Install TTS packages
echo -e "${CYAN}Installing TTS packages...${NC}"
python -m pip install \
    chatterbox-tts \
    pyttsx3>=2.90 \
    --quiet

# Try to install optional packages
echo -e "${CYAN}Installing optional optimization packages...${NC}"
python -m pip install \
    triton>=3.0.0 \
    xformers>=0.0.23 \
    --quiet || {
    echo -e "${YELLOW}Note: Some optional packages could not be installed. The app will still work.${NC}"
}

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To run the application, execute:"
echo "  bash start.sh"
echo ""

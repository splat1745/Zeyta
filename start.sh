#!/bin/bash

# Zeyta AI Web Application - Linux Start Script
# This script installs dependencies and starts the server

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   Zeyta AI Web Application${NC}"
echo -e "${CYAN}   Linux Start Script${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# GPU Configuration
# Defaulting to similar settings as Windows script, but these can be overridden
export CUDA_VISIBLE_DEVICES="0"
export OLLAMA_NUM_GPU="1"
export OLLAMA_GPU_LAYERS="99"
export CUDA_DEVICE_ORDER="PCI_BUS_ID"

echo -e "${CYAN}GPU Configuration:${NC}"
echo "   CUDA_VISIBLE_DEVICES = $CUDA_VISIBLE_DEVICES"
echo "   OLLAMA_NUM_GPU = $OLLAMA_NUM_GPU"
echo "   OLLAMA_GPU_LAYERS = $OLLAMA_GPU_LAYERS"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed or not in PATH.${NC}"
    echo "Please install Python 3.11 or higher."
    exit 1
fi

echo -e "[1/3] Checking Python version..."
python3 --version
echo ""

echo -e "[2/3] Installing dependencies..."

# Create main venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        echo "Trying to install venv package..."
        sudo apt-get install -y python3.12-venv python3-full
        python3 -m venv venv
    fi
fi

# Activate venv and install dependencies
source venv/bin/activate
echo "Using Python: $(which python)"
python -m pip install --upgrade pip setuptools wheel -q
python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}WARNING: Some packages may have failed to install.${NC}"
fi
echo ""

echo -e "[3/3] Starting Zeyta AI Web Server..."
echo ""

# System Integrity Check
echo -e "${CYAN}Checking system integrity...${NC}"

# 1. Ensure Critical Directories Exist
DIRS=("models" "uploads" "chat_logs" "agent_screenshots" "debug_files" "models/piper")
for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}   Created missing directory: $dir${NC}"
    fi
done

# 2. Check for Chatterbox Python 3.11 Venv
if [ ! -d "venv_chatterbox" ]; then
    echo -e "${YELLOW}Chatterbox venv (Python 3.11) not found!${NC}"
    echo -e "   Initializing smart setup script..."
    
    python3 setup/smart_setup.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Chatterbox venv created successfully.${NC}"
    else
        echo -e "${RED}Failed to create Chatterbox venv.${NC}"
    fi
else
    echo -e "${GREEN}Chatterbox venv found.${NC}"
fi
echo ""

# Set CHATTERBOX_PYTHON for the current session if it exists
if [ -f "venv_chatterbox/bin/python" ]; then
    export CHATTERBOX_PYTHON="$(pwd)/venv_chatterbox/bin/python"
elif [ -f "venv_chatterbox/Scripts/python.exe" ]; then
    # Fallback if somehow using Windows venv structure on Linux (unlikely but possible in WSL/Wine)
    export CHATTERBOX_PYTHON="$(pwd)/venv_chatterbox/Scripts/python.exe"
fi

echo -e "${CYAN}Starting web server...${NC}"
echo "   Server will be available at: https://localhost:5000"
echo "   (Accept the self-signed certificate warning in your browser)"
echo "   Press Ctrl+C to stop the server"
echo ""

# Ensure venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

python web_app.py

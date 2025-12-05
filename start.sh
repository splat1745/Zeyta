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
        echo "Please run: sudo apt-get install -y python3.12-venv python3-full"
        echo "Then try again."
        exit 1
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate
    echo "Using Python: $(which python)"
    echo "Upgrading pip..."
    python -m pip install --upgrade pip setuptools wheel --quiet
    
    echo "Installing dependencies (this may take 5-10 minutes on first run)..."
    python -m pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}WARNING: Some packages may have failed to install.${NC}"
        echo "Attempting to install core packages individually..."
        # Install core packages that must work
        python -m pip install flask psutil requests pillow --quiet || true
    fi
else
    echo "Virtual environment found. Activating..."
    source venv/bin/activate
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

# 2. Setup Chatterbox Python 3.11 Venv
echo -e "${CYAN}Configuring Chatterbox TTS...${NC}"

if [ ! -d "venv_chatterbox" ]; then
    echo "   Chatterbox venv not found. Creating with Python 3.11..."
    
    # Get workspace directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    WORKSPACE_PYTHON="$SCRIPT_DIR/Python-3.11.9/python"
    
    # Check if workspace Python 3.11 exists
    if [ -f "$WORKSPACE_PYTHON" ]; then
        echo "   Found Python 3.11.9 at: $WORKSPACE_PYTHON"
        
        # Create venv with workspace Python 3.11
        "$WORKSPACE_PYTHON" -m venv venv_chatterbox
        
        if [ $? -eq 0 ]; then
            # Activate and install Chatterbox with torch 2.1
            source venv_chatterbox/bin/activate
            
            echo "   Installing pip/setuptools..."
            python -m pip install --upgrade pip setuptools wheel -q
            
            echo "   Installing torch 2.1 for GPU (CUDA 12.1)..."
            python -m pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 \
                --index-url https://download.pytorch.org/whl/cu121 -q 2>/dev/null || true
            
            echo "   Installing Chatterbox TTS..."
            python -m pip install chatterbox-tts -q 2>/dev/null || true
            
            deactivate
            echo -e "${GREEN}Chatterbox Python 3.11 venv created successfully${NC}"
        else
            echo -e "${RED}Failed to create venv with Python 3.11${NC}"
        fi
    else
        echo -e "${YELLOW}Workspace Python 3.11 not found at: $WORKSPACE_PYTHON${NC}"
        echo "   Attempting alternative setup..."
    fi
else
    echo "Chatterbox venv found."
fi
echo ""

# 3. Set CHATTERBOX_PYTHON environment variable
echo -e "${CYAN}Setting environment variables...${NC}"

if [ -f "venv_chatterbox/bin/python" ]; then
    export CHATTERBOX_PYTHON="$(pwd)/venv_chatterbox/bin/python"
    echo -e "${GREEN}CHATTERBOX_PYTHON=$CHATTERBOX_PYTHON${NC}"
    
    # Verify it's Python 3.11
    CHATTERBOX_VERSION=$("$CHATTERBOX_PYTHON" --version 2>&1)
    echo -e "${GREEN}Using: $CHATTERBOX_VERSION${NC}"
elif [ -f "venv_chatterbox/Scripts/python.exe" ]; then
    export CHATTERBOX_PYTHON="$(pwd)/venv_chatterbox/Scripts/python.exe"
    echo -e "${GREEN}CHATTERBOX_PYTHON=$CHATTERBOX_PYTHON${NC}"
else
    echo -e "${YELLOW}Chatterbox venv not ready yet (will be created on first run)${NC}"
fi
echo ""

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

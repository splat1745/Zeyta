#!/bin/bash

# Setup Chatterbox Python 3.11 Virtual Environment
# This script creates a dedicated venv for Chatterbox TTS which requires Python 3.11

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   Chatterbox Python 3.11 Setup${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Get the workspace Python 3.11 path
WORKSPACE_PYTHON="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/Python-3.11.9/python"
VENV_DIR="venv_chatterbox"

if [ ! -f "$WORKSPACE_PYTHON" ]; then
    echo -e "${RED}Error: Python 3.11.9 not found at $WORKSPACE_PYTHON${NC}"
    echo "Please ensure Python-3.11.9 is built in the workspace."
    exit 1
fi

echo "Using Python: $WORKSPACE_PYTHON"
python_version=$("$WORKSPACE_PYTHON" --version 2>&1)
echo -e "${GREEN}$python_version${NC}"
echo ""

# Remove old venv if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing Chatterbox venv..."
    rm -rf "$VENV_DIR"
fi

echo "Creating Python 3.11 virtual environment..."
"$WORKSPACE_PYTHON" -m venv "$VENV_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create virtual environment.${NC}"
    exit 1
fi

# Activate the venv
source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel -q

echo "Installing Chatterbox TTS dependencies..."
echo "  - Installing torch 2.1 for GPU (CUDA 12.1)..."
python -m pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 \
    --index-url https://download.pytorch.org/whl/cu121 -q

echo "  - Installing numpy<1.26 for Chatterbox compatibility..."
python -m pip install "numpy<1.26" -q

echo "  - Installing Chatterbox TTS..."
python -m pip install chatterbox-tts -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Chatterbox venv setup completed successfully!${NC}"
    echo ""
    echo "Environment variables to use:"
    echo "  export CHATTERBOX_PYTHON=\"$(pwd)/$VENV_DIR/bin/python\""
    echo ""
    echo "Or add to your start script:"
    echo "  export CHATTERBOX_PYTHON=\"\$(cd \$(dirname \$0) && pwd)/$VENV_DIR/bin/python\""
else
    echo -e "${RED}Failed to install Chatterbox TTS.${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}Setup complete! Chatterbox venv is ready at: $VENV_DIR${NC}"

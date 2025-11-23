# 🤖 Agent Mode Setup Guide

## Overview
Agent Mode is an autonomous AI system that can:
- 👁️ **Analyze your screen** using vision AI models
- 🎯 **Execute tasks** with your permission
- 💬 **Chat intelligently** about what it sees
- 🖱️ **Control mouse and keyboard** for automation
- 📋 **Complete workflows** step-by-step

## Prerequisites

### 1. Install Ollama
Ollama is required to run AI models locally.

**Download**: https://ollama.ai/download

**Windows Installation**:
```powershell
# Download and run the installer from ollama.ai
# Or use winget:
winget install Ollama.Ollama
```

**Verify Installation**:
```powershell
ollama --version
```

### 2. Install AI Models

**For Vision & Screen Analysis** (Recommended):
```powershell
# LLaVA - Best for screen analysis
ollama pull llava

# Or use the larger, more capable version:
ollama pull llava:13b
```

**For Text-Only Tasks**:
```powershell
# Llama 3.2 - Fast and efficient
ollama pull llama3.2

# Mistral - Great reasoning
ollama pull mistral

# Qwen - Excellent for technical tasks
ollama pull qwen2.5
```

### 3. Start Ollama Service
```powershell
# Ollama should start automatically after installation
# Or start manually:
ollama serve
```

## Quick Start

### Step 1: Initialize Agent
1. Navigate to the **Agent** page
2. Click **"Initialize Agent"**
3. Wait for Ollama connection confirmation

### Step 2: Select a Model
1. Choose a model from the dropdown
2. **llava** recommended for screen analysis
3. Click to load the selected model

### Step 3: Grant Permissions
Select which actions the agent can perform:
- ✅ **Mouse Control**: Allow mouse clicks and movements
- ✅ **Keyboard Control**: Allow typing and key presses
- ⚠️ **File Operations**: Allow reading/writing files (use with caution)
- ⚠️ **System Commands**: Allow executing system commands (use with caution)

Click **"Save Permissions"** to apply.

### Step 4: Start Using!
Choose from:
- **Screen Analysis**: AI describes what's on your screen
- **Task Execution**: AI plans and executes tasks
- **Agent Chat**: Converse with full screen context

## Features

### 🖥️ Screen Analysis
The agent can see and understand your screen:
```
Example prompt: "What applications are currently open?"
Agent response: "I can see you have Chrome browser with 
several tabs open, VS Code in the background, and 
File Explorer showing your documents folder..."
```

**Use Cases**:
- Accessibility assistance
- UI testing and validation
- Documentation generation
- Tutorial creation

### 🎯 Task Execution
Describe what you want, and the agent will analyze and execute:

**Example Tasks**:
- "Open Notepad and type 'Hello World'"
- "Find and click the Start button"
- "Take a screenshot of the active window"
- "Organize desktop icons by name"

**Workflow**:
1. Enter task description
2. Agent analyzes screen
3. Agent suggests actions
4. You confirm
5. Agent executes with permissions

### 💬 Intelligent Chat
Chat with screen context:
- Check "Include Screen" to share what you're looking at
- Agent sees and understands your desktop
- Ask questions about your screen
- Get help with applications

**Example Conversation**:
```
You: "What's the error message in this window?"
Agent: "I can see a Windows error dialog saying 
'File not found: example.txt'. The error code is 0x80070002."

You: "How do I fix this?"
Agent: "Create the missing file or check if the path is correct..."
```

### 🖱️ Quick Actions
Pre-configured automation tasks:
- Move mouse to position
- Click specific coordinates
- Type text
- Press keyboard keys

## Safety & Permissions

### Permission System
Agent Mode uses a **granular permission system**:

| Permission | Risk Level | Use For |
|------------|-----------|----------|
| Mouse Control | Low | Click buttons, navigate UI |
| Keyboard Control | Medium | Type text, shortcuts |
| File Operations | High | Create/modify documents |
| System Commands | Critical | Install software, system changes |

### Best Practices
1. ✅ **Start with low-risk permissions** (mouse/keyboard only)
2. ✅ **Review suggested actions** before confirming
3. ✅ **Test on non-critical tasks** first
4. ⚠️ **Grant file/system permissions** only when needed
5. ⚠️ **Monitor agent actions** in the action history

### Security Notes
- ⚠️ Agent runs with **your user permissions**
- ⚠️ File operations can **modify/delete data**
- ⚠️ System commands can **install software** or **change settings**
- ✅ All actions are **logged** for review
- ✅ You **control permissions** at all times

## Use Cases

### 1. Automated Testing
```
Task: "Test the login form by entering test credentials"
1. Agent analyzes form fields
2. Types username
3. Types password
4. Clicks submit
5. Reports results
```

### 2. Data Entry
```
Task: "Fill out the customer form with data from clipboard"
1. Agent reads clipboard
2. Identifies form fields
3. Fills each field
4. Validates entries
5. Submits form
```

### 3. Research Assistant
```
Chat with screen: "Summarize this article"
1. Agent reads visible text
2. Analyzes content
3. Provides summary
4. Can navigate to sections
5. Answer questions
```

### 4. Accessibility Tool
```
Screen analysis: "Read the menu options"
1. Agent identifies UI elements
2. Reads text aloud (via TTS)
3. Helps with navigation
4. Can execute selections
```

## Troubleshooting

### Ollama Not Connected
**Problem**: "Ollama is not running"

**Solutions**:
```powershell
# Check if Ollama is running
Get-Process ollama

# Start Ollama manually
ollama serve

# Verify connection
curl http://localhost:11434/api/tags
```

### Model Not Loading
**Problem**: Model fails to load or appears empty

**Solutions**:
```powershell
# List installed models
ollama list

# Pull model if missing
ollama pull llava

# Remove and reinstall model
ollama rm llava
ollama pull llava
```

### Screen Capture Fails
**Problem**: "Failed to capture screen"

**Solutions**:
1. Check Windows privacy settings
2. Grant screen recording permission
3. Close conflicting screen capture tools
4. Restart the web application

### Actions Not Executing
**Problem**: "Permission denied" errors

**Solutions**:
1. Check permission checkboxes are enabled
2. Click "Save Permissions"
3. Refresh the page
4. Verify no other apps are blocking input

## Advanced Usage

### Custom Prompts
Enhance screen analysis with specific prompts:
```
"Identify all buttons and their labels"
"Find error messages or warnings"
"List all text input fields with their current values"
"Describe the color scheme and layout"
```

### Chaining Tasks
Break complex workflows into steps:
```
Task 1: "Open application X"
Wait for confirmation

Task 2: "Navigate to settings"
Wait for confirmation

Task 3: "Enable feature Y"
Execute
```

### Vision Models Comparison
| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| llava | 7B | Fast | Good | General screen analysis |
| llava:13b | 13B | Medium | Better | Detailed UI understanding |
| llava:34b | 34B | Slow | Best | Complex visual reasoning |

## Performance Tips

### 1. Model Selection
- **llava (7B)**: Fast, good for simple tasks
- **llava:13b**: Balanced, recommended for most use cases
- **llava:34b**: Slow but very accurate

### 2. Screen Resolution
- Lower resolution = faster analysis
- Capture specific regions for speed
- Use full screen for complex tasks

### 3. Prompt Optimization
- Be specific about what to look for
- Mention specific UI elements by name
- Use clear, concise language

### 4. Permission Management
- Only enable needed permissions
- Disable after completing tasks
- Review action history regularly

## API Integration

### REST API Endpoints
```python
# Initialize Agent
POST /api/agent/initialize

# Set Model
POST /api/agent/set-model
Body: {"model": "llava"}

# Analyze Screen
POST /api/agent/analyze-screen
Body: {"prompt": "Describe the screen"}

# Chat with Context
POST /api/agent/chat
Body: {"message": "What do you see?", "include_screen": true}

# Execute Action
POST /api/agent/execute-action
Body: {"action": {"type": "mouse_click", "x": 100, "y": 100}}
```

### Python Example
```python
import requests

# Analyze screen
response = requests.post('http://localhost:5000/api/agent/analyze-screen', 
    json={"prompt": "What's on the screen?"})
    
print(response.json()["analysis"])
```

## Limitations

### Current Limitations
- ⚠️ Runs on **local machine only** (not remote desktops)
- ⚠️ Requires **Ollama** to be running
- ⚠️ Vision models need **good GPU** for speed
- ⚠️ Screen capture limited to **primary monitor**
- ⚠️ Cannot interact with **elevated/admin windows**

### Future Enhancements
- 🔮 Multi-monitor support
- 🔮 Remote desktop compatibility
- 🔮 Scheduled task execution
- 🔮 Workflow recording/playback
- 🔮 Cloud model support

## Resources

### Official Links
- Ollama: https://ollama.ai
- LLaVA Model: https://llava-vl.github.io
- Documentation: https://github.com/ollama/ollama

### Recommended Models
1. **llava** - Vision + language understanding
2. **llama3.2** - General purpose, fast
3. **mistral** - Excellent reasoning
4. **qwen2.5** - Technical tasks

### Community
- GitHub Issues: Report bugs and feature requests
- Discord: Join the Zeyta AI community
- Wiki: Extended documentation and examples

---

## Summary

Agent Mode provides **autonomous AI capabilities** with:
- ✅ **Screen understanding** via vision AI
- ✅ **Task automation** with permissions
- ✅ **Safe execution** with user control
- ✅ **Local processing** for privacy

**Get started**: Install Ollama → Pull llava → Initialize Agent → Start automating!

**Remember**: Always review actions before confirming, and start with low-risk tasks to build confidence.

🤖 **Happy automating!**

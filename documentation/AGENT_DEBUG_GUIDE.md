# Agent AI Response Debug Guide

## Problem
The AI agent returns empty responses when trying to execute tasks like "Open Notepad and type Hello from Agent Mode!"

## Changes Made

### Enhanced Debugging in `agent.py`

1. **Model Validation**
   - Added check to ensure model is set before making requests
   - Logs model name, prompt length, and screenshot size

2. **Response Validation**
   - Verifies response object supports streaming (`iter_lines`)
   - Logs response status code and headers

3. **Streaming Diagnostics**
   - Tracks number of lines processed from stream
   - Logs first few raw lines and tokens
   - Shows chunk structure (keys available)
   - Reports if no lines were received

4. **Empty Response Tracking**
   - Logs exactly how many lines and tokens were processed
   - Distinguishes between "no data" and "empty tokens"

## How to Debug

### Step 1: Run the Debug Script

```powershell
python test_agent_debug.py
```

This will:
- Check if Ollama is running
- Verify models are available
- Select a vision model (llava preferred)
- Execute a simple test task
- Generate detailed logs in `agent_debug.log`

### Step 2: Check the Log File

Open `agent_debug.log` and look for:

1. **Model Information**
   ```
   [Agent] Model: llava:latest
   [Agent] Prompt length: 1234 chars
   [Agent] Screenshot size: 56789 bytes
   ```

2. **Response Status**
   ```
   [Agent] Response status: 200
   [Agent] Valid streaming response received
   ```

3. **Streaming Activity**
   ```
   [Agent] Starting to stream tokens from: <class 'requests.Response'>
   [Agent] Raw line 1: {"model":"llava:latest","created_at":...
   [Agent] First chunk keys: dict_keys(['model', 'created_at', 'response', 'done'])
   [Agent] Token 1: '{'
   [Agent] Token 2: '"'
   [Agent] Token 3: 'action'
   ```

4. **Completion**
   ```
   [Agent] Streaming complete. Total tokens: 156, Lines: 158
   ```

### Common Issues and Solutions

#### Issue 1: "No model selected"
**Symptom:** Log shows `[Agent] No model set!`

**Solution:**
- Make sure you selected a model in the web interface
- Or use: `python test_agent_debug.py` which auto-selects

#### Issue 2: "No streaming response received"
**Symptom:** Log shows `[Agent] No streaming response received`

**Solution:**
- Check if Ollama is running: `ollama list`
- Verify model is pulled: `ollama pull llava`
- Check Ollama logs for errors

#### Issue 3: "No lines received from streaming response"
**Symptom:** Log shows `lines_processed = 0`

**Solution:**
- Model might be loading (first request is slow)
- Check Ollama is responding: `curl http://localhost:11434/api/tags`
- Try a different model
- Increase timeout in payload

#### Issue 4: "Invalid AI response (no JSON found)"
**Symptom:** AI responds but not with valid JSON

**Solution:**
- Model might not understand the prompt format
- Try a different vision model (llava is recommended)
- Check if model supports vision tasks
- Review the actual response in logs to see what AI said

#### Issue 5: HTTP Error Codes
**Symptom:** `Response status: 404` or `Response status: 500`

**Solutions:**
- **404**: Model not found - pull the model first
- **500**: Ollama server error - check Ollama logs
- **503**: Ollama overloaded - wait and retry

## Testing Without Full Execution

If you want to test just the AI response without executing actions:

```python
from agent import AgentMode
from pathlib import Path

agent = AgentMode(Path.cwd())
agent.set_model("llava:latest")

# Test with auto_execute=False to see AI's plan without executing
result = agent.execute_task(
    "Open Notepad and type Hello!",
    auto_execute=False
)

print(result['action_plan'])  # See what AI wants to do
```

## Next Steps

1. Run `test_agent_debug.py`
2. Check `agent_debug.log` for detailed diagnostics
3. Look for the specific error pattern above
4. Apply the corresponding solution
5. If still stuck, share the relevant lines from `agent_debug.log`

## Quick Checklist

- [ ] Ollama is running (`ollama list` works)
- [ ] Vision model is installed (llava recommended)
- [ ] Model is selected in agent interface
- [ ] Permissions are granted (auto-granted in autonomous mode)
- [ ] No CUDA errors in logs
- [ ] Response status is 200
- [ ] Streaming response has data

## Log Locations

- Real-time output: Console/terminal
- Detailed logs: `agent_debug.log`
- Web app logs: Check browser console (F12)
- Ollama logs: Check Ollama service logs

---

**Created:** 2025-11-08
**Purpose:** Debug empty AI responses in agent mode

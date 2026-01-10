# Quick Fix Reference - Python 3.12 & Port Conflicts

## TL;DR - Quick Solutions

### Issue: "Chatterbox-TTS requires numpy<1.26... Python 3.12"

**On TTS, STT, or Chat:**
```bash
# Linux/macOS
export CHATTERBOX_PYTHON="$(pwd)/venv_chatterbox/bin/python"
python web_app.py

# Windows PowerShell
$env:CHATTERBOX_PYTHON = "$(Get-Location)\venv_chatterbox\Scripts\python.exe"
python web_app.py
```

**Or just run the setup:**
```bash
# Linux
./start.sh

# Windows
python setup/smart_setup.py
```

---

### Issue: "Port 5000 is in use by another program"

**Solution:** The app now handles this automatically! ✓

The app will:
1. ✓ Identify what's using port 5000
2. ✓ Try to close it if it's Zeyta
3. ✓ Use port 5001, 5002, etc. if needed
4. ✓ Tell you which port it's using

---

## Environment Info

Check what's available on your system:
```bash
curl http://localhost:5000/api/environment
```

Response will show:
- Python version (3.12? 3.11?)
- CUDA available?
- Chatterbox venv path
- What models are loaded

---

## Setup (First Time Only)

### Create venv_chatterbox with Python 3.11

**Linux:**
```bash
python3.11 -m venv venv_chatterbox
source venv_chatterbox/bin/activate
pip install -r requirements.txt
```

**Windows:**
```powershell
python -m venv venv_chatterbox
.\venv_chatterbox\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Or use automatic setup:**
```bash
python setup/smart_setup.py
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "Python 3.12" + TTS error | Install Python 3.11 venv (see Setup above) |
| Port 5000 in use | App auto-handles it now, or restart and port auto-increments |
| STT not working on 3.12 | Use Python 3.11 venv (same as TTS) |
| Chat/Ollama not working | Make sure TTS works first (Ollama depends on it) |
| venv_chatterbox not found | Run `python setup/smart_setup.py` or manual setup above |

---

## Files to Know About

| File | Purpose |
|------|---------|
| `web_app.py` | Main app (auto-detects venv, handles ports) |
| `venv_chatterbox/` | Python 3.11 isolated environment |
| `setup/smart_setup.py` | Auto-creates venv_chatterbox |
| `start.sh` | Linux starter (uses venv) |

---

## API Endpoints (New)

### GET `/api/environment`
Get system info:
```json
{
  "python_version": "3.12.0",
  "chatterbox_python": "/path/to/venv/python",
  "chatterbox_available": true,
  "tts_model_loaded": false
}
```

### POST `/api/initialize`
Initialize models with venv hints:
```bash
curl -X POST http://localhost:5000/api/initialize \
  -H "Content-Type: application/json" \
  -d '{"type": "tts"}'
```

---

## Logs to Check

**Check these for troubleshooting:**
```bash
# See if venv was auto-detected
# Look for: "✓ Auto-configured CHATTERBOX_PYTHON"

# See if port was auto-changed
# Look for: "✓ Using alternative port"

# See if subprocess mode was used
# Look for: "Chatterbox TTS loaded via subprocess"
```

---

## Still Having Issues?

1. **Check environment:** `curl http://localhost:5000/api/environment`
2. **Check logs:** Look at console output when app starts
3. **Reinstall venv:** `rm -rf venv_chatterbox && python setup/smart_setup.py`
4. **Check Python version:** `python --version` (should be 3.11 for venv_chatterbox)

---

**For detailed info, see:** `documentation/ZEYTA_VENV_AND_PORT_FIXES.md`

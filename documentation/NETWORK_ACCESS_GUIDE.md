# 🌐 Network Access Guide - Zeyta AI Web Application

## Overview
Your Zeyta AI web application is now accessible to all devices on your local network! Other devices can use your main PC as the processor while they act as clients.

## How It Works
- **Main PC (Server)**: Runs all AI models and processing
- **Client Devices**: Access the web interface and use your main PC's hardware
- **Configuration**: Flask is configured with `host='0.0.0.0'` to accept connections from any network device

## Accessing from Other Devices

### 1. Find Your Main PC's IP Address
Your current network IP addresses are shown when the server starts. Look for lines like:
```
 * Running on https://10.0.0.66:5000
```

You can also check manually:
- **Windows**: Run `ipconfig` in PowerShell and look for "IPv4 Address"
- **The IP will look like**: `192.168.x.x` or `10.0.0.x`

### 2. Access from Client Devices

On any device connected to the **same network**:

#### From Phones/Tablets:
1. Open your browser (Chrome, Safari, Firefox, etc.)
2. Type in the address bar: `https://YOUR_PC_IP:5000`
   - Example: `https://10.0.0.66:5000`
3. **Accept the security warning** (Advanced -> Proceed)
4. You'll see the Zeyta AI interface!

#### From Other Computers:
1. Open any web browser
2. Navigate to: `https://YOUR_PC_IP:5000`
   - Example: `https://10.0.0.66:5000`
3. Accept the certificate warning
4. Full functionality available!

### 3. What You Can Do from Client Devices
- ✅ **Text-to-Speech**: Generate audio using your main PC's GPU
- ✅ **Speech-to-Text**: Transcribe audio files
- ✅ **Chat with LLM**: Interact with the AI chatbot
- ✅ **Full Pipeline**: Voice → Transcription → AI Response → Speech
- ✅ **Model Management**: Load/unload models remotely
- ✅ **System Monitoring**: View GPU and model status

All processing happens on your main PC - clients just display the interface!

## Firewall Configuration

### Windows Firewall (if connection is blocked):

1. **Allow Python through firewall** (one-time setup):
   ```powershell
   # Run as Administrator
   New-NetFirewallRule -DisplayName "Zeyta AI Server" -Direction Inbound -Program "C:\Users\YOUR_USERNAME\AppData\Local\Microsoft\WindowsApps\python.exe" -Action Allow
   ```

2. **Or allow the port** (5000):
   ```powershell
   # Run as Administrator
   New-NetFirewallRule -DisplayName "Zeyta AI Port" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
   ```

3. **Check if port is open**:
   ```powershell
   netstat -an | Select-String "5000"
   ```

### Quick Test
From another device on your network:
```bash
# Ping your main PC to verify network connectivity
ping YOUR_PC_IP

# Example:
ping 10.0.0.66
```

## Troubleshooting

### "Can't connect" / "Site unreachable"
1. **Check server is running** on main PC
2. **Verify IP address** - it may change if DHCP assigns a new one
3. **Check firewall** - Windows Firewall might be blocking
4. **Same network** - Ensure both devices are on the same WiFi/network
5. **Use HTTPS** - Make sure you use `https://` not `http://`

### Connection Drops
- **Keep server running** - Don't close the terminal window
- **Main PC stays awake** - Adjust power settings to prevent sleep

### Slow Performance from Client
- **Network speed** - WiFi quality affects responsiveness
- **Main PC does processing** - Client speed doesn't matter much
- **Large files** - Audio file uploads depend on network speed

## Advanced: Port Forwarding (Optional)
To access from **outside your home network** (Internet):
1. Configure port forwarding on your router (Port 5000 → Your PC's IP)
2. Use your public IP address (find at whatismyip.com)
3. ⚠️ **Security Warning**: This exposes your server to the internet!
   - Add authentication
   - Use HTTPS (already enabled)
   - Or use a VPN instead

## Performance Notes
- **GPU utilization**: Only on the main PC (server)
- **Network bandwidth**: Mainly for audio file uploads/downloads
- **Latency**: Real-time features (live STT) work best on fast WiFi
- **Multiple clients**: Server can handle multiple devices simultaneously

## Current Server Configuration
```python
# From web_app.py
socketio.run(
    app,
    host='0.0.0.0',      # Listen on all network interfaces
    port=5000,            # Port number
    debug=False,
    allow_unsafe_werkzeug=True,
    ssl_context='adhoc'   # Enable HTTPS
)
```

## Example Devices Tested
- ✅ Android phones
- ✅ iPhones/iPads  
- ✅ Windows laptops
- ✅ Mac computers
- ✅ Linux machines
- ✅ Tablets

## Security Recommendations
For local network use:
- ✅ Keep server on trusted home network only
- ✅ Don't expose to public internet without proper security
- ✅ Use router's guest network isolation if needed

## Quick Reference
| What | Where |
|------|-------|
| **Main PC Access** | `https://localhost:5000` |
| **Network Access** | `https://YOUR_PC_IP:5000` |
| **Example IP** | `https://10.0.0.66:5000` |
| **Port** | 5000 |
| **Protocol** | HTTPS |

---

**Ready to use!** 🚀 Just start the server and access from any device on your network!

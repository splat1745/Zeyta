import sys
import os
import subprocess
import venv
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, env=None, capture=True):
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            env=env, 
            check=True, 
            capture_output=capture, 
            text=True
        )
        return True, result.stdout if capture else ""
    except subprocess.CalledProcessError as e:
        return False, (e.stderr + "\n" + e.stdout) if capture else ""

def find_python_311():
    """Find a Python 3.11 executable on the system."""
    # 1. Check if current process is 3.11
    if sys.version_info[:2] == (3, 11):
        return sys.executable

    # 2. Check PATH and common locations
    candidates = [
        "python3.11", 
        "python3.11.exe",
        "py -3.11",
        r"C:\Python311\python.exe",
        os.path.expanduser(r"~\AppData\Local\Microsoft\WindowsApps\python3.11.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe")
    ]
    
    for cmd in candidates:
        # Handle "py -3.11" separately
        if cmd.startswith("py "):
            try:
                # Ask py launcher for the path
                res = subprocess.run(["py", "-3.11", "-c", "import sys; print(sys.executable)"], capture_output=True, text=True)
                if res.returncode == 0:
                    return res.stdout.strip()
            except:
                pass
            continue

        path = shutil.which(cmd)
        if path: return path
        if os.path.exists(cmd): return cmd
            
    return None

def smart_install(venv_python, package_list):
    print(f"📦 Installing packages: {', '.join(package_list)}")
    success, output = run_command([venv_python, "-m", "pip", "install"] + package_list)
    
    if success:
        print("   ✅ Installation successful.")
        return True
    
    print("   ⚠️  Standard installation failed. Analyzing error...")
    error_msg = output.lower()
    
    # Strategy 1: Upgrade pip/setuptools/wheel (Fixes build issues)
    if "command 'python setup.py egg_info' failed" in error_msg or "wheel" in error_msg or "metadata" in error_msg:
        print("   🔧 Fix: Upgrading build tools (pip, setuptools, wheel)...")
        run_command([venv_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
        
        print("   🔄 Retrying installation...")
        success, _ = run_command([venv_python, "-m", "pip", "install"] + package_list)
        if success: return True

    # Strategy 2: No Cache (Fixes corrupted downloads)
    if "hash mismatch" in error_msg or "corrupted" in error_msg:
        print("   🔧 Fix: Disabling cache...")
        success, _ = run_command([venv_python, "-m", "pip", "install", "--no-cache-dir"] + package_list)
        if success: return True
    
    # Strategy 3: Pre-release (Fixes missing versions for new hardware/python)
    if "no matching distribution" in error_msg:
        print("   🔧 Fix: Trying pre-release versions...")
        success, _ = run_command([venv_python, "-m", "pip", "install", "--pre"] + package_list)
        if success: return True

    # Strategy 4: Numpy compatibility (Specific to 3.11/3.12 sometimes)
    if "numpy" in error_msg:
        print("   🔧 Fix: Installing specific numpy version...")
        run_command([venv_python, "-m", "pip", "install", "numpy<2.0"])
        success, _ = run_command([venv_python, "-m", "pip", "install"] + package_list)
        if success: return True

    print(f"   ❌ All auto-fix strategies failed. Error details:\n{output}")
    return False

def main():
    print("🤖 Smart Setup: Initializing...")
    venv_path = Path("venv_chatterbox")
    
    # 1. Create Venv if missing
    if not venv_path.exists():
        print(f"   📂 Creating venv at {venv_path}...")
        
        python_exe = find_python_311()
        if not python_exe:
            print("   ❌ Error: Python 3.11 not found! It is required for Chatterbox TTS.")
            print("      Please install Python 3.11 from python.org or Microsoft Store.")
            sys.exit(1)
            
        print(f"   🐍 Using Python executable: {python_exe}")
        
        try:
            # Use the found python to create the venv
            subprocess.run([python_exe, "-m", "venv", str(venv_path)], check=True)
        except Exception as e:
            print(f"   ❌ Failed to create venv: {e}")
            sys.exit(1)
    else:
        print("   ✅ Venv already exists.")

    # Locate venv python
    venv_python = venv_path / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = venv_path / "bin" / "python" # Fallback
        
    if not venv_python.exists():
        print("   ❌ Critical: Python executable not found inside venv!")
        sys.exit(1)
        
    venv_python = str(venv_python)

    # 2. Install Dependencies with Smart Recovery
    # Core dependencies
    deps = ["chatterbox-tts", "soundfile", "numpy"]
    
    if not smart_install(venv_python, deps):
        print("   ❌ Failed to install core dependencies.")
        sys.exit(1)
        
    # 3. Set Environment Variable (Persistent)
    print(f"   ⚙️  Setting CHATTERBOX_PYTHON environment variable...")
    try:
        subprocess.run(["setx", "CHATTERBOX_PYTHON", venv_python], check=True, capture_output=True)
        print("   ✅ Environment variable set.")
    except:
        print("   ⚠️  Could not set environment variable (might need admin).")

    print("✅ Smart Setup Complete.")

if __name__ == "__main__":
    main()

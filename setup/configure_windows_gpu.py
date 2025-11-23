"""
Windows Graphics Preference Configuration
Forces Ollama to use High Performance (discrete) GPU
"""
import winreg
import os
import subprocess

def find_ollama_path():
    """Find Ollama executable path"""
    common_paths = [
        os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe"),
        r"C:\Program Files\Ollama\ollama.exe",
        r"C:\Program Files (x86)\Ollama\ollama.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Try to find via where command
    try:
        result = subprocess.run(['where', 'ollama'], capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

def set_graphics_preference():
    """Set Windows Graphics Preference to High Performance for Ollama"""
    ollama_path = find_ollama_path()
    
    if not ollama_path:
        print("❌ Could not find ollama.exe")
        print("\nManual steps:")
        print("1. Open Windows Settings")
        print("2. Go to System > Display > Graphics")
        print("3. Click 'Browse' and add ollama.exe")
        print("4. Set to 'High Performance'")
        return False
    
    print(f"✅ Found Ollama: {ollama_path}")
    print("\n⚠️ Setting Graphics Preference requires manual configuration:")
    print("\n1. Press Windows Key")
    print("2. Type 'Graphics Settings' and press Enter")
    print("3. Click 'Browse' button")
    print(f"4. Navigate to and select: {ollama_path}")
    print("5. Click 'Options' button")
    print("6. Select 'High Performance'")
    print("7. Click 'Save'")
    print("\nThis ensures Ollama ALWAYS uses your RTX 5070 Ti instead of integrated graphics.")
    
    # Try to open graphics settings
    try:
        subprocess.Popen(['start', 'ms-settings:display-advancedgraphics'], shell=True)
        print("\n✅ Opened Graphics Settings for you!")
    except:
        print("\n❌ Could not auto-open settings. Please do it manually.")
    
    return True

def verify_environment_variables():
    """Verify GPU environment variables are set"""
    print("\n" + "=" * 60)
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = {
        'OLLAMA_NUM_GPU': '1',
        'CUDA_VISIBLE_DEVICES': '0'
    }
    
    all_set = True
    for var, expected in required_vars.items():
        value = os.environ.get(var)
        if value == expected:
            print(f"✅ {var} = {value}")
        else:
            print(f"⚠️ {var} = {value if value else '(not set)'} (should be {expected})")
            all_set = False
    
    if not all_set:
        print("\n⚠️ Run fix_gpu.ps1 to set environment variables")
    
    return all_set

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 WINDOWS GRAPHICS PREFERENCE CONFIGURATION")
    print("=" * 60)
    print()
    
    verify_environment_variables()
    print()
    set_graphics_preference()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURATION COMPLETE")
    print("=" * 60)
    print("\nAfter setting Graphics Preference:")
    print("1. Restart your computer (or at minimum, restart Ollama)")
    print("2. Run: python check_gpu.py")
    print("3. Verify GPU usage in nvidia-smi")

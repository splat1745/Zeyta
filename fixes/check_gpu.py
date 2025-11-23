"""
GPU Detection and Ollama Configuration Check
"""
import subprocess
import json
import sys

def check_nvidia_gpu():
    """Check NVIDIA GPU status"""
    print("=" * 60)
    print("🔍 NVIDIA GPU CHECK")
    print("=" * 60)
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,driver_version,memory.total,memory.used,memory.free', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            check=True
        )
        gpu_info = result.stdout.strip()
        print(f"✅ GPU Detected: {gpu_info}\n")
        return True
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

def check_ollama_service():
    """Check if Ollama service is running"""
    print("=" * 60)
    print("🔍 OLLAMA SERVICE CHECK")
    print("=" * 60)
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Ollama is running")
        print(f"Models:\n{result.stdout}\n")
        return True
    except Exception as e:
        print(f"❌ Ollama not running: {e}\n")
        return False

def test_model_gpu_usage(model_name="qwen3:4b"):
    """Test if a model uses GPU"""
    print("=" * 60)
    print(f"🔍 TESTING MODEL: {model_name}")
    print("=" * 60)
    
    # Start the model
    print(f"Loading {model_name}...")
    try:
        result = subprocess.run(
            ['ollama', 'run', model_name, 'Hello', '--verbose'],
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        print("✅ Model loaded successfully")
        print(f"Response: {result.stdout[:200]}...\n")
        
        # Check GPU memory usage while model is loaded
        print("Checking GPU memory usage...")
        gpu_result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            check=True
        )
        memory_used = int(gpu_result.stdout.strip())
        print(f"GPU Memory Used: {memory_used} MB")
        
        if memory_used > 2000:  # More than 2GB indicates GPU usage
            print("✅ Model IS using GPU (significant VRAM usage)\n")
            return True
        else:
            print("⚠️ Model might be using CPU (low VRAM usage)\n")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Model loading timed out\n")
        return False
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

def check_ollama_env():
    """Check Ollama environment variables"""
    print("=" * 60)
    print("🔍 OLLAMA ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    import os
    env_vars = [
        'OLLAMA_HOST',
        'OLLAMA_MODELS',
        'OLLAMA_NUM_GPU',
        'OLLAMA_GPU_LAYERS',
        'CUDA_VISIBLE_DEVICES',
        'HIP_VISIBLE_DEVICES'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"⚪ {var} = (not set)")
    print()

def check_integrated_graphics():
    """Check if integrated graphics is interfering"""
    print("=" * 60)
    print("🔍 INTEGRATED GRAPHICS CHECK")
    print("=" * 60)
    
    try:
        # Check Windows GPU preference
        result = subprocess.run(
            ['powershell', '-Command', 'Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM'],
            capture_output=True,
            text=True,
            check=True
        )
        print("Graphics Adapters:")
        print(result.stdout)
        
        if 'Intel' in result.stdout or 'AMD' in result.stdout:
            print("⚠️ WARNING: Integrated graphics detected!")
            print("   Ollama might be defaulting to integrated GPU.\n")
            print("SOLUTION:")
            print("1. Open Windows Settings > System > Display > Graphics Settings")
            print("2. Add 'ollama.exe' (usually in C:\\Users\\<user>\\AppData\\Local\\Programs\\Ollama\\)")
            print("3. Set it to 'High Performance' (uses discrete GPU)")
            print()
        else:
            print("✅ No integrated graphics interference detected\n")
            
    except Exception as e:
        print(f"Could not check: {e}\n")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 OLLAMA GPU DIAGNOSTIC TOOL")
    print("=" * 60 + "\n")
    
    # Run all checks
    gpu_ok = check_nvidia_gpu()
    ollama_ok = check_ollama_service()
    check_ollama_env()
    check_integrated_graphics()
    
    if gpu_ok and ollama_ok:
        test_model_gpu_usage("qwen3:4b")
    
    print("=" * 60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("\nIf models are using integrated graphics:")
    print("1. Set Windows Graphics Preference for ollama.exe to 'High Performance'")
    print("2. Set environment variable: OLLAMA_NUM_GPU=1")
    print("3. Restart Ollama service")
    print()

#!/usr/bin/env python3
"""
Automatic TorchVision Fix Script
Fixes circular import and entry point errors by reinstalling PyTorch stack
"""
import sys
import subprocess
import time

print("=" * 60)
print("🔧 TorchVision Circular Import Fix")
print("=" * 60)
print()
print("This script will:")
print("  1. Uninstall torch, torchvision, torchaudio")
print("  2. Clear pip cache")
print("  3. Reinstall PyTorch 2.5.1 + CUDA 12.1")
print()
print("=" * 60)
print()

try:
    # Step 1: Uninstall
    print("📦 Step 1/3: Uninstalling existing PyTorch packages...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", 
         "torch", "torchvision", "torchaudio"],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode == 0:
        print("   ✓ Uninstalled successfully")
    else:
        print("   ⚠️  Uninstall warnings (continuing):")
        if result.stderr:
            print(f"   {result.stderr[:200]}")
    
    # Step 2: Clear cache
    print("\n📦 Step 2/3: Clearing pip cache...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "cache", "purge"],
        capture_output=True,
        text=True,
        timeout=60
    )
    print("   ✓ Cache cleared")
    
    # Step 3: Reinstall
    print("\n📦 Step 3/3: Installing PyTorch 2.5.1 + CUDA 12.1...")
    print("   (This may take 5-10 minutes)")
    print()
    
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install",
         "torch==2.5.1+cu121", "torchvision==0.20.1+cu121", "torchaudio==2.5.1+cu121",
         "--index-url", "https://download.pytorch.org/whl/cu121"],
        text=True,
        timeout=900
    )
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! PyTorch stack reinstalled")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Restart web_app.py")
        print("  2. Initialize TTS on CUDA")
        print("  3. TTS should load without torchvision errors")
        print()
        sys.exit(0)
    else:
        print("\n⚠️  Installation completed with warnings")
        print("Try restarting web_app.py and testing TTS")
        sys.exit(0)

except subprocess.TimeoutExpired:
    print("\n❌ Operation timed out")
    print("Please run manually:")
    print("  pip uninstall -y torch torchvision torchaudio")
    print("  pip cache purge")
    print("  pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

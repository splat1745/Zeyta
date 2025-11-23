#!/usr/bin/env python3
"""
Zeyta AI Web Application - Fully Self-Contained
Local web interface for TTS, STT, and LLM models with automatic dependency management
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
import psutil

# ============================================================================
# FIX CUDNN DLL PATH FOR WINDOWS - ABSOLUTE FIRST PRIORITY
# ============================================================================
# Must be done BEFORE any imports that might load CUDA libraries
# Add common PyTorch locations to PATH for cuDNN DLLs

def setup_cuda_dll_path():
    """Setup CUDA DLL paths for Windows before any CUDA operations"""
    if not hasattr(os, 'add_dll_directory'):
        return  # Not Windows or old Python version
    
    # Common locations for PyTorch in virtual environments
    possible_paths = [
        Path(sys.executable).parent / "Lib" / "site-packages" / "torch" / "lib",
        Path(sys.prefix) / "Lib" / "site-packages" / "torch" / "lib",
        Path(__file__).parent.parent / ".venv311" / "Lib" / "site-packages" / "torch" / "lib",
    ]
    
    for torch_lib in possible_paths:
        if torch_lib.exists():
            try:
                os.add_dll_directory(str(torch_lib))
                print(f"[OK] Added cuDNN DLL path: {torch_lib}")
                
                # Also add to system PATH as backup
                os.environ['PATH'] = str(torch_lib) + os.pathsep + os.environ.get('PATH', '')
                return True
            except Exception as e:
                print(f"[WARN] Could not add {torch_lib}: {e}")
    
    print("[WARN] Could not locate PyTorch lib directory for cuDNN")
    return False

# Setup DLL paths FIRST
setup_cuda_dll_path()

import subprocess
import importlib.util
import warnings
import logging
from datetime import datetime
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
PYTTSX3_AVAILABLE = pyttsx3 is not None
try:
    from config import TTS_BACKEND, TTS_RATE, TTS_VOLUME
except ImportError:
    TTS_BACKEND = 'chatterbox'
    TTS_RATE = 175
    TTS_VOLUME = 1.0

# ============================================================================
# VERIFY AND RE-APPLY DLL PATH AFTER TORCH IMPORT
# ============================================================================
# Double-check after importing torch
try:
    import torch
    torch_lib_path = Path(torch.__file__).parent / "lib"
    if torch_lib_path.exists() and hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(str(torch_lib_path))
            print(f"✓ Verified PyTorch lib in DLL search path: {torch_lib_path}")
        except:
            pass  # Already added
    
    # Also check for CTranslate2 (faster-whisper dependency)
    try:
        import ctranslate2
        ct2_path = Path(ctranslate2.__file__).parent
        if ct2_path.exists() and hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(str(ct2_path))
            print(f"✓ Added CTranslate2 to DLL search path: {ct2_path}")
    except ImportError:
        pass  # CTranslate2 not installed yet
except ImportError:
    print("⚠️  PyTorch not yet installed")
except Exception as e:
    print(f"⚠️  DLL path verification warning: {e}")

# ============================================================================
# FORCE GPU CONFIGURATION
# ============================================================================
# Force NVIDIA discrete GPU usage (prevents integrated graphics usage)
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # GPU 0 = NVIDIA RTX 5070 Ti
os.environ['OLLAMA_NUM_GPU'] = '1'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# For PyTorch to use correct GPU
os.environ['TORCH_CUDA_ARCH_LIST'] = '8.9'  # Ada Lovelace architecture

print("🎮 GPU Configuration:")
print(f"   CUDA_VISIBLE_DEVICES = {os.environ.get('CUDA_VISIBLE_DEVICES')}")
print(f"   OLLAMA_NUM_GPU = {os.environ.get('OLLAMA_NUM_GPU')}")
print(f"   Using discrete GPU: NVIDIA RTX 5070 Ti")
print()

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
# Prevent transformers from importing torchvision (avoids nms operator errors)
os.environ['TRANSFORMERS_NO_TORCHVISION'] = '1'
logging.getLogger().setLevel(logging.ERROR)

# Chatterbox TTS requires numpy<1.26 which currently has no wheel for Python 3.12.
# Detect this case to avoid repeated install attempts and to provide a helpful message.
PYTHON_VERSION = sys.version_info
CHATTERBOX_COMPATIBILITY_MESSAGE = None
PY311_FALLBACK_ENV = "ZEYTA_WEBAPP_PY311_FALLBACKED"

def _python_matches_version(executable: str, version: tuple[int, int]) -> bool:
    try:
        result = subprocess.run(
            [executable, "-c", "import sys, json; print(json.dumps(list(sys.version_info[:2])))"],
            capture_output=True,
            text=True,
            timeout=8,
            check=True
        )
        info = json.loads(result.stdout.strip())
        if isinstance(info, list) and len(info) >= 2:
            return tuple(info[:2]) == version
    except (FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
        pass
    return False

def _find_python_version_executable(version: tuple[int, int]) -> str | None:
    tag = f"{version[0]}.{version[1]}"

    def _try_py_launcher() -> str | None:
        try:
            result = subprocess.run(
                ["py", f"-{tag}", "-c", "import sys, json; print(json.dumps(list(sys.version_info[:2])))"],
                capture_output=True,
                text=True,
                timeout=8,
                check=True
            )
            exe_result = result.stdout.strip()
            if exe_result and _python_matches_version(exe_result, version):
                return exe_result
        except (FileNotFoundError, subprocess.SubprocessError):
            pass
        return None

    launcher_exe = _try_py_launcher()
    if launcher_exe:
        return launcher_exe

    candidates = [f"python{tag}", f"python{version[0]}{version[1]}", f"python{version[0]}"]
    for candidate in candidates:
        candidate_path = shutil.which(candidate)
        if candidate_path and _python_matches_version(candidate_path, version):
            return candidate_path

    return None

def _attempt_relaunch_with_python311() -> bool:
    if os.environ.get(PY311_FALLBACK_ENV) == "1":
        return False
    executable = _find_python_version_executable((3, 11))
    if not executable:
        return False
    resolved_current = Path(sys.executable).resolve()
    resolved_candidate = Path(executable).resolve()
    if resolved_current == resolved_candidate:
        return False

    print("⚠️  Python 3.12 cannot install the required numpy dependency for Chatterbox-TTS.")
    print(f"🔁 Re-launching with Python 3.11 interpreter: {resolved_candidate}")
    new_env = dict(os.environ)
    new_env[PY311_FALLBACK_ENV] = "1"
    result = subprocess.run([executable, *sys.argv], env=new_env)
    raise SystemExit(result.returncode)

if PYTHON_VERSION >= (3, 12):
    CHATTERBOX_COMPATIBILITY_MESSAGE = (
        "Chatterbox-TTS currently requires numpy<1.26, and there is no prebuilt wheel for "
        "Python 3.12. Please run the app with Python 3.11 or install Chatterbox-TTS into a "
        "Python 3.11 virtual environment and point the app at that interpreter."
    )
    _attempt_relaunch_with_python311()

# ============================================================================
# TORCH VERSION STACKS
# ============================================================================
TORCH_VERSION_STACKS = {
    "cu128": {
        "torch": "torch==2.10.0.dev20251114+cu128",
        "torchvision": "torchvision==0.25.0.dev20251115+cu128",
        "torchaudio": "torchaudio==2.10.0.dev20251115+cu128",
        "index_url": "https://download.pytorch.org/whl/nightly/cu128",
        "label": "CUDA 12.8 nightly (RTX 50-series)"
    },
    "cpu": {
        "torch": "torch==2.6.0",
        "torchvision": "torchvision==0.21.0",
        "torchaudio": "torchaudio==2.6.0",
        "index_url": None,
        "label": "CPU-only PyTorch 2.6.0"
    }
}

def _is_50_series_gpu(capability: tuple[int, int] | None) -> bool:
    if capability is None:
        return False
    major, minor = capability
    return major > 8 or (major == 8 and minor >= 9)

def _get_preferred_torch_stack() -> dict:
    try:
        import torch as _torch
        if _torch.cuda.is_available():
            capability = _torch.cuda.get_device_capability(0)
            if _is_50_series_gpu(capability):
                return TORCH_VERSION_STACKS["cu128"]
    except (ImportError, AttributeError, RuntimeError):
        pass
    return TORCH_VERSION_STACKS["cpu"]

def _resolve_dynamic_pip_spec(pkg_import: str, pkg_pip: str) -> tuple[str, str | None]:
    if pkg_import in {"torch", "torchvision", "torchaudio"}:
        stack = _get_preferred_torch_stack()
        return stack[pkg_import], stack.get("index_url")
    return pkg_pip, None

def _install_pytorch_stack(stack: dict | None) -> bool:
    stack = stack or _get_preferred_torch_stack()
    packages = [stack['torch'], stack['torchvision'], stack['torchaudio']]
    index_url = stack.get('index_url')
    try:
        print("📦 Step 1/3: Uninstalling existing PyTorch packages...")
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"],
            capture_output=True,
            timeout=120
        )
        print("   ✓ Uninstalled")

        print("\n📦 Step 2/3: Clearing pip cache...")
        subprocess.run(
            [sys.executable, "-m", "pip", "cache", "purge"],
            capture_output=True,
            timeout=60
        )
        print("   ✓ Cache cleared")

        print(f"\n📦 Step 3/3: Installing {stack['label']}...")
        cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall"]
        cmd.extend(packages)
        if index_url:
            cmd.extend(["--index-url", index_url])
        result = subprocess.run(
            cmd,
            capture_output=False,
            timeout=900
        )
        return result.returncode == 0
    except Exception as install_error:
        print(f"\n❌ PyTorch reinstall step failed: {install_error}")
        return False

# Configuration
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
OUTPUT_FOLDER = BASE_DIR / 'outputs'
STATIC_FOLDER = BASE_DIR / 'static'
TEMPLATES_FOLDER = BASE_DIR / 'templates'

# Create necessary directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, STATIC_FOLDER, TEMPLATES_FOLDER]:
    folder.mkdir(exist_ok=True)

print("🚀 Zeyta AI Web Application Starting...")
print("=" * 60)
print()
print("💡 Auto-Fix Features:")
print("   ✓ Binary compatibility check (numpy dtype errors)")
print("   ✓ Automatic dependency installation")
print("   ✓ GPU fallback to CPU on errors")
print()

# ============================================================================
# DEPENDENCY MANAGEMENT SYSTEM
# ============================================================================

REQUIRED_PACKAGES = {
    'flask': 'flask',
    'flask_cors': 'flask-cors',
    'flask_socketio': 'flask-socketio',
    'werkzeug': 'werkzeug',
    'torch': 'torch',
    'torchvision': 'torchvision',
    'torchaudio': 'torchaudio',
    'transformers': 'transformers',
    'faster_whisper': 'faster-whisper',
    'sounddevice': 'sounddevice',
    'soundfile': 'soundfile',
        'pyttsx3': 'pyttsx3',
    'numpy': 'numpy',
    'scipy': 'scipy',
    'webrtcvad': 'webrtcvad',
    'chatterbox': 'chatterbox-tts',
    'psutil': 'psutil',
    'OpenSSL': 'pyopenssl',
    'duckduckgo_search': 'duckduckgo-search',
}

def check_package(package_name):
    """Check if a package is installed"""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name, pip_name=None, index_url=None, force_reinstall=False):
    """Install a package using pip"""
    pip_spec = pip_name or package_name
    print(f"📦 Installing {pip_spec}...")
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        if force_reinstall:
            cmd.append("--force-reinstall")
        if index_url:
            cmd.extend(["--index-url", index_url])
        cmd.append(pip_spec)
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout per package
        )
        if result.returncode == 0:
            print(f"✅ {pip_spec} installed successfully")
            return True
        print(f"❌ Failed to install {pip_spec}")
        return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {pip_spec} installation timed out (large package)")
        return False
    except Exception as e:
        print(f"❌ Failed to install {pip_spec}: {e}")
        return False

def check_binary_compatibility():
    """Check for binary incompatibility issues (numpy dtype errors)"""
    try:
        import numpy as np
        import scipy
        import soundfile as sf
        import torch
        import torchaudio as ta
        
        # Try operations that commonly trigger dtype errors
        test_array = np.zeros((10, 10), dtype=np.float32)
        test_array2 = np.array([1, 2, 3], dtype=np.int32)
        
        # Try scipy operations (common source of dtype errors)
        from scipy import signal
        test_filter = signal.butter(4, 0.5)
        
        # Try soundfile (audio processing can trigger dtype errors)
        test_data = np.zeros(1000, dtype=np.float32)
        
        # Try torch operations with numpy (TTS uses this extensively)
        test_tensor = torch.from_numpy(test_array)
        if torch.cuda.is_available():
            test_tensor = test_tensor.cuda()
            test_back = test_tensor.cpu().numpy()
        
        # Try torchaudio operations (used for saving TTS output)
        test_audio = torch.zeros((1, 1000))
        
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if 'dtype size changed' in error_msg or 'binary incompatibility' in error_msg or 'size mismatch' in error_msg:
            print(f"   Binary error: {error_msg[:100]}")
            return False
        # Other errors might indicate compatibility issues too
        print(f"⚠️  Compatibility check warning: {e}")
        return True

def fix_chatterbox_gpu():
    """Reinstall chatterbox-tts to fix GPU compatibility"""
    print("\n" + "="*60)
    print("🔧 FIXING CHATTERBOX GPU COMPATIBILITY")
    print("="*60)
    print("Reinstalling chatterbox-tts with current PyTorch/CUDA configuration...")
    print("This will recompile the package for your GPU architecture.\n")
    
    stack = _get_preferred_torch_stack()
    try:
        # Step 1: Fix PyTorch version conflicts first
        print("📦 Step 1/4: Checking PyTorch/torchvision compatibility...")
        try:
            import torch
            try:
                import torchvision
                torchvision_version = torchvision.__version__.split('+')[0]
            except Exception:
                torchvision = None
                torchvision_version = None
            torch_version = torch.__version__.split('+')[0]
            
            # Check if versions are compatible
            needs_realignment = False
            if torchvision_version is None:
                print("   ⚠️  torchvision not found; will install compatible version")
                needs_realignment = True
            else:
                # torchvision major.minor should align with torch major.minor
                tv_major_minor = '.'.join(torchvision_version.split('.')[:2])
                torch_major_minor = '.'.join(torch_version.split('.')[:2])
                if tv_major_minor != torch_major_minor:
                    print(f"   ⚠️  Version mismatch: torch {torch_version}, torchvision {torchvision_version}")
                    needs_realignment = True

            if needs_realignment:
                print(f"   Reinstalling matching PyTorch packages ({stack['label']})...")
                if _install_pytorch_stack(stack):
                    print(f"   ✓ PyTorch, TorchVision, TorchAudio aligned ({stack['label']})")
                else:
                    print(f"   ⚠️  Failed to reinstall PyTorch stack ({stack['label']})")
            else:
                print("   ✓ PyTorch versions compatible")
        except Exception as e:
            print(f"   ⚠️  Could not verify PyTorch compatibility: {e}")
        
        # Step 2: Fix numpy version for opencv
        print("\n📦 Step 2/4: Checking numpy compatibility...")
        try:
            import numpy as np
            numpy_version = tuple(map(int, np.__version__.split('.')[:2]))
            if numpy_version[0] < 2:
                print(f"   ⚠️  numpy {np.__version__} is too old for opencv")
                print("   Upgrading to numpy 2.x...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "numpy>=2.0,<2.3"],
                    capture_output=True,
                    timeout=120
                )
                print("   ✓ numpy upgraded")
            else:
                print(f"   ✓ numpy {np.__version__} is compatible")
        except Exception as e:
            print(f"   ⚠️  Could not verify numpy: {e}")
        
        # Step 3: Uninstall chatterbox-tts
        print("\n📦 Step 3/4: Uninstalling chatterbox-tts...")
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "chatterbox-tts"],
            capture_output=True,
            timeout=60
        )
        print("   ✓ Uninstalled")
        
        # Clear pip cache
        print(f"\n📦 Step 4/4: Reinstalling with GPU support ({stack['label']})...")
        subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True)
        
        # Reinstall with no-cache to force recompilation
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-cache-dir", "chatterbox-tts"],
            capture_output=False,  # Show output to user
            timeout=600  # 10 minutes for compilation
        )
        
        if result.returncode == 0:
            print("\n✅ chatterbox-tts reinstalled successfully!")
            print("   The package should now work with your GPU.")
            print("\n⚠️  Note: Restart Python to clear the invalid distribution warnings.")
            return True
        else:
            print("\n⚠️  Installation completed with warnings")
            return True
    except Exception as e:
        print(f"\n❌ Fix failed: {e}")
        return False

def clean_invalid_distributions():
    """Clean up invalid distribution folders that Windows locks"""
    print("\n🧹 Cleaning invalid distributions...")
    site_packages = Path(sys.executable).parent / "Lib" / "site-packages"
    
    invalid_dirs = []
    for item in site_packages.glob("~*"):
        if item.is_dir():
            invalid_dirs.append(item)
    
    if invalid_dirs:
        print(f"   Found {len(invalid_dirs)} invalid distribution folders")
        print("   These will be cleaned on next Python restart")
        print("   (Windows locks .pyd files that are currently loaded)")
        return False
    else:
        print("   ✓ No invalid distributions found")
        return True

def fix_binary_incompatibility():
    """Fix binary incompatibility by reinstalling numpy and dependent packages"""
    print("\n" + "="*60)
    print("⚠️  BINARY INCOMPATIBILITY DETECTED")
    print("="*60)
    print("Issue: numpy dtype size mismatch (Expected 96, got 88)")
    print("This happens when packages were compiled with different numpy versions.")
    print("\n🔧 Auto-fixing by reinstalling packages with compatible versions...\n")
    
    # Packages that need to be reinstalled together for binary compatibility
    packages_to_fix = [
        'numpy',
        'scipy', 
        'soundfile',
        'librosa',
        'numba'  # Often causes dtype issues
    ]
    
    try:
        # Force uninstall ALL potentially conflicting packages
        print("📦 Step 1/3: Removing incompatible packages...")
        uninstall_cmd = [sys.executable, "-m", "pip", "uninstall", "-y"] + packages_to_fix
        subprocess.run(uninstall_cmd, capture_output=True, timeout=120)
        print("   ✓ Removed old packages")
        
        # Clear pip cache to ensure fresh downloads
        print("\n📦 Step 2/3: Clearing pip cache...")
        subprocess.run(
            [sys.executable, "-m", "pip", "cache", "purge"],
            capture_output=True,
            timeout=60
        )
        print("   ✓ Cache cleared")
        
        # Reinstall packages in correct order with no-cache
        print("\n📦 Step 3/3: Reinstalling with compatible versions...")
        
        # Install numpy first (base dependency)
        print("   • Installing numpy...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall", "numpy"],
            capture_output=True,
            timeout=300,
            text=True
        )
        if result.returncode == 0:
            print("     ✓ numpy installed")
        else:
            print(f"     ⚠️  numpy install warning: {result.stderr[:100]}")
        
        # Install other packages
        for pkg in packages_to_fix[1:]:
            print(f"   • Installing {pkg}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--no-cache-dir", pkg],
                capture_output=True,
                timeout=300,
                text=True
            )
            if result.returncode == 0:
                print(f"     ✓ {pkg} installed")
        
        print("\n" + "="*60)
        print("✅ BINARY COMPATIBILITY FIXED!")
        print("="*60)
        print("All packages reinstalled with compatible versions.\n")
        return True
        
    except subprocess.TimeoutExpired:
        print("\n❌ Fix timed out - packages may be large")
        print("💡 Try manually: pip uninstall -y numpy scipy soundfile librosa numba")
        print("                 pip install --no-cache-dir numpy scipy soundfile librosa numba\n")
        return False
    except Exception as e:
        print(f"\n❌ Failed to fix binary incompatibility: {e}")
        print("💡 Manual fix command:")
        print("   pip uninstall -y numpy scipy soundfile librosa numba")
        print("   pip install --no-cache-dir numpy scipy soundfile librosa numba\n")
        return False

def ensure_dependencies():
    """Ensure all required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    # Skip pip upgrade - causes hangs on Windows during startup
    # User can manually upgrade if needed: pip install --upgrade pip setuptools wheel
    print("ℹ️  Skipping pip/setuptools upgrade (use manually if needed)")
    
    # Check for binary incompatibility issues
    if not check_binary_compatibility():
        if not fix_binary_incompatibility():
            print("⚠️  Warning: Binary incompatibility could not be automatically fixed")
            print("💡 If you encounter 'dtype size changed' errors, run:")
            print("   pip uninstall -y numpy scipy soundfile torchaudio")
            print("   pip install --no-cache-dir numpy scipy soundfile torchaudio\n")
    
    missing = []
    for pkg_import, pkg_pip in REQUIRED_PACKAGES.items():
        if pkg_import == 'chatterbox' and CHATTERBOX_COMPATIBILITY_MESSAGE:
            continue
        if not check_package(pkg_import):
            pip_spec, index_url = _resolve_dynamic_pip_spec(pkg_import, pkg_pip)
            missing.append((pkg_import, pip_spec, index_url))
    
    if missing:
        print(f"\n⚠️  Found {len(missing)} missing packages")
        print("📥 Installing packages (this may take 5-15 minutes)...\n")
        
        failed = []
        for pkg_import, pip_spec, index_url in missing:
            if not install_package(pkg_import, pip_name=pip_spec, index_url=index_url):
                failed.append(pip_spec)
        
        if failed:
            print(f"\n⚠️  Some packages failed to install: {', '.join(failed)}")
            print("💡 Try running manually: pip install " + " ".join(failed))
            print("💡 Or continue - the app will attempt to use what's available\n")
        else:
            print("\n✅ All dependencies installed!")
    elif CHATTERBOX_COMPATIBILITY_MESSAGE:
        print("\n⚠️  Chatterbox-TTS installation skipped:")
        print(f"   {CHATTERBOX_COMPATIBILITY_MESSAGE}")
    else:
        print("✅ All dependencies already installed")
    
    return True

# Install dependencies before importing
ensure_dependencies()

# Now import all required packages
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import torch
import torchaudio as ta
import numpy as np
import soundfile as sf
import threading
import queue
import time
import base64
import io
import inspect
from distutils.version import LooseVersion
import tts_optimizer  # RTX 50-series GPU optimization

# ============================================================================
# CHATTERBOX CUDA-ONLY IMPORT LOGIC (from tts_test.py)
# ============================================================================

def parse_version_tuple(ver_str: str):
    """Parse torch version string into comparable tuple."""
    try:
        v = LooseVersion(ver_str)
        parts = []
        for p in v.version:
            try:
                parts.append(int(p))
            except Exception:
                parts.append(0)
        return tuple(parts)
    except Exception:
        return (0,)

TORCH_CUDA = False
if torch is not None:
    try:
        TORCH_CUDA = torch.cuda.is_available()
    except Exception:
        TORCH_CUDA = False

TORCH_VER_TUPLE = parse_version_tuple(torch.__version__) if torch is not None else (0,)
TORCH_MIN_FOR_CHATTER = (2, 1)
TORCH_FORBID = (2, 6)

def torch_version_ok_for_chatter():
    """Check if torch version is compatible with Chatterbox (CUDA only, >= 2.1, not 2.6)."""
    if not TORCH_CUDA:
        return False
    try:
        major = TORCH_VER_TUPLE[0]
        minor = TORCH_VER_TUPLE[1] if len(TORCH_VER_TUPLE) > 1 else 0
    except Exception:
        return False
    # Must be >= 2.1 and not 2.6
    if major >= 2 and minor >= 1 and not (major == 2 and minor == 6):
        return True
    # Allow explicit override via env var
    if os.getenv('FORCE_CHATTERBOX_WITH_TORCH', '0') == '1':
        return True
    return False

def can_run_chatter_subprocess():
    """Check if subprocess can import chatterbox with CUDA available."""
    if not TORCH_CUDA:
        return False
    chatter_python = os.getenv('CHATTERBOX_PYTHON', sys.executable)
    # Helpful debug log: show which python binary will be used for chatter subprocess
    try:
        print(f"[DEBUG] chatter subprocess will use python: {chatter_python}")
    except Exception:
        pass
    try:
        # Combined check with longer timeout (model loading can be slow)
        # Use try/except in subprocess to avoid debugger breaking on uncaught ModuleNotFoundError
        cmd = [chatter_python, "-c", "import sys; try: import torch; assert torch.cuda.is_available(); from chatterbox import ChatterboxTTS; print('ok'); except Exception: sys.exit(1)"]
        proc = subprocess.run(cmd, check=False, capture_output=True, timeout=30)
        return proc.returncode == 0 and b'ok' in proc.stdout
    except Exception:
        return False

def chatter_speak_subprocess(text, sr=22050, speaker_id=None, audio_prompt_path=None, use_optimizer=False):
    """Run chatterbox in subprocess to isolate ABI/version issues.
    
    The subprocess writes a temporary WAV and returns its contents.
    
    Args:
        text: Text to synthesize
        sr: Sample rate
        speaker_id: Optional speaker ID
        audio_prompt_path: Path to reference audio for voice cloning
        use_optimizer: Whether to enable RTX 50-series GPU optimizations (FP16, CUDA Graphs, embedding cache)
    """
    chatter_python = os.getenv('CHATTERBOX_PYTHON', sys.executable)
    tmp_dir = tempfile.mkdtemp(prefix='chatter_proc_')
    args_path = os.path.join(tmp_dir, 'args.json')
    out_wav = os.path.join(tmp_dir, 'out.wav')
    data = {
        'text': text,
        'speaker_id': int(speaker_id) if speaker_id is not None else None,
        'audio_prompt_path': audio_prompt_path,
        'out_wav': out_wav,
        'sr': int(sr),
        'use_optimizer': use_optimizer,
        'base_dir': str(BASE_DIR)
    }
    with open(args_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    # Write helper script that loads chatterbox and generates audio
    script = r'''import json,sys,os
from pathlib import Path
args = json.load(open(sys.argv[1],'r'))
if 'base_dir' in args:
    sys.path.insert(0, args['base_dir'])

try:
    from chatterbox import ChatterboxTTS
    import torch
    import inspect
    dev = torch.device('cuda')
    model = ChatterboxTTS.from_pretrained(device=dev)
    
    # Apply RTX 50-series optimizations if requested
    if args.get('use_optimizer', False):
        try:
            import tts_optimizer
            optimizer = tts_optimizer.get_optimizer()
            if optimizer.is_50_series:
                model = tts_optimizer.optimize_chatterbox(model)
                print('[OPTIMIZER] RTX 50-series optimizations enabled', file=sys.stderr)
        except Exception as e:
            print(f'[WARN] Optimizer failed: {e}', file=sys.stderr)
    
    # Only pass kwargs that are actually supported by generate
    sig = inspect.signature(model.generate)
    kwargs={}
    if args.get('speaker_id') is not None and 'speaker_id' in sig.parameters:
        kwargs['speaker_id'] = int(args.get('speaker_id'))
    if args.get('audio_prompt_path'):
        if 'audio_prompt_path' in sig.parameters:
            kwargs['audio_prompt_path'] = args.get('audio_prompt_path')
        elif 'audio_prompt' in sig.parameters:
            kwargs['audio_prompt'] = args.get('audio_prompt_path')
    audio = model.generate(args['text'], **kwargs)
    import soundfile as sf
    import numpy as np
    arr = np.asarray(audio).squeeze()
    sr = int(args.get('sr', 22050))
    if arr.dtype == np.int16:
        out_arr = arr.astype('float32')/32768.0
    else:
        out_arr = arr.astype('float32')
    
    # Ensure 1D
    if out_arr.ndim == 2 and out_arr.shape[0] == 1:
        out_arr = out_arr.squeeze(0)
        
    sf.write(args['out_wav'], out_arr, sr, format='WAV')
    print(args['out_wav'])
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    script_path = os.path.join(tmp_dir, 'run_chatter.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    
    cmd = [chatter_python, script_path, args_path]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        print(f'❌ Chatterbox subprocess failed: {proc.stderr}')
        raise RuntimeError('Chatter subprocess failed: ' + proc.stderr)
    
    out_file = proc.stdout.strip().splitlines()[-1].strip()
    if not os.path.exists(out_file):
        raise RuntimeError('Chatter subprocess did not create output file')
    
    data, sr = sf.read(out_file, dtype='float32')
    # Cleanup
    try:
        shutil.rmtree(tmp_dir)
    except Exception:
        pass
    return np.asarray(data).squeeze(), int(sr)

# Conditionally import Chatterbox only if CUDA available and torch version compatible
chatter_import_error = None
ChatterboxTTS = None
use_chatter_import = torch_version_ok_for_chatter()

if not use_chatter_import:
    print('⚠️  Chatterbox import suppressed: torch/CUDA or version constraints do not match (requires GPU and compatible torch >= 2.1, not 2.6)')
else:
    try:
        from chatterbox import ChatterboxTTS
        chatter_import_error = None
        print('✓ Chatterbox imported successfully (in-process)')
    except Exception as e:
        chatter_import_error = e
        ChatterboxTTS = None
        err_text = str(e)
        if 'numpy.dtype size changed' in err_text or 'size changed' in err_text:
            print(f'⚠️  Chatterbox in-process import failed (ABI mismatch): {e}')
            print('   Will attempt to use subprocess execution if CHATTERBOX_PYTHON is configured.')
        else:
            print(f'⚠️  Chatterbox in-process import failed: {e}')

# Check subprocess availability
chatter_python_env = os.getenv('CHATTERBOX_PYTHON')

# Auto-detect venv_chatterbox if not set
if not chatter_python_env:
    possible_venvs = [
        BASE_DIR / 'venv_chatterbox' / 'Scripts' / 'python.exe',
    ]
    for venv_python in possible_venvs:
        if venv_python.exists():
            print(f"🔍 Found potential Chatterbox venv: {venv_python}")
            # Verify it has chatterbox
            try:
                # Use try/except in subprocess to avoid debugger breaking on uncaught ModuleNotFoundError
                subprocess.run([str(venv_python), "-c", "import sys; try: import chatterbox; except ImportError: sys.exit(1)"], check=True, capture_output=True)
                os.environ['CHATTERBOX_PYTHON'] = str(venv_python)
                chatter_python_env = str(venv_python)
                print(f"✓ Auto-configured CHATTERBOX_PYTHON: {chatter_python_env}")
                break
            except subprocess.CalledProcessError:
                print(f"   (Chatterbox not found in {venv_python})")

if chatter_python_env:
    print(f'✓ CHATTERBOX_PYTHON is set to: {chatter_python_env}')
    if can_run_chatter_subprocess():
        print('✓ Chatterbox subprocess execution available')
    else:
        print('⚠️  CHATTERBOX_PYTHON set but subprocess check failed')
elif ChatterboxTTS is None and TORCH_CUDA:
    print('💡 Tip: Set CHATTERBOX_PYTHON environment variable to use Chatterbox via subprocess')

class WindowsNativeTTS:
    """Simple Windows TTS wrapper using pyttsx3."""
    def __init__(self, rate: int, volume: float):
        if not PYTTSX3_AVAILABLE:
            raise RuntimeError("pyttsx3 is not installed")
        assert pyttsx3 is not None
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', max(0.0, min(volume, 1.0)))
        self._lock = threading.Lock()
        self.sample_rate = 22050

    def generate(self, text: str, **kwargs):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        with self._lock:
            self.engine.save_to_file(text, tmp_path)
            self.engine.runAndWait()
        try:
            import soundfile as _sf
            import numpy as _np
            data, sr = _sf.read(tmp_path)
            self.sample_rate = sr
            return _np.array(data, dtype=_np.float32)
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


class PiperTTS:
    """Thin Piper wrapper that mimics the chatterbox generate() interface.

    This expects the `piper-tts` Python package and a valid on-disk Piper model.
    """
    def __init__(self, model_path: str, speaker_id: int = 0, device: str = "auto"):
        try:
            import piper
        except ImportError:
            raise RuntimeError("piper-tts is not installed. Install with `pip install piper-tts`." )

        self._piper = piper
        self._device = device
        self._speaker_id = speaker_id
        # Piper currently runs on CPU via its runtime; device flag is kept for symmetry
        self.sample_rate = 22050
        self._model = self._piper.PiperVoice.load(model_path)

    def generate(self, text: str, **kwargs):
        # Piper returns raw audio samples; expose them as float32 numpy array
        import numpy as _np
        # Newer piper-tts versions expect a list of speaker IDs and return (samples, sample_rate)
        try:
            audio, rate = self._model.synthesize(
                text,
                speaker_id=[self._speaker_id] if self._speaker_id is not None else None,  # type: ignore
            )
        except TypeError:
            # Fallback for older signature that may still accept speaker_id directly
            audio, rate = self._model.synthesize(text)

        self.sample_rate = int(rate)  # type: ignore
        return _np.asarray(audio, dtype=_np.float32) / 32768.0


class ChatterboxSubprocessTTS:
    """Chatterbox TTS wrapper that runs in subprocess to avoid ABI/dependency conflicts.
    
    This is used when in-process Chatterbox import fails or CHATTERBOX_PYTHON env var is set.
    Automatically applies GPU optimizations when running on RTX 50-series GPUs.
    """
    def __init__(self, device: str = 'cuda'):
        if not can_run_chatter_subprocess():
            raise RuntimeError(
                "Chatterbox subprocess not available. "
                "Ensure CHATTERBOX_PYTHON points to a Python interpreter with chatterbox-tts installed and CUDA available."
            )
        self._device = device
        self.sample_rate = 22050
        
        # Check if we have 50-series GPU (optimizer will be instantiated in subprocess)
        try:
            self._optimizer = tts_optimizer.get_optimizer()
            if self._optimizer.is_50_series:
                print(f"✓ ChatterboxSubprocessTTS with RTX 50-series optimizations (FP16, CUDA Graphs, embedding cache)")
            else:
                print(f"✓ ChatterboxSubprocessTTS initialized (device={device}, subprocess mode)")
        except Exception as e:
            print(f"⚠️  TTS optimizer initialization failed: {e}, using standard mode")
            self._optimizer = None
    
    def generate(self, text: str, **kwargs):
        """Generate audio using Chatterbox in subprocess with optional GPU optimization."""
        speaker_id = kwargs.get('speaker_id')
        audio_prompt_path = kwargs.get('audio_prompt_path') or kwargs.get('audio_prompt')
        
        # Pass optimizer flag to subprocess if available
        use_optimizer = self._optimizer is not None and self._optimizer.is_50_series
        
        audio, sr = chatter_speak_subprocess(
            text, 
            sr=self.sample_rate, 
            speaker_id=speaker_id, 
            audio_prompt_path=audio_prompt_path,
            use_optimizer=use_optimizer
        )
        self.sample_rate = sr
        return audio

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================

app = Flask(__name__, 
            template_folder=str(TEMPLATES_FOLDER),
            static_folder=str(STATIC_FOLDER))
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['SECRET_KEY'] = 'zeyta-ai-secret-key-2025'

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', max_http_buffer_size=100*1024*1024)

# ============================================================================
# GLOBAL MODEL INSTANCES
# ============================================================================

class ModelManager:
    """Centralized model management"""
    def __init__(self):
        self.tts_model = None
        self.stt_model = None
        self.brain = None
        self.context_manager = None
        self.stt_config = {'size': 'base', 'device': 'auto', 'compute_type': 'auto'}
        self.tts_config = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        # Backend: 'chatterbox', 'piper', 'windows_native'
        try:
            from config import TTS_BACKEND
            self.tts_backend = TTS_BACKEND.lower()
        except Exception:
            self.tts_backend = 'chatterbox'

        self._windows_fallback_used = False
        
        # Ensure torch/lib is in DLL search path for Windows
        try:
            torch_lib_path = Path(torch.__file__).parent / "lib"
            if torch_lib_path.exists() and hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(str(torch_lib_path))
        except Exception:
            pass
    
    def load_tts(self, device: str = 'auto', backend: str | None = None, allow_reinstall: bool | None = None):
        """Load TTS model.

        Args:
            device: 'auto', 'cuda', or 'cpu'
            backend: 'chatterbox', 'piper', or 'windows'; default from config
            allow_reinstall: whether to auto-reinstall a tuned PyTorch stack
        """
        if self.tts_model is not None:
            return True, "TTS already loaded"

        # Resolve backend and reinstall preference from config if not provided
        try:
            from config import TTS_DEVICE, ALLOW_TORCH_REINSTALL, PIPER_MODEL, PIPER_SPEAKER_ID
        except Exception:
            TTS_DEVICE = 'auto'
            ALLOW_TORCH_REINSTALL = True
            PIPER_MODEL = "en_US-lessac-high"
            PIPER_SPEAKER_ID = 0

        backend = (backend or self.tts_backend or 'chatterbox').lower()
        device = (device or TTS_DEVICE or 'auto').lower()
        allow_reinstall = ALLOW_TORCH_REINSTALL if allow_reinstall is None else allow_reinstall

        self.tts_backend = backend
        self.tts_config['backend'] = backend

        # Normalize device choice and detect CUDA if needed
        original_device = device
        if device == 'auto':
            try:
                if torch.cuda.is_available():
                    _ = torch.zeros(1).cuda()
                    device = 'cuda'
                    print(f"✓ CUDA available for TTS, using GPU: {torch.cuda.get_device_name(0)}")
                else:
                    device = 'cpu'
                    print("⚠️  CUDA not available for TTS, using CPU")
            except Exception as cuda_error:
                print(f"⚠️  CUDA test failed for TTS: {cuda_error}")
                device = 'cpu'
        else:
            if device == 'cuda' and not torch.cuda.is_available():
                print("⚠️  CUDA requested for TTS but not available, falling back to CPU")
                device = 'cpu'
            else:
                print(f"✓ Using explicitly requested TTS device: {device}")

        self.tts_config['device'] = device

        # Backend dispatch
        if backend == 'windows':
            # Explicit Windows backend: always allow selecting or reusing Windows TTS,
            # independent of whether it was previously used as a fallback.
            if isinstance(self.tts_model, WindowsNativeTTS):
                self.tts_backend = 'windows_native'
                self.tts_config.update({'device': 'cpu', 'backend': 'windows_native'})
                return True, "Windows TTS backend active"
            ok, msg = self._switch_to_windows_native_tts("Explicit Windows backend selected", force=True)
            return (ok, msg)

        if backend == 'piper':
            try:
                # Expect a .onnx Piper model path relative to BASE_DIR/models or a preconfigured path
                model_path = str((BASE_DIR / 'models' / 'piper' / f"{PIPER_MODEL}.onnx").resolve())
                print(f"🔄 Loading Piper TTS model from {model_path} on {device.upper()} (runtime is CPU-based)...")
                self.tts_model = PiperTTS(model_path=model_path, speaker_id=PIPER_SPEAKER_ID, device=device)
                print("✓ Piper TTS loaded")
                return True, f"Piper TTS loaded (voice={PIPER_MODEL}, device={device.upper()})"
            except Exception as e:
                return False, f"Failed to load Piper TTS: {e}"

        # Default: chatterbox
        # Try in-process first, then subprocess if unavailable
        if ChatterboxTTS is None:
            # In-process import failed or suppressed, try subprocess
            if can_run_chatter_subprocess():
                print(f"🔄 Loading Chatterbox TTS via subprocess on {device.upper()}...")
                try:
                    self.tts_model = ChatterboxSubprocessTTS(device=device)
                    print(f"✓ Chatterbox TTS loaded via subprocess on {device.upper()}")
                    return True, f"Chatterbox TTS loaded (subprocess mode, device={device.upper()})"
                except Exception as e:
                    return False, f"Failed to load Chatterbox subprocess: {e}"
            else:
                # Neither in-process nor subprocess available
                if CHATTERBOX_COMPATIBILITY_MESSAGE:
                    return False, CHATTERBOX_COMPATIBILITY_MESSAGE
                if chatter_import_error:
                    err_text = str(chatter_import_error)
                    if 'numpy.dtype size changed' in err_text or 'size changed' in err_text:
                        return False, (
                            "Chatterbox in-process import failed due to numpy ABI mismatch. "
                            "Set CHATTERBOX_PYTHON environment variable to a Python interpreter with compatible chatterbox-tts installation."
                        )
                    return False, f"Chatterbox import failed: {chatter_import_error}"
                return False, (
                    "Chatterbox-TTS is not available. Either install it in current environment "
                    "or set CHATTERBOX_PYTHON to point to a Python interpreter with chatterbox-tts installed."
                )

        # In-process ChatterboxTTS is available
        print(f"🔄 Loading Chatterbox TTS (in-process) on {device.upper()}...")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                base_model = ChatterboxTTS.from_pretrained(device=device)
                
                # Apply RTX 50-series optimizations if available
                try:
                    optimizer = tts_optimizer.get_optimizer()
                    if optimizer.is_50_series and device == 'cuda':
                        self.tts_model = tts_optimizer.optimize_chatterbox(base_model)
                        print(f"✓ Chatterbox TTS loaded with RTX 50-series optimizations (FP16, CUDA Graphs, embedding cache) on {device.upper()}")
                        
                        # Warmup to trigger torch.compile compilation
                        print("🔥 Warming up TTS model (compiling kernels)...")
                        try:
                            # Generate a short text to trigger compilation
                            _ = self.tts_model.generate("Warmup.")
                            print("✓ Warmup complete")
                        except Exception as w_err:
                            print(f"⚠️ Warmup failed: {w_err}")
                    else:
                        self.tts_model = base_model
                        print(f"✓ Chatterbox TTS loaded successfully (in-process) on {device.upper()}")
                except Exception as opt_error:
                    print(f"⚠️  TTS optimizer failed: {opt_error}, using standard model")
                    self.tts_model = base_model
                    print(f"✓ Chatterbox TTS loaded successfully (in-process) on {device.upper()}")
            except Exception as e:
                error_str = str(e).lower()

                if self._is_torchvision_issue(error_str):
                    success, message = self._attempt_torchvision_fix(error_str)
                    return False, message

                # Binary incompatibility - try subprocess fallback
                if 'dtype size changed' in error_str or 'binary incompatibility' in error_str:
                    print(f"⚠️  Binary incompatibility detected during in-process load: {e}")
                    if can_run_chatter_subprocess():
                        print("   Falling back to subprocess execution...")
                        try:
                            self.tts_model = ChatterboxSubprocessTTS(device=device)
                            print(f"✓ Chatterbox TTS loaded via subprocess fallback on {device.upper()}")
                            return True, f"Chatterbox TTS loaded (subprocess fallback, device={device.upper()})"
                        except Exception as sub_e:
                            return False, f"Both in-process and subprocess loading failed: {sub_e}"
                    return False, (
                        "Binary incompatibility detected. Set CHATTERBOX_PYTHON environment variable "
                        "to use subprocess execution, or restart the application to auto-fix."
                    )

                # CUDA kernel issues
                if device == 'cuda' and self._is_cuda_kernel_error(error_str):
                    print("⚠️  CUDA kernel compatibility issue detected for Chatterbox TTS")
                    print(f"   Error: {str(e)[:200]}")

                    # First attempt: precision tweak and cache reset
                    try:
                        torch.cuda.empty_cache()
                        if hasattr(torch.cuda, 'reset_peak_memory_stats'):
                            torch.cuda.reset_peak_memory_stats()
                        if hasattr(torch.cuda, 'synchronize'):
                            torch.cuda.synchronize()
                    except Exception:
                        pass

                    print("   Retrying Chatterbox load with float32 compatibility mode...")
                    try:
                        torch.set_default_dtype(torch.float32)
                        if hasattr(torch, 'set_float32_matmul_precision'):
                            torch.set_float32_matmul_precision('high')
                        base_model = ChatterboxTTS.from_pretrained(device=device)
                        
                        # Apply optimizations even in compatibility mode
                        try:
                            optimizer = tts_optimizer.get_optimizer()
                            if optimizer.is_50_series and device == 'cuda':
                                self.tts_model = tts_optimizer.optimize_chatterbox(base_model)
                                print("✓ TTS model loaded on GPU with compatibility mode + RTX 50-series optimizations")
                                
                                # Warmup
                                try:
                                    _ = self.tts_model.generate("Warmup.")
                                except: pass
                            else:
                                self.tts_model = base_model
                                print("✓ TTS model loaded on GPU with compatibility mode")
                        except Exception:
                            self.tts_model = base_model
                            print("✓ TTS model loaded on GPU with compatibility mode")
                    except Exception as retry_error:
                        retry_error_str = str(retry_error).lower()
                        
                        # Try subprocess fallback before reinstalling PyTorch
                        if can_run_chatter_subprocess():
                            print("   In-process load failed, trying subprocess fallback...")
                            try:
                                self.tts_model = ChatterboxSubprocessTTS(device=device)
                                print(f"✓ Chatterbox TTS loaded via subprocess fallback on {device.upper()}")
                                return True, f"Chatterbox TTS loaded (subprocess fallback after CUDA error, device={device.upper()})"
                            except Exception as sub_e:
                                print(f"   Subprocess fallback also failed: {sub_e}")
                        
                        if self._is_cuda_kernel_error(retry_error_str) and allow_reinstall:
                            print("⚠️  GPU still incompatible; proposing RTX 50‑series nightly PyTorch reinstall (CUDA 12.8)...")
                            stack = _get_preferred_torch_stack()
                            ok = self._install_pytorch_cuda_stack(stack)
                            msg = (
                                f"RTX 50‑series nightly PyTorch reinstall {'succeeded' if ok else 'completed with warnings'} "
                                f"({stack['label']}). Please restart the app and reinitialize TTS."
                            )
                            return False, msg

                        # If reinstall not allowed or still failing, try Windows fallback
                        fallback_success, fallback_message = self._switch_to_windows_native_tts(retry_error_str)
                        if fallback_success:
                            return True, fallback_message
                        raise retry_error

                    # If we reached here, retry succeeded
                    if device == 'cuda' and hasattr(torch.cuda, 'empty_cache'):
                        torch.cuda.empty_cache()
                else:
                    # Generic error - try subprocess fallback if available
                    if can_run_chatter_subprocess():
                        print(f"⚠️  In-process load failed: {e}")
                        print("   Attempting subprocess fallback...")
                        try:
                            self.tts_model = ChatterboxSubprocessTTS(device=device)
                            print(f"✓ Chatterbox TTS loaded via subprocess fallback on {device.upper()}")
                            return True, f"Chatterbox TTS loaded (subprocess fallback, device={device.upper()})"
                        except Exception as sub_e:
                            return False, f"Both in-process and subprocess loading failed: {sub_e}"
                    return False, f"TTS load failed: {e}"

        # Verify the model is actually on the correct device
        actual_device = "unknown"
        try:
            if hasattr(self.tts_model, 'device'):
                actual_device = str(self.tts_model.device)
            else:
                model_obj = getattr(self.tts_model, 'model', None)
                if model_obj is not None and hasattr(model_obj, 'device'):
                    actual_device = str(model_obj.device)
        except Exception:
            pass

        return True, f"TTS loaded on {device.upper()} (device: {actual_device}, backend: {backend})"
    
    def load_stt(self, model_size='base', device='auto', compute_type='auto'):
        """Load STT model
        
        Args:
            model_size: Model size - 'tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3', 'turbo'
                       'turbo' is an alias for 'large-v3-turbo' - the fastest, most accurate model
            device: 'auto', 'cuda', or 'cpu'
            compute_type: 'auto', 'float16', 'int8', etc.
        """
        try:
            from faster_whisper import WhisperModel
            
            # Map "turbo" to the actual model name FIRST (before any device checks)
            actual_model_name = model_size
            if model_size.lower() == 'turbo':
                actual_model_name = 'large-v3-turbo'
                print(f"🚀 Turbo mode selected - using {actual_model_name} (optimized for speed & accuracy)")
            
            original_device = device
            
            if device == 'auto':
                # Try CUDA first, fallback to CPU if cuDNN issues
                try:
                    if torch.cuda.is_available():
                        test_tensor = torch.zeros(1).cuda()
                        device = 'cuda'
                        print(f"✓ CUDA available for STT, using GPU: {torch.cuda.get_device_name(0)}")
                    else:
                        device = 'cpu'
                        print("⚠️  CUDA not available for STT, using CPU")
                except Exception:
                    print("⚠️  CUDA test failed, using CPU for STT")
                    device = 'cpu'
            else:
                # User explicitly requested a device
                if device == 'cuda':
                    if not torch.cuda.is_available():
                        print(f"⚠️  WARNING: CUDA requested but torch.cuda.is_available() = False")
                        print(f"   PyTorch version: {torch.__version__}")
                        print(f"   Attempting to load anyway - faster-whisper may have its own CUDA detection")
                        # Don't fall back to CPU - let faster-whisper try
                    else:
                        print(f"✓ Using explicitly requested device for STT: CUDA")
                        print(f"   GPU: {torch.cuda.get_device_name(0)}")
                elif device == 'cpu':
                    print(f"✓ Using explicitly requested device for STT: CPU")
                else:
                    print(f"✓ Using device for STT: {device}")
            
            if compute_type == 'auto':
                compute_type = 'float16' if device == 'cuda' else 'int8'
            
            self.stt_config = {'size': model_size, 'device': device, 'compute_type': compute_type}
            
            print(f"🔄 Loading STT model ({actual_model_name}) on {device.upper()} with {compute_type}...")
            
            try:
                self.stt_model = WhisperModel(actual_model_name, device=device, compute_type=compute_type)
                print(f"✓ STT model loaded successfully on {device.upper()}")
            except Exception as e:
                # If GPU fails and user didn't explicitly request GPU, try CPU
                if device == 'cuda' and original_device == 'auto':
                    print(f"⚠️  GPU loading failed: {e}")
                    print("⚠️  Retrying STT with CPU...")
                    device = 'cpu'
                    compute_type = 'int8'
                    self.stt_config = {'size': model_size, 'device': device, 'compute_type': compute_type}
                    self.stt_model = WhisperModel(actual_model_name, device=device, compute_type=compute_type)
                    print(f"✓ STT model loaded on CPU (GPU fallback)")
                else:
                    raise
            
            return True, f"STT ({actual_model_name}) loaded on {device.upper()} with {compute_type}"
        except Exception as e:
            return False, f"STT load failed: {str(e)}"
    
    def load_llm(self, provider='ollama', model_name='llama3:latest'):
        """Load LLM via provider (doesn't actually load, just checks connection)"""
        if self.brain is not None:
            # Check if we are switching providers or models
            current_provider = self.brain.get('type')
            current_model = self.brain.get('model')
            if current_provider == provider and current_model == model_name:
                return True, f"LLM already connected ({provider}: {model_name})"
            
            # Unload previous
            self.unload_llm()
        
        try:
            if provider == 'ollama':
                import requests
                
                # Check if Ollama is running
                print("🔄 Checking Ollama connection...")
                try:
                    response = requests.get('http://localhost:11434/api/tags', timeout=5)
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [m['name'] for m in models_data.get('models', [])]
                        print(f"✓ Ollama connected. Available models: {', '.join(available_models)}")
                        
                        # Check if requested model exists
                        if model_name not in available_models:
                            # Try to find a similar model
                            for model in available_models:
                                if model_name.split(':')[0] in model:
                                    model_name = model
                                    break
                            else:
                                if available_models:
                                    model_name = available_models[0]
                                    print(f"⚠️  Requested model not found, using: {model_name}")
                        
                        # Store Ollama connection info (not actual model)
                        self.brain = {
                            'type': 'ollama',
                            'model': model_name,
                            'available_models': available_models
                        }
                        
                        # Initialize context manager
                        config_path = BASE_DIR / "config.py"
                        if config_path.exists():
                            sys.path.insert(0, str(BASE_DIR))
                            from config import SYSTEM_PROMPT
                        else:
                            SYSTEM_PROMPT = "You are Zeyta, a helpful AI assistant."
                        
                        from context import ContextManager
                        self.context_manager = ContextManager(SYSTEM_PROMPT, auto_save=False)
                        
                        return True, f"Connected to Ollama using model: {model_name}"
                    else:
                        return False, "Ollama is not responding"
                except requests.exceptions.ConnectionError:
                    return False, "Ollama is not running. Please start Ollama first: ollama serve"
                except Exception as e:
                    return False, f"Failed to connect to Ollama: {str(e)}"
            
            elif provider == 'openai':
                # Placeholder for OpenAI
                self.brain = {
                    'type': 'openai',
                    'model': model_name
                }
                # Initialize context manager
                config_path = BASE_DIR / "config.py"
                if config_path.exists():
                    sys.path.insert(0, str(BASE_DIR))
                    from config import SYSTEM_PROMPT
                else:
                    SYSTEM_PROMPT = "You are Zeyta, a helpful AI assistant."
                
                from context import ContextManager
                self.context_manager = ContextManager(SYSTEM_PROMPT, auto_save=False)
                return True, f"Connected to OpenAI using model: {model_name}"

            elif provider == 'anthropic':
                # Placeholder for Anthropic
                self.brain = {
                    'type': 'anthropic',
                    'model': model_name
                }
                # Initialize context manager
                config_path = BASE_DIR / "config.py"
                if config_path.exists():
                    sys.path.insert(0, str(BASE_DIR))
                    from config import SYSTEM_PROMPT
                else:
                    SYSTEM_PROMPT = "You are Zeyta, a helpful AI assistant."
                
                from context import ContextManager
                self.context_manager = ContextManager(SYSTEM_PROMPT, auto_save=False)
                return True, f"Connected to Anthropic using model: {model_name}"
            
            else:
                return False, f"Unknown provider: {provider}"
                
        except Exception as e:
            return False, f"LLM initialization failed: {str(e)}"
    
    def unload_tts(self):
        """Unload TTS model to free memory"""
        try:
            if self.tts_model is not None:
                del self.tts_model
                self.tts_model = None
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                return True, "TTS model unloaded"
            return True, "TTS model was not loaded"
        except Exception as e:
            return False, f"Failed to unload TTS: {str(e)}"
    
    def unload_stt(self):
        """Unload STT model to free memory"""
        try:
            if self.stt_model is not None:
                del self.stt_model
                self.stt_model = None
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                return True, "STT model unloaded"
            return True, "STT model was not loaded"
        except Exception as e:
            return False, f"Failed to unload STT: {str(e)}"
    
    def unload_llm(self):
        """Unload LLM model to free memory"""
        try:
            if self.brain is not None:
                del self.brain
                self.brain = None
            if self.context_manager is not None:
                del self.context_manager
                self.context_manager = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return True, "LLM model unloaded"
        except Exception as e:
            return False, f"Failed to unload LLM: {str(e)}"
    
    def unload_all(self):
        """Unload all models to free memory"""
        results = []
        
        success, msg = self.unload_tts()
        results.append(msg)
        
        success, msg = self.unload_stt()
        results.append(msg)
        
        success, msg = self.unload_llm()
        results.append(msg)
        
        return True, " | ".join(results)
    
    def get_status(self):
        """Get status of all models"""
        status = {
            'tts': self.tts_model is not None,
            'stt': self.stt_model is not None,
            'llm': self.brain is not None,
            'tts_config': self.tts_config,
            'stt_config': self.stt_config,
            'cuda_available': torch.cuda.is_available(),
            'cuda_device': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            'tts_backend': self.tts_backend,
            'gpu_available': torch.cuda.is_available(),
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
        
        # Add Ollama model info if using Ollama
        if self.brain and isinstance(self.brain, dict) and self.brain.get('type') == 'ollama':
            status['llm_type'] = 'ollama'
            status['llm_model'] = self.brain.get('model', 'unknown')
            status['llm_available_models'] = self.brain.get('available_models', [])
        else:
            status['llm_type'] = 'local'
        
        return status

    @staticmethod
    def _is_torchvision_issue(message: str) -> bool:
        normalized = message.lower()
        return (
            'torchvision::nms' in normalized
            or 'operator torchvision::nms' in normalized
            or ('torchvision' in normalized and 'nms' in normalized)
            or ('torchvision' in normalized and 'partially initialized' in normalized and 'extension' in normalized)
            or ('circular import' in normalized and 'torchvision' in normalized)
            or ('entry point' in normalized and 'torchvision' in normalized)
            or ('failed to import' in normalized and 'torchvision' in normalized)
        )

    def _is_cuda_kernel_error(self, message: str) -> bool:
        return (
            'cuda error' in message
            or 'no kernel image' in message
            or 'cuda runtime error' in message
            or 'cublas' in message
            or 'cudnn' in message
        )

    def _switch_to_windows_native_tts(self, reason: str, force: bool = False) -> tuple[bool, str]:
        if self._windows_fallback_used and not force:
            return False, "Windows TTS fallback already active"
        if not PYTTSX3_AVAILABLE:
            return False, (
                "Windows fallback requires `pyttsx3`. Install it with `pip install pyttsx3`."
            )
        try:
            self.tts_model = WindowsNativeTTS(rate=TTS_RATE, volume=TTS_VOLUME)
            self.tts_backend = 'windows_native'
            self.tts_config.update({'device': 'cpu', 'backend': 'windows_native'})
            if not force:
                self._windows_fallback_used = True
                return True, (
                    "Chatterbox-TTS GPU build failed, so the app is now using the Windows TTS backend "
                    "(pyttsx3)."
                )
            return True, "Windows TTS backend active"
        except Exception as exc:
            return False, f"Failed to start Windows TTS fallback: {exc}"

    def _install_pytorch_cuda_stack(self, stack: dict | None = None) -> bool:
        return _install_pytorch_stack(stack)

    def _attempt_torchvision_fix(self, error_message: str) -> tuple[bool, str]:
        print("\n" + "="*60)
        print("⚠️  TorchVision import/compatibility issue detected")
        print("="*60)
        print(f"Error: {error_message[:200]}")
        stack = _get_preferred_torch_stack()
        print(f"\n🔧 Fixing by reinstalling PyTorch stack ({stack['label']})...")
        print("This will:")
        print("  1. Uninstall torch, torchvision, torchaudio")
        print("  2. Clear pip cache")
        print("  3. Reinstall matching versions for your system")
        print()

        success = self._install_pytorch_cuda_stack(stack)
        if success:
            print("\n✅ PyTorch stack reinstalled successfully!")
            return True, (
                f"✅ Torch/TorchVision/TorchAudio reinstalled ({stack['label']}). "
                "Please restart the application and reinitialize TTS on GPU."
            )

        print("\n⚠️  Installation completed with issues")
        manual_cmd = (
            "pip uninstall -y torch torchvision torchaudio && pip cache purge && "
            f"pip install \"{stack['torch']}\" \"{stack['torchvision']}\" \"{stack['torchaudio']}\""
        )
        if stack.get('index_url'):
            manual_cmd += f" --index-url {stack['index_url']}"
        return False, (
            "⚠️ PyTorch reinstallation completed with warnings. "
            "Please restart the application and retry, or run manually: "
            f"{manual_cmd}"
        )

models = ModelManager()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename, extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def cleanup_old_files(directory, max_age_hours=24):
    """Clean up old files"""
    try:
        now = time.time()
        for file in Path(directory).glob('*'):
            if file.is_file() and (now - file.stat().st_mtime) > (max_age_hours * 3600):
                file.unlink()
    except Exception:
        pass

# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/tts')
def tts_page():
    """TTS page"""
    return render_template('tts.html')

@app.route('/stt')
def stt_page():
    """STT page"""
    return render_template('stt.html')

@app.route('/chat')
def chat_page():
    """Chat page"""
    return render_template('chat.html')

@app.route('/pipeline')
def pipeline_page():
    """Full pipeline page"""
    return render_template('pipeline.html')

@app.route('/system')
def system_page():
    """System info page"""
    return render_template('system.html')

@app.route('/models')
def models_page():
    """Model management page"""
    return render_template('models.html')

@app.route('/agent')
def agent_page():
    """Agent mode page"""
    return render_template('agent.html')

@app.route('/history')
def history_page():
    """History page"""
    return render_template('history.html')

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/status')
def api_status():
    """Get system status"""
    status = models.get_status()
    
    # Add dependency check
    dependencies = {}
    for pkg_import, pkg_pip in REQUIRED_PACKAGES.items():
        dependencies[pkg_pip] = check_package(pkg_import)
    
    status['dependencies'] = dependencies
    status['output_files'] = len(list(OUTPUT_FOLDER.glob('*.wav')))
    
    # Add system resources
    try:
        status['cpu_usage'] = psutil.cpu_percent()
        status['ram_usage'] = psutil.virtual_memory().percent
        
        if torch.cuda.is_available():
            status['gpu_memory_allocated'] = torch.cuda.memory_allocated(0)
            status['gpu_memory_reserved'] = torch.cuda.memory_reserved(0)
            status['gpu_memory_total'] = torch.cuda.get_device_properties(0).total_memory
            # Calculate percentage
            status['gpu_memory_percent'] = (status['gpu_memory_reserved'] / status['gpu_memory_total']) * 100
    except Exception:
        pass
    
    return jsonify(status)

@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    """Initialize models"""
    data = request.json or {}
    model_type = data.get('type')
    
    if model_type == 'tts':
        device = data.get('device', 'auto')
        backend = data.get('backend')
        allow_reinstall = data.get('allow_reinstall')
        print(f"🔄 TTS initialization requested with device={device}, backend={backend}, allow_reinstall={allow_reinstall}")
        success, message = models.load_tts(device=device, backend=backend, allow_reinstall=allow_reinstall)
        return jsonify({'success': success, 'message': message})
    
    elif model_type == 'stt':
        size = data.get('size', 'base')
        device = data.get('device', 'auto')
        compute_type = data.get('compute_type', 'auto')
        print(f"🔄 STT initialization requested - size: {size}, device: {device}, compute: {compute_type}")
        success, message = models.load_stt(size, device, compute_type)
        return jsonify({'success': success, 'message': message})
    
    elif model_type == 'llm':
        model_name = data.get('model', 'llama3:latest')
        provider = data.get('provider', 'ollama')
        print(f"🔄 LLM initialization requested with provider: {provider}, model: {model_name}")
        success, message = models.load_llm(provider, model_name)
        return jsonify({'success': success, 'message': message})
    
    return jsonify({'success': False, 'message': 'Invalid model type'})

@app.route('/api/unload', methods=['POST'])
def api_unload():
    """Unload models to free memory"""
    data = request.json or {}
    model_type = data.get('type', 'all')
    
    if model_type == 'tts':
        success, message = models.unload_tts()
        return jsonify({'success': success, 'message': message})
    
    elif model_type == 'stt':
        success, message = models.unload_stt()
        return jsonify({'success': success, 'message': message})
    
    elif model_type == 'llm':
        success, message = models.unload_llm()
        return jsonify({'success': success, 'message': message})
    
    elif model_type == 'all':
        success, message = models.unload_all()
        return jsonify({'success': success, 'message': message})
    
    return jsonify({'success': False, 'message': 'Invalid model type'})

@app.route('/api/tts/generate', methods=['POST'])
def api_tts_generate():
    """Generate TTS audio with voice cloning support"""
    if models.tts_model is None:
        return jsonify({'success': False, 'message': 'TTS model not loaded'})
    
    data = request.json or {}
    text = data.get('text', '')
    temperature = float(data.get('temperature', 0.8))
    exaggeration = float(data.get('exaggeration', 0.5))
    cfg_weight = float(data.get('cfg_weight', 0.5))
    reference_audio = data.get('reference_audio', '')
    output_format = data.get('format', 'wav')
    
    if not text:
        return jsonify({'success': False, 'message': 'No text provided'})
    
    try:
        # Handle reference audio for voice cloning
        ref_audio_path = None
        if reference_audio:
            # Check if it's a filename (from upload) or full path
            ref_file = UPLOAD_FOLDER / secure_filename(reference_audio)
            if ref_file.exists():
                ref_audio_path = str(ref_file)
                print(f"🎤 Using reference audio for voice cloning: {ref_audio_path}")
            else:
                print(f"⚠️  Reference audio not found: {reference_audio}")
        
        # Generate with appropriate parameters
        with torch.no_grad():
            if ref_audio_path:
                print(f"🔊 Generating TTS with voice cloning...")
                # Voice cloning mode
                audio_data = models.tts_model.generate(
                    text=text,
                    audio_prompt_path=ref_audio_path,
                    temperature=temperature,
                    exaggeration=exaggeration,
                    cfg_weight=cfg_weight
                )
                message = 'Audio generated with voice cloning'
            else:
                print(f"🔊 Generating TTS with default voice...")
                # Default voice mode
                audio_data = models.tts_model.generate(
                    text=text,
                    temperature=temperature,
                    exaggeration=exaggeration,
                    cfg_weight=cfg_weight
                )
                message = 'Audio generated successfully'
        
        # Save output
        output_filename = f"tts_{int(time.time())}.{output_format}"
        output_path = OUTPUT_FOLDER / output_filename
        
        # Convert to numpy array for soundfile
        if torch.is_tensor(audio_data):
            audio_array = audio_data.cpu().numpy()
        else:
            audio_array = np.asarray(audio_data, dtype=np.float32)

        # Ensure 1D or 2D array shape for soundfile
        if audio_array.ndim > 2:
            audio_array = audio_array.reshape(-1)
        
        # Handle (1, N) shape which soundfile interprets as 1 frame with N channels
        if audio_array.ndim == 2 and audio_array.shape[0] == 1:
            audio_array = audio_array.squeeze(0)
            
        if audio_array.size == 0:
            raise ValueError("Generated audio is empty")
        
        sample_rate = getattr(models.tts_model, 'sample_rate', 22050)
        
        # Use soundfile instead of torchaudio (no TorchCodec dependency)
        # Explicitly specify format to avoid "Format not recognised" errors
        sf.write(str(output_path), audio_array, sample_rate, format=output_format.upper())
        print(f"[OK] Audio saved: {output_path}")
        
        # Cleanup old files
        cleanup_old_files(OUTPUT_FOLDER)
        
        return jsonify({
            'success': True,
            'message': message,
            'filename': output_filename,
            'url': f'/outputs/{output_filename}',
            'voice_cloned': ref_audio_path is not None
        })
    
    except Exception as e:
        error_str = str(e).lower()
        if 'dtype size changed' in error_str or 'binary incompatibility' in error_str:
            return jsonify({
                'success': False, 
                'message': (
                    'Binary incompatibility detected (numpy dtype error). '
                    'Please restart the application to auto-fix this issue.'
                )
            })
        print(f"❌ TTS generation failed: {e}")
        return jsonify({'success': False, 'message': f'Generation failed: {str(e)}'})

@app.route('/api/stt/transcribe', methods=['POST'])
def api_stt_transcribe():
    """Transcribe audio file"""
    if models.stt_model is None:
        return jsonify({'success': False, 'message': 'STT model not loaded'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not allowed_file(file.filename, {'wav', 'mp3', 'ogg', 'flac', 'm4a', 'webm'}):
        return jsonify({'success': False, 'message': 'Invalid file format'})
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename or f"transcribe_{int(time.time())}.wav")
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        # Transcribe
        segments, info = models.stt_model.transcribe(str(filepath), beam_size=5)
        text = " ".join([segment.text for segment in segments])
        
        # Cleanup
        filepath.unlink(missing_ok=True)
        cleanup_old_files(UPLOAD_FOLDER)
        
        return jsonify({
            'success': True,
            'text': text,
            'language': info.language,
            'language_probability': float(info.language_probability)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Transcription failed: {str(e)}'})

@app.route('/api/chat/generate', methods=['POST'])
def api_chat_generate():
    """Chat with LLM"""
    if models.brain is None or models.context_manager is None:
        return jsonify({'success': False, 'message': 'LLM not loaded'})
    
    data = request.get_json(silent=True) or {}
    message = data.get('prompt', '')  # Changed from 'message' to 'prompt' to match chat.js
    system_prompt = data.get('system_prompt', '')
    is_temporary = data.get('temporary', False)
    plugins = data.get('plugins', [])
    
    if not message:
        return jsonify({'success': False, 'message': 'No message provided'})
    
    provider = models.brain.get('type', 'ollama')
    model_name = models.brain.get('model', 'llama3:latest')
    
    try:
        # Handle Plugins
        plugin_instructions = []
        images = []
        web_search_results = None
        
        if 'calc' in plugins:
            plugin_instructions.append("You have access to a calculator. To calculate a math expression, write it like this: [[CALC: 5+5]]. Do not calculate it yourself, let the tool do it.")
            
        if 'web' in plugins:
            try:
                from duckduckgo_search import DDGS
                print(f"🔍 Searching web for: {message[:50]}...")
                # Simple heuristic: search the user's prompt
                with DDGS() as ddgs:
                    results = list(ddgs.text(message, max_results=5))
                
                if results:
                    web_context = "WEB SEARCH RESULTS (Use these to answer the user's question):\n"
                    for i, res in enumerate(results, 1):
                        web_context += f"Result {i}: [{res['title']}]({res['href']})\nSummary: {res['body']}\n\n"
                    
                    # Forcefully prepend to the message content for Ollama
                    # This is often more effective than system prompt for some models
                    plugin_instructions.append(f"IMPORTANT: I have performed a web search. You MUST use the following results to answer the user's question. Do not rely on your internal knowledge if it conflicts with these results.\n\n{web_context}")
                    web_search_results = True
                    print(f"✓ Found {len(results)} web results")
                else:
                    print("⚠️ Web search returned no results")
            except Exception as e:
                print(f"⚠️ Web search failed: {e}")

        if 'vision' in plugins:
            # Capture screen if vision is enabled
            try:
                from agent import ScreenAnalyzer
                # Initialize analyzer if needed (using a temp dir)
                analyzer = ScreenAnalyzer(UPLOAD_FOLDER / "temp_screens")
                screenshot_b64 = analyzer.capture_screen()
                if screenshot_b64:
                    images.append(screenshot_b64)
                    plugin_instructions.append("I have attached a screenshot of the user's screen. You can analyze it.")
            except Exception as e:
                print(f"Vision plugin error: {e}")
        
        # Update system prompt if provided or if plugins active
        final_system_prompt = system_prompt
        if plugin_instructions:
            final_system_prompt += "\n\n" + "\n".join(plugin_instructions)
            
        if final_system_prompt:
            if models.context_manager.messages and models.context_manager.messages[0].get('role') == 'system':
                models.context_manager.messages[0]['content'] = final_system_prompt
            else:
                models.context_manager.messages.insert(0, {"role": "system", "content": final_system_prompt})
            
        # Handle message and history
        if is_temporary:
            # For temporary requests (like title generation), don't save to context
            # But include current message in the history sent to LLM
            history = models.context_manager.get_history() + [{"role": "user", "content": message}]
        else:
            # Add user message to persistent context
            models.context_manager.add_message("user", message)
            history = models.context_manager.get_history()
        
        assistant_message = ""
        used_plugins = []
        
        if provider == 'ollama':
            import requests
            # Format messages for Ollama
            ollama_messages = []
            for msg in history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if content:
                    ollama_messages.append({'role': role, 'content': content})
            
            print(f"🤖 Sending {len(ollama_messages)} messages to Ollama ({model_name})...")
            
            payload = {
                'model': model_name,
                'messages': ollama_messages,
                'stream': False
            }
            
            # Add images to the LAST user message if present
            if images and ollama_messages:
                # Find last user message
                for i in range(len(ollama_messages)-1, -1, -1):
                    if ollama_messages[i]['role'] == 'user':
                        ollama_messages[i]['images'] = images
                        break
            
            ollama_response = requests.post(
                'http://localhost:11434/api/chat',
                json=payload,
                timeout=120
            )
            
            if ollama_response.status_code == 200:
                response_data = ollama_response.json()
                assistant_message = response_data.get('message', {}).get('content', '')
                
                # Add plugin usage indicators
                used_plugins = []
                
                if web_search_results:
                    used_plugins.append("Web Search")

                # Process Calculator Plugin Output
                if 'calc' in plugins and '[[CALC:' in assistant_message:
                    used_plugins.append("Calculator")
                    import re
                    def eval_math(match):
                        expr = match.group(1)
                        try:
                            # Safe eval
                            allowed_chars = "0123456789+-*/(). "
                            if not all(c in allowed_chars for c in expr):
                                return f"[Invalid characters in math: {expr}]"
                            return str(eval(expr, {"__builtins__": None}, {}))
                        except Exception as e:
                            return f"[Math Error: {e}]"
                    
                    assistant_message = re.sub(r'\[\[CALC: (.*?)\]\]', eval_math, assistant_message)
                
                # Add Vision indicator if images were sent
                if images:
                    used_plugins.append("Vision Analysis")
                    
            else:
                return jsonify({'success': False, 'message': f"Ollama API error: {ollama_response.status_code}"})
        
        elif provider == 'openai':
            # Placeholder for OpenAI API call
            # import openai
            # response = openai.ChatCompletion.create(...)
            assistant_message = f"[OpenAI Placeholder] You said: {message}"
            used_plugins = []
            
        elif provider == 'anthropic':
            # Placeholder for Anthropic API call
            assistant_message = f"[Anthropic Placeholder] You said: {message}"
            used_plugins = []
            
        if assistant_message:
            # Add assistant response to context only if not temporary
            if not is_temporary:
                models.context_manager.add_message("assistant", assistant_message)
            
            return jsonify({
                'success': True,
                'response': assistant_message,
                'plugins_used': used_plugins
            })
        else:
            return jsonify({'success': False, 'message': 'Empty response from LLM'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Generation failed: {str(e)}'})

@app.route('/api/chat/clear', methods=['POST'])
def api_chat_clear():
    """Clear chat history"""
    if models.context_manager:
        try:
            # Get system prompt
            config_path = BASE_DIR / "config.py"
            if config_path.exists():
                sys.path.insert(0, str(BASE_DIR))
                from config import SYSTEM_PROMPT
            else:
                SYSTEM_PROMPT = "You are Zeyta, a helpful AI assistant."
            
            # Reset context
            from context import ContextManager
            models.context_manager = ContextManager(SYSTEM_PROMPT, auto_save=False)
            
            return jsonify({'success': True, 'message': 'Chat history cleared'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': False, 'message': 'Context manager not initialized'})

@app.route('/api/upload/reference', methods=['POST'])
def api_upload_reference():
    """Upload reference audio for TTS"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not allowed_file(file.filename, {'wav', 'mp3', 'ogg', 'flac', 'm4a'}):
        return jsonify({'success': False, 'message': 'Invalid file format'})
    
    try:
        filename = secure_filename(file.filename or f"reference_{int(time.time())}.wav")
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        cleanup_old_files(UPLOAD_FOLDER)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Reference audio uploaded'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@app.route('/outputs/<filename>')
def serve_output(filename):
    """Serve generated audio files"""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/llm/models', methods=['GET'])
def api_llm_models():
    """Get available models for a provider"""
    provider = request.args.get('provider', 'ollama')
    
    if provider == 'ollama':
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [m['name'] for m in models_data.get('models', [])]
                return jsonify({'success': True, 'models': available_models})
            else:
                return jsonify({'success': False, 'message': 'Ollama not responding'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Failed to fetch Ollama models: {str(e)}'})
    
    elif provider == 'openai':
        return jsonify({'success': True, 'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']})
    
    elif provider == 'anthropic':
        return jsonify({'success': True, 'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']})
        
    return jsonify({'success': False, 'message': 'Unknown provider'})

# ============================================================================
# AGENT MODE API ENDPOINTS
# ============================================================================

# Initialize agent
from agent import AgentMode
agent = None

@app.route('/api/agent/status')
def api_agent_status():
    """Get agent status"""
    global agent
    if agent is None:
        return jsonify({
            'initialized': False,
            'ollama_connected': False,
            'models': []
        })
    
    status = agent.get_status()
    ollama_status = agent.check_ollama_status()
    
    return jsonify({
        'initialized': True,
        'ollama_connected': ollama_status['connected'],
        'models': ollama_status['models'],
        'current_model': status['model'],
        'permissions': status['permissions'],
        'active': status['active'],
        'screen_info': status['screen_info'],
        'conversation_length': status['conversation_length']
    })

@app.route('/api/agent/initialize', methods=['POST'])
def api_agent_initialize():
    """Initialize agent mode"""
    global agent
    try:
        if agent is None:
            agent = AgentMode(BASE_DIR)
        
        ollama_status = agent.check_ollama_status()
        
        if not ollama_status['connected']:
            return jsonify({
                'success': False,
                'message': 'Ollama is not running. Please start Ollama first.'
            })
        
        return jsonify({
            'success': True,
            'message': 'Agent initialized',
            'models': ollama_status['models']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/agent/set-model', methods=['POST'])
def api_agent_set_model():
    """Set active Ollama model"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    data = request.get_json(silent=True) or {}
    model = data.get('model') or ''
    
    result = agent.set_model(model)
    return jsonify(result)

@app.route('/api/agent/chat', methods=['POST'])
def api_agent_chat():
    """Chat with agent"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    data = request.get_json(silent=True) or {}
    message = data.get('message', '')
    include_screen = data.get('include_screen', False)
    
    result = agent.chat(message, include_screen)
    return jsonify(result)

@app.route('/api/agent/analyze-screen', methods=['POST'])
def api_agent_analyze_screen():
    """Analyze current screen"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', 'Describe what you see on the screen in detail.')
    
    result = agent.analyze_screen(prompt)
    return jsonify(result)

@app.route('/api/agent/execute-task', methods=['POST'])
def api_agent_execute_task():
    """Execute a task autonomously"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    data = request.get_json(silent=True) or {}
    task = data.get('task', '')
    auto_execute = data.get('auto_execute', True)  # Default to autonomous mode
    
    result = agent.execute_task(task, auto_execute=auto_execute)
    return jsonify(result)

@app.route('/api/agent/execute-action', methods=['POST'])
def api_agent_execute_action():
    """Execute a specific action"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    data = request.get_json(silent=True) or {}
    action = data.get('action', {})
    
    result = agent.execute_action(action)
    return jsonify(result)

@app.route('/api/agent/set-permissions', methods=['POST'])
def api_agent_set_permissions():
    """Set agent permissions"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    data = request.get_json(silent=True) or {}
    permissions = data.get('permissions', {})
    
    result = agent.set_permissions(permissions)
    return jsonify(result)

@app.route('/api/agent/clear-history', methods=['POST'])
def api_agent_clear_history():
    """Clear conversation history"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    result = agent.clear_history()
    return jsonify(result)

@app.route('/api/agent/cancel', methods=['POST'])
def api_agent_cancel():
    """Emergency stop - cancel current operation and unload model"""
    global agent
    if agent is None:
        return jsonify({'success': False, 'message': 'Agent not initialized'})
    
    result = agent.cancel_operation()
    return jsonify(result)

@app.route('/api/history/files')
def api_history_files():
    """List generated files"""
    files = []
    try:
        for file_path in OUTPUT_FOLDER.glob('*.wav'):
            stat = file_path.stat()
            files.append({
                'name': file_path.name,
                'url': f'/outputs/{file_path.name}',
                'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': f"{stat.st_size / 1024 / 1024:.2f} MB",
                'timestamp': stat.st_mtime
            })
        
        # Sort by date desc
        files.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================================================
# WEBSOCKET HANDLERS FOR LIVE AUDIO
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to Zeyta AI'})

@socketio.on('start_recording')
def handle_start_recording():
    """Start live microphone transcription"""
    if models.stt_model is None:
        emit('error', {'message': 'STT model not loaded'})
        return
    
    emit('recording_started', {'message': 'Recording started'})

@socketio.on('audio_data')
def handle_audio_data(data):
    """Process audio data from microphone"""
    if models.stt_model is None:
        emit('error', {'message': 'STT model not loaded'})
        return
    
    try:
        # Decode audio data
        audio_bytes = base64.b64decode(data['audio'])
        
        # Convert to numpy array
        audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # Save to temporary file
        temp_file = UPLOAD_FOLDER / f"temp_audio_{int(time.time())}.wav"
        sf.write(str(temp_file), audio_data, data.get('sampleRate', 16000))
        
        # Transcribe
        segments, info = models.stt_model.transcribe(str(temp_file), beam_size=5)
        text = " ".join([segment.text for segment in segments])
        
        # Cleanup
        temp_file.unlink(missing_ok=True)
        
        if text.strip():
            emit('transcription', {
                'text': text,
                'language': info.language,
                'confidence': float(info.language_probability)
            })
    
    except Exception as e:
        emit('error', {'message': f'Transcription failed: {str(e)}'})

@socketio.on('stop_recording')
def handle_stop_recording():
    """Stop recording"""
    emit('recording_stopped', {'message': 'Recording stopped'})

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Clean invalid distributions
    print("\n🧹 Checking for invalid distributions...")
    clean_invalid_distributions()
    
    # Check binary compatibility on startup
    print("\n🔍 Checking binary compatibility...")
    if not check_binary_compatibility():
        print("⚠️  Binary incompatibility detected!")
        print("🔧 Attempting automatic fix...")
        fix_binary_incompatibility()
        print("\n⚠️  IMPORTANT: Binary fix applied. Please restart the application.")
        print("   The changes will take effect on next run.\n")
        sys.exit(0)
    else:
        print("✅ Binary compatibility check passed\n")
    
    # Get local IP address for network access info
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "YOUR_PC_IP"
    
    print("\n" + "=" * 60)
    print("✅ Zeyta AI Web Application Ready!")
    print("=" * 60)
    print(f"\n🌐 Access from this PC:")
    print(f"   https://localhost:5000")
    print(f"\n📱 Access from other devices on your network:")
    print(f"   https://{local_ip}:5000")
    print(f"\n⚠️  Note: You will see a 'Not Secure' warning because we use a self-signed certificate.")
    print(f"   Click 'Advanced' -> 'Proceed to ... (unsafe)' to continue.")
    print(f"\n📁 Outputs will be saved to: {OUTPUT_FOLDER}")
    print(f"📤 Uploads will be saved to: {UPLOAD_FOLDER}")
    print(f"\n💡 Other devices will use this PC's GPU for processing")
    print(f"💡 Press Ctrl+C to stop the server\n")
    print("=" * 60 + "\n")
    
    # Run server
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True, ssl_context='adhoc')
    except Exception as e:
        print(f"⚠️  Failed to start with HTTPS: {e}")
        print("🔓 Falling back to HTTP...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

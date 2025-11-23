#!/usr/bin/env python3
"""
Check interpreter info and whether chatterbox/tensor availability are present.
Run like:
  python check_interpreter.py
"""
import sys
import os
import importlib.util

print('Python:', sys.executable)
print('Python Version:', sys.version.replace('\n', ' '))
print('CHATTERBOX_PYTHON env:', os.environ.get('CHATTERBOX_PYTHON'))

# Which pip is used by this Python
try:
    import subprocess
    pip_info = subprocess.run([sys.executable, '-m', 'pip', '-V'], capture_output=True, text=True)
    print('pip info:', pip_info.stdout.strip())
except Exception as e:
    print('pip info failed:', e)

# Check chatterbox import
try:
    spec = importlib.util.find_spec('chatterbox')
    print('Chatterbox installed:', spec is not None)
except Exception as e:
    print('Chatterbox import test raised:', e)

# Check torch
try:
    import torch
    print('Torch:', torch.__version__, 'CUDA available:', torch.cuda.is_available())
    try:
        props = torch.cuda.get_device_properties(0)
        print('GPU device name:', props.name, 'compute capability:', props.major, '.', props.minor)
    except Exception as e:
        print('GPU properties check failed:', e)
except Exception as e:
    print('Torch import failed:', e)

# Show where importer would resolve chatterbox
try:
    import importlib
    if importlib.util.find_spec('chatterbox'):
        import chatterbox
        print('Chatterbox module path:', chatterbox.__file__)
except Exception:
    pass

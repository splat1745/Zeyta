"""
Chatterbox TTS Loader
=====================

Loads and manages Chatterbox TTS model directly from a dedicated venv.
Ensures model stays in memory and optimizations are preserved.
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple

# Try to detect Chatterbox venv
CHATTERBOX_PYTHON = os.getenv('CHATTERBOX_PYTHON')
if CHATTERBOX_PYTHON:
    CHATTERBOX_PYTHON = str(Path(CHATTERBOX_PYTHON).absolute())

# Fallback: common locations
COMMON_VENV_PATHS = [
    Path(__file__).parent.parent / 'venv_chatterbox' / 'Scripts' / 'python.exe',
    Path.cwd() / 'venv_chatterbox' / 'Scripts' / 'python.exe',
    Path.home() / 'venv_chatterbox' / 'Scripts' / 'python.exe',
    Path(__file__).parent.parent.parent / 'venv_chatterbox' / 'Scripts' / 'python.exe',  # One more level up
]

def find_chatterbox_python() -> Optional[str]:
    """Find Python interpreter with Chatterbox installed."""
    # Explicit setting
    if CHATTERBOX_PYTHON and Path(CHATTERBOX_PYTHON).exists():
        return CHATTERBOX_PYTHON
    
    # Check common locations
    for path in COMMON_VENV_PATHS:
        if path.exists():
            # Verify Chatterbox is installed
            result = subprocess.run(
                [str(path), '-c', 'import chatterbox'],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                return str(path)
    
    # If not found in common locations, try to find any venv with chatterbox
    print("[DEBUG] Searching for venv_chatterbox in current directory and parent directories...")
    current = Path.cwd()
    for _ in range(3):  # Search up to 3 levels up
        venv_path = current / 'venv_chatterbox' / 'Scripts' / 'python.exe'
        if venv_path.exists():
            result = subprocess.run(
                [str(venv_path), '-c', 'import chatterbox'],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                return str(venv_path)
        current = current.parent
    
    return None


class ChatterboxLoader:
    """In-process loader for Chatterbox with optimizations and voice cloning."""
    
    def __init__(self):
        self.model = None
        self.sample_rate = 22050
        self.device = 'cuda'
        self.is_loaded = False
        self._voice_cache = {}  # Cache for voice embeddings
    
    def load_from_venv(self, python_path: Optional[str] = None) -> bool:
        """Load Chatterbox using dedicated venv."""
        if python_path is None:
            python_path = find_chatterbox_python()
        
        if python_path is None:
            print("[CHATTERBOX] No Python interpreter with Chatterbox found")
            print("[CHATTERBOX] Run: .\\setup_chatterbox_venv.ps1")
            return False
        
        print(f"[CHATTERBOX] Using: {python_path}")
        
        # Try in-process import first
        try:
            # This only works if current venv has chatterbox
            from chatterbox import ChatterboxTTS
            import torch
            
            print("[CHATTERBOX] Loading model...")
            device = torch.device('cuda')
            self.model = ChatterboxTTS.from_pretrained(device=device)
            self.sample_rate = getattr(self.model, 'sample_rate', 22050)
            self.is_loaded = True
            print("[CHATTERBOX] Model loaded successfully")
            return True
            
        except ImportError:
            # Chatterbox not in current venv, skip loading
            # (Will use subprocess if needed)
            print("[CHATTERBOX] Not available in current venv")
            return False
        except Exception as e:
            print(f"[CHATTERBOX] Failed to load in-process: {e}")
            return False
    
    def extract_voice(self, audio_path: str) -> Optional[object]:
        """Extract voice embedding from reference audio for cloning."""
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Chatterbox model not loaded")
        
        # Check cache first
        if audio_path in self._voice_cache:
            print(f"[VOICE] Using cached embedding from {audio_path}")
            return self._voice_cache[audio_path]
        
        import torch
        import soundfile as sf
        import scipy.signal
        from pathlib import Path
        
        try:
            audio_path = str(Path(audio_path).absolute())
            
            if not Path(audio_path).exists():
                print(f"[VOICE] Audio file not found: {audio_path}")
                return None
            
            print(f"[VOICE] Extracting embedding from: {audio_path}")
            
            # Load audio using soundfile instead of torchaudio (avoids torchcodec)
            audio_data, sr = sf.read(audio_path)
            
            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Resample if needed
            if sr != self.sample_rate:
                num_samples = int(len(audio_data) * self.sample_rate / sr)
                audio_data = scipy.signal.resample(audio_data, num_samples)
            
            # Convert to tensor
            waveform = torch.from_numpy(audio_data).float().to(self.device)
            if waveform.dim() == 1:
                waveform = waveform.unsqueeze(0)  # Add channel dimension
            
            # Extract voice embedding using the model
            with torch.inference_mode():
                # Try to extract voice embedding
                if hasattr(self.model, 'extract_voice_embedding'):
                    voice_embedding = self.model.extract_voice_embedding(waveform)
                elif hasattr(self.model, 'encode_voice'):
                    voice_embedding = self.model.encode_voice(waveform)
                else:
                    # Fallback: use audio as prompt directly
                    print(f"[VOICE] Model doesn't support embedding extraction, will use audio directly")
                    voice_embedding = waveform
            
            # Cache the embedding
            self._voice_cache[audio_path] = voice_embedding
            print(f"[VOICE] Embedding cached for faster subsequent use")
            
            return voice_embedding
            
        except Exception as e:
            print(f"[VOICE] Failed to extract embedding: {e}")
            return None
    
    def generate(self, text: str, voice_cloning_audio: Optional[str] = None, **kwargs) -> Tuple:
        """Generate audio with optional voice cloning."""
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Chatterbox model not loaded")
        
        import torch
        import numpy as np
        
        # Handle voice cloning
        if voice_cloning_audio:
            voice_embedding = self.extract_voice(voice_cloning_audio)
            if voice_embedding is not None:
                # Chatterbox expects audio_prompt_path, not audio_prompt
                # Pass the file path directly
                kwargs['audio_prompt_path'] = voice_cloning_audio
                print(f"[VOICE] Using voice clone from: {voice_cloning_audio}")
        
        with torch.inference_mode():
            audio = self.model.generate(text, **kwargs)
        
        # Convert to numpy
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        
        arr = np.asarray(audio).squeeze()
        if arr.dtype == np.int16:
            arr = arr.astype(np.float32) / 32768.0
        elif arr.dtype == np.int32:
            arr = arr.astype(np.float32) / 2147483648.0
        else:
            arr = arr.astype(np.float32)
        
        if arr.size == 0:
            arr = np.zeros(self.sample_rate // 2, dtype=np.float32)
        
        return arr, self.sample_rate
    
    def clear_voice_cache(self):
        """Clear cached voice embeddings."""
        self._voice_cache.clear()
        print("[VOICE] Cache cleared")


def get_chatterbox_loader() -> ChatterboxLoader:
    """Get global Chatterbox loader instance."""
    global _chatterbox_loader
    if '_chatterbox_loader' not in globals():
        _chatterbox_loader = ChatterboxLoader()
    return _chatterbox_loader

# Quick Start - RTX 50-Series TTS Optimization

## Installation (5 minutes)

```powershell
# 1. Install PyTorch nightly with CUDA 12.4+
pip install --pre torch torchaudio torchvision --index-url https://download.pytorch.org/whl/nightly/cu124

# 2. Install dependencies
pip install triton psutil soundfile piper-tts chatterbox-tts

# 3. Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

## Quick Test (1 minute)

```powershell
# Run optimized TTS test
python tts_test_rtx50.py

# Output files created:
# - output_fast_rtx50.wav (Piper, fastest)
# - output_cinematic_rtx50.wav (Chatterbox, highest quality)
# - output_auto_rtx50.wav (Automatic selection)
```

## Benchmark (3 minutes)

```powershell
# Compare baseline vs optimized
python benchmark_rtx50.py

# Shows speedup, throughput, and time saved
```

## Usage in Your Code

```python
# Import optimized TTS
from tts_test_rtx50 import speak

# Generate speech (automatically optimized)
speak("Hello world", mode="cinematic", outfile="output.wav")

# With voice cloning
speak(
    "This is a test",
    mode="cinematic",
    audio_prompt="reference.wav",
    outfile="cloned.wav"
)
```

## What's Optimized

✅ **PyTorch nightly** - RTX 50-series compatibility  
✅ **Hybrid precision** - FP32 for STFT, BF16 for models  
✅ **CUDA graphs** - Zero Python overhead  
✅ **Flash-attention** - Faster attention mechanism  
✅ **torch.compile** - Kernel fusion with reduce-overhead  
✅ **Thread optimization** - Physical cores only  
✅ **Weight preloading** - RAM → GPU before inference  
✅ **Pinned memory** - Faster CPU-GPU transfers  
✅ **Preallocated buffers** - No runtime allocation  
✅ **Batch preprocessing** - Minimize transfers  

## Expected Performance

| GPU | Speedup vs Baseline | Throughput (chars/sec) |
|-----|---------------------|------------------------|
| RTX 50-series | 2-4x | 300-600 |
| RTX 40-series | 1.5-3x | 200-400 |
| RTX 30-series | 1.2-2x | 150-300 |

## Troubleshooting

**Issue:** Import errors  
**Fix:** `pip install -r requirements.txt`

**Issue:** CUDA out of memory  
**Fix:** Set `PREALLOCATE_BUFFERS = False` in tts_test_rtx50.py

**Issue:** Slow first run  
**Expected:** Includes compilation, graph capture. Subsequent runs are fast.

**Issue:** Audio quality issues  
**Fix:** Hybrid precision prevents this - STFT stays in FP32

## Files Created

```
tts_test_rtx50.py          - Optimized TTS engine ⭐
benchmark_rtx50.py         - Benchmark script
documentation/RTX50_OPTIMIZATION_GUIDE.md - Full guide
```

## Next Steps

1. ✅ Run `python tts_test_rtx50.py` to verify
2. ✅ Run `python benchmark_rtx50.py` to measure speedup
3. ✅ Read `RTX50_OPTIMIZATION_GUIDE.md` for details
4. ✅ Integrate optimized TTS into your application

## Support

For issues or questions, see:
- RTX50_OPTIMIZATION_GUIDE.md (detailed documentation)
- PyTorch forums (torch.compile, CUDA graphs)
- NVIDIA Developer forums (RTX 50-series specific)

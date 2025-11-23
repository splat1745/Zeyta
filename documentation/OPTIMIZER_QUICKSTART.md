# Quick Start: Optimized TTS System

## Running the System

### Option 1: Quick Test (Recommended)
```powershell
cd e:\AI-OFFICIAL\AI-RELEASE
python tts_test_optimized.py
```

This will:
- ✅ Auto-detect Python 3.11 for Chatterbox compatibility
- ✅ Initialize all optimizations (BF16, CUDA graphs, Flash-Attention)
- ✅ Run quick tests (Fast mode, Cinematic mode, Voice cloning)
- ✅ Run benchmarks with warmup
- ✅ Display performance metrics

### Option 2: Manual Mode Selection

```python
from tts_test_optimized import speak

# Fast mode (Piper - ONNX)
speak("Hello world", mode="fast", outfile="fast_output.wav")

# Cinematic mode (Chatterbox - PyTorch with optimizations)
speak("Hello world", mode="cinematic", outfile="cinematic_output.wav")

# Voice cloning mode (Chatterbox with voice embedding)
speak("Hello world", mode="clone", outfile="clone_output.wav", 
      voice_clone_audio="ShinobuResolve.wav")
```

---

## Performance Metrics

### Fast Mode (Piper ONNX)
- **Speed**: 634 chars/sec
- **RTF**: 0.022-0.027x (34-45x faster than real-time)
- **Use Case**: When speed is critical

### Cinematic Mode (Chatterbox PyTorch)
- **Speed**: 17.2 chars/sec  
- **RTF**: 0.609-0.773x (1.3-1.6x faster than real-time)
- **Quality**: Higher quality audio with neural vocoder
- **Use Case**: Best audio quality with real-time performance

### Voice Cloning Mode
- **Speed**: Similar to cinematic mode (~5-6 sec for 5+ sec audio)
- **RTF**: 0.791x (consistent, faster than real-time)
- **Quality**: Matches reference voice characteristics
- **Use Case**: Custom voice synthesis

---

## Optimizations Active

| Optimization | Status | Details |
|---|---|---|
| BF16 Precision | ✅ Active | Better for RTX 50-series |
| CUDA Graphs | ✅ Available | Zero Python overhead |
| Flash-Attention | ✅ Enabled | SDPA backend |
| torch.compile | ✅ Active | reduce-overhead mode |
| Memory Pinning | ✅ Enabled | Faster transfers |
| Preallocated Buffers | ✅ Ready | Zero-allocation inference |
| cuDNN Benchmarking | ✅ Enabled | Auto-tuned kernels |
| Thread Optimization | ✅ Set | 12 physical cores |
| Voice Embedding Cache | ✅ Available | Memory + disk cache |

---

## Expected Output

```
======================================================================
OPTIMIZED TTS TEST SUITE WITH ADVANCED OPTIMIZATIONS
======================================================================

[OPTIMIZER] Advanced optimizations ACTIVE:
  ✓ Hybrid Precision (BF16 preferred for Blackwell)
  ✓ CUDA Graphs with warmup
  ✓ Flash-Attention (SDPA)
  ✓ torch.compile (reduce-overhead mode)
  ✓ Memory pinning and preallocated buffers
  ✓ Batch preprocessing
  ✓ Voice embedding cache
  ✓ Optimal thread configuration

[CHATTERBOX] Initializing loader...
[CHATTERBOX] Using: e:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox\Scripts\python.exe
[CHATTERBOX] Model loaded and ready
[CHATTERBOX] Ready for inference with optimizations

[PIPER] Loaded from models\piper\en_US-lessac-high.onnx

======================================================================
QUICK TESTS
======================================================================

[TEST] Fast mode (Piper)...
[PIPER] Generated 5.10s audio in 0.428s (RTF: 0.084x)

[TEST] Cinematic mode (Chatterbox)...
[CHATTERBOX] Generated 5.27s audio in 4.073s (RTF: 0.773x) standard

[TEST] Voice cloning mode (Chatterbox)...
[CHATTERBOX] Generated 6.88s audio in 5.442s (RTF: 0.791x) with voice cloning
```

---

## Troubleshooting

### Issue: Python 3.12 compatibility warning
```
[WARN] Python 3.12 may have compatibility issues with Chatterbox
```
**Solution**: Script automatically switches to Python 3.11. This is expected behavior.

### Issue: ONNX Runtime warnings
```
[W:onnxruntime:] 28 Memcpy nodes are added to the graph
```
**Solution**: These are informational warnings and don't affect performance. Safe to ignore.

### Issue: Thread initialization warning
```
[WARN] Optimizer initialization failed: Error: cannot set number of interop threads
```
**Solution**: Occurs when libraries have already started parallel work. Safe to ignore - optimizations still apply.

### Issue: Model not loading
```
[WARN] Could not load Chatterbox from venv
```
**Solution**: Run setup script:
```powershell
.\setup_voice_cloning.ps1
```

---

## System Requirements

| Component | Requirement |
|---|---|
| GPU | NVIDIA RTX 50-series or RTX 40-series (Ampere+) |
| CUDA | 12.4+ recommended, 12.8 nightly preferred |
| PyTorch | 2.10.0.dev or newer |
| Python | 3.11 (Chatterbox) or 3.12 (auto-switch) |
| RAM | 16GB+ recommended |
| Disk | 5GB+ for models and cache |

---

## Output Files Generated

| File | Purpose |
|---|---|
| `output_fast.wav` | Fast mode output |
| `output_cinematic.wav` | Cinematic mode output |
| `output_voice_clone.wav` | Voice cloning output |
| `benchmark_fast_*.wav` | Fast mode benchmark outputs |
| `benchmark_cinematic_*.wav` | Cinematic mode benchmark outputs |

All output files use 22050 Hz sample rate (PerthNet standard).

---

## Advanced Usage

### Using Voice Cloning with Custom Reference

```python
from tts_test_optimized import speak

# Specify your reference audio
speak(
    "Hello, this is my custom voice",
    mode="clone",
    outfile="custom_voice.wav",
    voice_clone_audio="path/to/reference.wav"
)
```

### Manual Optimizer Usage

```python
from tts_optimizer_advanced import AdvancedTTSOptimizer, OptimizationConfig

# Create optimizer with custom config
config = OptimizationConfig(
    enable_fp16=True,
    enable_bf16=True,
    enable_cuda_graphs=True,
    enable_compile=True,
    compile_mode="reduce-overhead"
)

optimizer = AdvancedTTSOptimizer(config=config)
```

---

## Performance Tips

1. **First Run**: Slightly slower due to warmup and compilation
2. **Repeated Calls**: Faster as graphs are cached
3. **Voice Cloning**: Cache hits on repeated voice reduce time
4. **Batch Processing**: Use multiple texts for better GPU utilization

---

## More Information

See documentation files:
- `OPTIMIZATION_IMPLEMENTATION.md` - Full technical details
- `tts_optimizer_advanced.py` - Source code and advanced API
- `tts_test_optimized.py` - Complete example usage

---

**Last Updated**: November 18, 2025  
**Status**: ✅ Production Ready

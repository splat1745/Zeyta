# Chatterbox Setup and Optimization Guide

## Quick Start

### Step 1: Setup Chatterbox Virtual Environment

Run the dedicated Chatterbox venv setup:

```powershell
.\setup_chatterbox_venv.ps1
```

This creates a separate Python environment with compatible versions:
- PyTorch 2.1.0 (compatible with Chatterbox)
- Chatterbox TTS
- Required audio libraries

### Step 2: Set Environment Variable (Optional but Recommended)

To use Chatterbox in tests, set the Python path:

```powershell
# Temporary (current session only)
$env:CHATTERBOX_PYTHON = "C:\full\path\to\venv_chatterbox\Scripts\python.exe"

# Permanent (add to PowerShell profile)
# Edit: $PROFILE
# Add: $env:CHATTERBOX_PYTHON = "C:\full\path\to\venv_chatterbox\Scripts\python.exe"
```

### Step 3: Run Tests

Run the optimized test suite:

```powershell
python tts_test_optimized.py
```

The script will:
1. Try to load Chatterbox from the dedicated venv (if available)
2. Load Piper TTS (always available if installed)
3. Run performance benchmarks on both engines
4. Report RTF (Real-Time Factor) and throughput metrics

## Architecture

### Direct Loading (Preferred)
When Chatterbox is found in a venv, it's loaded directly in-process:
- No subprocess overhead
- Full optimization pipeline applied
- Model stays in memory
- Minimal latency

### Chatterbox Loader (`scripts/chatterbox_loader.py`)
The ChatterboxLoader class:
- Searches for Python with Chatterbox installed
- Attempts in-process loading first
- Manages model lifecycle
- Handles dtype conversions

## Performance Expectations

### RTX 5070 Ti (RTX 50-Series)
- **Piper**: 0.02-0.04 RTF (25-50x realtime)
- **Chatterbox**: 0.1-0.2 RTF (5-10x realtime) with full optimizations

### Key Optimizations Applied
- Hybrid precision (FP32 for STFT, FP16/BF16 for models)
- Flash-attention via SDPA
- torch.compile with reduce-overhead mode
- CUDA graphs after warmup
- Memory pinning and preallocated buffers
- Batch preprocessing
- Physical core thread optimization

## Troubleshooting

### Issue: Chatterbox not found
**Solution**: 
1. Run `.\setup_chatterbox_venv.ps1`
2. Set `$env:CHATTERBOX_PYTHON` environment variable
3. Check venv exists at `venv_chatterbox`

### Issue: NumPy/ABI errors
**Solution**: 
- The dedicated venv isolates versions
- Never mix Chatterbox with main venv PyTorch
- Each has compatible versions:
  - Main venv: PyTorch 2.10 nightly (cu128)
  - Chatterbox venv: PyTorch 2.1 (cu121)

### Issue: Low RTF values
**Solution**: 
- This is good! Lower RTF means faster generation
- RTF = Time to generate / Audio duration
- RTF < 0.1 means 10x faster than realtime

### Issue: CUDA memory errors
**Solutions**:
1. Reduce batch size in OptimizationConfig
2. Disable buffer preallocation: `preallocate_buffers=False`
3. Check available GPU memory: `nvidia-smi`

## Configuration

### Enable/Disable Optimizations

Edit `OptimizationConfig` in `tts_test_optimized.py`:

```python
config = OptimizationConfig(
    enable_fp16=True,              # Use FP16 precision
    enable_bf16=True,              # Prefer BF16 (better)
    enable_flash_attention=True,   # Flash-attention
    enable_cuda_graphs=True,       # CUDA graphs
    enable_compile=True,           # torch.compile
    compile_mode="reduce-overhead", # Fastest
    pin_memory=True,               # Pin GPU memory
    preload_weights=True,          # Preload weights
    batch_preprocessing=True,      # Batch preprocessing
    use_inference_mode=True,       # Inference mode
    num_threads=12,                # CPU threads (auto-detected)
    preallocate_buffers=True       # Buffer pool
)
```

## Performance Monitoring

The test script provides detailed metrics:
- **Time**: Generation time in seconds
- **RTF**: Real-Time Factor (lower is faster)
- **Throughput**: Characters/words per second
- **GPU**: NVIDIA GPU usage (nvidia-smi)

Example output:
```
======================================================================
RESULTS: FAST
======================================================================
Generation Time:
  Average: 0.290s ± 0.193s
  Best: 0.166s
  Worst: 0.674s

Real-Time Factor (RTF):
  Average: 0.037x
  Best: 0.021x

Throughput:
  465.3 chars/sec
  93.1 words/sec
```

## Development

### Adding New TTS Engines

1. Create loader class (like `ChatterboxLoader`)
2. Implement `generate()` method
3. Add to test script initialization
4. Define in benchmark section

### Custom Optimizations

See `TTS_OPTIMIZATION_GUIDE.md` for:
- Profiling with torch.profiler
- Custom optimization pipelines
- CUDA graph debugging
- Advanced configuration

## Files

| File | Purpose |
|------|---------|
| `tts_test_optimized.py` | Main test suite |
| `tts_optimizer_advanced.py` | Advanced optimizer implementation |
| `scripts/chatterbox_loader.py` | Chatterbox loader |
| `setup_chatterbox_venv.ps1` | Venv setup script |
| `install_optimized.ps1` | Full optimization setup |
| `TTS_OPTIMIZATION_GUIDE.md` | Comprehensive guide |

## License

Same as parent project.

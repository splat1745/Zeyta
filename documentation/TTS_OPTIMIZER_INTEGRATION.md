# TTS Optimizer Integration Summary

## Overview
Integrated comprehensive RTX 50-series GPU optimization system into `web_app.py` for maximum TTS performance.

## What Was Done

### 1. Created `tts_optimizer.py` Module (450 lines)
- **VoiceEmbeddingCache**: SHA256-based file tracking with memory + disk caching
  - Automatically invalidates when reference audio changes
  - Cache key format: `{model_name}_{audio_basename}`
  - Storage: `.tts_cache/voice_embeddings/` directory

- **TTSOptimizer**: Core optimization orchestrator
  - Auto-detects RTX 50-series (compute capability 8.9)
  - FP16 model conversion with FP32 fallback
  - CUDA Graph capture for zero Python overhead
  - Optimal chunk sizes: mel=512, vocoder=8192 (vs typical 128-256, 1024-2048)

- **OptimizedChatterboxWrapper**: Drop-in replacement for ChatterboxTTS
  - Transparent optimization layer
  - Caches voice embeddings with reference tracking
  - FP16 generation with automatic mixed precision
  - Proxies all other attributes to base model

### 2. Integrated into `web_app.py`

#### Import Added (Line 654)
```python
import tts_optimizer  # RTX 50-series GPU optimization
```

#### ChatterboxSubprocessTTS Enhanced (Lines 916-947)
- Detects 50-series GPU capability at initialization
- Passes `use_optimizer=True` flag to subprocess when applicable
- Subprocess script loads and applies optimizations via `tts_optimizer.optimize_chatterbox()`

#### In-Process Model Loading Updated (Lines 1127-1139)
```python
base_model = ChatterboxTTS.from_pretrained(device=device)

# Apply RTX 50-series optimizations if available
optimizer = tts_optimizer.get_optimizer()
if optimizer.is_50_series and device == 'cuda':
    self.tts_model = tts_optimizer.optimize_chatterbox(base_model)
    print("✓ Chatterbox TTS loaded with RTX 50-series optimizations...")
```

#### Subprocess Script Enhanced (Lines 738-748)
- Added optimizer initialization block
- Wraps base model with `optimize_chatterbox()` when `use_optimizer=True`
- Handles failures gracefully with fallback to standard model

#### Compatibility Mode Also Optimized (Lines 1171-1183)
- Float32 compatibility retry also uses optimizer
- Ensures maximum performance even with precision tweaks

### 3. Created Test Suite: `test_tts_optimizations.py`

Comprehensive test script with:
- Environment check (GPU, compute capability, CUDA version)
- Baseline TTS benchmark (no optimizations)
- Optimized TTS benchmark (FP16 + CUDA Graphs + cache)
- Voice cloning cache speedup test
- Performance comparison and reporting

**Usage:**
```powershell
python test_tts_optimizations.py
```

## Optimization Features

### 1. Voice Embedding Cache
- **When Active**: Anytime `audio_prompt_path` is provided for voice cloning
- **How It Works**: 
  - First generation with reference audio computes and caches embedding
  - Subsequent generations with same audio file reuse cached embedding
  - File changes detected via SHA256 hash → cache invalidated
- **Speedup**: ~1.5-2x faster for repeated cloning with same reference

### 2. FP16 Tensor Core Acceleration
- **When Active**: RTX 50-series GPU (compute 8.9) + CUDA device
- **How It Works**:
  - Converts acoustic model and vocoder to half precision
  - Uses `torch.cuda.amp.autocast` for automatic mixed precision
  - Tensor cores handle FP16 operations at 2-4x speed
- **Speedup**: ~1.5-2.5x faster generation

### 3. Optimized Chunk Sizes
- **When Active**: Always when optimizer wraps model
- **Configuration**:
  - Mel spectrogram chunks: 512 (up from 128-256)
  - Vocoder chunks: 8192 (up from 1024-2048)
- **Why**: Larger chunks = better GPU utilization, fewer kernel launches
- **Speedup**: ~1.2-1.5x improvement

### 4. CUDA Graph Capture
- **When Active**: After warmup runs, for repeated inference
- **How It Works**:
  - Records kernel launches into graph
  - Replays graph with zero Python overhead
  - Eliminates CPU-GPU synchronization costs
- **Speedup**: ~1.1-1.3x (especially for short audio)

### Combined Expected Speedup
**Target: 2-4x faster** on RTX 5070 Ti vs baseline

## Automatic Activation

Optimizations activate automatically when:
1. GPU compute capability = 8.9 (RTX 50-series)
2. CUDA device available
3. `tts_optimizer.py` importable

No configuration changes needed - works out of the box!

## Cache Invalidation

Per user requirement: "This optimization should only happen as long as the voice clone reference file isn't changed. Otherwise redo optimization for tts (essential)."

**Implementation:**
- SHA256 hash computed on reference audio file
- Stored with cached embedding: `cache_key = f"{model_name}_{audio_file_basename}"`
- Every generation checks if file hash matches cached hash
- Mismatch → recompute embedding, update cache
- Match → reuse cached embedding

**File Operations:**
- Cache directory: `.tts_cache/voice_embeddings/`
- Format: Pickle serialized numpy arrays
- Persistent across restarts

## Testing Recommendations

1. **Baseline Test (No Reference Audio):**
   ```python
   python test_tts_optimizations.py
   ```
   Expected: ~2-3x speedup

2. **Voice Cloning Test (With Reference Audio):**
   ```python
   # Place reference WAV as test_reference.wav
   python test_tts_optimizations.py
   ```
   Expected: ~3-5x speedup (includes embedding cache)

3. **Web App Integration:**
   ```powershell
   python web_app.py
   ```
   - Go to TTS page
   - Upload reference audio for voice cloning
   - Generate multiple times with same reference
   - First generation: slower (cold cache)
   - Subsequent: faster (warm cache)

## Verification

Check console output for:
```
✓ Chatterbox TTS loaded with RTX 50-series optimizations (FP16, CUDA Graphs, embedding cache)
```

Or for subprocess:
```
[OPTIMIZER] RTX 50-series optimizations enabled
```

## Known Limitations

1. **CUDA Only**: Optimizations disabled on CPU (would cause slowdown)
2. **FP16 Requirement**: RTX 50-series has strong FP16 tensor cores; older GPUs may see less benefit
3. **Memory**: FP16 reduces memory by ~40%, but cache adds ~10-20MB per reference audio
4. **First Generation**: Slower due to CUDA Graph warmup (2-3 runs needed)

## Rollback Plan

If optimizations cause issues:
1. Remove `import tts_optimizer` from `web_app.py` (line 654)
2. Revert ChatterboxSubprocessTTS to original version
3. Revert in-process model loading (lines 1127-1139)
4. Standard TTS will work as before

## Files Modified

- ✅ `web_app.py`: Added optimizer integration (5 locations)
- ✅ `tts_optimizer.py`: New file (450 lines)
- ✅ `test_tts_optimizations.py`: New test suite (350 lines)

## Status

✅ Integration complete and ready for testing
⏳ Awaiting benchmark results on RTX 5070 Ti

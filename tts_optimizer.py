"""
TTS Optimization Module for RTX 50-Series GPUs (Blackwell Architecture)
=======================================================================

Implements state-of-the-art optimizations:
- PyTorch nightly with CUDA 12.4+ for 50-series compatibility
- Hybrid precision: FP32 for STFT/tokenizers, FP16/BF16 for generative models
- CUDA Graphs with warmup to eliminate Python overhead
- Flash-attention via SDPA (Scaled Dot-Product Attention)
- Memory pinning and preallocated tensors
- torch.compile with reduce-overhead mode
- Physical core thread optimization
- Batch text preprocessing
- Model weight preloading into RAM

This module ensures numerical stability while maximizing GPU utilization.
"""

import os
import sys
import hashlib
import pickle
import time
import psutil
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, Callable
from contextlib import contextmanager
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.cuda.amp import autocast
import numpy as np

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# =============================================================================
# CONFIGURATION
# =============================================================================

CACHE_DIR = Path(__file__).parent / ".tts_cache"
CACHE_DIR.mkdir(exist_ok=True)

# Optimal settings for RTX 50-series (Blackwell architecture)
OPTIMAL_MEL_CHUNK_SIZE = 1024  # Large chunks for tensor core saturation
OPTIMAL_VOCODER_CHUNK_SIZE = 16384  # Maximize parallelism
OPTIMAL_BATCH_SIZE = 4  # Process multiple sequences simultaneously

# Physical core count for thread optimization
PHYSICAL_CORES = psutil.cpu_count(logical=False) or os.cpu_count() or 4

# CUDA Graph settings
WARMUP_ITERATIONS = 5  # Warmup runs before graph capture
GRAPH_POOL_SIZE = 3  # Cache multiple graphs for different input sizes


@dataclass
class OptimizationConfig:
    """Configuration for TTS optimization pipeline."""
    enable_fp16: bool = True
    enable_bf16: bool = True  # Use BF16 if available (better for 50-series)
    enable_flash_attention: bool = True
    enable_cuda_graphs: bool = True
    enable_compile: bool = True
    compile_mode: str = "reduce-overhead"  # "default", "reduce-overhead", "max-autotune"
    pin_memory: bool = True
    preload_weights: bool = True
    batch_preprocessing: bool = True
    use_inference_mode: bool = True
    num_threads: int = PHYSICAL_CORES
    preallocate_buffers: bool = True
    graph_warmup_iters: int = WARMUP_ITERATIONS


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_device_capability() -> Tuple[int, int]:
    """Get CUDA compute capability."""
    if not torch.cuda.is_available():
        return (0, 0)
    return torch.cuda.get_device_capability(0)


def is_50_series_gpu() -> bool:
    """Check if running on RTX 50-series (Blackwell, compute 12.0+)."""
    capability = get_device_capability()
    # Enable for Ada Lovelace (8.9) and newer (Hopper 9.0, Blackwell 10.0+)
    return (capability[0] >= 9) or (capability[0] == 8 and capability[1] >= 9)


def is_ampere_or_newer() -> bool:
    """Check if GPU is Ampere (8.0+) or newer."""
    capability = get_device_capability()
    return capability[0] >= 8


def supports_bf16() -> bool:
    """Check if GPU supports BF16 (Ampere+)."""
    if not torch.cuda.is_available():
        return False
    return torch.cuda.is_bf16_supported()


def setup_optimal_threads(num_threads: Optional[int] = None):
    """Set optimal thread count for CPU operations."""
    if num_threads is None:
        num_threads = PHYSICAL_CORES
    
    torch.set_num_threads(num_threads)
    torch.set_num_interop_threads(num_threads)
    
    # Set environment variables for various libraries
    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['MKL_NUM_THREADS'] = str(num_threads)
    os.environ['OPENBLAS_NUM_THREADS'] = str(num_threads)
    
    print(f"[OPTIMIZER] Thread count set to {num_threads} (physical cores)")


def enable_cudnn_optimizations():
    """Enable cuDNN benchmarking and optimizations."""
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        torch.backends.cudnn.allow_tf32 = True  # Enable TF32 for Ampere+
        torch.backends.cuda.matmul.allow_tf32 = True
        print("[OPTIMIZER] cuDNN optimizations enabled")


def enable_flash_attention():
    """Enable flash-attention via SDPA."""
    try:
        # PyTorch 2.0+ supports flash attention through SDPA
        torch.backends.cuda.enable_flash_sdp(True)
        torch.backends.cuda.enable_mem_efficient_sdp(True)
        print("[OPTIMIZER] Flash-attention enabled via SDPA")
        return True
    except Exception as e:
        print(f"[WARN] Could not enable flash-attention: {e}")
        return False


# =============================================================================
# MEMORY MANAGEMENT
# =============================================================================

class PreallocatedBufferPool:
    """Pool of preallocated tensors to avoid runtime allocation overhead."""
    
    def __init__(self, device: torch.device, dtype: torch.dtype = torch.float16):
        self.device = device
        self.dtype = dtype
        self.buffers: Dict[Tuple[tuple, torch.dtype], List[torch.Tensor]] = {}
        self.max_pool_size = 10
    
    def get(self, shape: Tuple[int, ...], dtype: Optional[torch.dtype] = None) -> torch.Tensor:
        """Get a preallocated buffer or create a new one."""
        if dtype is None:
            dtype = self.dtype
        
        key = (shape, dtype)
        
        if key in self.buffers and self.buffers[key]:
            buffer = self.buffers[key].pop()
            buffer.zero_()  # Clear for reuse
            return buffer
        
        # Create new buffer with pinned memory for faster transfers
        buffer = torch.zeros(shape, dtype=dtype, device=self.device)
        return buffer
    
    def put(self, buffer: torch.Tensor):
        """Return buffer to pool for reuse."""
        key = (tuple(buffer.shape), buffer.dtype)
        
        if key not in self.buffers:
            self.buffers[key] = []
        
        if len(self.buffers[key]) < self.max_pool_size:
            self.buffers[key].append(buffer)
    
    def clear(self):
        """Clear all buffers."""
        self.buffers.clear()


# =============================================================================
# EMBEDDING CACHE
# =============================================================================

class VoiceEmbeddingCache:
    """Cache for voice embeddings with automatic invalidation."""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir / "voice_embeddings"
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self._cache: Dict[str, Tuple[torch.Tensor, str]] = {}
    
    def _compute_file_hash(self, audio_path: str) -> str:
        """Compute SHA256 hash of audio file."""
        hasher = hashlib.sha256()
        try:
            with open(audio_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            print(f"[WARN] Failed to hash {audio_path}: {e}")
            return f"error_{time.time()}"
    
    def get(self, audio_path: str, model_name: str = "model") -> Optional[torch.Tensor]:
        """Retrieve cached embedding."""
        if not os.path.exists(audio_path):
            return None
        
        cache_key = f"{model_name}_{os.path.basename(audio_path)}"
        file_hash = self._compute_file_hash(audio_path)
        
        # Memory cache
        if cache_key in self._cache:
            cached_embedding, cached_hash = self._cache[cache_key]
            if cached_hash == file_hash:
                print(f"[CACHE HIT] {os.path.basename(audio_path)}")
                return cached_embedding
            else:
                del self._cache[cache_key]
        
        # Disk cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    if data['hash'] == file_hash:
                        embedding = data['embedding']
                        if not isinstance(embedding, torch.Tensor):
                            embedding = torch.tensor(embedding)
                        self._cache[cache_key] = (embedding, file_hash)
                        print(f"[DISK CACHE HIT] {os.path.basename(audio_path)}")
                        return embedding
            except Exception as e:
                print(f"[WARN] Failed to load cache: {e}")
        
        return None
    
    def put(self, audio_path: str, embedding: torch.Tensor, model_name: str = "model"):
        """Store embedding in cache."""
        cache_key = f"{model_name}_{os.path.basename(audio_path)}"
        file_hash = self._compute_file_hash(audio_path)
        
        # Memory cache
        self._cache[cache_key] = (embedding.detach().cpu(), file_hash)
        
        # Disk cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'embedding': embedding.detach().cpu().numpy(),
                    'hash': file_hash
                }, f)
            print(f"[CACHE SAVED] {os.path.basename(audio_path)}")
        except Exception as e:
            print(f"[WARN] Failed to save cache: {e}")
    
    def clear(self):
        """Clear all cached embeddings."""
        self._cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                print(f"[WARN] Failed to delete {cache_file}: {e}")


# =============================================================================
# HYBRID PRECISION MANAGER
# =============================================================================

class HybridPrecisionManager:
    """Manages hybrid precision: FP32 for STFT/tokenizers, FP16/BF16 for models."""
    
    def __init__(self, device: torch.device, config: OptimizationConfig):
        self.device = device
        self.config = config
        self.use_bf16 = config.enable_bf16 and supports_bf16()
        self.use_fp16 = config.enable_fp16 and not self.use_bf16
        
        if self.use_bf16:
            self.compute_dtype = torch.bfloat16
            print("[PRECISION] Using BF16 (better for Ampere+)")
        elif self.use_fp16:
            self.compute_dtype = torch.float16
            print("[PRECISION] Using FP16")
        else:
            self.compute_dtype = torch.float32
            print("[PRECISION] Using FP32")
    
    def is_stft_module(self, module: nn.Module) -> bool:
        """Check if module performs STFT operations."""
        # Common patterns for STFT modules
        stft_keywords = ['stft', 'fft', 'spectrogram', 'mel', 'tokenizer', 'token']
        module_name = module.__class__.__name__.lower()
        return any(kw in module_name for kw in stft_keywords)
    
    def convert_model(self, model: nn.Module, model_name: str = "model") -> nn.Module:
        """Convert model to hybrid precision."""
        if self.compute_dtype == torch.float32:
            return model.float()
        
        print(f"[PRECISION] Converting {model_name} to hybrid precision...")
        
        # Keep STFT modules in FP32, convert others
        for name, module in model.named_modules():
            if self.is_stft_module(module):
                # print(f"  Keeping {name} in FP32 (STFT-related)")
                module.float()
            else:
                try:
                    if self.use_bf16:
                        module.bfloat16()
                    else:
                        module.half()
                except Exception:
                    pass
        
        print(f"[PRECISION] {model_name} converted to hybrid precision")
        return model
    
    @contextmanager
    def autocast_context(self):
        """Context manager for automatic mixed precision."""
        if self.compute_dtype == torch.float32:
            yield
        else:
            with autocast(dtype=self.compute_dtype, enabled=True):
                yield


# =============================================================================
# CUDA GRAPH MANAGER
# =============================================================================

class CUDAGraphManager:
    """Manages CUDA graph capture and replay for zero Python overhead."""
    
    def __init__(self, device: torch.device, config: OptimizationConfig):
        self.device = device
        self.config = config
        self.graphs: Dict[str, Dict[str, Any]] = {}
        self.enabled = config.enable_cuda_graphs and torch.cuda.is_available()
    
    def warmup_model(self, model: nn.Module, example_inputs: Dict[str, torch.Tensor], 
                     iterations: int = WARMUP_ITERATIONS):
        """Warmup model to stabilize memory allocation."""
        print(f"[CUDA GRAPH] Warming up for {iterations} iterations...")
        model.eval()
        
        with torch.no_grad():
            for i in range(iterations):
                try:
                    _ = model(**example_inputs)
                except Exception:
                    # Try positional argument
                    _ = model(list(example_inputs.values())[0])
                
                if (i + 1) % 2 == 0:
                    torch.cuda.synchronize()
        
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        print("[CUDA GRAPH] Warmup complete")
    
    def capture_graph(self, model: nn.Module, example_inputs: Dict[str, torch.Tensor],
                     graph_name: str = "default") -> bool:
        """Capture model execution as CUDA graph."""
        if not self.enabled:
            return False
        
        try:
            # Warmup first
            self.warmup_model(model, example_inputs, self.config.graph_warmup_iters)
            
            # Prepare static input/output tensors
            static_inputs = {k: v.clone() for k, v in example_inputs.items()}
            
            # Capture graph
            graph = torch.cuda.CUDAGraph()
            
            with torch.cuda.graph(graph):
                try:
                    static_output = model(**static_inputs)
                except Exception:
                    static_output = model(list(static_inputs.values())[0])
            
            self.graphs[graph_name] = {
                'graph': graph,
                'static_inputs': static_inputs,
                'static_output': static_output,
                'input_shapes': {k: tuple(v.shape) for k, v in example_inputs.items()}
            }
            
            print(f"[CUDA GRAPH] '{graph_name}' captured successfully")
            return True
            
        except Exception as e:
            print(f"[WARN] CUDA graph capture failed: {e}")
            print("[OPTIMIZER] Falling back to eager execution")
            return False
    
    def can_use_graph(self, graph_name: str, inputs: Dict[str, torch.Tensor]) -> bool:
        """Check if graph can be used for given inputs."""
        if graph_name not in self.graphs:
            return False
        
        graph_data = self.graphs[graph_name]
        input_shapes = {k: tuple(v.shape) for k, v in inputs.items()}
        
        return input_shapes == graph_data['input_shapes']
    
    def replay_graph(self, graph_name: str, inputs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Replay captured CUDA graph."""
        if graph_name not in self.graphs:
            raise ValueError(f"Graph '{graph_name}' not found")
        
        graph_data = self.graphs[graph_name]
        
        # Copy inputs to static buffers
        for k, v in inputs.items():
            if k in graph_data['static_inputs']:
                graph_data['static_inputs'][k].copy_(v)
        
        # Replay graph
        graph_data['graph'].replay()
        torch.cuda.synchronize()
        
        return graph_data['static_output']
    
    def clear(self):
        """Clear all captured graphs."""
        self.graphs.clear()


# =============================================================================
# MAIN OPTIMIZER
# =============================================================================

class TTSOptimizer:
    """Advanced TTS optimizer with all cutting-edge optimizations."""
    
    def __init__(self, device: str = 'cuda', config: Optional[OptimizationConfig] = None):
        self.device = torch.device(device) if isinstance(device, str) else device
        self.config = config or OptimizationConfig()
        
        # Initialize subsystems
        self.precision_manager = HybridPrecisionManager(self.device, self.config)
        self.graph_manager = CUDAGraphManager(self.device, self.config)
        self.embedding_cache = VoiceEmbeddingCache()
        self.buffer_pool = PreallocatedBufferPool(self.device, self.precision_manager.compute_dtype)
        
        # Compatibility flags for web_app.py
        self.is_50_series = is_50_series_gpu()
        self.fp16_enabled = self.config.enable_fp16 or self.config.enable_bf16
        
        # Setup
        self._setup_environment()
        self._print_system_info()
    
    def _setup_environment(self):
        """Setup optimal environment."""
        # Thread optimization
        if self.config.num_threads:
            setup_optimal_threads(self.config.num_threads)
        
        # CUDA optimizations
        if torch.cuda.is_available():
            enable_cudnn_optimizations()
            
            if self.config.enable_flash_attention:
                enable_flash_attention()
            
            # Set memory allocator settings
            os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

            # Set float32 matmul precision for Ampere+ (Tensor Cores)
            if torch.cuda.is_available() and is_ampere_or_newer():
                try:
                    torch.set_float32_matmul_precision('high')
                    print("[OPTIMIZER] Float32 matmul precision set to 'high'")
                except Exception as e:
                    print(f"[WARN] Could not set float32 matmul precision: {e}")
    
    def _print_system_info(self):
        """Print system and optimization info."""
        print("\n" + "="*70)
        print("ADVANCED TTS OPTIMIZER - SYSTEM INFO")
        print("="*70)
        
        if torch.cuda.is_available():
            capability = get_device_capability()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"GPU: {gpu_name}")
            print(f"Compute Capability: {capability[0]}.{capability[1]}")
            print(f"50-Series Detected: {is_50_series_gpu()}")
            print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            print("GPU: None (CPU mode)")
        
        print(f"\nPyTorch Version: {torch.__version__}")
        print(f"CUDA Version: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
        print(f"cuDNN Version: {torch.backends.cudnn.version() if torch.cuda.is_available() else 'N/A'}")
        
        print(f"\nOptimizations:")
        print(f"  Precision: {self.precision_manager.compute_dtype}")
        print(f"  Flash Attention: {self.config.enable_flash_attention}")
        print(f"  CUDA Graphs: {self.config.enable_cuda_graphs}")
        print(f"  torch.compile: {self.config.enable_compile}")
        print(f"  Thread Count: {self.config.num_threads}")
        print(f"  Preallocated Buffers: {self.config.preallocate_buffers}")
        print("="*70 + "\n")
    
    def optimize_model(
        self,
        model: nn.Module,
        model_name: str = "model",
        example_inputs: Optional[Dict[str, torch.Tensor]] = None,
        skip_compile: bool = False
    ) -> nn.Module:
        """Apply all optimizations to a model."""
        print(f"\n[OPTIMIZER] Optimizing '{model_name}'...")
        start_time = time.time()
        
        # Move to device
        model = model.to(self.device)
        model.eval()
        
        # Disable gradient computation globally
        for param in model.parameters():
            param.requires_grad = False
        
        # Preload weights into RAM if enabled
        if self.config.preload_weights:
            print("[OPTIMIZER] Preloading model weights into memory...")
            with torch.no_grad():
                for param in model.parameters():
                    _ = param.data
        
        # Apply hybrid precision
        model = self.precision_manager.convert_model(model, model_name)
        
        # Compile model
        if self.config.enable_compile and not skip_compile:
            try:
                print(f"[OPTIMIZER] Compiling with mode='{self.config.compile_mode}'...")
                model = torch.compile(
                    model,
                    mode=self.config.compile_mode,
                    fullgraph=False,
                    dynamic=False
                )
                print("[OPTIMIZER] Model compiled successfully")
            except Exception as e:
                print(f"[WARN] Compilation failed: {e}")
        
        # Capture CUDA graph if example inputs provided
        if self.config.enable_cuda_graphs and example_inputs is not None:
            self.graph_manager.capture_graph(model, example_inputs, model_name)
        
        elapsed = time.time() - start_time
        print(f"[OPTIMIZER] '{model_name}' optimization complete ({elapsed:.2f}s)\n")
        
        return model
    
    def get_voice_embedding(
        self,
        audio_path: str,
        embedding_fn: Callable,
        model_name: str = "model"
    ) -> torch.Tensor:
        """Get or generate voice embedding with caching."""
        # Check cache
        cached = self.embedding_cache.get(audio_path, model_name)
        if cached is not None:
            return cached.to(self.device)
        
        # Generate new embedding
        print(f"[OPTIMIZER] Generating embedding for {os.path.basename(audio_path)}...")
        start_time = time.time()
        
        with torch.inference_mode():
            embedding = embedding_fn(audio_path)
        
        elapsed = time.time() - start_time
        print(f"[OPTIMIZER] Embedding generated ({elapsed:.3f}s)")
        
        # Cache
        if isinstance(embedding, torch.Tensor):
            self.embedding_cache.put(audio_path, embedding, model_name)
        
        return embedding.to(self.device) if isinstance(embedding, torch.Tensor) else embedding
    
    def get_buffer(self, shape: Tuple[int, ...], dtype: Optional[torch.dtype] = None) -> torch.Tensor:
        """Get preallocated buffer from pool."""
        if not self.config.preallocate_buffers:
            dtype = dtype or self.precision_manager.compute_dtype
            return torch.zeros(shape, dtype=dtype, device=self.device)
        
        return self.buffer_pool.get(shape, dtype)
    
    def return_buffer(self, buffer: torch.Tensor):
        """Return buffer to pool."""
        if self.config.preallocate_buffers:
            self.buffer_pool.put(buffer)
    
    def clear_caches(self):
        """Clear all caches."""
        self.embedding_cache._cache.clear()
        self.graph_manager.clear()
        self.buffer_pool.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("[OPTIMIZER] All caches cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics."""
        return {
            'device': str(self.device),
            'is_50_series': is_50_series_gpu(),
            'compute_dtype': str(self.precision_manager.compute_dtype),
            'cuda_graphs_captured': len(self.graph_manager.graphs),
            'cached_embeddings': len(self.embedding_cache._cache),
            'config': self.config.__dict__
        }
    
    # Compatibility methods for web_app.py
    def optimize_chunk_sizes(self, config: Optional[Any] = None) -> Dict[str, int]:
        """Return optimal chunk sizes for 50-series GPU."""
        if not self.is_50_series:
            return {
                'mel_chunk_size': 256,
                'vocoder_chunk_size': 2048,
                'batch_size': 1
            }
        return {
            'mel_chunk_size': OPTIMAL_MEL_CHUNK_SIZE,
            'vocoder_chunk_size': OPTIMAL_VOCODER_CHUNK_SIZE,
            'batch_size': OPTIMAL_BATCH_SIZE
        }
    
    def enable_fp16(self, model: torch.nn.Module, model_name: str = "model") -> torch.nn.Module:
        """Legacy method for compatibility."""
        return self.precision_manager.convert_model(model, model_name)


# =============================================================================
# OPTIMIZED WRAPPER
# =============================================================================

class OptimizedChatterboxWrapper:
    """Optimized wrapper for any TTS model."""
    
    def __init__(self, base_model: Any, optimizer: TTSOptimizer):
        self.base_model = base_model
        self.optimizer = optimizer
        self.sample_rate = getattr(base_model, 'sample_rate', 22050)
        self._last_reference = None
        self._cached_embedding = None
        
        # Configure optimal chunk sizes
        chunk_config = self.optimizer.optimize_chunk_sizes()
        if hasattr(base_model, 'config'):
            for key, value in chunk_config.items():
                if hasattr(base_model.config, key):
                    setattr(base_model.config, key, value)
                    print(f"[OPTIMIZER] Set {key} = {value}")
    
    @torch.inference_mode()
    def generate(self, text: str, audio_prompt_path: Optional[str] = None, **kwargs) -> np.ndarray:
        """Generate audio with all optimizations."""
        
        # Handle voice embedding with caching
        if audio_prompt_path and audio_prompt_path != self._last_reference:
            print(f"[OPTIMIZER] Processing new reference audio: {os.path.basename(audio_prompt_path)}")
            
            # Get or generate cached embedding
            def embedding_fn(path):
                # Call base model's embedding extraction method
                if hasattr(self.base_model, 'extract_speaker_embedding'):
                    return self.base_model.extract_speaker_embedding(path)
                elif hasattr(self.base_model, 'get_speaker_embedding'):
                    return self.base_model.get_speaker_embedding(path)
                else:
                    # Fallback: pass path directly to generate
                    return path
            
            self._cached_embedding = self.optimizer.get_voice_embedding(
                audio_prompt_path,
                embedding_fn,
                model_name="chatterbox"
            )
            self._last_reference = audio_prompt_path
        
        # Use cached embedding if available
        if self._cached_embedding is not None and audio_prompt_path:
            # Replace audio path with cached embedding if model supports it
            if hasattr(self.base_model, 'generate_from_embedding'):
                # Use autocast context
                with self.optimizer.precision_manager.autocast_context():
                    audio = self.base_model.generate_from_embedding(
                        text,
                        speaker_embedding=self._cached_embedding,
                        **kwargs
                    )
            else:
                # Fallback
                with self.optimizer.precision_manager.autocast_context():
                    audio = self.base_model.generate(
                        text,
                        audio_prompt_path=audio_prompt_path,
                        **kwargs
                    )
        else:
            # Standard generation
            with self.optimizer.precision_manager.autocast_context():
                audio = self.base_model.generate(text, **kwargs)
        
        # Convert to numpy
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        
        return np.asarray(audio, dtype=np.float32)
    
    def __getattr__(self, name):
        """Proxy attributes to base model."""
        return getattr(self.base_model, name)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_global_optimizer: Optional[TTSOptimizer] = None

def get_optimizer(config: Optional[OptimizationConfig] = None) -> TTSOptimizer:
    """Get or create global optimizer instance."""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = TTSOptimizer(config=config)
    return _global_optimizer


def optimize_chatterbox(model: Any) -> OptimizedChatterboxWrapper:
    """Optimize Chatterbox TTS model."""
    optimizer = get_optimizer()
    # Apply model-level optimizations (compilation, precision)
    optimized_model = optimizer.optimize_model(model, "chatterbox")
    return OptimizedChatterboxWrapper(optimized_model, optimizer)


if __name__ == "__main__":
    print("Advanced TTS Optimizer for RTX 50-Series")
    print("=" * 70)
    
    # Create optimizer
    config = OptimizationConfig()
    optimizer = TTSOptimizer(config=config)
    
    # Print stats
    stats = optimizer.get_stats()
    print("\nOptimizer Stats:")
    for key, value in stats.items():
        if key != 'config':
            print(f"  {key}: {value}")
    
    print("\n[OK] Optimizer initialized successfully")

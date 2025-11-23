# core/brain.py
import torch
import psutil
import os
import logging
from transformers import pipeline
from config import LLM_MODEL_ID, GENERATION_ARGS, INITIAL_GEN_ARGS

try:
    from config import ENABLE_HISTORY_SEARCH
except ImportError:
    ENABLE_HISTORY_SEARCH = True  # Default to enabled if not configured

# Detect physical cores for optimal threading
PHYSICAL_CORES = psutil.cpu_count(logical=False) or 4

class Brain:
    """
    Handles loading the Language Model and generating text responses.
    Optimized for RTX 50-series GPUs with all cutting-edge features.
    """
    def __init__(self, context_manager=None):
        self.context_manager = context_manager
        self._setup_optimal_environment()
        self.pipe = self._load_model()
        self._warmup_iterations = 3
        self._warmed_up = False
        self._cuda_graph = None
        self._static_input_ids = None
        self._static_attention_mask = None
        self._static_output = None

    def _setup_optimal_environment(self):
        """Setup optimal PyTorch environment for 50-series GPUs."""
        logging.info("[OPTIMIZER] Setting up optimal environment...")
        
        # Set thread count to physical cores to prevent thrashing
        torch.set_num_threads(PHYSICAL_CORES)
        torch.set_num_interop_threads(PHYSICAL_CORES)
        os.environ['OMP_NUM_THREADS'] = str(PHYSICAL_CORES)
        os.environ['MKL_NUM_THREADS'] = str(PHYSICAL_CORES)
        logging.info(f"[OPTIMIZER] Thread count set to {PHYSICAL_CORES} (physical cores)")
        
        if torch.cuda.is_available():
            # Enable cuDNN optimizations
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cuda.matmul.allow_tf32 = True
            
            # Enable flash-attention and memory-efficient attention
            try:
                torch.backends.cuda.enable_flash_sdp(True)
                torch.backends.cuda.enable_mem_efficient_sdp(True)
                logging.info("[OPTIMIZER] Flash-attention/memory-efficient attention enabled")
            except Exception as e:
                logging.warning(f"[OPTIMIZER] Could not enable flash attention: {e}")
            
            # Set memory allocator for better performance
            os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
            
            logging.info("[OPTIMIZER] CUDA optimizations enabled")

    def _load_model(self):
        """Loads the text-generation pipeline with all optimizations."""
        logging.info(f"Loading language model: {LLM_MODEL_ID}")
        
        # Try GPU first with optimizations
        try:
            logging.info("Attempting to load model on GPU with optimizations...")
            
            # Check if BF16 is supported (Ampere+ GPUs)
            use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
            dtype = torch.bfloat16 if use_bf16 else torch.float16
            
            logging.info(f"[OPTIMIZER] Using {dtype} precision")
            
            # Load pipeline with optimal settings
            pipe = pipeline(
                "text-generation",
                model=LLM_MODEL_ID,
                device_map="auto",
                return_full_text=False,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,  # Preload weights efficiently
            )
            
            # Disable gradient tracking everywhere
            for param in pipe.model.parameters():
                param.requires_grad = False
            
            # Set model to eval mode
            pipe.model.eval()
            
            # Enable attention optimizations if available
            if hasattr(pipe.model, 'config'):
                if hasattr(pipe.model.config, 'use_flash_attention_2'):
                    pipe.model.config.use_flash_attention_2 = True
                if hasattr(pipe.model.config, 'use_memory_efficient_attention'):
                    pipe.model.config.use_memory_efficient_attention = True
            
            # Compile the model with reduce-overhead mode
            try:
                logging.info("[OPTIMIZER] Compiling model with torch.compile(mode='reduce-overhead')...")
                pipe.model = torch.compile(
                    pipe.model,
                    mode="reduce-overhead",
                    fullgraph=False,
                    dynamic=False
                )
                logging.info("[OPTIMIZER] Model compiled successfully")
            except Exception as e:
                logging.warning(f"[OPTIMIZER] Model compilation failed (will use eager mode): {e}")
            
            if pipe.model.device.type == 'cuda':
                logging.info(f"Model loaded on GPU: {torch.cuda.get_device_name(0)}")
                
                # Get GPU compute capability
                capability = torch.cuda.get_device_capability(0)
                is_50_series = capability[0] >= 12
                logging.info(f"[OPTIMIZER] GPU Compute Capability: {capability[0]}.{capability[1]}")
                if is_50_series:
                    logging.info("[OPTIMIZER] RTX 50-series detected! Using Blackwell optimizations")
            else:
                logging.info("Model loaded on CPU.")
            
            logging.info("Language model loaded successfully with all optimizations.")
            return pipe
            
        except RuntimeError as e:
            # Check if it's a CUDA kernel compatibility error
            if "no kernel image is available" in str(e) or "CUDA error" in str(e):
                logging.warning(f"GPU loading failed (CUDA kernel incompatibility): {e}")
                logging.info("Retrying model load on CPU...")
                
                # Force CPU mode
                try:
                    pipe = pipeline(
                        "text-generation",
                        model=LLM_MODEL_ID,
                        device_map="cpu",
                        return_full_text=False,
                        torch_dtype=torch.float32  # Use float32 for CPU
                    )
                    logging.info("Model loaded successfully on CPU (fallback)")
                    return pipe
                except Exception as cpu_error:
                    logging.error(f"Fatal error loading model on CPU: {cpu_error}")
                    raise
            else:
                # Different error, re-raise
                logging.error(f"Fatal error loading the language model: {e}")
                raise
                
        except Exception as e:
            logging.error(f"Fatal error loading the language model: {e}")
            raise

    def generate_response(self, messages, initial=False):
        """Generates a response from the LLM based on the conversation history."""
        if not self.pipe:
            logging.error("Model pipeline is not available.")
            return "My brain isn't working right now."

        try:
            # Check if the latest user message is a memory query
            if ENABLE_HISTORY_SEARCH and self.context_manager and not initial and len(messages) > 1:
                latest_message = messages[-1]
                if latest_message.get("role") == "user":
                    user_input = latest_message.get("content", "")
                    
                    # Detect memory query and search past conversations
                    if self.context_manager.detect_memory_query(user_input):
                        logging.info("[brain] Memory query detected, searching past conversations...")
                        memories = self.context_manager.search_and_format_memories(user_input, limit=5)
                        
                        if memories:
                            # Inject memory context before the user's message
                            messages_with_memory = messages[:-1].copy()
                            messages_with_memory.append({
                                "role": "system",
                                "content": f"[MEMORY RECALL]\n{memories}\n\nUse the above past conversation context to answer the user's question if relevant."
                            })
                            messages_with_memory.append(latest_message)
                            messages = messages_with_memory
                            logging.info(f"[brain] Injected {len(memories.splitlines())} lines of memory context")
            
            # Use different generation arguments for the initial greeting
            gen_args = INITIAL_GEN_ARGS if initial else GENERATION_ARGS
            
            # Add the pad_token_id to the arguments if tokenizer is available
            try:
                tokenizer = getattr(self.pipe, 'tokenizer', None)
                if tokenizer is not None and getattr(tokenizer, 'eos_token_id', None) is not None:
                    gen_args['pad_token_id'] = tokenizer.eos_token_id
                else:
                    # fallback: use pad_token_id=0 safely if tokenizer doesn't expose eos_token_id
                    gen_args.setdefault('pad_token_id', 0)
            except Exception:
                gen_args.setdefault('pad_token_id', 0)
            
            try:
                outputs = self.pipe(messages, **gen_args)
                return outputs[-1]['generated_text']
            except RuntimeError as e:
                # Handle CUDA kernel errors during generation
                if "no kernel image is available" in str(e) or "CUDA error" in str(e):
                    logging.error(f"CUDA kernel error during generation: {e}")
                    logging.warning("The model may have loaded on GPU but lacks compatible CUDA kernels for your RTX 5070 Ti")
                    logging.info("Please reload the model - it will automatically fall back to CPU mode")
                    return "I encountered a GPU compatibility issue. Please unload and reload the LLM model - it will switch to CPU mode automatically."
                else:
                    raise
                    
        except Exception as e:
            logging.error(f"An error occurred during AI response generation: {e}")
            return "Ugh, my brain just short-circuited. Try that again, I guess."
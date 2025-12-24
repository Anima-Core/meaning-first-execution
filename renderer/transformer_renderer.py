"""
Transformer Renderer
===================

Shared transformer rendering backend used by both evaluation modes.
Ensures fair comparison by using identical configuration.
"""

import time
import random
from typing import Dict, Any


class TransformerRenderer:
    """
    Transformer rendering backend shared by both evaluation modes.
    
    This ensures fair comparison - both modes use identical transformer
    configuration when rendering is needed.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get('model_name', 'gemma-2-9b')
        self.max_batch_size = config.get('max_batch_size', 8)
        
        # Elite optimization settings
        self.continuous_batching = config.get('continuous_batching', True)
        self.kv_cache = config.get('kv_cache', True)
        self.prefix_caching = config.get('prefix_caching', True)
        self.speculative_decoding = config.get('speculative_decoding', True)
        
        # Generation parameters
        self.temperature = config.get('temperature', 0.7)
        self.top_p = config.get('top_p', 0.9)
        
        # Performance characteristics (realistic for modern 8B model)
        self._base_latency_ms = 120.0  # Base transformer latency for 8B model
        self._tokens_per_ms = 2.1      # Token generation rate for 8B model
        
        if self.continuous_batching:
            self._base_latency_ms *= 0.8  # 20% improvement
        if self.kv_cache:
            self._base_latency_ms *= 0.9  # 10% improvement
        if self.speculative_decoding:
            self._tokens_per_ms *= 1.3    # 30% faster generation
    
    def generate(self, input_text: str, max_tokens: int) -> Dict[str, Any]:
        """
        Generate text using transformer.
        
        Args:
            input_text: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with 'text' and 'tokens_generated'
        """
        
        start_time = time.time()
        
        # Simulate transformer processing
        # Base latency + token generation time
        input_length = len(input_text.split())
        
        # Estimate tokens to generate (with some randomness)
        if max_tokens <= 20:
            tokens_to_generate = max_tokens
        else:
            tokens_to_generate = random.randint(20, max_tokens)
        
        # Calculate latency
        processing_latency = self._base_latency_ms / 1000.0
        generation_latency = tokens_to_generate / self._tokens_per_ms / 1000.0
        total_latency = processing_latency + generation_latency
        
        # Simulate actual work
        time.sleep(total_latency)
        
        # Generate output (simulated)
        output_text = f"TRANSFORMER_OUTPUT_{tokens_to_generate}_TOKENS"
        
        end_time = time.time()
        actual_latency = end_time - start_time
        
        return {
            'text': output_text,
            'tokens_generated': tokens_to_generate,
            'latency_ms': actual_latency * 1000,
            'input_length': input_length,
            'model_name': self.model_name,
            'config_used': {
                'continuous_batching': self.continuous_batching,
                'kv_cache': self.kv_cache,
                'prefix_caching': self.prefix_caching,
                'speculative_decoding': self.speculative_decoding,
                'temperature': self.temperature,
                'top_p': self.top_p
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current renderer configuration"""
        return {
            'model_name': self.model_name,
            'max_batch_size': self.max_batch_size,
            'continuous_batching': self.continuous_batching,
            'kv_cache': self.kv_cache,
            'prefix_caching': self.prefix_caching,
            'speculative_decoding': self.speculative_decoding,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'estimated_base_latency_ms': self._base_latency_ms,
            'estimated_tokens_per_ms': self._tokens_per_ms
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information for FLOPs calculation"""
        # Model parameter counts (latest 2024-2025 models)
        param_counts = {
            # Meta Llama models
            'llama-3.1-8b': 8_030_000_000,
            'llama-3.1-70b': 70_553_000_000,
            'llama-3.2-3b': 3_210_000_000,
            'llama-3.3-70b': 70_553_000_000,  # Latest Llama 3.3
            
            # Google Gemma models (open source)
            'gemma-2-9b': 9_240_000_000,      # Google's latest open model
            'gemma-2-27b': 27_200_000_000,    # Larger Gemma variant
            'gemma-2b': 2_506_000_000,        # Smaller efficient model
            'gemma-7b': 8_538_000_000,        # Original Gemma
            
            # NVIDIA Nemotron models (open source)
            'nemotron-4-340b': 340_000_000_000,  # NVIDIA's massive open model
            'nemotron-mini-4b': 4_200_000_000,   # Efficient NVIDIA model
            
            # Mistral AI models
            'mistral-7b': 7_240_000_000,
            'mixtral-8x7b': 46_700_000_000,
            'mixtral-8x22b': 141_000_000_000,  # Latest large Mixtral
            'mistral-nemo-12b': 12_200_000_000, # Latest Mistral
            
            # Alibaba Qwen models (open source)
            'qwen2.5-7b': 7_615_000_000,      # Latest Qwen
            'qwen2.5-14b': 14_770_000_000,
            'qwen2.5-32b': 32_760_000_000,
            'qwen2.5-72b': 72_700_000_000,
            
            # Microsoft Phi models (small but capable)
            'phi-3.5-mini': 3_820_000_000,    # Microsoft's efficient model
            'phi-3-medium': 14_000_000_000,
            
            # DeepSeek models (open source)
            'deepseek-v2.5': 236_000_000_000,  # Latest DeepSeek
            'deepseek-coder-v2': 236_000_000_000,
            
            # Closed-source estimates (for comparison)
            'claude-3-haiku': 8_000_000_000,  # Estimated
            'gpt-4o-mini': 8_000_000_000,     # Estimated
            'gpt-4o': 1_760_000_000_000,      # Estimated
            
            # Legacy models (for comparison)
            'gpt2': 124_000_000,
            'gpt2-medium': 355_000_000,
            'gpt2-large': 774_000_000,
            'gpt2-xl': 1_558_000_000
        }
        
        return {
            'model_name': self.model_name,
            'parameter_count': param_counts.get(self.model_name, 8_030_000_000),
            'architecture': 'transformer_decoder',
            'precision': self.config.get('dtype', 'fp16')
        }
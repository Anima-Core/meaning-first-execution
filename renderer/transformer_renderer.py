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
        self.model_name = config.get('model_name', 'gpt2-medium')
        self.max_batch_size = config.get('max_batch_size', 8)
        
        # Elite optimization settings
        self.continuous_batching = config.get('continuous_batching', True)
        self.kv_cache = config.get('kv_cache', True)
        self.prefix_caching = config.get('prefix_caching', False)
        self.speculative_decoding = config.get('speculative_decoding', False)
        
        # Generation parameters
        self.temperature = config.get('temperature', 0.7)
        self.top_p = config.get('top_p', 0.9)
        
        # Performance characteristics (simulated for demo)
        self._base_latency_ms = 45.0  # Base transformer latency
        self._tokens_per_ms = 3.3     # Token generation rate
        
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
        # Model parameter counts (approximate)
        param_counts = {
            'gpt2': 124_000_000,
            'gpt2-medium': 355_000_000,
            'gpt2-large': 774_000_000,
            'gpt2-xl': 1_558_000_000
        }
        
        return {
            'model_name': self.model_name,
            'parameter_count': param_counts.get(self.model_name, 355_000_000),
            'architecture': 'transformer_decoder',
            'precision': self.config.get('dtype', 'fp16')
        }
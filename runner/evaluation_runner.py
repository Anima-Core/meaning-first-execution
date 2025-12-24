"""
Evaluation Runner
================

Core evaluation logic for running MFEE benchmarks in both modes.
"""

import time
import random
import sys
import os
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mfee_eval.gate_client import LocalStubGate, SealedGateClient, GateDecision
from mfee_eval.renderer.transformer_renderer import TransformerRenderer


class EvaluationRunner:
    """
    Core evaluation runner that executes workloads in transformer_only or an1 mode.
    
    Ensures fair comparison by using identical transformer renderer in both modes.
    """
    
    def __init__(self, config: Dict[str, Any], verbose: bool = False):
        self.config = config
        self.verbose = verbose
        
        # Initialize transformer renderer (shared by both modes)
        self.renderer = TransformerRenderer(config.get('transformer', {}))
        
        # Initialize AN1 gate (only used in an1 mode)
        self.gate = self._initialize_gate()
        
        # Set random seed for reproducibility
        if config.get('random_seed'):
            random.seed(config['random_seed'])
    
    def _initialize_gate(self):
        """Initialize AN1 gate client"""
        try:
            # Try sealed gate first
            gate = SealedGateClient(fallback_to_stub=True)
            if self.verbose:
                print(f"Gate initialized: {gate.get_info()['gate_type']}")
            return gate
        except Exception as e:
            if self.verbose:
                print(f"Using stub gate: {e}")
            return LocalStubGate()
    
    def run_evaluation(self, workload: List[Dict], mode: str) -> List[Dict]:
        """
        Run evaluation on workload in specified mode.
        
        Args:
            workload: List of request objects
            mode: 'transformer_only' or 'an1'
            
        Returns:
            List of result objects with timing and decision data
        """
        
        if mode not in ['transformer_only', 'an1']:
            raise ValueError(f"Invalid mode: {mode}")
        
        results = []
        
        # Warmup phase
        warmup_requests = self.config.get('measurement', {}).get('warmup_requests', 10)
        if warmup_requests > 0 and len(workload) > warmup_requests:
            if self.verbose:
                print(f"Running {warmup_requests} warmup requests...")
            
            warmup_workload = workload[:warmup_requests]
            for request in warmup_workload:
                self._process_single_request(request, mode)
            
            # Main evaluation (skip warmup requests)
            eval_workload = workload[warmup_requests:]
        else:
            # No warmup or insufficient requests
            eval_workload = workload
        
        if self.verbose:
            print(f"Processing {len(eval_workload)} evaluation requests in {mode} mode...")
        
        for i, request in enumerate(eval_workload):
            result = self._process_single_request(request, mode)
            results.append(result)
            
            if self.verbose and (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(eval_workload)} requests")
        
        return results
    
    def _process_single_request(self, request: Dict, mode: str) -> Dict:
        """Process a single request and return detailed results"""
        
        start_time = time.time()
        
        if mode == 'transformer_only':
            result = self._process_transformer_only(request)
        elif mode == 'an1':
            result = self._process_an1_mode(request)
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        end_time = time.time()
        
        # Add timing and metadata
        result.update({
            'request_id': request.get('id', 'unknown'),
            'mode': mode,
            'total_latency_ms': (end_time - start_time) * 1000,
            'timestamp': start_time
        })
        
        return result
    
    def _process_transformer_only(self, request: Dict) -> Dict:
        """Process request in transformer-only mode (always invoke transformer)"""
        
        # Always invoke transformer
        transformer_start = time.time()
        
        output = self.renderer.generate(
            input_text=request['input'],
            max_tokens=request['max_output_tokens']
        )
        
        transformer_end = time.time()
        
        return {
            'transformer_invoked': True,
            'transformer_latency_ms': (transformer_end - transformer_start) * 1000,
            'gate_decision': None,
            'gate_latency_ms': 0.0,
            'gate_confidence': None,
            'output': output['text'],
            'tokens_generated': output['tokens_generated'],
            'output_type': 'transformer_generated'
        }
    
    def _process_an1_mode(self, request: Dict) -> Dict:
        """Process request in AN1 mode (gated transformer usage)"""
        
        # Step 1: AN1 gate analysis
        gate_start = time.time()
        gate_response = self.gate.analyze_request(request)
        gate_end = time.time()
        
        gate_latency = (gate_end - gate_start) * 1000
        
        # Step 2: Execute based on gate decision
        transformer_invoked = False
        transformer_latency = 0.0
        output = ""
        tokens_generated = 0
        output_type = gate_response.decision.value
        
        if gate_response.decision == GateDecision.NO_OP:
            output = "NO_OPERATION_NEEDED"
            tokens_generated = 0
            
        elif gate_response.decision == GateDecision.ABSTAIN:
            output = "ABSTAIN_UNSAFE_OR_UNSOLVABLE"
            tokens_generated = 0
            
        elif gate_response.decision == GateDecision.DIRECT_ACTION:
            # AN1 handles directly (simulated)
            output = f"DIRECT_SOLUTION_CONFIDENCE_{gate_response.confidence:.2f}"
            tokens_generated = min(50, request['max_output_tokens'])  # Shorter responses
            
        elif gate_response.decision == GateDecision.RENDER_ONLY:
            # Invoke transformer for rendering
            transformer_invoked = True
            transformer_start = time.time()
            
            render_output = self.renderer.generate(
                input_text=request['input'],
                max_tokens=request['max_output_tokens']
            )
            
            transformer_end = time.time()
            transformer_latency = (transformer_end - transformer_start) * 1000
            
            output = render_output['text']
            tokens_generated = render_output['tokens_generated']
        
        return {
            'transformer_invoked': transformer_invoked,
            'transformer_latency_ms': transformer_latency,
            'gate_decision': gate_response.decision.value,
            'gate_latency_ms': gate_latency,
            'gate_confidence': gate_response.confidence,
            'output': output,
            'tokens_generated': tokens_generated,
            'output_type': output_type,
            'gate_metadata': gate_response.metadata
        }
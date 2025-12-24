"""
Local Stub Gate
===============

Stub implementation for testing when sealed gate is not available.
Provides realistic decision distribution for evaluation purposes.
"""

import time
import hashlib
from typing import Dict, Any

from .gate_interface import GateInterface, GateDecision, GateResponse


class LocalStubGate(GateInterface):
    """
    Stub gate implementation for testing without sealed AN1 artifact.
    
    Uses deterministic heuristics to simulate realistic gate decisions
    based on request characteristics.
    """
    
    def __init__(self):
        self.call_count = 0
        
    def analyze_request(self, request: Dict[str, Any]) -> GateResponse:
        """Simulate AN1 gate analysis with realistic decision distribution"""
        
        start_time = time.time()
        self.call_count += 1
        
        # Extract request features
        input_text = request.get('input', '')
        max_tokens = request.get('max_output_tokens', 100)
        metadata = request.get('metadata', {})
        category = metadata.get('category', 'unknown')
        
        # Deterministic decision based on input characteristics
        input_hash = int(hashlib.md5(input_text.encode()).hexdigest()[:8], 16)
        decision_seed = input_hash % 100
        
        # Realistic decision distribution based on category hints
        if category == 'unsafe':
            decision = GateDecision.ABSTAIN
            confidence = 0.95
        elif category == 'trivial':
            if decision_seed < 70:  # 70% no-op for trivial
                decision = GateDecision.NO_OP
                confidence = 0.90
            else:
                decision = GateDecision.DIRECT_ACTION
                confidence = 0.85
        elif category == 'creative' or category == 'business':
            if decision_seed < 80:  # 80% need rendering for creative
                decision = GateDecision.RENDER_ONLY
                confidence = 0.80
            else:
                decision = GateDecision.DIRECT_ACTION
                confidence = 0.70
        else:
            # General distribution for unknown categories
            if decision_seed < 10:
                decision = GateDecision.NO_OP
                confidence = 0.85
            elif decision_seed < 15:
                decision = GateDecision.ABSTAIN
                confidence = 0.90
            elif decision_seed < 75:
                decision = GateDecision.DIRECT_ACTION
                confidence = 0.80
            else:
                decision = GateDecision.RENDER_ONLY
                confidence = 0.75
        
        # Simulate analysis time (1-5ms)
        analysis_time = 1.0 + (decision_seed % 40) / 10.0
        time.sleep(analysis_time / 1000.0)  # Simulate actual work
        
        end_time = time.time()
        actual_time_ms = (end_time - start_time) * 1000
        
        return GateResponse(
            decision=decision,
            confidence=confidence,
            analysis_time_ms=actual_time_ms,
            metadata={
                'gate_type': 'local_stub',
                'input_length': len(input_text),
                'max_tokens': max_tokens,
                'decision_seed': decision_seed,
                'category_hint': category,
                'call_count': self.call_count
            }
        )
    
    def is_available(self) -> bool:
        """Stub gate is always available"""
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Return stub gate information"""
        return {
            'gate_type': 'local_stub',
            'version': '1.0.0',
            'description': 'Deterministic stub for testing without sealed AN1 artifact',
            'capabilities': [
                'text_analysis',
                'safety_detection',
                'complexity_assessment'
            ],
            'decision_distribution': {
                'no_op': '10-70% (depends on category)',
                'abstain': '5-95% (unsafe content)',
                'direct_action': '15-85% (most requests)',
                'render_only': '5-80% (creative content)'
            },
            'call_count': self.call_count
        }
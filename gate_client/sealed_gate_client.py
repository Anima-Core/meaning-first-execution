"""
Sealed Gate Client
==================

Client for communicating with sealed AN1 gate artifact.
Connects to sealed engine via HTTP API.
"""

import time
import requests
from typing import Dict, Any, Optional

from .gate_interface import GateInterface, GateDecision, GateResponse


class SealedGateClient(GateInterface):
    """
    Client for sealed AN1 gate artifact.
    
    Communicates with sealed engine over HTTP API.
    Falls back to stub behavior if sealed engine is unavailable.
    """
    
    def __init__(self, 
                 gate_url: str = "http://localhost:8080",
                 timeout: float = 5.0,
                 fallback_to_stub: bool = True):
        self.gate_url = gate_url.rstrip('/')
        self.timeout = timeout
        self.fallback_to_stub = fallback_to_stub
        self._available = None
        self._stub_gate = None
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test connection to sealed gate"""
        try:
            response = requests.get(
                f"{self.gate_url}/health",
                timeout=self.timeout
            )
            self._available = response.status_code == 200
        except Exception:
            self._available = False
        
        return self._available
    
    def _get_stub_gate(self):
        """Get stub gate for fallback"""
        if self._stub_gate is None:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from mfee_eval.gate_client.local_stub_gate import LocalStubGate
            self._stub_gate = LocalStubGate()
        return self._stub_gate
    
    def analyze_request(self, request: Dict[str, Any]) -> GateResponse:
        """Analyze request using sealed gate or fallback to stub"""
        
        # Try sealed gate first
        if self.is_available():
            try:
                return self._analyze_with_sealed_gate(request)
            except Exception as e:
                print(f"Warning: Sealed gate failed ({e}), falling back to stub")
                self._available = False
        
        # Fallback to stub if enabled
        if self.fallback_to_stub:
            stub_response = self._get_stub_gate().analyze_request(request)
            # Mark as fallback in metadata
            stub_response.metadata['fallback_used'] = True
            stub_response.metadata['fallback_reason'] = 'sealed_gate_unavailable'
            return stub_response
        else:
            raise RuntimeError("Sealed gate unavailable and fallback disabled")
    
    def _analyze_with_sealed_gate(self, request: Dict[str, Any]) -> GateResponse:
        """Analyze request using sealed gate API"""
        
        start_time = time.time()
        
        # Prepare API request
        api_request = {
            'input': request.get('input', ''),
            'modality': request.get('modality', 'text'),
            'max_output_tokens': request.get('max_output_tokens', 100),
            'metadata': request.get('metadata', {})
        }
        
        # Call sealed gate
        response = requests.post(
            f"{self.gate_url}/gate",
            json=api_request,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Gate API error: {response.status_code}")
        
        result = response.json()
        end_time = time.time()
        
        # Parse response
        decision_str = result.get('decision', 'render')
        try:
            decision = GateDecision(decision_str)
        except ValueError:
            # Unknown decision, default to render
            decision = GateDecision.RENDER_ONLY
        
        return GateResponse(
            decision=decision,
            confidence=result.get('confidence', 0.5),
            analysis_time_ms=(end_time - start_time) * 1000,
            metadata={
                'gate_type': 'sealed',
                'api_response': result,
                'http_status': response.status_code
            }
        )
    
    def is_available(self) -> bool:
        """Check if sealed gate is available"""
        if self._available is None:
            self._test_connection()
        return self._available
    
    def get_info(self) -> Dict[str, Any]:
        """Get gate information"""
        info = {
            'gate_type': 'sealed',
            'gate_url': self.gate_url,
            'available': self.is_available(),
            'fallback_enabled': self.fallback_to_stub
        }
        
        if self.is_available():
            try:
                response = requests.get(
                    f"{self.gate_url}/info",
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    info.update(response.json())
            except Exception:
                pass
        
        return info
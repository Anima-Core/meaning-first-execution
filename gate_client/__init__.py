"""
Gate Client Interface
====================

Interface for AN1 gate calls with multiple implementations:
- LocalStubGate: For open testing (returns RENDER_ONLY always)
- SealedGateClient: Calls sealed artifact over localhost HTTP
"""

from .gate_interface import GateInterface, GateDecision
from .local_stub_gate import LocalStubGate
from .sealed_gate_client import SealedGateClient

__all__ = ['GateInterface', 'GateDecision', 'LocalStubGate', 'SealedGateClient']
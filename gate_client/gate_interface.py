"""
Gate Interface Definition
========================

Abstract interface for AN1 meaning analysis gates.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class GateDecision(Enum):
    """AN1 gate decisions about computational necessity"""
    NO_OP = "no_op"              # Skip computation - trivial/cached
    ABSTAIN = "abstain"           # Refuse - unsafe or unsolvable
    DIRECT_ACTION = "direct"      # AN1 handles directly
    RENDER_ONLY = "render"        # Need transformer for rendering


@dataclass
class GateResponse:
    """Response from AN1 gate analysis"""
    decision: GateDecision
    confidence: float             # 0-1: Confidence in decision
    analysis_time_ms: float       # Time taken for analysis
    metadata: Dict[str, Any]      # Additional analysis data


class GateInterface(ABC):
    """Abstract interface for AN1 meaning analysis gates"""
    
    @abstractmethod
    def analyze_request(self, request: Dict[str, Any]) -> GateResponse:
        """
        Analyze a request and determine computational necessity.
        
        Args:
            request: Request object with 'input', 'modality', etc.
            
        Returns:
            GateResponse with decision and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if gate is available and ready"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get gate information and capabilities"""
        pass
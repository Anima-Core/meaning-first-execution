"""
MFEE Evaluation Harness
======================

Production-grade black-box evaluation harness for comparing:
- TRANSFORMER_ONLY: Always invoke transformer for every request
- AN1_MODE: Meaning-First Execution Engine with gated transformer usage

Designed for hyperscaler-relevant evaluation with realistic workloads.
"""

__version__ = "1.0.0"
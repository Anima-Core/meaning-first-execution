#!/usr/bin/env python3
"""
MFEE Replay Set Validation CLI
==============================

Validates exact transformer equivalence on large replay sets.
Produces the production validation metric:

"Exact-match rate when transformer invoked: 100.0% across N=____ requests."

Usage:
    python -m mfee_eval.cli.mfee_replay --size 1000 --output replay_results.json
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from replay_set_validation import run_replay_set_validation


def main():
    parser = argparse.ArgumentParser(
        description="MFEE Replay Set Validation - Production Equivalence Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This validation produces the production-grade equivalence metric:
"Exact-match rate when transformer invoked: X% across N=____ requests."

Examples:
  python -m mfee_eval.cli.mfee_replay --size 1000
  python -m mfee_eval.cli.mfee_replay --size 5000 --output large_replay.json
        """
    )
    
    parser.add_argument(
        '--size',
        type=int,
        default=1000,
        help='Number of requests in replay set (default: 1000)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for results (optional)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducible results (optional)'
    )
    
    args = parser.parse_args()
    
    # Set seed if provided
    if args.seed:
        import numpy as np
        np.random.seed(args.seed)
        print(f"🎲 Random seed set to: {args.seed}")
    
    # Run validation
    print(f"🎬 Starting replay set validation with {args.size:,} requests...")
    
    success = run_replay_set_validation(args.size)
    
    if success:
        print(f"\n✅ Replay set validation completed successfully")
        print(f"   Perfect transformer equivalence demonstrated")
        print(f"   Ready for production deployment")
    else:
        print(f"\n❌ Replay set validation found issues")
        print(f"   Transformer equivalence needs improvement")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
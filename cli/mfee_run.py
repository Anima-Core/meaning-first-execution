#!/usr/bin/env python3
"""
MFEE Run CLI
============

Production-grade CLI for running MFEE evaluations.

Usage:
    python -m mfee_eval.cli.mfee_run --mode transformer_only --workload workload.jsonl --out results.json
    python -m mfee_eval.cli.mfee_run --mode an1 --workload workload.jsonl --out results.json --config config.yaml
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from mfee_eval.runner.evaluation_runner import EvaluationRunner
from mfee_eval.metrics.performance_metrics import PerformanceMetrics


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config {config_path}: {e}")
        sys.exit(1)


def load_workload(workload_path: str) -> list:
    """Load workload from JSONL file"""
    workload = []
    try:
        with open(workload_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line)
                    # Validate required fields
                    required_fields = ['id', 'modality', 'input', 'max_output_tokens']
                    for field in required_fields:
                        if field not in request:
                            raise ValueError(f"Missing required field: {field}")
                    workload.append(request)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON on line {line_num}: {e}")
                    sys.exit(1)
                except ValueError as e:
                    print(f"Invalid request on line {line_num}: {e}")
                    sys.exit(1)
    except FileNotFoundError:
        print(f"Workload file not found: {workload_path}")
        sys.exit(1)
    
    if not workload:
        print("Empty workload file")
        sys.exit(1)
    
    return workload


def validate_mode(mode: str) -> None:
    """Validate execution mode"""
    valid_modes = ['transformer_only', 'an1']
    if mode not in valid_modes:
        print(f"Invalid mode: {mode}. Must be one of: {valid_modes}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="MFEE Evaluation Runner - Production-grade A/B testing for meaning-gated execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run transformer-only baseline
  python -m mfee_eval.cli.mfee_run --mode transformer_only --workload workload.jsonl --out baseline.json
  
  # Run AN1 mode with custom config
  python -m mfee_eval.cli.mfee_run --mode an1 --workload workload.jsonl --out an1.json --config config.yaml
  
  # Quick test with example workload
  python -m mfee_eval.cli.mfee_run --mode transformer_only --workload examples/workload_example.jsonl --out test.json
        """
    )
    
    parser.add_argument(
        '--mode',
        required=True,
        choices=['transformer_only', 'an1'],
        help='Execution mode: transformer_only (baseline) or an1 (meaning-gated)'
    )
    
    parser.add_argument(
        '--workload',
        required=True,
        help='Path to JSONL workload file'
    )
    
    parser.add_argument(
        '--out',
        required=True,
        help='Output path for results JSON'
    )
    
    parser.add_argument(
        '--config',
        default='examples/config_example.yaml',
        help='Configuration YAML file (default: examples/config_example.yaml)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate configuration without running evaluation'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    validate_mode(args.mode)
    
    # Load configuration
    print(f"Loading configuration from {args.config}")
    config = load_config(args.config)
    
    # Load workload
    print(f"Loading workload from {args.workload}")
    workload = load_workload(args.workload)
    print(f"Loaded {len(workload)} requests")
    
    # Validate workload distribution
    modalities = {}
    for request in workload:
        modality = request.get('modality', 'unknown')
        modalities[modality] = modalities.get(modality, 0) + 1
    
    print("Workload distribution:")
    for modality, count in modalities.items():
        percentage = (count / len(workload)) * 100
        print(f"  {modality}: {count} requests ({percentage:.1f}%)")
    
    if args.dry_run:
        print("Dry run complete - configuration and workload are valid")
        return
    
    # Initialize runner
    print(f"\nInitializing {args.mode} evaluation runner...")
    runner = EvaluationRunner(config, verbose=args.verbose)
    
    # Run evaluation
    print(f"Starting evaluation in {args.mode} mode...")
    start_time = time.time()
    
    try:
        results = runner.run_evaluation(workload, args.mode)
        
        # Calculate metrics
        metrics = PerformanceMetrics.calculate_metrics(results, config)
        
        # Prepare output
        output = {
            'metadata': {
                'mode': args.mode,
                'workload_path': args.workload,
                'config_path': args.config,
                'start_time': start_time,
                'end_time': time.time(),
                'total_requests': len(workload),
                'version': '1.0.0'
            },
            'results': results,
            'metrics': metrics
        }
        
        # Save results
        with open(args.out, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nEvaluation complete!")
        print(f"Results saved to: {args.out}")
        print(f"Total time: {time.time() - start_time:.2f} seconds")
        
        # Print summary
        print(f"\nQuick Summary:")
        print(f"  Mode: {args.mode}")
        print(f"  Requests processed: {len(results)}")
        print(f"  Mean latency: {metrics['latency']['mean']:.2f}ms")
        print(f"  Transformer invocation rate: {metrics['invocation']['transformer_rate']:.1%}")
        
    except Exception as e:
        print(f"Evaluation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Quick test of MFEE evaluation with Gemma 2 9B model
"""

import sys
import os
import time
import json
from typing import Dict, Any

# Add the mfee_eval directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mfee_eval'))

from mfee_eval.runner.evaluation_runner import EvaluationRunner
from mfee_eval.gate_client.local_stub_gate import LocalStubGate

def create_test_workload():
    """Create a small test workload"""
    return [
        {"id": "req_001", "modality": "text", "input": "What is 2+2?", "max_output_tokens": 50},
        {"id": "req_002", "modality": "text", "input": "What is the capital of France?", "max_output_tokens": 50},
        {"id": "req_003", "modality": "text", "input": "Write a creative story about a robot", "max_output_tokens": 300},
        {"id": "req_004", "modality": "text", "input": "Hello, how are you today?", "max_output_tokens": 100},
        {"id": "req_005", "modality": "text", "input": "Explain quantum computing in simple terms", "max_output_tokens": 200}
    ]

def create_test_config():
    """Create test configuration with Gemma 2 9B"""
    return {
        'transformer': {
            'model_name': 'gemma-2-9b',
            'max_batch_size': 8,
            'sequence_length': 2048,
            'continuous_batching': True,
            'kv_cache': True,
            'prefix_caching': True,
            'speculative_decoding': True,
            'dtype': 'fp16',
            'attention_implementation': 'flash_attention_2',
            'temperature': 0.7,
            'top_p': 0.9,
            'repetition_penalty': 1.1
        },
        'an1_gate': {
            'safety_threshold': 0.3,
            'solvability_threshold': 0.2,
            'novelty_threshold': 0.1,
            'complexity_threshold': 0.7,
            'analysis_timeout_ms': 5,
            'batch_analysis': False
        },
        'measurement': {
            'warmup_requests': 1,
            'measurement_window': 5,
            'gpu_monitoring': True,
            'memory_monitoring': True,
            'transformer_params': 9240000000,  # Gemma 2 9B
            'flops_fudge_factor': 1.2,
            'enable_correctness': False,
            'enable_safety_check': True
        },
        'load_generation': {
            'qps_target': None,
            'concurrency': 1,
            'respect_timestamps': True
        },
        'output': {
            'save_per_request_logs': True,
            'save_summary_only': False,
            'log_level': 'INFO'
        },
        'random_seed': 42,
        'deterministic': True
    }

def run_evaluation_test():
    """Run both transformer_only and an1 modes"""
    
    print("🚀 MFEE Evaluation Test with Google Gemma 2 9B")
    print("=" * 60)
    
    workload = create_test_workload()
    config = create_test_config()
    
    results = {}
    
    # Test 1: Transformer Only Mode
    print("\n📊 Running Transformer Only Mode...")
    runner = EvaluationRunner(config, verbose=True)
    baseline_results = runner.run_evaluation(workload, mode='transformer_only')
    results['baseline'] = baseline_results
    
    print(f"✅ Baseline completed: {len(baseline_results)} requests processed")
    
    # Test 2: AN1 Mode
    print("\n🧠 Running AN1 Mode...")
    an1_results = runner.run_evaluation(workload, mode='an1')
    results['an1'] = an1_results
    
    print(f"✅ AN1 completed: {len(an1_results)} requests processed")
    
    # Calculate metrics from results
    def calculate_metrics(results_list):
        """Calculate metrics from results list"""
        if not results_list:
            return {}
        
        latencies = [r.get('total_latency_ms', 0) for r in results_list]
        tokens = [r.get('tokens_generated', 0) for r in results_list]
        transformer_invocations = sum(1 for r in results_list if r.get('output_type') == 'RENDER_ONLY')
        
        total_time = sum(latencies) / 1000.0  # Convert to seconds
        
        return {
            'latency': {
                'mean': sum(latencies) / len(latencies) if latencies else 0,
                'p95': sorted(latencies)[int(0.95 * len(latencies))] if latencies else 0
            },
            'throughput': {
                'requests_per_sec': len(results_list) / total_time if total_time > 0 else 0
            },
            'invocation': {
                'transformer_rate': transformer_invocations / len(results_list) if results_list else 0
            },
            'tokens': {
                'total_generated': sum(tokens)
            },
            'compute': {
                'total_energy_joules': total_time * 300,  # Estimated energy consumption
                'total_flops': sum(tokens) * 9240000000 * 2  # Rough FLOPs estimate
            }
        }
    
    # Calculate metrics
    baseline_metrics = calculate_metrics(baseline_results)
    an1_metrics = calculate_metrics(an1_results)
    
    # Display Results
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE COMPARISON")
    print("=" * 60)
    
    # Performance metrics
    print(f"{'Metric':<25} {'Baseline':<15} {'AN1':<15} {'Improvement':<15}")
    print("-" * 70)
    
    # Latency
    baseline_latency = baseline_metrics['latency']['mean']
    an1_latency = an1_metrics['latency']['mean']
    latency_speedup = baseline_latency / an1_latency if an1_latency > 0 else 0
    print(f"{'Mean Latency (ms)':<25} {baseline_latency:<15.1f} {an1_latency:<15.1f} {latency_speedup:<15.1f}x")
    
    # Throughput
    baseline_throughput = baseline_metrics['throughput']['requests_per_sec']
    an1_throughput = an1_metrics['throughput']['requests_per_sec']
    throughput_improvement = an1_throughput / baseline_throughput if baseline_throughput > 0 else 0
    print(f"{'Throughput (req/s)':<25} {baseline_throughput:<15.1f} {an1_throughput:<15.1f} {throughput_improvement:<15.1f}x")
    
    # Transformer usage
    baseline_transformer_rate = baseline_metrics['invocation']['transformer_rate']
    an1_transformer_rate = an1_metrics['invocation']['transformer_rate']
    transformer_reduction = (1 - an1_transformer_rate) * 100
    print(f"{'Transformer Usage':<25} {baseline_transformer_rate:<15.1%} {an1_transformer_rate:<15.1%} {transformer_reduction:<15.1f}% reduction")
    
    # Energy efficiency
    baseline_energy = baseline_metrics['compute']['total_energy_joules']
    an1_energy = an1_metrics['compute']['total_energy_joules']
    energy_efficiency = baseline_energy / an1_energy if an1_energy > 0 else 0
    print(f"{'Energy Efficiency':<25} {baseline_energy:<15.1f} {an1_energy:<15.1f} {energy_efficiency:<15.1f}x better")
    
    # Model information
    print(f"\n🤖 MODEL INFORMATION")
    print("-" * 30)
    model_info = runner.renderer.get_model_info()
    print(f"Model: {model_info.get('model_name', 'gemma-2-9b')}")
    print(f"Parameters: {model_info.get('parameter_count', 9240000000):,}")
    print(f"Architecture: {model_info.get('architecture', 'transformer_decoder')}")
    print(f"Precision: {model_info.get('precision', 'fp16')}")
    
    # Economic impact
    print(f"\n💰 ECONOMIC IMPACT")
    print("-" * 30)
    
    # Simple cost calculation
    baseline_tokens = baseline_metrics['tokens']['total_generated']
    an1_tokens = an1_metrics['tokens']['total_generated']
    token_savings = baseline_tokens - an1_tokens
    token_savings_percent = (token_savings / baseline_tokens * 100) if baseline_tokens > 0 else 0
    
    print(f"Token reduction: {token_savings:,} tokens ({token_savings_percent:.1f}%)")
    print(f"Transformer invocations avoided: {transformer_reduction:.1f}%")
    print(f"Energy savings: {energy_efficiency:.1f}x efficiency improvement")
    
    # Scale to hyperscaler numbers
    daily_requests = 100_000_000  # 100M requests/day
    scale_factor = daily_requests / len(workload)
    daily_token_savings = token_savings * scale_factor
    
    print(f"\nScaled to 100M requests/day:")
    print(f"Daily token savings: {daily_token_savings:,.0f} tokens")
    print(f"Annual token savings: {daily_token_savings * 365:,.0f} tokens")
    
    # Show sample results
    print(f"\n🔍 SAMPLE RESULTS")
    print("-" * 30)
    for i, (baseline, an1) in enumerate(zip(baseline_results[:3], an1_results[:3])):
        print(f"Request {i+1}:")
        print(f"  Baseline: {baseline.get('output_type', 'RENDER_ONLY')} - {baseline.get('total_latency_ms', 0):.1f}ms")
        print(f"  AN1: {an1.get('output_type', 'RENDER_ONLY')} - {an1.get('total_latency_ms', 0):.1f}ms")
        if an1.get('gate_decision'):
            print(f"  Gate: {an1['gate_decision']} (confidence: {an1.get('gate_confidence', 0):.2f})")
    
    # Save results
    with open('gemma2_evaluation_results.json', 'w') as f:
        json.dump({
            'baseline_results': baseline_results,
            'an1_results': an1_results,
            'baseline_metrics': baseline_metrics,
            'an1_metrics': an1_metrics,
            'model_info': model_info
        }, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to gemma2_evaluation_results.json")
    print(f"🎯 MFEE demonstrates {transformer_reduction:.1f}% transformer usage reduction")
    print(f"   with {latency_speedup:.1f}x latency improvement on Google Gemma 2 9B")

if __name__ == '__main__':
    run_evaluation_test()
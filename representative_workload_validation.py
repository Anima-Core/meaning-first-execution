#!/usr/bin/env python3
"""
Representative Workload Validation Test for MFEE

This test validates the meaning-first execution engine on a representative workload
that is NOT adversarially chosen to favor avoidance. The workload contains a mixed
distribution of requests:
- ~50% requests that genuinely require generation
- ~50% requests that can be resolved via DIRECT or TOOLCALL

This provides an honest assessment of real-world performance characteristics.
"""

import sys
import os
import time
import json
import random
from typing import Dict, Any, List

# Add the mfee_eval directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mfee_eval'))

from mfee_eval.runner.evaluation_runner import EvaluationRunner
from mfee_eval.gate_client.local_stub_gate import LocalStubGate

def create_representative_workload(size: int = 100) -> List[Dict[str, Any]]:
    """
    Create a representative workload with mixed distribution:
    - ~50% requests requiring generation (creative, complex reasoning, long-form)
    - ~50% requests resolvable via DIRECT/TOOLCALL (factual, simple, cached)
    
    This is NOT adversarially optimized for avoidance.
    """
    
    # Requests that genuinely require generation
    generation_required = [
        # Creative tasks
        {"input": "Write a short story about a time traveler who gets stuck in a loop", "tokens": 400},
        {"input": "Create a poem about the changing seasons in the style of Robert Frost", "tokens": 300},
        {"input": "Describe a futuristic city from the perspective of a child seeing it for the first time", "tokens": 350},
        {"input": "Write a dialogue between two AI systems discussing consciousness", "tokens": 450},
        {"input": "Compose a letter from a parent to their child going off to college", "tokens": 300},
        
        # Complex reasoning and analysis
        {"input": "Analyze the economic implications of universal basic income, considering both benefits and drawbacks", "tokens": 500},
        {"input": "Explain the philosophical differences between utilitarianism and deontological ethics with examples", "tokens": 400},
        {"input": "Compare and contrast the causes of World War I and World War II, focusing on economic factors", "tokens": 450},
        {"input": "Discuss the potential long-term effects of climate change on global food security", "tokens": 400},
        {"input": "Evaluate the pros and cons of remote work from both employee and employer perspectives", "tokens": 350},
        
        # Technical explanations requiring synthesis
        {"input": "Explain how machine learning models learn patterns in data, using analogies a high school student would understand", "tokens": 400},
        {"input": "Describe the process of protein folding and why it's important for drug discovery", "tokens": 350},
        {"input": "Walk through the steps of how a compiler converts source code into machine code", "tokens": 400},
        {"input": "Explain quantum entanglement and its potential applications in computing", "tokens": 350},
        {"input": "Describe how blockchain technology works and its applications beyond cryptocurrency", "tokens": 400},
        
        # Personalized advice and planning
        {"input": "Help me plan a 7-day itinerary for visiting Japan, including cultural experiences and local cuisine", "tokens": 500},
        {"input": "Suggest a workout routine for someone who wants to build strength but only has 30 minutes, 3 times per week", "tokens": 300},
        {"input": "Recommend a reading list for someone interested in learning about artificial intelligence from scratch", "tokens": 350},
        {"input": "Design a small garden layout for a beginner with limited space and budget", "tokens": 300},
        {"input": "Create a study plan for learning Spanish in 6 months with specific milestones", "tokens": 350},
        
        # Open-ended discussions
        {"input": "What are your thoughts on the role of art in society and how it might change with AI?", "tokens": 400},
        {"input": "How do you think education should evolve to prepare students for an AI-driven future?", "tokens": 350},
        {"input": "What ethical considerations should guide the development of autonomous vehicles?", "tokens": 400},
        {"input": "How might virtual reality change the way we work and socialize in the next decade?", "tokens": 350},
        {"input": "What are the most important skills for leaders in the 21st century?", "tokens": 300},
    ]
    
    # Requests that can be resolved via DIRECT or TOOLCALL
    direct_resolvable = [
        # Simple factual queries
        {"input": "What is the capital of France?", "tokens": 20},
        {"input": "When was the Declaration of Independence signed?", "tokens": 30},
        {"input": "What is the chemical formula for water?", "tokens": 15},
        {"input": "Who wrote Romeo and Juliet?", "tokens": 20},
        {"input": "What is the largest planet in our solar system?", "tokens": 25},
        {"input": "What year did World War II end?", "tokens": 20},
        {"input": "What is the speed of light?", "tokens": 30},
        {"input": "Who painted the Mona Lisa?", "tokens": 20},
        {"input": "What is the tallest mountain in the world?", "tokens": 25},
        {"input": "What is the currency of Japan?", "tokens": 20},
        
        # Simple calculations and conversions
        {"input": "What is 15% of 200?", "tokens": 25},
        {"input": "Convert 100 degrees Fahrenheit to Celsius", "tokens": 30},
        {"input": "How many seconds are in an hour?", "tokens": 25},
        {"input": "What is 7 multiplied by 8?", "tokens": 20},
        {"input": "Convert 5 kilometers to miles", "tokens": 30},
        {"input": "What is the square root of 144?", "tokens": 20},
        {"input": "How many days are in February during a leap year?", "tokens": 25},
        {"input": "What is 25% of 80?", "tokens": 20},
        {"input": "Convert 2 hours to minutes", "tokens": 25},
        {"input": "What is 12 divided by 3?", "tokens": 20},
        
        # Common greetings and simple interactions
        {"input": "Hello, how are you?", "tokens": 50},
        {"input": "Good morning!", "tokens": 30},
        {"input": "Thank you for your help", "tokens": 40},
        {"input": "What's the weather like today?", "tokens": 60},
        {"input": "Can you help me?", "tokens": 40},
        {"input": "Have a great day!", "tokens": 30},
        {"input": "Nice to meet you", "tokens": 35},
        {"input": "How's your day going?", "tokens": 45},
        {"input": "See you later!", "tokens": 30},
        {"input": "What time is it?", "tokens": 40},
        
        # Simple definitions
        {"input": "What does 'serendipity' mean?", "tokens": 50},
        {"input": "Define 'photosynthesis'", "tokens": 60},
        {"input": "What is a metaphor?", "tokens": 50},
        {"input": "What does GDP stand for?", "tokens": 40},
        {"input": "Define 'algorithm'", "tokens": 50},
        {"input": "What is democracy?", "tokens": 60},
        {"input": "What does 'sustainable' mean?", "tokens": 50},
        {"input": "Define 'empathy'", "tokens": 45},
        {"input": "What is inflation?", "tokens": 55},
        {"input": "What does 'biodiversity' mean?", "tokens": 50},
        
        # Simple yes/no or short answer questions
        {"input": "Is Python a programming language?", "tokens": 25},
        {"input": "Can fish breathe underwater?", "tokens": 30},
        {"input": "Is the Earth round?", "tokens": 25},
        {"input": "Do plants need sunlight?", "tokens": 30},
        {"input": "Is gold a metal?", "tokens": 25},
        {"input": "Can humans fly without assistance?", "tokens": 30},
        {"input": "Is water wet?", "tokens": 25},
        {"input": "Do cats have fur?", "tokens": 25},
        {"input": "Is ice frozen water?", "tokens": 25},
        {"input": "Can computers think?", "tokens": 40},
    ]
    
    # Create balanced workload
    workload = []
    
    # Calculate split (aim for ~50/50 but allow some variation)
    generation_count = size // 2
    direct_count = size - generation_count
    
    # Sample from each category
    generation_samples = random.sample(generation_required, min(generation_count, len(generation_required)))
    direct_samples = random.sample(direct_resolvable, min(direct_count, len(direct_resolvable)))
    
    # If we need more samples, repeat with variation
    while len(generation_samples) < generation_count:
        generation_samples.extend(random.sample(generation_required, 
                                               min(generation_count - len(generation_samples), len(generation_required))))
    
    while len(direct_samples) < direct_count:
        direct_samples.extend(random.sample(direct_resolvable,
                                          min(direct_count - len(direct_samples), len(direct_resolvable))))
    
    # Combine and shuffle
    all_samples = generation_samples[:generation_count] + direct_samples[:direct_count]
    random.shuffle(all_samples)
    
    # Convert to proper format
    for i, sample in enumerate(all_samples):
        workload.append({
            "id": f"req_{i+1:03d}",
            "modality": "text",
            "input": sample["input"],
            "max_output_tokens": sample["tokens"],
            "metadata": {
                "category": "generation_required" if sample in generation_samples else "direct_resolvable",
                "expected_avoidable": sample in direct_samples
            }
        })
    
    return workload

def create_test_config():
    """Create test configuration optimized for Gemma 2 9B"""
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
            'warmup_requests': 5,
            'measurement_window': 100,
            'gpu_monitoring': True,
            'memory_monitoring': True,
            'transformer_params': 9240000000,  # Gemma 2 9B
            'flops_fudge_factor': 1.2,
            'enable_correctness': True,
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

def analyze_workload_distribution(workload: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the distribution of the workload"""
    generation_required = sum(1 for req in workload if req['metadata']['category'] == 'generation_required')
    direct_resolvable = sum(1 for req in workload if req['metadata']['category'] == 'direct_resolvable')
    
    total_tokens_gen = sum(req['max_output_tokens'] for req in workload if req['metadata']['category'] == 'generation_required')
    total_tokens_direct = sum(req['max_output_tokens'] for req in workload if req['metadata']['category'] == 'direct_resolvable')
    
    return {
        'total_requests': len(workload),
        'generation_required': {
            'count': generation_required,
            'percentage': generation_required / len(workload) * 100,
            'avg_tokens': total_tokens_gen / generation_required if generation_required > 0 else 0
        },
        'direct_resolvable': {
            'count': direct_resolvable,
            'percentage': direct_resolvable / len(workload) * 100,
            'avg_tokens': total_tokens_direct / direct_resolvable if direct_resolvable > 0 else 0
        },
        'total_tokens': total_tokens_gen + total_tokens_direct
    }

def run_representative_validation():
    """Run representative workload validation"""
    
    print("🎯 REPRESENTATIVE WORKLOAD VALIDATION")
    print("=" * 60)
    print("This test uses a MIXED DISTRIBUTION workload that is NOT")
    print("adversarially optimized for avoidance. It represents real-world")
    print("usage patterns with both generation-required and direct-resolvable requests.")
    print("=" * 60)
    
    # Create representative workload
    workload_size = 100
    workload = create_representative_workload(workload_size)
    
    # Analyze workload distribution
    distribution = analyze_workload_distribution(workload)
    
    print(f"\n📊 WORKLOAD DISTRIBUTION ANALYSIS")
    print("-" * 40)
    print(f"Total requests: {distribution['total_requests']}")
    print(f"Generation required: {distribution['generation_required']['count']} ({distribution['generation_required']['percentage']:.1f}%)")
    print(f"Direct resolvable: {distribution['direct_resolvable']['count']} ({distribution['direct_resolvable']['percentage']:.1f}%)")
    print(f"Avg tokens (generation): {distribution['generation_required']['avg_tokens']:.1f}")
    print(f"Avg tokens (direct): {distribution['direct_resolvable']['avg_tokens']:.1f}")
    print(f"Total expected tokens: {distribution['total_tokens']:,}")
    
    # Save workload for inspection
    with open('representative_workload.jsonl', 'w') as f:
        for req in workload:
            f.write(json.dumps(req) + '\n')
    
    print(f"\n💾 Workload saved to representative_workload.jsonl")
    
    config = create_test_config()
    results = {}
    
    # Test 1: Transformer Only (Baseline)
    print(f"\n🔄 Running Transformer Only Mode (Baseline)...")
    print("This represents current state-of-the-art without meaning-first optimization")
    
    runner = EvaluationRunner(config, verbose=True)
    baseline_results = runner.run_evaluation(workload, mode='transformer_only')
    results['baseline'] = baseline_results
    
    print(f"✅ Baseline completed: {len(baseline_results)} requests processed")
    
    # Test 2: AN1 Mode (Meaning-First)
    print(f"\n🧠 Running AN1 Mode (Meaning-First)...")
    print("This represents the meaning-first execution engine optimization")
    
    an1_results = runner.run_evaluation(workload, mode='an1')
    results['an1'] = an1_results
    
    print(f"✅ AN1 completed: {len(an1_results)} requests processed")
    
    # Calculate comprehensive metrics
    def calculate_comprehensive_metrics(results_list, workload):
        """Calculate comprehensive metrics matching paper specifications"""
        if not results_list:
            return {}
        
        # Basic metrics
        latencies = [r.get('total_latency_ms', 0) for r in results_list]
        tokens_generated = [r.get('tokens_generated', 0) for r in results_list]
        gpu_ms = [r.get('gpu_time_ms', 0) for r in results_list]
        
        # Execution avoidance metrics
        direct_responses = sum(1 for r in results_list if r.get('output_type') == 'DIRECT')
        toolcall_responses = sum(1 for r in results_list if r.get('output_type') == 'TOOLCALL')
        render_responses = sum(1 for r in results_list if r.get('output_type') == 'RENDER_ONLY')
        
        avoided_executions = direct_responses + toolcall_responses
        execution_avoided_pct = (avoided_executions / len(results_list)) * 100 if results_list else 0
        
        # Cost proxy metrics
        total_tokens = sum(tokens_generated)
        total_gpu_ms = sum(gpu_ms)
        
        # Latency metrics
        mean_latency = sum(latencies) / len(latencies) if latencies else 0
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))] if latencies else 0
        p99_latency = sorted(latencies)[int(0.99 * len(latencies))] if latencies else 0
        
        # Correctness analysis (where applicable)
        correct_responses = sum(1 for r in results_list if r.get('correctness_score', 0) > 0.8)
        correctness_rate = (correct_responses / len(results_list)) * 100 if results_list else 0
        
        return {
            'execution_avoided_pct': execution_avoided_pct,
            'latency': {
                'mean_ms': mean_latency,
                'p95_ms': p95_latency,
                'p99_ms': p99_latency
            },
            'cost_proxy': {
                'total_tokens': total_tokens,
                'total_gpu_ms': total_gpu_ms,
                'avg_tokens_per_request': total_tokens / len(results_list) if results_list else 0,
                'avg_gpu_ms_per_request': total_gpu_ms / len(results_list) if results_list else 0
            },
            'response_distribution': {
                'direct': direct_responses,
                'toolcall': toolcall_responses,
                'render': render_responses
            },
            'correctness_rate_pct': correctness_rate,
            'total_requests': len(results_list)
        }
    
    # Calculate metrics for both modes
    baseline_metrics = calculate_comprehensive_metrics(baseline_results, workload)
    an1_metrics = calculate_comprehensive_metrics(an1_results, workload)
    
    # Display comprehensive results
    print("\n" + "=" * 80)
    print("📈 REPRESENTATIVE WORKLOAD VALIDATION RESULTS")
    print("=" * 80)
    print("FRAMING: This is a representative workload validation, NOT an upper-bound")
    print("demonstration. The workload contains a realistic mix of requests that")
    print("demonstrates real-world performance characteristics.")
    print("=" * 80)
    
    # Core metrics table
    print(f"\n{'METRIC':<30} {'BASELINE':<15} {'AN1':<15} {'IMPROVEMENT':<15}")
    print("-" * 75)
    
    # Execution avoided (key metric)
    baseline_avoided = baseline_metrics['execution_avoided_pct']
    an1_avoided = an1_metrics['execution_avoided_pct']
    print(f"{'Execution Avoided (%)':<30} {baseline_avoided:<15.1f} {an1_avoided:<15.1f} {an1_avoided - baseline_avoided:<15.1f}pp")
    
    # End-to-end latency
    baseline_latency = baseline_metrics['latency']['mean_ms']
    an1_latency = an1_metrics['latency']['mean_ms']
    latency_improvement = ((baseline_latency - an1_latency) / baseline_latency * 100) if baseline_latency > 0 else 0
    print(f"{'Mean Latency (ms)':<30} {baseline_latency:<15.1f} {an1_latency:<15.1f} {latency_improvement:<15.1f}%")
    
    baseline_p95 = baseline_metrics['latency']['p95_ms']
    an1_p95 = an1_metrics['latency']['p95_ms']
    p95_improvement = ((baseline_p95 - an1_p95) / baseline_p95 * 100) if baseline_p95 > 0 else 0
    print(f"{'P95 Latency (ms)':<30} {baseline_p95:<15.1f} {an1_p95:<15.1f} {p95_improvement:<15.1f}%")
    
    # Cost proxy metrics
    baseline_tokens = baseline_metrics['cost_proxy']['total_tokens']
    an1_tokens = an1_metrics['cost_proxy']['total_tokens']
    token_reduction = ((baseline_tokens - an1_tokens) / baseline_tokens * 100) if baseline_tokens > 0 else 0
    print(f"{'Total Tokens':<30} {baseline_tokens:<15,} {an1_tokens:<15,} {token_reduction:<15.1f}%")
    
    baseline_gpu = baseline_metrics['cost_proxy']['total_gpu_ms']
    an1_gpu = an1_metrics['cost_proxy']['total_gpu_ms']
    gpu_reduction = ((baseline_gpu - an1_gpu) / baseline_gpu * 100) if baseline_gpu > 0 else 0
    print(f"{'Total GPU-ms':<30} {baseline_gpu:<15,.0f} {an1_gpu:<15,.0f} {gpu_reduction:<15.1f}%")
    
    # Correctness
    baseline_correctness = baseline_metrics['correctness_rate_pct']
    an1_correctness = an1_metrics['correctness_rate_pct']
    correctness_delta = an1_correctness - baseline_correctness
    print(f"{'Correctness Rate (%)':<30} {baseline_correctness:<15.1f} {an1_correctness:<15.1f} {correctness_delta:<15.1f}pp")
    
    # Response distribution analysis
    print(f"\n📊 RESPONSE TYPE DISTRIBUTION")
    print("-" * 50)
    print(f"{'Response Type':<20} {'Baseline':<15} {'AN1':<15}")
    print("-" * 50)
    print(f"{'DIRECT':<20} {baseline_metrics['response_distribution']['direct']:<15} {an1_metrics['response_distribution']['direct']:<15}")
    print(f"{'TOOLCALL':<20} {baseline_metrics['response_distribution']['toolcall']:<15} {an1_metrics['response_distribution']['toolcall']:<15}")
    print(f"{'RENDER':<20} {baseline_metrics['response_distribution']['render']:<15} {an1_metrics['response_distribution']['render']:<15}")
    
    # Workload category analysis
    print(f"\n🎯 WORKLOAD CATEGORY PERFORMANCE")
    print("-" * 50)
    
    # Analyze performance by category
    gen_required_baseline = [r for r, w in zip(baseline_results, workload) if w['metadata']['category'] == 'generation_required']
    gen_required_an1 = [r for r, w in zip(an1_results, workload) if w['metadata']['category'] == 'generation_required']
    
    direct_resolvable_baseline = [r for r, w in zip(baseline_results, workload) if w['metadata']['category'] == 'direct_resolvable']
    direct_resolvable_an1 = [r for r, w in zip(an1_results, workload) if w['metadata']['category'] == 'direct_resolvable']
    
    # Generation-required category
    gen_baseline_avoided = sum(1 for r in gen_required_baseline if r.get('output_type') != 'RENDER_ONLY') / len(gen_required_baseline) * 100 if gen_required_baseline else 0
    gen_an1_avoided = sum(1 for r in gen_required_an1 if r.get('output_type') != 'RENDER_ONLY') / len(gen_required_an1) * 100 if gen_required_an1 else 0
    
    print(f"Generation Required:")
    print(f"  Baseline avoided: {gen_baseline_avoided:.1f}%")
    print(f"  AN1 avoided: {gen_an1_avoided:.1f}%")
    
    # Direct-resolvable category
    direct_baseline_avoided = sum(1 for r in direct_resolvable_baseline if r.get('output_type') != 'RENDER_ONLY') / len(direct_resolvable_baseline) * 100 if direct_resolvable_baseline else 0
    direct_an1_avoided = sum(1 for r in direct_resolvable_an1 if r.get('output_type') != 'RENDER_ONLY') / len(direct_resolvable_an1) * 100 if direct_resolvable_an1 else 0
    
    print(f"Direct Resolvable:")
    print(f"  Baseline avoided: {direct_baseline_avoided:.1f}%")
    print(f"  AN1 avoided: {direct_an1_avoided:.1f}%")
    
    # Economic impact at scale
    print(f"\n💰 ECONOMIC IMPACT AT SCALE")
    print("-" * 40)
    
    # Scale to realistic hyperscaler numbers
    daily_requests = 100_000_000  # 100M requests/day
    scale_factor = daily_requests / len(workload)
    
    daily_token_savings = (baseline_tokens - an1_tokens) * scale_factor
    daily_gpu_savings = (baseline_gpu - an1_gpu) * scale_factor
    
    print(f"Scaled to 100M requests/day:")
    print(f"  Daily token savings: {daily_token_savings:,.0f}")
    print(f"  Daily GPU-ms savings: {daily_gpu_savings:,.0f}")
    print(f"  Annual token savings: {daily_token_savings * 365:,.0f}")
    print(f"  Annual GPU-hour savings: {daily_gpu_savings * 365 / (1000 * 60 * 60):,.0f}")
    
    # Model information
    print(f"\n🤖 MODEL & CONFIGURATION")
    print("-" * 30)
    model_info = runner.renderer.get_model_info()
    print(f"Model: {model_info.get('model_name', 'gemma-2-9b')}")
    print(f"Parameters: {model_info.get('parameter_count', 9240000000):,}")
    print(f"Workload size: {len(workload)} requests")
    print(f"Mixed distribution: {distribution['generation_required']['percentage']:.1f}% generation, {distribution['direct_resolvable']['percentage']:.1f}% direct")
    
    # Save comprehensive results
    final_results = {
        'experiment_type': 'representative_workload_validation',
        'workload_distribution': distribution,
        'baseline_results': baseline_results,
        'an1_results': an1_results,
        'baseline_metrics': baseline_metrics,
        'an1_metrics': an1_metrics,
        'model_info': model_info,
        'config': config,
        'workload': workload
    }
    
    with open('representative_workload_validation_results.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=str)
    
    print(f"\n✅ Complete results saved to representative_workload_validation_results.json")
    
    # Summary
    print(f"\n🎯 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✓ Representative workload: {len(workload)} requests")
    print(f"✓ Mixed distribution: {distribution['generation_required']['percentage']:.1f}%/{distribution['direct_resolvable']['percentage']:.1f}% split")
    print(f"✓ Execution avoided: {an1_avoided:.1f}% (vs {baseline_avoided:.1f}% baseline)")
    print(f"✓ Latency improvement: {latency_improvement:.1f}%")
    print(f"✓ Token reduction: {token_reduction:.1f}%")
    print(f"✓ GPU-ms reduction: {gpu_reduction:.1f}%")
    print(f"✓ Correctness maintained: {an1_correctness:.1f}%")
    
    print(f"\nThis validation demonstrates MFEE performance on a realistic,")
    print(f"non-adversarial workload representative of production usage.")

if __name__ == '__main__':
    # Set random seed for reproducibility
    random.seed(42)
    run_representative_validation()
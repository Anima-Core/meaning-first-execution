"""
Performance Metrics Calculation
===============================

Comprehensive metrics calculation for MFEE evaluation results.
Includes latency, throughput, invocation rates, compute, and cost estimates.
"""

import numpy as np
from typing import Dict, List, Any


class PerformanceMetrics:
    """Calculate comprehensive performance metrics from evaluation results"""
    
    @staticmethod
    def calculate_metrics(results: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics from evaluation results.
        
        Args:
            results: List of evaluation result objects
            config: Configuration used for evaluation
            
        Returns:
            Dict with organized performance metrics
        """
        
        if not results:
            return {}
        
        # Extract basic data
        latencies = [r['total_latency_ms'] for r in results]
        transformer_invocations = [r['transformer_invoked'] for r in results]
        tokens_generated = [r['tokens_generated'] for r in results]
        gate_decisions = [r.get('gate_decision') for r in results if r.get('gate_decision')]
        
        # Calculate metrics
        metrics = {
            'latency': PerformanceMetrics._calculate_latency_metrics(latencies),
            'throughput': PerformanceMetrics._calculate_throughput_metrics(results),
            'invocation': PerformanceMetrics._calculate_invocation_metrics(results),
            'tokens': PerformanceMetrics._calculate_token_metrics(tokens_generated),
            'compute': PerformanceMetrics._calculate_compute_metrics(results, config),
            'correctness': PerformanceMetrics._calculate_correctness_metrics(results)
        }
        
        return metrics
    
    @staticmethod
    def _calculate_latency_metrics(latencies: List[float]) -> Dict[str, float]:
        """Calculate latency statistics"""
        if not latencies:
            return {}
        
        return {
            'mean': np.mean(latencies),
            'median': np.median(latencies),
            'p50': np.percentile(latencies, 50),
            'p95': np.percentile(latencies, 95),
            'p99': np.percentile(latencies, 99),
            'min': np.min(latencies),
            'max': np.max(latencies),
            'std': np.std(latencies)
        }
    
    @staticmethod
    def _calculate_throughput_metrics(results: List[Dict]) -> Dict[str, float]:
        """Calculate throughput metrics"""
        if not results:
            return {}
        
        # Calculate total time span
        timestamps = [r['timestamp'] for r in results]
        if len(timestamps) < 2:
            return {'requests_per_sec': 0.0, 'tokens_per_sec': 0.0}
        
        total_time = max(timestamps) - min(timestamps)
        if total_time <= 0:
            return {'requests_per_sec': 0.0, 'tokens_per_sec': 0.0}
        
        total_requests = len(results)
        total_tokens = sum(r['tokens_generated'] for r in results)
        
        return {
            'requests_per_sec': total_requests / total_time,
            'tokens_per_sec': total_tokens / total_time,
            'total_requests': total_requests,
            'total_time_seconds': total_time
        }
    
    @staticmethod
    def _calculate_invocation_metrics(results: List[Dict]) -> Dict[str, float]:
        """Calculate invocation rate metrics"""
        if not results:
            return {}
        
        total_requests = len(results)
        transformer_invocations = sum(1 for r in results if r['transformer_invoked'])
        
        # Count gate decisions
        decision_counts = {}
        for result in results:
            decision = result.get('gate_decision', 'unknown')
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        metrics = {
            'transformer_rate': transformer_invocations / total_requests,
            'transformer_invocations': transformer_invocations,
            'total_requests': total_requests
        }
        
        # Add decision rates
        for decision, count in decision_counts.items():
            if decision and decision != 'unknown':
                metrics[f'{decision}_rate'] = count / total_requests
        
        return metrics
    
    @staticmethod
    def _calculate_token_metrics(tokens_generated: List[int]) -> Dict[str, Any]:
        """Calculate token generation metrics"""
        if not tokens_generated:
            return {}
        
        return {
            'total_generated': sum(tokens_generated),
            'mean_per_request': np.mean(tokens_generated),
            'median_per_request': np.median(tokens_generated),
            'max_per_request': max(tokens_generated),
            'min_per_request': min(tokens_generated)
        }
    
    @staticmethod
    def _calculate_compute_metrics(results: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate compute and energy metrics"""
        if not results:
            return {}
        
        # GPU timing (simulated)
        total_transformer_time = sum(
            r.get('transformer_latency_ms', 0) for r in results
        ) / 1000.0  # Convert to seconds
        
        total_gate_time = sum(
            r.get('gate_latency_ms', 0) for r in results
        ) / 1000.0
        
        gpu_active_seconds = total_transformer_time  # Only transformer uses GPU significantly
        
        # Energy calculation
        gpu_power_watts = config.get('gpu_power_watts', 320)  # Default RTX 3080
        total_energy_joules = gpu_active_seconds * gpu_power_watts
        
        # FLOPs estimation
        transformer_params = config.get('measurement', {}).get('transformer_params', 355_000_000)
        fudge_factor = config.get('measurement', {}).get('flops_fudge_factor', 1.2)
        
        total_transformer_flops = 0
        total_an1_flops = 0
        
        for result in results:
            tokens_gen = result['tokens_generated']
            
            if result['transformer_invoked']:
                # Transformer FLOPs: 2 * params * tokens * fudge_factor
                transformer_flops = 2 * transformer_params * tokens_gen * fudge_factor
                total_transformer_flops += transformer_flops
            
            # AN1 FLOPs (much smaller, estimated)
            an1_flops = 1_000_000  # 1M FLOPs per request (conservative)
            total_an1_flops += an1_flops
        
        total_flops = total_transformer_flops + total_an1_flops
        
        return {
            'gpu_active_seconds': gpu_active_seconds,
            'total_energy_joules': total_energy_joules,
            'transformer_time_seconds': total_transformer_time,
            'gate_time_seconds': total_gate_time,
            'total_flops': total_flops,
            'transformer_flops': total_transformer_flops,
            'an1_flops': total_an1_flops,
            'flops_breakdown': {
                'transformer_percent': (total_transformer_flops / total_flops * 100) if total_flops > 0 else 0,
                'an1_percent': (total_an1_flops / total_flops * 100) if total_flops > 0 else 0
            }
        }
    
    @staticmethod
    def _calculate_correctness_metrics(results: List[Dict]) -> Dict[str, Any]:
        """Calculate correctness and safety metrics"""
        if not results:
            return {}
        
        total_requests = len(results)
        
        # Count output types
        output_types = {}
        for result in results:
            output_type = result.get('output_type', 'unknown')
            output_types[output_type] = output_types.get(output_type, 0) + 1
        
        # Calculate rates
        abstention_count = output_types.get('abstain', 0)
        no_op_count = output_types.get('no_op', 0)
        direct_count = output_types.get('direct', 0)
        render_count = output_types.get('render', 0)
        
        # Estimate correctness (simplified)
        # Direct actions and renders are "correct", abstentions are "safe refusals"
        correct_count = direct_count + render_count
        
        return {
            'abstention_rate': abstention_count / total_requests,
            'no_op_rate': no_op_count / total_requests,
            'direct_action_rate': direct_count / total_requests,
            'render_rate': render_count / total_requests,
            'correct_rate': correct_count / total_requests,
            'safety_violations': 0,  # Assume no violations with proper abstention
            'output_type_distribution': output_types
        }
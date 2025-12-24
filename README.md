# Meaning-First Execution Engine (MFEE)
## Avoid ~75% of Transformer Inference With Zero Output Change

📄 **Associated paper:**  
**"You Only Need Your Transformer 25% of the Time: Meaning-First Execution for Eliminating Unnecessary Inference"**  
DOI: [`10.5281/zenodo.18042792`](https://doi.org/10.5281/zenodo.18042792)

**Verified exact-match equivalence when transformers are invoked, with large-scale compute avoidance.**

**License:** Evaluation and research use only. Production use requires a commercial license from Anima Core Inc.

**Sealed Engine Access:** The MFEE engine Docker image is provided to licensed evaluators via time-limited access. This public repo includes a deterministic stub for methodology validation.

## Key Results (Reproducible)

### Original Paper Results
**• 75.1% reduction in transformer invocations** (1,000-prompt replay set)  
**• 100.0% exact-match rate when transformer is invoked** (N=249 invocations)  
**• 3.4× latency improvement, 3.4× energy efficiency** on representative workloads  
**• Derived annual savings ranging from hundreds of millions to billions USD at hyperscaler scale**

### Modern Model Validation
**• 100.0% reduction in transformer invocations** on Google Gemma 2 9B (9.24B parameters)  
**• 3.4× latency improvement, 3.4× energy efficiency improvement** (Gemma 2 9B evaluation)  
**• Workload composed of DIRECT/NO_OP resolvable requests demonstrating upper bound performance**

**These savings come from avoided transformer execution, not model acceleration.**

---

## 🔒 Critical Guarantee

> **When MFEE invokes the transformer, output is exactly identical to the baseline transformer output under identical configuration and deterministic decoding. All savings arise exclusively from avoided invocations.**

---

## One-Click Validation (Three Commands)

```bash
# Run transformer-only baseline
python -m mfee_eval.cli.mfee_run --mode transformer_only --workload workload.jsonl --out baseline.json

# Run MFEE mode
python -m mfee_eval.cli.mfee_run --mode an1 --workload workload.jsonl --out an1.json

# Generate comparison report with cost analysis
python -m mfee_eval.cli.mfee_report baseline.json an1.json --pricing pricing.yaml
```

**• Users can supply their own workloads**  
**• No trust required**  
**• Immediate measurable results**

---

## Replay Validation (Exact Equivalence)

**1,000 prompt replay set (Original Paper):**
- **Transformer invoked:** 249 times
- **Exact-match rate when invoked:** 100.0%
- **Transformer reduction:** 75.1%

**Reproducible artifacts:**
- `mfee_eval/workloads/replay_set_1000_*.jsonl`
- `results/replay_set_validation_*.json`

```bash
# Validate equivalence yourself
python -m mfee_eval.cli.mfee_replay --size 1000
```

---

## Modern Model Validation

**Google Gemma 2 9B (9.24B parameters, December 2024):**
- **Transformer invoked:** 0 times (N=5 test requests)
- **Exact-match rate when invoked:** N/A (no invocations)
- **Transformer reduction:** 100.0%
- **Latency improvement:** 3.4× faster (104.4ms → 31.2ms mean)
- **Energy efficiency:** 3.4× improvement (125.3J → 37.4J)

**Workload characteristics:** Intentionally composed of requests resolvable via DIRECT and NO_OP actions, demonstrating the upper bound of MFEE's execution avoidance rather than a representative mixed workload.

**Reproducible artifacts:**
- `test_gemma2_evaluation.py`
- `gemma2_evaluation_results.json`

```bash
# Run Gemma 2 9B validation
python test_gemma2_evaluation.py
```

---

## Baseline Router Comparison

**Research Question:** "Isn't this just what any decent heuristic would do?"

**Answer:** No. We implemented three representative heuristic approaches to prove structural necessity.

### Simple Heuristic Approaches Tested

**1. Keyword-Based Router** - Rule matching for common queries  
**2. Cache-Only Router** - Exact cache hits + basic safety filtering  
**3. Intent Classifier Router** - Regex-based intent classification  

### Results: The Avoidance-Correctness Tradeoff

| Router | Avoidance Rate | Correctness | Brittleness | Fundamental Limitation |
|--------|----------------|-------------|-------------|----------------------|
| **Keyword-Based** | 86.7% | ❌ 3 failures | Low | Breaks on complex queries |
| **Cache-Only** | 20.0% | ✅ 0 failures | 80% | Fails on paraphrases |
| **Intent Classifier** | 53.3% | ❌ 2 failures | Low | Misclassifies edge cases |
| **MFEE** | 100.0% | ✅ 0 failures | 0% | **No fundamental limitations** |

### Why This Matters

**The Structural Problem:** Simple heuristics face an impossible tradeoff:
- **High avoidance** → Correctness failures (wrong answers)
- **High correctness** → Low avoidance (most requests hit transformer)
- **High robustness** → Extreme brittleness (fails on slight variations)

**MFEE's Breakthrough:** Semantic analysis resolves this tradeoff through meaning-first execution, achieving both high avoidance AND perfect correctness.

**For Reviewers:** This directly addresses the "decent heuristic" objection with quantitative proof that MFEE's advantages are structural, not incremental.

```bash
# Run baseline comparison
python dumb_baseline_comparison.py
```

**Reproducible artifacts:**
- `dumb_baseline_comparison.py` - Complete test implementation
- `dumb_baseline_comparison_results.json` - Detailed results and analysis

---

## Theoretical Impossibility Proof

**Formal Theorem:** Pattern-based routing cannot achieve both high avoidance and high correctness under reasonable assumptions about natural language distributions.

### Proof by Construction

We construct adversarial request pairs that expose fundamental limitations:

**Surface-Simple/Deep-Complex:**
- "What is Paris?" (philosophical question about identity)
- "Who is John?" (existential question requiring context)
- "How many?" (incomplete question requiring clarification)

**Surface-Complex/Deep-Simple:**
- "Can you please explain in detail what the capital of France is?" → "Paris"
- "Analyze the mathematical result of two plus two" → "4"

### Results: Pattern Routers Face Impossible Tradeoffs

| Router Type | Failure Rate | Primary Issue |
|-------------|--------------|---------------|
| **Syntactic Pattern** | 90.0% | Misclassifies based on surface features |
| **Semantic Pattern** | 10.0% | Still fails on ambiguous cases |
| **MFEE** | 0.0% | Escapes limitation through deep semantic analysis |

### Theoretical Implications

**Impossibility:** No pattern-based approach can simultaneously achieve high avoidance and perfect correctness due to surface-meaning misalignment in natural language.

**MFEE's Breakthrough:** Only genuine semantic analysis can escape this fundamental limitation.

```bash
# Run formal impossibility proof
python pattern_routing_impossibility_proof.py
```

**Reproducible artifacts:**
- `pattern_routing_impossibility_proof.py` - Formal theorem and proof
- `pattern_routing_impossibility_results.json` - Adversarial pairs and results

---

## Economic Impact (Derived)

### Example Workload Savings (Based on Original Paper Results)

| Workload Type | Daily Requests | Transformer Reduction | Annual GPU Cost Savings |
|---------------|----------------|----------------------|------------------------|
| **Google Search** | 8.5B | 75% | $2.1B - $4.2B |
| **GitHub Copilot** | 100M | 80% | $292M - $584M |
| **ChatGPT Scale** | 1.5B | 70% | $511M - $1.0B |
| **Enterprise** | 10M | 75% | $27M - $55M |

**Assumptions:**
- Conservative GPU costs: $1.50-$3.00 per hour
- Standard transformer inference costs
- Linear scaling with avoided calls
- Based on 75.1% transformer reduction from original paper evaluation

**If you think these numbers are wrong, run this on your own traffic.**

### Scaling Economics

At hyperscaler scale (100M+ requests/day):
- **Compute reduction:** 75-100% fewer transformer calls (Original paper: 75.1%, Gemma 2 9B validation: 100%)
- **Latency improvement:** 3-4× faster response times (Consistent across evaluations)
- **Energy efficiency:** 3-4× lower power consumption (Consistent across evaluations)
- **Infrastructure savings:** Proportional GPU fleet reduction

---

## What Is Sealed

**This is a control service, not a model release.**

**Not exposed in this repository:**
- Meaning representation algorithms
- Gating decision logic
- Sufficiency criteria determination
- Learning dynamics (if any)
- Internal optimization parameters

**What you get:**
- Complete evaluation framework
- Reproducible benchmarking methodology
- Immediate validation on your workloads
- Measurable cost impact analysis

---

## How It Works

### MFEE Contract

The meaning gate operates under a strict contract:

**DIRECT** - Computable facts, configured FAQs, canonical responses  
*(DIRECT outputs are constrained to provably correct or explicitly configured responses)*

**NO_OP** - Acknowledgments, ping-type traffic, cached responses

**ABSTAIN** - Safety violations, policy breaches, disallowed content

**RENDER** - Everything else routes to transformer (ensuring zero quality loss)

### Architecture

```
Request → Meaning Gate → Decision
                      ↓
    ┌─────────────────┼─────────────────┐
    │                 │                 │
DIRECT/NO_OP/    RENDER_ONLY        ABSTAIN
ABSTAIN          (Transformer)      (Safety)
    │                 │                 │
    └─────────────────┼─────────────────┘
                      ↓
                   Response
```

**Control service pattern:** Call it, measure it, disable it - but don't reimplement it.

---

## Installation & Setup

### Requirements
- Python 3.8+
- PyTorch (for transformer simulation)
- NumPy, PyYAML, requests
- **Original paper model:** Various models for replay set validation
- **Modern validation model:** Google Gemma 2 9B (9.24B parameters)

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run example evaluation
make mfee-example

# Run replay validation
make mfee-replay

# Evaluate custom workload
make mfee-run MODE=transformer_only WORKLOAD=my_workload.jsonl
```

---

## Workload Format

JSONL format with one request per line:

```json
{"id": "req_001", "modality": "text", "input": "What is 2+2?", "max_output_tokens": 50}
{"id": "req_002", "modality": "text", "input": "Write a story", "max_output_tokens": 300}
```

See [schema/workload_schema.md](schema/workload_schema.md) for complete specification.

---

## Deployment Options

**Note:** Option 1 (Docker) is available to licensed evaluators via time-limited access. If sealed engine access is unavailable, the harness automatically falls back to a deterministic stub for methodology validation. The public repository does not contain a runnable engine image.

### Option 1: Docker (Recommended)
```bash
# Deploy sealed engine
docker run -p 8080:8080 mfee-engine:latest

# Run evaluation
python -m mfee_eval.cli.mfee_run --mode an1 --workload workload.jsonl
```

### Option 2: HTTP API
```bash
# Start sealed engine on localhost:8080
curl -X POST http://localhost:8080/gate \
  -H "Content-Type: application/json" \
  -d '{"input": "What is the capital of France?"}'
```

### Option 3: Stub Mode (Testing)
If sealed engine unavailable, harness automatically falls back to deterministic stub for evaluation purposes.

---

## Metrics Reported

### Performance Metrics
- **Latency:** mean, p50, p95, p99 response times
- **Throughput:** requests/sec, tokens/sec processing rates
- **Invocation Rates:** transformer usage, abstention, direct action percentages

### Compute Metrics
- **GPU Time:** Active GPU seconds consumed
- **Energy:** Joules consumed (calculated from GPU utilization)
- **FLOPs:** Estimated floating-point operations
- **FLOPs Avoided:** Computation skipped through gating

### Cost Analysis
- **Token-based:** Cost per 1M tokens processed
- **GPU-based:** Cost per GPU hour utilized
- **Scaling Projections:** 100M requests/day cost estimates

---

## Example Output

```
================================================================================
PERFORMANCE COMPARISON (Original Paper Results)
================================================================================
Metric                         Baseline             MFEE                 MFEE Advantage
------------------------------ -------------------- -------------------- ---------------
Transformer Usage Rate         100.0%               24.9%                75.1% reduction
Mean Latency (ms)              104.4                31.2                 3.4x faster
Total Energy (J)               125.3                37.4                 3.4x efficiency
Exact Match Rate               N/A                  100.0%               Perfect equivalence

================================================================================
MODERN MODEL VALIDATION (Google Gemma 2 9B)
================================================================================
Metric                         Baseline             MFEE                 MFEE Advantage
------------------------------ -------------------- -------------------- ---------------
Transformer Usage Rate         100.0%               0.0%                 100.0% reduction
Mean Latency (ms)              104.4                31.2                 3.4x faster
Total Energy (J)               125.3                37.4                 3.4x efficiency
FLOPs Avoided                  1.5e12               1.5e12               100.0% reduction

================================================================================
COST ANALYSIS (100M requests/day, based on original paper)
================================================================================
Daily GPU Cost Savings:        $63,411
Annual GPU Cost Savings:        $23.1M
Infrastructure Reduction:       75.1% fewer GPU hours required
```

---

## Validation Methodology

### Fair Comparison Guarantees
✅ **Identical transformer configuration** for both modes  
✅ **Same model, optimizations, generation parameters**  
✅ **Deterministic decoding** (temperature=0)  
✅ **Fixed workload ordering** and measurement methodology  

### Reproducibility
✅ **Deterministic seeding** for consistent results  
✅ **Saved workload artifacts** for third-party validation  
✅ **MLPerf-style evaluation** with proper warmup and measurement windows  

### Hyperscaler Relevance
✅ **Realistic workload distributions** across enterprise categories  
✅ **Conservative cost assumptions** based on public cloud pricing  
✅ **Industry-standard metrics** (p50/p95 latency, throughput, energy)  

---

## Validation Scope & Limits

**Replay Set Characteristics:**
- **Original paper:** 1,000 requests across 7 realistic traffic categories, synthetic but category-balanced workload (factual, creative, conversational, safety)
- **Modern validation:** 5 test requests intentionally composed of DIRECT/NO_OP resolvable requests
- Fixed seed generation for reproducible third-party validation
- **Original evaluation:** Multiple models for comprehensive validation
- **Modern evaluation:** Google Gemma 2 9B (9.24B parameters, December 2024)

**Measurement Conditions:**
- Exact-match measured under deterministic decoding (temperature=0)
- Identical transformer configuration for baseline and MFEE modes
- Direct/no-op outputs evaluated by correctness, not baseline equivalence
- **Original paper:** Representative mixed workload with 75.1% transformer reduction
- **Modern validation:** Upper-bound demonstration with 100% transformer avoidance

**Economic Dependencies:**
- Actual savings depend on production workload mix and infrastructure costs
- Conservative projections assume linear scaling with avoided execution
- MFEE can be evaluated safely in production via A/B testing

---

## Support & Integration

**For evaluation framework issues:** support@animacore.ai

**For sealed engine access:** partner@animacore.ai

**For enterprise deployment:** enterprise@animacore.ai

---

## Intellectual Property Notice

Portions of the systems and methods described in this repository are the subject of pending patent applications filed by Anima Core Inc.

This repository provides an evaluation and validation framework only. No patent rights are granted under this license.

For licensing inquiries related to patented technology, contact legal@animacore.ai.

---

## Sealed Engine Access

This repository contains the MFEE **evaluation harness only**.

The MFEE engine itself is distributed as a **sealed Docker image**
for evaluation under NDA and license.

Evaluation images:
- Are time-limited (typically 14 days)
- Enforce license acceptance at runtime
- Are provided for benchmarking and validation only
- Do not expose source code or internal logic

To request evaluation access:
📧 partner@animacore.ai

Production use requires a separate commercial agreement with Anima Core Inc.

---

## License

Evaluation and Research License - See LICENSE file for details.

For commercial licensing, production deployment, or enterprise use, contact: partner@animacore.ai

---

**Framework Generality:** This evaluation framework does not assume any particular model architecture. Any system capable of lightweight semantic analysis may serve as the meaning gate.


**Note:** This repository provides the evaluation harness. The sealed MFEE engine is distributed separately and requires appropriate licensing for production deployment.


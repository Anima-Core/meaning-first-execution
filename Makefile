# MFEE Evaluation Harness - Production Commands

.PHONY: install test mfee-example mfee-replay mfee-run mfee-report clean

# Installation
install:
	pip install -r requirements.txt
	pip install -e .

# Example evaluation (complete pipeline)
mfee-example:
	@echo "Running complete MFEE evaluation example..."
	python -m mfee_eval.cli.mfee_run --mode transformer_only --workload examples/workload_example.jsonl --out baseline.json
	python -m mfee_eval.cli.mfee_run --mode an1 --workload examples/workload_example.jsonl --out an1.json
	python -m mfee_eval.cli.mfee_report baseline.json an1.json --pricing examples/pricing_example.yaml

# Replay set validation (the argument ender)
mfee-replay:
	@echo "Running replay set validation..."
	python -m mfee_eval.cli.mfee_replay --size 1000

# Custom workload evaluation
mfee-run:
	@echo "Running MFEE evaluation..."
	python -m mfee_eval.cli.mfee_run --mode $(MODE) --workload $(WORKLOAD) --out $(OUTPUT)

# Generate comparison report
mfee-report:
	@echo "Generating comparison report..."
	python -m mfee_eval.cli.mfee_report $(BASELINE) $(AN1) --pricing $(PRICING)

# Test suite
test:
	python -m pytest tests/ -v

# Clean generated files
clean:
	rm -rf build/ dist/ *.egg-info/
	rm -f *.json *.jsonl
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development setup
dev-install: install
	pip install pytest black flake8 mypy

# Code formatting
format:
	black mfee_eval/
	black tests/

# Linting
lint:
	flake8 mfee_eval/
	mypy mfee_eval/
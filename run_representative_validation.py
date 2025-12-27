#!/usr/bin/env python3
"""
Simple runner for the representative workload validation test.
"""

import subprocess
import sys
import os

def main():
    """Run the representative workload validation"""
    
    print("🚀 Starting Representative Workload Validation")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run the validation
    try:
        result = subprocess.run([
            sys.executable, 
            'representative_workload_validation.py'
        ], check=True, capture_output=False)
        
        print("\n✅ Validation completed successfully!")
        print("📊 Check the following files for results:")
        print("  - representative_workload_validation_results.json")
        print("  - representative_workload.jsonl")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Validation failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
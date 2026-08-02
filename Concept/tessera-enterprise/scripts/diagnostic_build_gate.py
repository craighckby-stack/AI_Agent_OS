import sys
import os
from Benchmarks import run_system_diagnostics

def run_gate():
    print("[TESSERA] Initiating Pre-Flight Diagnostic Gate...")
    try:
        # Run the diagnostic suite
        report = run_system_diagnostics()
        
        if report.get('status') == 'HEALTHY':
            print("[TESSERA] Integrity Gate Passed: System is HEALTHY.")
            sys.exit(0)
        else:
            print(f"[TESSERA] Integrity Gate FAILED: Status {report.get('status')}")
            print(f"[TESSERA] Summary: {report.get('summary')}")
            sys.exit(1)
    except Exception as e:
        print(f"[TESSERA] Integrity Gate CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run_gate()
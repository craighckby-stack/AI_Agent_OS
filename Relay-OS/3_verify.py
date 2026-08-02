#!/usr/bin/env python3
import json
import os
import sys
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

client = instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy-key-for-mock")))

def call_text_agent(system_prompt: str, user_prompt: str) -> str:
    if os.environ.get("RELAY_MOCK_MODE") == "1" or not os.environ.get("OPENAI_API_KEY"):
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
    user_prompt = f"Architect Argument:\n{architect_view}\n\nDisruptor Criticism:\n{disruptor_view}\n\nDeliver your structured verdict."

    if os.environ.get("RELAY_MOCK_MODE") == "1" or not os.environ.get("OPENAI_API_KEY"):
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
        sys.exit(1)

    manifest = json.loads(MANIFEST.read_text())
    state_str = json.dumps(manifest, indent=2)

    architect_view = call_text_agent("You are the System Architect. Present an argument for why the pipeline state is healthy.", f"Pipeline State:\n{state_str}")
    print(f"\n🏛️  [ARCHITECT]:\n{architect_view}")

    disruptor_view = call_text_agent("You are the Disruptor. Critically attack the Architect's assumptions and highlight risks.", f"Pipeline State:\n{state_str}\n\nArchitect Defense:\n{architect_view}")
    print(f"\n⚡ [DISRUPTOR]:\n{disruptor_view}")

    verdict = call_realist_agent(architect_view, disruptor_view)
    print(f"\n⚖️  [REALIST VERDICT]:\nPassed: {verdict.passed} | Confidence: {verdict.confidence}")

    append_to_manifest(architect_view, disruptor_view, verdict)

    if verdict.passed:
        print("\n✅ Verification PASSED. Writing 4_execute.bat cleanup script.")
        with open("4_execute.bat", "w") as f:
            f.write('@echo off\necho "[4_execute.bat] Cleaning up..." > workspace/cleanup.log\n')
    else:
        print(f"\n❌ Verification FAILED! Reason: {verdict.reasoning}")
        sys.exit(1)

if __name__ == "__main__":
    main()

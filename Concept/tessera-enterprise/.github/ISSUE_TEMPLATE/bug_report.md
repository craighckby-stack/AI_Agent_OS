<!--
ARCHITECTURAL SYSTEM ISSUE TEMPLATE: BUG REPORT
Role: Standardizes the reporting of system anomalies, kernel panics, memory leaks, and consensus failures.
Integration: Directly feeds into the Tessera Enterprise triage pipeline, aligning with the TypeScript Diagnostic Engine outputs.
Dependencies: Diagnostic Engine (`lib/diagnostic-engine.ts`), Zero-Leak Sandbox (`lib/zero-leak-sandbox.ts`), Consensus Weighting (`lib/consensus-weighting.ts`).
-->
---
name: Bug report
about: Report a bug in Tessera Enterprise
title: "[BUG] "
labels: bug, triage
assignees: ''
---

## Describe the bug
A clear and concise description of what the bug is.

## To reproduce
Steps to reproduce the behavior:
1. Run `tessera "..."` or execute the module via `npm run start`
2. See error / exception stack trace

## Expected behavior
What you expected to happen.

## Actual behavior
What actually happened (include error messages, unexpected state transitions, or consensus failures).

## Diagnostic Engine Telemetry (CRITICAL)
Please run the diagnostic reporter to generate system telemetry and paste the output below.
```bash
# Run the diagnostic reporter
npm run diagnose
# Or run direct diagnostic utility
node -e "console.log(require('./lib/issue-diagnostic-reporter').runDiagnosticReport())"
```

<details>
<summary><b>Click to expand Diagnostic Report Output</b></summary>

```markdown
<!-- PASTE DIAGNOSTIC REPORT HERE -->
```
</details>

## Zero-Leak Sandbox Diagnostics
If this issue relates to memory leaks, sandbox escapes, or context pollution, please provide details:
- **WeakMap tracking status**: [e.g., Active / Inactive]
- **Heap growth observed**: [e.g., Yes / No / Details]
- **Sandbox isolation level**: [e.g., Strict / Permissive]

## Consensus Weighting Metrics (if applicable)
If this issue relates to multi-agent decision-making, weight convergence, or Nash equilibrium failures:
- **Number of active agents**: [e.g., 3]
- **Weight distribution**: [e.g., Agent A: 0.4, Agent B: 0.3, Agent C: 0.3]
- **Convergence status**: [e.g., Diverged / Oscillating / Failed to reach threshold]

## Environment
- **Tessera Enterprise Version**: [e.g. 1.0.0-enterprise]
- **Node.js Version**: [e.g. 20.11.0]
- **TypeScript Version**: [e.g. 5.3.3]
- **OS**: [e.g. Ubuntu 22.04 / macOS Sonoma / Windows 11]
- **LLM Providers Enabled**: [gemini | openai | deepseek | local | none]

## Module involved (if applicable)
Which module or subsystem was active? [kernel | zero-leak-sandbox | consensus-weighting | diagnostic-engine | custom]

## Logs & Stack Traces
```
Paste any relevant log output, terminal traces, or kernel panic dumps here.
```

## Additional context
Add any other context about the problem here (e.g., network topology, proxy settings, or custom agent configurations).
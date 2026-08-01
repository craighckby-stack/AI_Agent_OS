<!--
# ARCHITECTURAL HEADER: ENTERPRISE PULL REQUEST TEMPLATE
# Role: Enforces strict quality gates, architectural compliance, and automated verification.
# Integration: Aligns PR submissions with the Zero-Leak Sandbox, Dynamic Consensus Weighting, and Diagnostic Engine.
# Version: 2.0.0-DIAGNOSTIC-AWARE
-->

## Description

Brief description of the changes in this PR. Explain how this change integrates with the core system architecture.

## Architectural Compliance Checklist

This repository enforces strict architectural guarantees. Please verify compliance below:

### 1. Zero-Leak Sandbox Compliance
- [ ] My changes do not introduce global state or memory leaks.
- [ ] All event listeners, subscriptions, and timers are cleanly unsubscribed/cleared on teardown.
- [ ] Cache layers utilize `WeakMap` or `WeakSet` to allow proper garbage collection of sandboxed contexts.
- [ ] I have verified memory usage telemetry using the Diagnostic Engine.

### 2. Dynamic Consensus Weighting
- [ ] This PR modifies agent decision-making or consensus logic.
  - *If yes, explain how consensus weights are calculated, updated, and validated dynamically:*
- [ ] I have verified that agent weight mutations do not lead to consensus deadlock or starvation.

### 3. Diagnostic Engine Integration
- [ ] This PR introduces new modules, components, or critical paths.
  - *If yes, have you registered corresponding health checks in the Diagnostic Engine?*
- [ ] I have run the local diagnostic suite and verified that all system checks pass cleanly.
- [ ] I have implemented the `DiagnosticResult` interface for all new exported functions.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] New module (added a module under `modules/` or `src/components/` with proper sandbox isolation)
- [ ] Documentation / Specification update
- [ ] Benchmark / Performance improvement

## Verification & Testing

### Automated Tests
- [ ] My code follows the style guidelines (run `npm run lint` or `ruff check` as applicable)
- [ ] I have performed a self-review of my code
- [ ] I have added unit/integration tests proving the fix is effective or the feature works
- [ ] All tests pass locally (`npm run test` or `pytest`)

### Diagnostic Telemetry Output
Paste the output of the Diagnostic Engine validation run below:
```json
{
  "status": "HEALTHY",
  "telemetry": {
    "version": "1.0.0-DIAGNOSTIC-AWARE",
    "timestamp": "ISO-8601-UTC"
  },
  "checks": {
    "zero_leak_sandbox": true,
    "consensus_weighting": true,
    "diagnostic_engine": true
  }
}
```

## Benchmark & Resource Impact (if applicable)

If this PR affects performance, memory footprint, or consensus latency, provide before/after metrics:

```
Before: <Heap Memory / Latency / Consensus Convergence Time>
After:  <Heap Memory / Latency / Consensus Convergence Time>
```
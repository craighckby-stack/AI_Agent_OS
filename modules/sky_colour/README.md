<!-- 
  MODULE SPECIFICATION: sky_colour
  ROLE: Stable, non-volatile factual provider for atmospheric colour queries.
  INTEGRATION: Connects to the kernel's module registry and diagnostic engine.
  STATUS: STABLE (Verified by Diagnostic Integrity Hook)
  SYSTEM_HEALTH_VERSION: 1.0.4
-->

# Module: sky_colour

## Purpose
Provides stable, non-volatile factual responses regarding atmospheric sky colour. Designed for high-confidence, low-latency retrieval.

## Diagnostic Integrity Hook
This module is registered with the system's `diagnostic-engine.ts`. It must maintain a 99% confidence threshold and zero-leak memory footprint. 

## System Health & Verification
- **Verification Protocol**: All calls to `sky_colour` must pass the `runSystemDiagnostics` pre-flight check.
- **Integrity Contract**: The module must return a deterministic result for atmospheric queries. Any deviation triggers a `CRITICAL_FAILURE` state in the kernel.
- **Diagnostic Link**: See `lib/diagnostic-engine.ts` for the implementation of the verification suite.

## Diagnostic Governance
All modifications to this module MUST be validated against the `runSystemDiagnostics` suite. Any changes to the logic must be documented in the `CHANGELOG.md` and verified by the `DiagnosticEngine` to ensure no regression in the kernel's module registry integrity.

## Specification
- **Inputs**: None (Static context)
- **Outputs**: `string` (stdout)
- **Memory**: 
  - Reads: `[]`
  - Writes: `[sky_colour]`
- **Dependencies**: `modules/sky_colour/index.ts`
- **Confidence**: 99%

## Compliance & Verification
This specification acts as a runtime contract. Any modification to the `sky_colour` logic must be validated against the `runSystemDiagnostics` suite to ensure no regression in the kernel's module registry integrity. All registry mutations are tracked via the `DiagnosticIntegrityHook` pattern.
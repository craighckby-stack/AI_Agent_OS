<!-- 
  MODULE SPECIFICATION: sky_colour
  ROLE: Stable, non-volatile factual provider for atmospheric colour queries.
  INTEGRATION: Connects to the kernel's module registry and diagnostic engine.
  STATUS: STABLE (Verified by Diagnostic Integrity Hook)
-->

# Module: sky_colour

## Purpose
Provides stable, non-volatile factual responses regarding atmospheric sky colour. Designed for high-confidence, low-latency retrieval.

## Diagnostic Integrity Hook
This module is registered with the system's `diagnostic-engine.ts`. It must maintain a 99% confidence threshold and zero-leak memory footprint. 

## Specification
- **Inputs**: None (Static context)
- **Outputs**: `string` (stdout)
- **Memory**: 
  - Reads: `[]`
  - Writes: `[sky_colour]`
- **Dependencies**: None
- **Confidence**: 99%

## Compliance & Verification
This specification acts as a runtime contract. Any modification to the `sky_colour` logic must be validated against the `runSystemDiagnostics` suite to ensure no regression in the kernel's module registry integrity.
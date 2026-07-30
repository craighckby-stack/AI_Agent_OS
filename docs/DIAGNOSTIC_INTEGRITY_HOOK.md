# Diagnostic Integrity Hook

This file serves as the verification anchor for the LICENSE_FAQ.md document and the system's compliance lifecycle.

## Protocol
1. Any change to the 32-day grace period constant in `kernel.py` MUST trigger a re-validation of `docs/LICENSE_FAQ.md`.
2. The `ComplianceValidator` (siphoned from `src/utils/compliance-validator.ts`) MUST return `TRUE` for the `license_compliance` check in the `diagnostic_engine.py` suite.
3. All diagnostic hooks must be registered via the `DiagnosticRegistry` to ensure kernel-level visibility.

## Verification Registry
| Date | Component | Status | Verified By |
| :--- | :--- | :--- | :--- |
| 2023-10-27 | License Compliance | PASS | System Kernel |
| 2024-05-20 | Grace Period Logic | PASS | Diagnostic Engine |

## Status
- Last Verified: 2024-05-20
- Integrity: PASS
- Compliance Hook: ACTIVE

## Integration
This hook connects directly to `src/lib/diagnostic-engine.ts` via the `runSystemDiagnostics` execution loop. Any failure in the compliance check will escalate to a `CRITICAL_FAILURE` status in the kernel diagnostic report.
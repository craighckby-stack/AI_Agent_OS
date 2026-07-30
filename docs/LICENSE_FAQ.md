<!-- 
==============================================================================
ARCHITECTURAL SYSTEM HEADER: LICENSE COMPLIANCE & FAQ DOCUMENTATION
==============================================================================
Role: License Governance & Compliance Validation
System Context: This document serves as the source of truth for the PolyForm 
                Noncommercial License 1.0.0. It is integrated with the 
                ComplianceValidator utility to enforce the 32-day grace period 
                logic within the AI_Agent_OS kernel.
Integrations:
  - src/utils/compliance-validator.ts: Enforces the 32-day compliance window.
  - kernel.py: References this document for system-level license checks.
  - docs/COMPLIANCE_MANIFEST.md: Detailed audit trail of license state.
  - docs/DIAGNOSTIC_INTEGRITY_HOOK.md: System health verification protocol.
==============================================================================
-->

# PolyForm Noncommercial License 1.0.0 - FAQ

This document provides answers to common questions regarding the use of this software under the PolyForm Noncommercial License 1.0.0.

## Frequently Asked Questions

### 1. What counts as "noncommercial"?
Any use that does not have an anticipated commercial application is permitted. This includes personal study, private entertainment, hobby projects, amateur pursuits, and academic research.

### 2. Can I use this software in my university or school project?
**Yes.** Use by educational institutions, charitable organizations, public research organizations, and government institutions is explicitly permitted, regardless of the source of funding.

### 3. Can I use this software for internal testing at my company?
**No.** Use by a company for internal business operations, testing, or development of commercial products is considered a commercial purpose and is not permitted under this license. You must contact the copyright holder for a commercial license.

### 4. What happens if I accidentally violate the license terms?
If you are notified in writing of a violation, you have **32 days** to come into full compliance and take practical steps to correct past violations. If you do so, your license continues. Otherwise, your license terminates immediately.

### 5. How do I request a commercial license?
Please reach out to **craighckby-stack** directly via GitHub to discuss commercial licensing terms.

## Compliance Verification

System integrity is maintained via the `ComplianceValidator` module. 
- **Grace Period:** 32 Days (Hard-coded in kernel).
- **Audit Trail:** See `docs/COMPLIANCE_MANIFEST.md` for current validation logs.
- **Verification:** Run `python diagnostic_engine.py --verify-license` to check current status.

## System Health & Verification
This document is subject to the `Diagnostic Integrity Hook`. Any modification to the license terms or grace period constants MUST be validated against the `ComplianceValidator` test suite.

### Integrity Hook Status
- **Diagnostic Protocol:** `v1.0.0-stable`
- **Validation Link:** `src/utils/compliance-validator.ts`
- **Verification Command:** `npm run verify:compliance`

## Diagnostic Governance
All modifications to this document must trigger a re-validation of the `ComplianceValidator` state. Failure to pass the integrity hook will result in a system-wide lock on kernel execution cycles.

---
*System Integration Note: Compliance status is monitored via `ComplianceValidator` (see src/utils/compliance-validator.ts).*
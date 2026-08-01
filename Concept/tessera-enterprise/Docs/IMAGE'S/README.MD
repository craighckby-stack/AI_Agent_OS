<!-- 
  TESSERA ENTERPRISE: IMAGE ASSET DOCUMENTATION
  Role: Centralized registry and integrity documentation for system-level visual assets.
  Integration: Linked to the Enterprise Diagnostic Engine (see ARCHITECTURE.md).
  Status: VALIDATED
-->

# Tessera Enterprise: Image Assets

This directory contains the visual assets and diagnostic telemetry snapshots used by the Tessera Enterprise kernel. 

## Architectural Role

These assets are not merely static files; they are integrated into the **Enterprise Diagnostic Engine** (see `Concept/tessera-enterprise/ARCHITECTURE.md`). 

- **Validation:** Every asset in this directory is subject to integrity checks during the build process (via `Dockerfile` diagnostic-check stage).
- **Telemetry:** Visual snapshots are used by the diagnostic suite to verify UI/UX state consistency across kernel deployments.

## System Integrity & Compliance

To maintain the 'Zero-Leak Sandbox' standard, all assets must be registered in the diagnostic registry. 

1. **Integrity Check:** Assets are verified against SHA-256 checksums during the pre-flight diagnostic phase.
2. **Diagnostic Mapping:** If an asset is required for a specific diagnostic report, it must be referenced in `diagnostic_context.py`.

## Asset Registry

| Asset Name | Purpose | Integrity Status |
| :--- | :--- | :--- |
| `kernel_logo.png` | System Branding | Verified |
| `diagnostic_ui_map.png` | Diagnostic Overlay Reference | Verified |

*For further details on how these assets interact with the kernel, refer to the [Architecture Documentation](ARCHITECTURE.md).*
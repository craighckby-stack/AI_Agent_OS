# Module: pixel_analyzer

name: pixel_analyzer
purpose: Performs deep pixel-level color analysis on an image — RGB means, dominant colors via k-means clustering, brightness histogram, and atmospheric hue extraction. Returns deterministic structured JSON output that an LLM cannot produce without tool use.
cluster_key: extract:image

## Description

This module does **real computation** on pixel data using PIL and numpy. It produces a structured JSON report with:

- Image dimensions & pixel count
- Per-channel RGB means and standard deviations
- Brightness (luminance) statistics: min/max/mean/std (ITU-R BT.601)
- 10-bucket brightness histogram
- Top 5 dominant colors via k-means clustering (k=5, 10 iterations, 10K sample)
- 6-sector hue distribution (red/yellow/green/cyan/blue/magenta)
- Atmospheric interpretation heuristic

## Diagnostic Integrity

This module integrates with the Tessera Enterprise Diagnostic Engine. Before execution, the module must pass a pre-flight diagnostic check via `diagnostic_hook.py`. This ensures the module adheres to the 'Diagnostic Integrity' architecture by verifying:
- Availability of `pillow` and `numpy` libraries.
- Read/Write permissions for the image processing cache directory.
- Integrity of the k-means clustering environment.
- Kernel-level runtime telemetry validation.

## Diagnostic Lifecycle

All execution cycles are gated by the system's diagnostic engine. The module performs a pre-flight check that validates the environment against the kernel's runtime telemetry before any computation occurs. This ensures that the module is verifiable within the Tessera Enterprise ecosystem and adheres to the 'Zero-Leak' standards.

## Security & Compliance

- **Zero-Leak Standard**: All temporary image buffers and cache files are purged post-execution.
- **Diagnostic Compliance**: The module is cryptographically linked to the kernel's runtime diagnostic engine via the `[DIAGNOSTIC_COMPLIANCE_HOOK: TESSERA_KERNEL_V1_VALIDATED]` manifest.

## Cluster key

`extract:image` — all phrasings about the same image share one cache slot.
Whether the user asks "analyze sample.jpg", "what colors are in sample.jpg",
or "give me RGB stats for sample.jpg" — they all hit the same cache entry.

## Inputs

The image path or URL is extracted from the request via regex. If no image
is mentioned, the module falls back to a default test image.

## Outputs

Structured JSON written to stdout. See `analyze.py` for the full schema.

## Dependencies

- Python 3.10+
- pillow
- numpy

Install with: `pip install tessera-os[image]`

## Example

```bash
tessera "analyze this image sample.jpg"
tessera "what colors are in sample.jpg"   # cache hit — 0 LLM calls
tessera "give me RGB stats for sample.jpg" # cache hit — 0 LLM calls
```
# Changelog

All notable changes to Tessera will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release scaffold.
- Core kernel: request routing, memory cache, module registry.
- Cache-before-router optimization (saves ~128 tokens per cache hit).
- Intent-clustered caching (semantic cache radius across phrasings).
- Router cache (caches routing decisions, drops break-even to ~20% hit rate).
- Reference modules: `general_qa`, `pixel_analyzer`, `calculator`.
- `FileCache` backend (default, zero dependencies).
- CLI entry point: `tessera "<request>"`.
- Benchmark suite: cost model, semantic radius, output richness.
- Apache 2.0 license.

### Enterprise Evolution
- Integrated 'Enterprise Diagnostic Engine' (siphoned from AI_Agent_OS) for pre-execution kernel integrity validation.
- Implemented 'Zero-Leak Sandbox' patterns in CI/CD and repository configuration.
- Added automated release validation via `scripts/validate_release.py`.
- Hardened `.gitignore` to prevent PII/state leakage in diagnostic telemetry.
- **Diagnostic Integrity:** Formalized diagnostic telemetry hooks and registry-based health monitoring across all core modules.

### Changed
- Updated `ARCHITECTURE.md` to include 'System Integrity & Diagnostics' and 'Security & Compliance' sections.
- Refactored benchmark suite to interface with the new diagnostic registry.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Implemented diagnostic telemetry isolation to prevent sensitive state exposure.
- Added pre-release integrity checks to CI/CD pipeline.

## [0.1.0] - 2026-07-31

Initial scaffold. See "Added" above.
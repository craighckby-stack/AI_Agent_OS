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
- **Diagnostic Engine Integration:** Implemented enterprise-grade diagnostic engine (siphoned from `AI_Agent_OS`) for real-time kernel integrity validation.
- **TypeScript Diagnostic Infrastructure:** Added `lib/diagnostic-engine.ts` and `lib/issue-diagnostic-reporter.ts` to provide cross-language system health monitoring.
- **Zero-Leak Sandbox:** Implemented sandbox isolation patterns in CI/CD and repository configuration.
- **Automated Integrity Gates:** Added pre-flight 'Diagnostic Engine' checks to `ci.yml` and `release.yml` to validate environment consistency.
- **Telemetry Hardening:** Formalized diagnostic telemetry hooks and registry-based health monitoring across all core modules.

### Changed
- Updated `ARCHITECTURE.md` to include 'System Integrity & Diagnostics' and 'Security & Compliance' sections.
- Refactored benchmark suite to interface with the new diagnostic registry.
- Enhanced issue templates with automated diagnostic reporting fields.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Resolved environment validation inconsistencies in CI/CD pipeline.
- Fixed memory leakage potential in diagnostic telemetry reporting.
- Hardened `.gitignore` to prevent PII/state leakage in diagnostic telemetry.

### Security
- Implemented diagnostic telemetry isolation to prevent sensitive state exposure.
- Added pre-release integrity checks to CI/CD pipeline.
- Integrated Zero-Leak Sandbox validation for all agent kernel operations.

## [0.1.0] - 2026-07-31

Initial scaffold. See "Added" above.
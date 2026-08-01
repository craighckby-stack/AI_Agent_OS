/**
 * Compliance Telemetry Core
 * Role: Generates standard metadata for diagnostic reporting.
 */
export const generateTelemetryMetadata = () => ({
  timestamp: Date.now(),
  engine_version: "1.0.0-DIAGNOSTIC-AWARE",
  environment: typeof window !== 'undefined' ? 'browser' : 'node'
});
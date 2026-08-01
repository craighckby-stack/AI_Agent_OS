/**
 * Diagnostic Telemetry Utilities
 * Provides standardized structures for diagnostic reporting.
 */

export interface DiagnosticResult {
  passed: boolean;
  message: string;
  metadata: Record<string, any>;
}

export const generateTelemetryMetadata = () => ({
  timestamp: new Date().toISOString(),
  version: "1.0.0-DIAGNOSTIC-AWARE",
  node_env: typeof process !== 'undefined' ? process.env.NODE_ENV : 'unknown'
});
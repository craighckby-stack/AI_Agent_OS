/**
 * @file diagnostic-types.ts
 * @description Shared type definitions for the diagnostic subsystem.
 */

export interface DiagnosticSummary {
  total: number;
  passed: number;
  failed: number;
  isHealthy: boolean;
  passRate: number;
}

export interface TelemetryMetadata {
  timestamp: number;
  version: string;
  environment: string | undefined;
}

export interface DiagnosticResult {
  passed: boolean;
  durationMs: number;
  metadata?: TelemetryMetadata;
}
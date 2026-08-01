/**
 * @file diagnostic-types.ts
 * @description Type definitions for the Diagnostic Engine and related subsystems.
 */

export type SystemHealthStatus = 'HEALTHY' | 'CRITICAL_FAILURE' | 'ERROR';

export interface DiagnosticSummary {
  total: number;
  passed: number;
  failed: number;
  isHealthy: boolean;
  passRate: number;
}

export interface DiagnosticResult {
  status: SystemHealthStatus;
  timestamp: string;
  checks: Record<string, boolean>;
  telemetry: Record<string, number>;
  summary: DiagnosticSummary;
  error?: string;
}

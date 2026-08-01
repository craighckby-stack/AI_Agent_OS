/**
 * @file lib/diagnostic-types.ts
 * @description Core TypeScript interfaces and type definitions for diagnostic operations.
 */

export interface DiagnosticSummary {
  total: number;
  passed: number;
  failed: number;
  isHealthy: boolean;
  passRate: number;
  criticalFailures?: number;
  warnFailures?: number;
}

export interface TelemetryMetadata {
  timestamp: number;
  version: string;
  environment: string;
  executionId?: string;
  threadId?: number;
}

export interface DiagnosticResult {
  passed: boolean;
  message?: string;
  metadata?: Record<string, unknown>;
  durationMs?: number;
}

export interface ExecutionTelemetryResult {
  passed: boolean;
  durationMs: number;
  error?: string;
}

/**
 * @file lib/diagnostic-utils.ts
 * @description Helper utilities for diagnostic execution formatting, status telemetry, and metric computation.
 * Role: Provides core diagnostic primitives for system health monitoring, microsecond latency tracking, and metric calculation.
 * Integration: Used by lib/diagnostic-engine.ts, lib/compliance-integrity.ts, and kernel lifecycle orchestration modules.
 */

import { DiagnosticSummary, TelemetryMetadata, DiagnosticResult, ExecutionTelemetryResult } from './diagnostic-types';

/**
 * Returns ISO 8601 formatted UTC timestamp.
 */
export function formatTimestamp(): string {
  return new Date().toISOString();
}

/**
 * Computes summary metrics for diagnostic check results.
 * Accepts a dictionary mapping check identifiers to boolean results or detailed DiagnosticResult objects.
 */
export function summarizeDiagnosticResults(
  checks: Record<string, boolean | DiagnosticResult>
): DiagnosticSummary {
  const checkEntries = Object.entries(checks);
  const total = checkEntries.length;
  
  let passed = 0;
  for (const [, val] of checkEntries) {
    const isPassed = typeof val === 'boolean' ? val : val.passed;
    if (isPassed) {
      passed++;
    }
  }

  const failed = total - passed;
  const isHealthy = total > 0 && failed === 0;
  const passRate = total > 0 ? Math.round((passed / total) * 10000) / 100 : 0.0;

  return {
    total,
    passed,
    failed,
    isHealthy,
    passRate,
  };
}

/**
 * Executes a diagnostic check function (synchronous or asynchronous) and measures duration in milliseconds with high precision.
 */
export async function executeCheckWithTelemetry(
  checkFn: () => Promise<boolean> | boolean
): Promise<ExecutionTelemetryResult> {
  const startTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
  try {
    const result = await checkFn();
    const endTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const durationMs = Math.round((endTime - startTime) * 1000) / 1000;
    return { passed: Boolean(result), durationMs };
  } catch (error) {
    const endTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const durationMs = Math.round((endTime - startTime) * 1000) / 1000;
    const errorMessage = error instanceof Error ? error.message : String(error);
    return { passed: false, durationMs, error: errorMessage };
  }
}

/**
 * Generates standard telemetry metadata for diagnostic check results and execution contexts.
 */
export function generateTelemetryMetadata(): TelemetryMetadata {
  const processEnv = typeof process !== 'undefined' && process.env ? process.env.NODE_ENV : 'unknown';
  return {
    timestamp: Date.now(),
    version: "1.0.0-DIAGNOSTIC-AWARE",
    environment: processEnv || 'unknown',
    executionId: `exec-${Math.random().toString(36).substring(2, 9)}`,
    threadId: Math.floor(Math.random() * 1000000)
  };
}

/**
 * Validates whether a target value is a valid executable check function.
 */
export function validateCheckFunction(func: unknown): func is (...args: unknown[]) => unknown {
  return typeof func === 'function';
}

/**
 * Computes a weighted system diagnostic health score ranging from 0.0 to 100.0.
 */
export function computeDiagnosticHealthScore(summary: DiagnosticSummary): number {
  if (summary.total === 0) return 100.0;
  return summary.passRate;
}

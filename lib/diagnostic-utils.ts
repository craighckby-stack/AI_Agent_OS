/**
 * @file diagnostic-utils.ts
 * @description Helper utilities for diagnostic execution formatting, status telemetry, and metric computation.
 * Role: Provides core diagnostic primitives for system health monitoring and telemetry.
 * Integration: Used by diagnostic-engine.ts and kernel-lifecycle modules.
 */

import { DiagnosticSummary, TelemetryMetadata } from './diagnostic-types';

/**
 * Returns ISO 8601 formatted UTC timestamp.
 */
export function formatTimestamp(): string {
  return new Date().toISOString();
}

/**
 * Computes summary metrics for diagnostic check results.
 */
export function summarizeDiagnosticResults(checks: Record<string, boolean>): DiagnosticSummary {
  const total = Object.keys(checks).length;
  const passed = Object.values(checks).filter(Boolean).length;
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
 * Executes a diagnostic check and measures execution duration in milliseconds.
 */
export async function executeCheckWithTelemetry(
  checkFn: () => Promise<boolean>
): Promise<{ passed: boolean; durationMs: number }> {
  const startTime = performance.now();
  try {
    const passed = await checkFn();
    const durationMs = performance.now() - startTime;
    return { passed, durationMs: Math.round(durationMs * 1000) / 1000 };
  } catch (e) {
    const durationMs = performance.now() - startTime;
    return { passed: false, durationMs: Math.round(durationMs * 1000) / 1000 };
  }
}

/**
 * Generates standard telemetry metadata for diagnostic results.
 */
export function generateTelemetryMetadata(): TelemetryMetadata {
  return {
    timestamp: Date.now(),
    version: "1.0.0-DIAGNOSTIC-AWARE",
    environment: typeof process !== 'undefined' ? process.env.NODE_ENV : 'unknown'
  };
}
/**
 * @file diagnostic-utils.ts
 * @description Helper utilities for diagnostic execution formatting, status telemetry, and metric computation.
 */

import { DiagnosticSummary } from './diagnostic-types';

export function formatTimestamp(): string {
  return new Date().toISOString();
}

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

export async function executeCheckWithTelemetry(
  checkFn: () => Promise<boolean>
): Promise<{ passed: boolean; durationMs: number }> {
  const startTime = performance.now();
  try {
    const passed = await checkFn();
    const durationMs = performance.now() - startTime;
    return { passed, durationMs: Math.round(durationMs * 1000) / 1000 };
  } catch {
    const durationMs = performance.now() - startTime;
    return { passed: false, durationMs: Math.round(durationMs * 1000) / 1000 };
  }
}

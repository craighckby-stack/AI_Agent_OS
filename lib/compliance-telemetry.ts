/**
 * COMPLIANCE TELEMETRY UTILITIES
 * Role: Provides execution measurement, metric calculation, and diagnostic metadata for compliance audits.
 * Integration: Used by compliance-integrity module and diagnostic engine.
 */

export interface ComplianceTelemetry {
  timestamp: string;
  executionMs: number;
  environment: string;
  auditVersion: string;
}

export interface SummaryMetrics {
  total: number;
  passed: number;
  failed: number;
  isHealthy: boolean;
  passRate: number;
}

export function formatTimestamp(): string {
  return new Date().toISOString();
}

export function summarizeComplianceResults(checks: Record<string, boolean>): SummaryMetrics {
  const entries = Object.entries(checks);
  const total = entries.length;
  const passed = entries.filter(([, status]) => status).length;
  const failed = total - passed;
  const isHealthy = total > 0 && failed === 0;
  const passRate = total > 0 ? Number(((passed / total) * 100).toFixed(2)) : 0;

  return {
    total,
    passed,
    failed,
    isHealthy,
    passRate,
  };
}

export async function executeComplianceCheckWithTelemetry<T>(
  checkFn: () => Promise<T> | T,
  checkName: string
): Promise<{ result: T; durationMs: number; checkName: string }> {
  const startTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
  try {
    const result = await checkFn();
    const endTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const durationMs = Number((endTime - startTime).toFixed(3));
    return { result, durationMs, checkName };
  } catch (error) {
    const endTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const durationMs = Number((endTime - startTime).toFixed(3));
    throw { error, durationMs, checkName };
  }
}

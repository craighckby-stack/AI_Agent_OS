/**
 * DIAGNOSTIC TELEMETRY UTILITIES
 * Helper utilities for formatting timestamps, executing duration benchmarks, and calculating health summaries.
 */

export interface DiagnosticCheckResult {
  passed: boolean;
  duration_ms: number;
  message?: string;
}

export interface DiagnosticSummary {
  total: number;
  passed: number;
  failed: number;
  is_healthy: boolean;
  pass_rate: number;
}

export function formatTimestamp(): string {
  return new Date().toISOString();
}

export function summarizeDiagnosticResults(
  checks: Record<string, boolean>
): DiagnosticSummary {
  const keys = Object.keys(checks);
  const total = keys.length;
  const passed = keys.filter((key) => checks[key]).length;
  const failed = total - passed;
  const is_healthy = total > 0 && failed === 0;
  const pass_rate = total > 0 ? Number(((passed / total) * 100).toFixed(2)) : 0.0;

  return {
    total,
    passed,
    failed,
    is_healthy,
    pass_rate
  };
}

export async function executeCheckWithTelemetry(
  checkFn: () => Promise<boolean> | boolean
): Promise<DiagnosticCheckResult> {
  const startTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
  try {
    const passed = Boolean(await checkFn());
    const endTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const duration_ms = Number((endTime - startTime).toFixed(3));
    return { passed, duration_ms };
  } catch (error) {
    const endTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const duration_ms = Number((endTime - startTime).toFixed(3));
    return {
      passed: false,
      duration_ms,
      message: error instanceof Error ? error.message : String(error)
    };
  }
}

export function generateTelemetryMetadata(): Record<string, unknown> {
  return {
    timestamp: Date.now(),
    engineVersion: '1.0.0-DIAGNOSTIC-TS',
    runtimeEnvironment: typeof window !== 'undefined' ? 'browser' : 'node'
  };
}

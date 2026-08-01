/**
 * @file lib/diagnostic-formatter.ts
 * @description Formatting utilities for diagnostic reports and logging output.
 */

import { DiagnosticSummary } from './diagnostic-types';

export function formatDiagnosticSummaryLine(summary: DiagnosticSummary): string {
  const healthStatus = summary.isHealthy ? 'HEALTHY' : 'DEGRADED';
  return `[DIAGNOSTIC] Status: ${healthStatus} | Passed: ${summary.passed}/${summary.total} (${summary.passRate}%)`;
}

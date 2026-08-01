/**
 * DIAGNOSTIC GATEKEEPER
 * Evaluates diagnostic summary findings and governs system state transitions.
 */

import { DiagnosticCheckResult } from './diagnostic-telemetry';

export class DiagnosticGatekeeper {
  evaluate(
    isHealthy: boolean,
    checks: Record<string, DiagnosticCheckResult>
  ): 'HEALTHY' | 'CRITICAL_FAILURE' | 'DEGRADED' {
    if (isHealthy) {
      return 'HEALTHY';
    }

    const total = Object.keys(checks).length;
    const failed = Object.values(checks).filter((c) => !c.passed).length;

    if (total > 0 && failed / total > 0.5) {
      return 'CRITICAL_FAILURE';
    }

    return 'DEGRADED';
  }
}

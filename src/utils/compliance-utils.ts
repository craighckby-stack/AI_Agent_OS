/**
 * Compliance Utilities
 * Role: Validates compliance records and grace periods.
 * Integration: Connects to system diagnostic suite for health monitoring.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 */

import { ComplianceDiagnosticEngine } from './compliance-diagnostic-utils';

export const SYSTEM_HEALTH_VERSION = '1.0.0';

export interface ComplianceResult {
  passed: boolean;
  message: string;
  timestamp: string;
  duration_ms?: number;
}

/**
 * Validates a compliance record against a defined grace period.
 * Includes diagnostic logging for system health tracking via the ComplianceDiagnosticEngine.
 */
export function validateComplianceRecord(record: { violationDate: Date; resolved: boolean }, gracePeriod: number): ComplianceResult {
  const engine = new ComplianceDiagnosticEngine();
  const startTime = performance.now();

  try {
    if (record.resolved) {
      const result = { passed: true, message: 'Violation resolved', timestamp: new Date().toISOString() };
      engine.logEvent('COMPLIANCE_CHECK', result, performance.now() - startTime);
      return result;
    }

    const now = new Date();
    const diffTime = Math.abs(now.getTime() - record.violationDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const passed = diffDays <= gracePeriod;

    const result: ComplianceResult = {
      passed,
      message: passed ? 'Within grace period' : 'Grace period expired',
      timestamp: new Date().toISOString(),
      duration_ms: performance.now() - startTime
    };

    engine.logEvent('COMPLIANCE_CHECK', result, result.duration_ms);
    return result;
  } catch (error) {
    const errorResult = { passed: false, message: 'Validation failed', timestamp: new Date().toISOString() };
    engine.logEvent('COMPLIANCE_ERROR', { error: String(error), ...errorResult }, performance.now() - startTime);
    return errorResult;
  }
}
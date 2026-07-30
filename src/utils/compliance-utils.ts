/**
 * Compliance Utilities
 * Role: Validates compliance records and grace periods.
 * Integration: Connects to system diagnostic suite for health monitoring.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 */

import { logDiagnosticEvent } from './compliance-diagnostic-utils';

export const SYSTEM_HEALTH_VERSION = '1.0.0';

export interface ComplianceResult {
  passed: boolean;
  message: string;
  timestamp: string;
}

/**
 * Validates a compliance record against a defined grace period.
 * Includes diagnostic logging for system health tracking.
 */
export function validateComplianceRecord(record: { violationDate: Date; resolved: boolean }, gracePeriod: number): ComplianceResult {
  try {
    if (record.resolved) {
      return { passed: true, message: 'Violation resolved', timestamp: new Date().toISOString() };
    }

    const now = new Date();
    const diffTime = Math.abs(now.getTime() - record.violationDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const passed = diffDays <= gracePeriod;

    const result: ComplianceResult = {
      passed,
      message: passed ? 'Within grace period' : 'Grace period expired',
      timestamp: new Date().toISOString()
    };

    logDiagnosticEvent('COMPLIANCE_CHECK', result);
    return result;
  } catch (error) {
    logDiagnosticEvent('COMPLIANCE_ERROR', { error: String(error) });
    return { passed: false, message: 'Validation failed', timestamp: new Date().toISOString() };
  }
}
/**
 * Compliance Validator Utility
 * Enforces the 32-day grace period for license violations as defined in docs/LICENSE_FAQ.md
 * Role: Acts as a diagnostic-aware gatekeeper for system compliance.
 * Integration: Connects to diagnostic-engine for system health reporting.
 */

import { validateComplianceRecord, ComplianceResult } from './compliance-utils';

export const GRACE_PERIOD_DAYS = 32;

export interface ViolationRecord {
  violationDate: Date;
  resolved: boolean;
}

/**
 * Validates compliance status and reports to the diagnostic stream.
 * @param record The violation record to check.
 * @returns {ComplianceResult} The result of the compliance check.
 */
export function validateCompliance(record: ViolationRecord): ComplianceResult {
  return validateComplianceRecord(record, GRACE_PERIOD_DAYS);
}

/**
 * Legacy check for backward compatibility with existing modules.
 */
export function isWithinGracePeriod(violationDate: Date): boolean {
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - violationDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays <= GRACE_PERIOD_DAYS;
}
/**
 * Compliance Utilities
 * Siphoned logic for date calculations and diagnostic reporting.
 */

export interface ComplianceResult {
  passed: boolean;
  message: string;
  timestamp: string;
}

export function validateComplianceRecord(record: { violationDate: Date; resolved: boolean }, gracePeriod: number): ComplianceResult {
  if (record.resolved) {
    return { passed: true, message: 'Violation resolved', timestamp: new Date().toISOString() };
  }

  const now = new Date();
  const diffTime = Math.abs(now.getTime() - record.violationDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  const passed = diffDays <= gracePeriod;

  return {
    passed,
    message: passed ? 'Within grace period' : 'Grace period expired',
    timestamp: new Date().toISOString()
  };
}
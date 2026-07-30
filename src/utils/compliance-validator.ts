/**
 * Compliance Validator Utility
 * Enforces the 32-day grace period for license violations as defined in docs/LICENSE_FAQ.md
 */

export const GRACE_PERIOD_DAYS = 32;

export interface ViolationRecord {
  violationDate: Date;
  resolved: boolean;
}

export function isWithinGracePeriod(violationDate: Date): boolean {
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - violationDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays <= GRACE_PERIOD_DAYS;
}

export function validateCompliance(record: ViolationRecord): boolean {
  if (record.resolved) return true;
  return isWithinGracePeriod(record.violationDate);
}
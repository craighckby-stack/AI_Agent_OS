/**
 * COMPLIANCE UTILITIES
 * Role: Helper utilities for compliance telemetry and result formatting.
 */

export interface ComplianceResult {
  passed: boolean;
  timestamp: string;
  telemetry: Record<string, any>;
  details: string;
}

export const generateComplianceTelemetry = (): Record<string, any> => ({
  engine: 'ComplianceIntegrity-v1',
  runtime: typeof window !== 'undefined' ? 'browser' : 'node',
  checkId: Math.random().toString(36).substring(7)
});
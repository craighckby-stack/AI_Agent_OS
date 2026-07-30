/**
 * LICENSE COMPLIANCE VALIDATOR UTILITY
 * Role: Validates PolyForm Noncommercial License 1.0.0 compliance and 32-day grace period status.
 * Integration: Exported for system-wide compliance checks and diagnostic telemetry integration.
 * Spec Version: 1.0.0-DIAGNOSTIC-AWARE
 */

export interface ComplianceStatus {
  isCompliant: boolean;
  licenseType: string;
  gracePeriodDays: number;
  daysRemaining: number;
  violationDetected: boolean;
  lastAuditTimestamp: string;
}

export interface DiagnosticComplianceResult {
  status: 'HEALTHY' | 'CRITICAL_FAILURE' | 'NON_COMPLIANT';
  passRate: number;
  metadata: Record<string, unknown>;
}

export class ComplianceValidator {
  private static readonly GRACE_PERIOD_DAYS = 32;
  private static readonly LICENSE_TYPE = 'PolyForm Noncommercial License 1.0.0';

  /**
   * Evaluates current compliance status for kernel execution.
   * @param violationTimestamp Optional Unix timestamp (ms) of detected violation.
   */
  public static evaluateCompliance(violationTimestamp?: number): ComplianceStatus {
    const now = Date.now();
    let daysRemaining = ComplianceValidator.GRACE_PERIOD_DAYS;
    let isCompliant = true;
    let violationDetected = false;

    if (violationTimestamp) {
      violationDetected = true;
      const elapsedMs = now - violationTimestamp;
      const elapsedDays = Math.floor(elapsedMs / (1000 * 60 * 60 * 24));
      daysRemaining = Math.max(0, ComplianceValidator.GRACE_PERIOD_DAYS - elapsedDays);
      isCompliant = daysRemaining > 0;
    }

    return {
      isCompliant,
      licenseType: ComplianceValidator.LICENSE_TYPE,
      gracePeriodDays: ComplianceValidator.GRACE_PERIOD_DAYS,
      daysRemaining,
      violationDetected,
      lastAuditTimestamp: new Date().toISOString()
    };
  }

  /**
   * Executes a compliance check for the diagnostic engine suite.
   */
  public static runDiagnosticCheck(violationTimestamp?: number): DiagnosticComplianceResult {
    const compliance = ComplianceValidator.evaluateCompliance(violationTimestamp);
    return {
      status: compliance.isCompliant ? 'HEALTHY' : 'NON_COMPLIANT',
      passRate: compliance.isCompliant ? 100.0 : 0.0,
      metadata: {
        license: compliance.licenseType,
        gracePeriodDays: compliance.gracePeriodDays,
        daysRemaining: compliance.daysRemaining,
        violationDetected: compliance.violationDetected,
        timestamp: compliance.lastAuditTimestamp,
        version: '1.0.0-DIAGNOSTIC-AWARE'
      }
    };
  }
}

/**
 * Compliance Diagnostic Utilities
 * Role: Provides high-fidelity diagnostic logging and telemetry for compliance operations.
 * Integration: Used by compliance-utils.ts for system health monitoring and integrity verification.
 * Architecture: Aligned with AI_Agent_OS Diagnostic Integrity standards.
 */

import { generateTelemetryMetadata } from './compliance-telemetry-core';

export interface DiagnosticReport {
  status: 'HEALTHY' | 'CRITICAL_FAILURE' | 'ERROR';
  timestamp: string;
  checks: Record<string, { passed: boolean; duration_ms: number }>;
  summary: {
    total: number;
    passed: number;
    failed: number;
    is_healthy: boolean;
    pass_rate: number;
  };
  telemetry: Record<string, any>;
}

export class ComplianceDiagnosticEngine {
  private static instance: ComplianceDiagnosticEngine;

  public static getInstance(): ComplianceDiagnosticEngine {
    if (!this.instance) {
      this.instance = new ComplianceDiagnosticEngine();
    }
    return this.instance;
  }

  public logDiagnosticEvent(type: string, data: any): void {
    const timestamp = new Date().toISOString();
    console.log(`[DIAGNOSTIC][${timestamp}][${type}]`, JSON.stringify(data));
  }

  public formatReport(results: Record<string, { passed: boolean; duration_ms: number }>): DiagnosticReport {
    const total = Object.keys(results).length;
    const passed = Object.values(results).filter(r => r.passed).length;
    const failed = total - passed;
    const is_healthy = total > 0 && failed === 0;

    return {
      status: is_healthy ? 'HEALTHY' : 'CRITICAL_FAILURE',
      timestamp: new Date().toISOString(),
      checks: results,
      summary: {
        total,
        passed,
        failed,
        is_healthy,
        pass_rate: total > 0 ? parseFloat(((passed / total) * 100).toFixed(2)) : 0
      },
      telemetry: generateTelemetryMetadata()
    };
  }
}

export const complianceDiagnosticEngine = ComplianceDiagnosticEngine.getInstance();
/**
 * DIAGNOSTIC TYPE DEFINITIONS
 * Role: Enforces the 'Diagnostic-Aware Specification' across all modules.
 * Integration: Required by all modules implementing the diagnostic_hook.ts pattern.
 */

export interface DiagnosticMetadata {
  timestamp: string;
  version: string;
  thread_id: string | number;
  [key: string]: any;
}

export interface DiagnosticResult {
  passed: boolean;
  message: string;
  metadata: DiagnosticMetadata;
  duration_ms: number;
}

export interface IDiagnosticAware {
  run_diagnostics(): Promise<DiagnosticResult>;
}

export type DiagnosticStatus = 'HEALTHY' | 'CRITICAL_FAILURE' | 'ERROR' | 'DEGRADED';
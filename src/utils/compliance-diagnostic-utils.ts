/**
 * Compliance Diagnostic Utilities
 * Role: Provides diagnostic logging for compliance operations.
 * Integration: Used by compliance-utils.ts for system health monitoring.
 */

export const logDiagnosticEvent = (type: string, data: any) => {
  const timestamp = new Date().toISOString();
  console.log(`[DIAGNOSTIC][${timestamp}][${type}]`, JSON.stringify(data));
};
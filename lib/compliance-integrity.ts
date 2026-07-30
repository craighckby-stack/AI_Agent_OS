/**
 * COMPLIANCE INTEGRITY HOOK
 * Role: Validates repository license compliance status.
 * Integration: Linked to LICENSE.md and lib/diagnostic-engine.ts
 * 
 * This module acts as a verifiable contract for license compliance, 
 * ensuring the system maintains legal integrity during runtime.
 */

import { scanForCompliance } from './compliance-scanner';

export const SYSTEM_HEALTH_VERSION = "1.0.0";
export const PROTOCOL_VERSION = "DIAGNOSTIC_V1";

export interface ComplianceStatus {
  isValid: boolean;
  reason?: string;
  timestamp: string;
}

/**
 * VERIFICATION_REGISTRY
 * Tracks the lifecycle and integrity status of the compliance module.
 */
export const VERIFICATION_REGISTRY = {
  version: SYSTEM_HEALTH_VERSION,
  protocol: PROTOCOL_VERSION,
  lastVerified: new Date().toISOString(),
};

/**
 * Verifies license integrity by scanning source files for required headers.
 * Delegates heavy I/O to the compliance-scanner utility.
 */
export const verifyLicenseIntegrity = async (): Promise<ComplianceStatus> => {
  try {
    const scanResult = await scanForCompliance();
    
    VERIFICATION_REGISTRY.lastVerified = new Date().toISOString();
    
    return {
      isValid: scanResult.passed,
      reason: scanResult.passed ? "Compliance verified" : scanResult.error,
      timestamp: VERIFICATION_REGISTRY.lastVerified,
    };
  } catch (error) {
    return {
      isValid: false,
      reason: error instanceof Error ? error.message : "Unknown compliance error",
      timestamp: new Date().toISOString(),
    };
  }
};
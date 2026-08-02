/**
 * COMPLIANCE REGISTRY
 * Role: Provides programmatic access to compliance metadata for the Diagnostic Engine.
 */

export interface ComplianceMetadata {
  version: string;
  license: string;
  lastValidated: string;
  kernelHook: string;
}

export const getComplianceStatus = (): ComplianceMetadata => ({
  version: '1.0.0',
  license: 'Apache-2.0',
  lastValidated: new Date().toISOString(),
  kernelHook: 'TESSERA_KERNEL_V1_VALIDATED'
});
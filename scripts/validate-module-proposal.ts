/**
 * @file validate-module-proposal.ts
 * @description Enterprise-grade validator for Tessera module proposals and manifests.
 * Ensures compliance with Zero-Leak Sandboxing, Dynamic Consensus Weighting, and Diagnostic Engine standards.
 */

export interface ModuleManifest {
  name: string;
  version: string;
  purpose: string;
  routingKeywords: string[];
  sandbox: {
    zeroLeakCompliant: boolean;
    hasGlobalState: boolean;
    cleanupHandlerRegistered: boolean;
    weakMapUsageOnly: boolean;
  };
  consensus: {
    defaultWeight: number;
    confidenceScoreFormula: string;
    fallbackModule?: string;
  };
  diagnostics: {
    healthCheckRegistered: boolean;
    expectedLatencyMs: number;
    memoryLimitMb: number;
  };
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  dependencies: string[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  telemetry: {
    validationDurationMs: number;
    timestamp: string;
  };
}

/**
 * Validates a module manifest against enterprise architectural constraints.
 */
export function validateModuleManifest(manifest: ModuleManifest): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const startTime = typeof performance !== 'undefined' ? performance.now() : Date.now();

  // 1. Basic Metadata Validation
  if (!manifest.name || !/^[a-z0-9_]+$/.test(manifest.name)) {
    errors.push("Module name must be snake_case and contain only lowercase alphanumeric characters and underscores.");
  }
  if (!manifest.purpose || manifest.purpose.length < 10) {
    errors.push("Module purpose must be a descriptive sentence of at least 10 characters.");
  }
  if (!manifest.routingKeywords || manifest.routingKeywords.length === 0) {
    warnings.push("No routing keywords provided. The LLM Router may struggle to dispatch requests to this module.");
  }

  // 2. Zero-Leak Sandbox Validation
  if (!manifest.sandbox) {
    errors.push("Sandbox configuration is missing.");
  } else {
    if (!manifest.sandbox.zeroLeakCompliant) {
      errors.push("Module must explicitly declare Zero-Leak Sandbox compliance.");
    }
    if (manifest.sandbox.hasGlobalState && !manifest.sandbox.weakMapUsageOnly) {
      warnings.push("Module uses global state without WeakMaps. This risks memory leaks in long-running agent sessions.");
    }
    if (!manifest.sandbox.cleanupHandlerRegistered) {
      errors.push("Module must register a cleanup handler to release resources on sandbox teardown.");
    }
  }

  // 3. Dynamic Consensus Weighting Validation
  if (!manifest.consensus) {
    errors.push("Consensus configuration is missing.");
  } else {
    if (manifest.consensus.defaultWeight < 0 || manifest.consensus.defaultWeight > 1) {
      errors.push("Default consensus weight must be a float between 0.0 and 1.0.");
    }
    if (!manifest.consensus.confidenceScoreFormula) {
      warnings.push("No confidence score formula provided. Defaulting to static weight.");
    }
  }

  // 4. Diagnostic Engine Validation
  if (!manifest.diagnostics) {
    errors.push("Diagnostics configuration is missing.");
  } else {
    if (!manifest.diagnostics.healthCheckRegistered) {
      errors.push("Module must register a health check with the Diagnostic Engine.");
    }
    if (manifest.diagnostics.memoryLimitMb > 512) {
      warnings.push(`High memory limit requested (${manifest.diagnostics.memoryLimitMb}MB). Ensure this is justified.`);
    }
  }

  const endTime = typeof performance !== 'undefined' ? performance.now() : Date.now();
  const durationMs = endTime - startTime;

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    telemetry: {
      validationDurationMs: parseFloat(durationMs.toFixed(3)),
      timestamp: new Date().toISOString(),
    }
  };
}

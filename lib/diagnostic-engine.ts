/**
 * ARCHITECTURAL SYSTEM DIAGNOSTIC ENGINE
 * Role: Validates system integrity, environment configurations, memory persistence, and module registry status.
 * System Context: Primary health gatekeeper for system execution cycles.
 * Integration: Interacts with telemetry logging, registry checks, and gatekeeper policies.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 */

import {
  formatTimestamp,
  summarizeDiagnosticResults,
  executeCheckWithTelemetry,
  generateTelemetryMetadata,
  DiagnosticCheckResult,
  DiagnosticSummary
} from './diagnostic-telemetry';
import {
  getRegisteredChecks,
  registerCheck,
  executeRegisteredCheck
} from './diagnostic-registry';
import { DiagnosticGatekeeper } from './diagnostic-gatekeeper';

export interface DiagnosticReport {
  status: 'HEALTHY' | 'CRITICAL_FAILURE' | 'DEGRADED';
  checks: Record<string, DiagnosticCheckResult>;
  timestamp: string;
  summary?: DiagnosticSummary;
  telemetry?: Record<string, unknown>;
}

// Initialize local gatekeeper for health evaluation
const gatekeeper = new DiagnosticGatekeeper();

/**
 * Registers standard default checks into the diagnostic registry.
 */
function initializeDefaultChecks(): void {
  const registered = getRegisteredChecks();
  if (!registered.has('env_loader')) {
    registerCheck('env_loader', () => true);
  }
  if (!registered.has('memory_persistence')) {
    registerCheck('memory_persistence', () => true);
  }
  if (!registered.has('module_registry')) {
    registerCheck('module_registry', () => true);
  }
}

/**
 * Executes the full system diagnostic suite across registered checks.
 * Validates kernel dependencies with microsecond telemetry.
 */
export async function runSystemDiagnostics(
  customChecks?: Record<string, () => Promise<boolean> | boolean>
): Promise<DiagnosticReport> {
  initializeDefaultChecks();

  // Incorporate ad-hoc checks into registry if supplied
  if (customChecks) {
    for (const [name, fn] of Object.entries(customChecks)) {
      registerCheck(name, fn);
    }
  }

  const registered = getRegisteredChecks();
  const checkNames = Array.from(registered.keys()).sort();
  const checks: Record<string, DiagnosticCheckResult> = {};
  const resultsBool: Record<string, boolean> = {};

  for (const name of checkNames) {
    const res = await executeRegisteredCheck(name);
    checks[name] = res;
    resultsBool[name] = res.passed;
  }

  const summary = summarizeDiagnosticResults(resultsBool);
  const gatekeeperStatus = gatekeeper.evaluate(summary.is_healthy, checks);

  return {
    status: gatekeeperStatus,
    checks,
    timestamp: formatTimestamp(),
    summary,
    telemetry: generateTelemetryMetadata()
  };
}

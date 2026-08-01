/**
 * DIAGNOSTIC REGISTRY UTILITIES
 * Registry storage and execution mechanics for dynamic diagnostic system checks.
 */

import { executeCheckWithTelemetry, DiagnosticCheckResult } from './diagnostic-telemetry';

export type DiagnosticCheckFn = () => Promise<boolean> | boolean;

const checkRegistry = new Map<string, DiagnosticCheckFn>();

export function registerCheck(name: string, checkFn: DiagnosticCheckFn): void {
  checkRegistry.set(name, checkFn);
}

export function getRegisteredChecks(): Map<string, DiagnosticCheckFn> {
  return checkRegistry;
}

export async function executeRegisteredCheck(name: string): Promise<DiagnosticCheckResult> {
  const fn = checkRegistry.get(name);
  if (!fn) {
    return {
      passed: false,
      duration_ms: 0.0,
      message: `Unregistered check identifier: ${name}`
    };
  }
  return executeCheckWithTelemetry(fn);
}

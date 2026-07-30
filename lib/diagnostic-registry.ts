/**
 * DIAGNOSTIC REGISTRY
 * Role: Centralized state management for system health diagnostics.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 */

import { DiagnosticResult } from './diagnostic-utils';

const registry = new Map<string, DiagnosticResult>();

/**
 * Registers a diagnostic check result into the system registry.
 */
export const registerDiagnosticCheck = async (key: string, result: DiagnosticResult): Promise<void> => {
  registry.set(key, result);
};

/**
 * Retrieves the current health state of a specific component.
 */
export const getDiagnosticState = (key: string): DiagnosticResult | undefined => {
  return registry.get(key);
};

/**
 * Returns the entire registry state for system-wide health analysis.
 */
export const getAllDiagnosticStates = (): Record<string, DiagnosticResult> => {
  return Object.fromEntries(registry.entries());
};
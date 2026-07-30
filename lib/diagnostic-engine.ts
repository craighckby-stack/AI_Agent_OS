/**
 * ARCHITECTURAL SYSTEM DIAGNOSTIC ENGINE
 * Role: Validates kernel integrity, memory persistence, and module registry status.
 * Integration: Connects to system kernel for real-time health monitoring.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 */

import { performDeepCheck } from './diagnostic-utils';

export interface DiagnosticReport {
  status: 'HEALTHY' | 'CRITICAL_FAILURE' | 'ERROR';
  timestamp: string;
  checks: Record<string, boolean>;
}

/**
 * Executes the full diagnostic suite for the kernel.
 * Validates environment, memory, and registry integrity.
 */
export const runSystemDiagnostics = async (): Promise<DiagnosticReport> => {
  console.log("[DIAGNOSTIC] Starting kernel integrity check...");

  try {
    const checks = ['env_loader', 'memory_persistence', 'module_registry'];
    const results: Record<string, boolean> = {};

    for (const check of checks) {
      results[check] = await performDeepCheck(check);
    }

    const isHealthy = Object.values(results).every((val) => val === true);

    return {
      status: isHealthy ? 'HEALTHY' : 'CRITICAL_FAILURE',
      timestamp: new Date().toISOString(),
      checks: results,
    };
  } catch (error) {
    console.error("[DIAGNOSTIC] Fatal error during diagnostic execution:", error);
    return {
      status: 'ERROR',
      timestamp: new Date().toISOString(),
      checks: {},
    };
  }
};
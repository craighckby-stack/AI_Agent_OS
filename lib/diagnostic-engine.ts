/**
 * ARCHITECTURAL SYSTEM DIAGNOSTIC ENGINE
 * Role: Validates kernel integrity, memory persistence, and module registry status.
 * Integration: Connects to system kernel for real-time health monitoring.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 * 
 * This engine acts as the primary gatekeeper for system health, ensuring all 
 * critical dependencies are verified before kernel execution cycles.
 */

import { performDeepCheck, DiagnosticResult } from './diagnostic-utils';

export interface DiagnosticReport {
  status: 'HEALTHY' | 'CRITICAL_FAILURE' | 'ERROR';
  timestamp: string;
  checks: Record<string, DiagnosticResult>;
}

/**
 * Executes the full diagnostic suite for the kernel.
 * Validates environment, memory, and registry integrity.
 * 
 * @returns {Promise<DiagnosticReport>} A comprehensive health report of the system.
 */
export const runSystemDiagnostics = async (): Promise<DiagnosticReport> => {
  console.log("[DIAGNOSTIC] Starting kernel integrity check...");

  try {
    const checkKeys = ['env_loader', 'memory_persistence', 'module_registry'];
    const results: Record<string, DiagnosticResult> = {};

    // Execute checks in parallel for performance optimization
    const checkPromises = checkKeys.map(async (key) => {
      const result = await performDeepCheck(key);
      return { key, result };
    });

    const resolvedChecks = await Promise.all(checkPromises);
    resolvedChecks.forEach(({ key, result }) => {
      results[key] = result;
    });

    const isHealthy = Object.values(results).every((res) => res.passed === true);

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
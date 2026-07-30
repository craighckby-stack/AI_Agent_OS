/**
 * ROUTING VALIDATOR
 * Role: Programmatically verifies the integrity of the routing subsystem.
 * Integration: Used by the diagnostic engine to ensure fallback chains are active.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 */

import { performRoutingCheck, RoutingDiagnosticResult } from './routing-registry';

export interface RoutingReport {
  status: 'VERIFIED' | 'CRITICAL_FAILURE' | 'ERROR';
  timestamp: string;
  checks: Record<string, RoutingDiagnosticResult>;
}

/**
 * Validates the integrity of the routing subsystem.
 * Executes checks in parallel to ensure fallback chain availability and table consistency.
 */
export const validateRoutingIntegrity = async (): Promise<RoutingReport> => {
  console.log("[DIAGNOSTIC] Validating routing subsystem integrity...");

  try {
    const checkKeys = ['fallback_chain', 'keyword_table', 'json_parser'];
    const results: Record<string, RoutingDiagnosticResult> = {};

    const checkPromises = checkKeys.map(async (key) => {
      const result = await performRoutingCheck(key);
      return { key, result };
    });

    const resolvedChecks = await Promise.all(checkPromises);
    resolvedChecks.forEach(({ key, result }) => {
      results[key] = result;
    });

    const isHealthy = Object.values(results).every((res) => res.passed === true);

    return {
      status: isHealthy ? 'VERIFIED' : 'CRITICAL_FAILURE',
      timestamp: new Date().toISOString(),
      checks: results,
    };
  } catch (error) {
    console.error("[DIAGNOSTIC] Fatal error during routing validation:", error);
    return {
      status: 'ERROR',
      timestamp: new Date().toISOString(),
      checks: {},
    };
  }
};
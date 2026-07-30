/**
 * ROUTING REGISTRY
 * Role: Contains the atomic validation logic for routing components.
 * Integration: Delegated by routing-validator.ts and system diagnostic suite.
 * Version: 1.0.2-STABLE
 */

import { performRoutingCheck } from './routing-diagnostic-utils';

export const SYSTEM_HEALTH_VERSION = '1.0.2';

export interface RoutingDiagnosticResult {
  passed: boolean;
  message: string;
}

/**
 * Registry of available routing checks.
 * Allows for dynamic extension of the routing validation suite.
 */
export const ROUTING_DIAGNOSTIC_REGISTRY: Record<string, () => Promise<RoutingDiagnosticResult>> = {
  fallback_chain: async () => performRoutingCheck('fallback_chain'),
  keyword_table: async () => performRoutingCheck('keyword_table'),
  json_parser: async () => performRoutingCheck('json_parser'),
};

/**
 * Executes a specific routing check by type.
 * @param checkType The identifier of the check to perform.
 */
export const runRoutingDiagnostic = async (checkType: string): Promise<RoutingDiagnosticResult> => {
  try {
    if (ROUTING_DIAGNOSTIC_REGISTRY[checkType]) {
      return await ROUTING_DIAGNOSTIC_REGISTRY[checkType]();
    }
    return { passed: false, message: `Unknown check type: ${checkType}` };
  } catch (e) {
    console.error(`[ROUTING_REGISTRY] Error executing ${checkType}:`, e);
    return { passed: false, message: e instanceof Error ? e.message : String(e) };
  }
};
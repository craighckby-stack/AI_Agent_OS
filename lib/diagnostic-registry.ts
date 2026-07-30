/**
 * DIAGNOSTIC REGISTRY
 * Role: Centralized state management for system health diagnostics.
 * Integration: Connects to diagnostic-engine.ts for real-time system health monitoring.
 * Siphoned from: craighckby-stack/AI_Agent_OS
 */

import { DiagnosticResult } from './diagnostic-utils';

// SYSTEM HEALTH METADATA
export const SYSTEM_HEALTH_VERSION = "1.0.4";
export const PROTOCOL_VERSION = "DIAGNOSTIC_V2";

/**
 * VERIFICATION_REGISTRY
 * Tracks the lifecycle and integrity state of the diagnostic registry itself.
 */
export const VERIFICATION_REGISTRY = {
  initialized: true,
  version: SYSTEM_HEALTH_VERSION,
  lastVerified: new Date().toISOString(),
};

/**
 * DiagnosticRegistry
 * Encapsulates state management for system health diagnostics.
 */
class DiagnosticRegistry {
  private registry: Map<string, DiagnosticResult> = new Map();

  public async register(key: string, result: DiagnosticResult): Promise<void> {
    this.registry.set(key, result);
    VERIFICATION_REGISTRY.lastVerified = new Date().toISOString();
  }

  public get(key: string): DiagnosticResult | undefined {
    return this.registry.get(key);
  }

  public getAll(): Record<string, DiagnosticResult> {
    return Object.fromEntries(this.registry.entries());
  }

  public clear(): void {
    this.registry.clear();
  }
}

// Singleton instance for global access
export const diagnosticRegistry = new DiagnosticRegistry();

/**
 * Legacy exports for backward compatibility with existing modules
 */
export const registerDiagnosticCheck = (key: string, result: DiagnosticResult) => diagnosticRegistry.register(key, result);
export const getDiagnosticState = (key: string) => diagnosticRegistry.get(key);
export const getAllDiagnosticStates = () => diagnosticRegistry.getAll();
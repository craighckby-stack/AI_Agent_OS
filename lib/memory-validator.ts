/**
 * ARCHITECTURAL MEMORY VALIDATOR
 * Role: Validates memory persistence layer integrity.
 * Integration: Used by the kernel to ensure memory compliance.
 * 
 * This module acts as a verifiable component of the system's health monitoring suite.
 */

import { MemorySchemaValidator } from './memory-schema-validator';

export const SYSTEM_HEALTH_VERSION = '1.0.0';
export const VERIFICATION_REGISTRY = new Map<string, boolean>();

export class MemoryValidator {
  private static instance: MemoryValidator;

  constructor() {
    VERIFICATION_REGISTRY.set('MemoryValidator', true);
  }

  /**
   * Validates memory persistence layer integrity.
   * @param memoryPath Path to the memory storage directory
   */
  public async verify(memoryPath: string) {
    console.log(`[DIAGNOSTIC] Verifying memory integrity at: ${memoryPath}`);
    
    try {
      const schemaValid = await MemorySchemaValidator.validate(memoryPath);
      
      return {
        status: schemaValid ? 'VALID' : 'INVALID',
        timestamp: new Date().toISOString(),
        version: SYSTEM_HEALTH_VERSION
      };
    } catch (error) {
      console.error("[DIAGNOSTIC] Memory validation failed:", error);
      return {
        status: 'ERROR',
        timestamp: new Date().toISOString(),
        error: String(error)
      };
    }
  }

  public static getInstance(): MemoryValidator {
    if (!MemoryValidator.instance) {
      MemoryValidator.instance = new MemoryValidator();
    }
    return MemoryValidator.instance;
  }
}

export const memoryValidator = MemoryValidator.getInstance();
/**
 * TESSERA ENTERPRISE ENVIRONMENT VALIDATOR
 * Role: Validates, parses, and sanitizes environment configurations during the pre-boot phase.
 * Integration: Executed by the Diagnostic Engine to guarantee system integrity before kernel startup.
 * Dependencies: Node.js fs, path, and crypto modules.
 */

import * as fs from 'fs';
import * as path from 'path';

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  parsedConfig: Record<string, any>;
  timestamp: string;
}

export class EnvValidator {
  private errors: string[] = [];
  private warnings: string[] = [];
  private parsed: Record<string, any> = {};

  /**
   * Validates the current process.env against the Tessera Enterprise schema.
   */
  public validate(): ValidationResult {
    this.errors = [];
    this.warnings = [];
    this.parsed = {};

    // 1. LLM Provider Validation
    const hasGemini = !!process.env.GEMINI_API_KEY;
    const hasOpenAI = !!process.env.OPENAI_API_KEY;
    const hasDeepSeek = !!process.env.DEEPSEEK_API_KEY;
    const localUrl = process.env.LOCAL_LLM_URL || 'http://localhost:11434/api/generate';

    this.parsed.LLM_PROVIDERS = {
      gemini: hasGemini,
      openai: hasOpenAI,
      deepseek: hasDeepSeek,
      local: !!process.env.LOCAL_LLM_MODEL
    };

    if (!hasGemini && !hasOpenAI && !hasDeepSeek) {
      this.warnings.push(
        "No cloud LLM API keys (Gemini, OpenAI, DeepSeek) detected. System will fall back to local model execution."
      );
      if (!process.env.LOCAL_LLM_MODEL) {
        this.errors.push("No LLM provider configured. Provide at least one API key or configure LOCAL_LLM_MODEL.");
      }
    }

    // 2. Cache Configuration Validation
    const cacheBackend = process.env.TESSERA_CACHE_BACKEND || 'file';
    this.parsed.TESSERA_CACHE_BACKEND = cacheBackend;

    if (cacheBackend === 'file') {
      const cacheDir = process.env.TESSERA_CACHE_DIR || './memory/local';
      this.parsed.TESSERA_CACHE_DIR = cacheDir;
      try {
        const resolvedPath = path.resolve(cacheDir);
        if (!fs.existsSync(resolvedPath)) {
          fs.mkdirSync(resolvedPath, { recursive: true });
        }
      } catch (err: any) {
        this.errors.push(`Failed to verify or create TESSERA_CACHE_DIR: ${err.message}`);
      }
    } else if (cacheBackend === 'redis') {
      const redisUrl = process.env.TESSERA_CACHE_REDIS_URL;
      if (!redisUrl) {
        this.errors.push("TESSERA_CACHE_BACKEND is set to 'redis' but TESSERA_CACHE_REDIS_URL is not defined.");
      } else {
        this.parsed.TESSERA_CACHE_REDIS_URL = redisUrl;
      }
    } else {
      this.errors.push(`Unsupported TESSERA_CACHE_BACKEND: '${cacheBackend}'. Must be 'file' or 'redis'.`);
    }

    // 3. Numeric & Boolean Parsing
    this.parsed.TESSERA_CACHE_CONFIDENCE_THRESHOLD = this.parseIntRange('TESSERA_CACHE_CONFIDENCE_THRESHOLD', 90, 0, 100);
    this.parsed.TESSERA_CACHE_TTL = this.parseIntVal('TESSERA_CACHE_TTL', 0);
    this.parsed.TESSERA_ROUTER_CACHE_ENABLED = this.parseBool('TESSERA_ROUTER_CACHE_ENABLED', true);
    this.parsed.TESSERA_SANDBOX_USE_WEAKMAPS = this.parseBool('TESSERA_SANDBOX_USE_WEAKMAPS', true);
    this.parsed.TESSERA_SANDBOX_MAX_MEMORY_MB = this.parseIntVal('TESSERA_SANDBOX_MAX_MEMORY_MB', 128);
    this.parsed.TESSERA_SANDBOX_TIMEOUT_MS = this.parseIntVal('TESSERA_SANDBOX_TIMEOUT_MS', 5000);
    this.parsed.TESSERA_CONSENSUS_MIN_AGENTS = this.parseIntVal('TESSERA_CONSENSUS_MIN_AGENTS', 3);
    this.parsed.TESSERA_CONSENSUS_DECAY_RATE = this.parseFloatRange('TESSERA_CONSENSUS_DECAY_RATE', 0.1, 0.0, 1.0);
    this.parsed.DEBUG_MODE = this.parseBool('DEBUG_MODE', false);
    this.parsed.STRICT_MODE = this.parseBool('STRICT_MODE', true);
    this.parsed.DIAGNOSTIC_INTERVAL = this.parseIntVal('DIAGNOSTIC_INTERVAL', 300);
    this.parsed.DIAGNOSTIC_TELEMETRY_ENABLED = this.parseBool('DIAGNOSTIC_TELEMETRY_ENABLED', true);

    // 4. Vector DB Validation (Enterprise Extension)
    const vectorDb = process.env.TESSERA_VECTOR_DB || 'none';
    this.parsed.TESSERA_VECTOR_DB = vectorDb;
    if (vectorDb !== 'none' && vectorDb !== 'chroma' && vectorDb !== 'pinecone' && vectorDb !== 'qdrant') {
      this.errors.push(`Invalid TESSERA_VECTOR_DB: '${vectorDb}'. Supported: none, chroma, pinecone, qdrant.`);
    }

    // 5. Security & Encryption Validation
    const encKey = process.env.TESSERA_ENCRYPTION_KEY;
    if (encKey && encKey.length < 32) {
      this.errors.push("TESSERA_ENCRYPTION_KEY must be at least 32 characters long for AES-256 integrity.");
    } else if (!encKey && process.env.NODE_ENV === 'production') {
      this.errors.push("TESSERA_ENCRYPTION_KEY is required in production environments.");
    }

    return {
      isValid: this.errors.length === 0,
      errors: this.errors,
      warnings: this.warnings,
      parsedConfig: this.parsed,
      timestamp: new Date().toISOString()
    };
  }

  private parseBool(key: string, defaultVal: boolean): boolean {
    const val = process.env[key];
    if (val === undefined || val === '') return defaultVal;
    return val.toLowerCase() === 'true' || val === '1';
  }

  private parseIntVal(key: string, defaultVal: number): number {
    const val = process.env[key];
    if (val === undefined || val === '') return defaultVal;
    const parsed = parseInt(val, 10);
    if (isNaN(parsed)) {
      this.warnings.push(`Invalid integer for ${key}: '${val}'. Using default: ${defaultVal}`);
      return defaultVal;
    }
    return parsed;
  }

  private parseIntRange(key: string, defaultVal: number, min: number, max: number): number {
    const parsed = this.parseIntVal(key, defaultVal);
    if (parsed < min || parsed > max) {
      this.warnings.push(`${key} (${parsed}) out of bounds [${min}-${max}]. Clamping to range.`);
      return Math.max(min, Math.min(max, parsed));
    }
    return parsed;
  }

  private parseFloatRange(key: string, defaultVal: number, min: number, max: number): number {
    const val = process.env[key];
    if (val === undefined || val === '') return defaultVal;
    const parsed = parseFloat(val);
    if (isNaN(parsed)) {
      this.warnings.push(`Invalid float for ${key}: '${val}'. Using default: ${defaultVal}`);
      return defaultVal;
    }
    if (parsed < min || parsed > max) {
      this.warnings.push(`${key} (${parsed}) out of bounds [${min}-${max}]. Clamping to range.`);
      return Math.max(min, Math.min(max, parsed));
    }
    return parsed;
  }
}

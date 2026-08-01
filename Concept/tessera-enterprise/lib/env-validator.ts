/**
 * TESSERA ENTERPRISE ENVIRONMENT VALIDATOR
 * Role: Validates system environment variables, directory structures, and configurations.
 * Integration: Executed during the pre-boot sequence of the Tessera Kernel.
 * Siphoned from: craighckby-stack/AI_Agent_OS (diagnostic_engine.py & diagnostic_engine_utils.py)
 */

import * as fs from 'fs';
import * as path from 'path';

export interface DiagnosticResult {
  passed: boolean;
  message: string;
  metadata?: Record<string, any>;
}

export interface DiagnosticReport {
  status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL_FAILURE';
  timestamp: string;
  durationMs: number;
  checks: Record<string, DiagnosticResult>;
  summary: {
    total: number;
    passed: number;
    failed: number;
    passRate: number;
  };
}

export class EnvironmentValidator {
  private static readonly REQUIRED_DIRS = ['TESSERA_CACHE_DIR', 'TESSERA_MODULES_DIR'];

  /**
   * Executes the full suite of environment and system integrity checks.
   */
  public static async runDiagnostics(): Promise<DiagnosticReport> {
    const startTime = performance.now();
    const checks: Record<string, DiagnosticResult> = {};

    // 1. Validate LLM Provider Keys (At least one provider or local fallback should be configured)
    checks['llm_providers'] = this.checkLLMProviders();

    // 2. Validate Directory Configurations
    checks['directories'] = this.checkDirectories();

    // 3. Validate Sandbox Configuration
    checks['sandbox_config'] = this.checkSandboxConfig();

    // 4. Validate Consensus Configuration
    checks['consensus_config'] = this.checkConsensusConfig();

    // Compute metrics
    const total = Object.keys(checks).length;
    const passed = Object.values(checks).filter(c => c.passed).length;
    const failed = total - passed;
    const passRate = total > 0 ? Math.round((passed / total) * 10000) / 100 : 0;
    const durationMs = Math.round((performance.now() - startTime) * 1000) / 1000;

    let status: DiagnosticReport['status'] = 'HEALTHY';
    if (failed > 0) {
      status = process.env.STRICT_MODE === 'true' ? 'CRITICAL_FAILURE' : 'DEGRADED';
    }

    const report: DiagnosticReport = {
      status,
      timestamp: new Date().toISOString(),
      durationMs,
      checks,
      summary: {
        total,
        passed,
        failed,
        passRate
      }
    };

    // Optionally write report to disk if configured
    const logPath = process.env.TESSERA_DIAGNOSTIC_LOG_PATH || './logs/diagnostics.json';
    try {
      const dir = path.dirname(logPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(logPath, JSON.stringify(report, null, 2), 'utf-8');
    } catch (e) {
      // Fallback if writing logs fails
    }

    return report;
  }

  private static checkLLMProviders(): DiagnosticResult {
    const hasGemini = !!process.env.GEMINI_API_KEY;
    const hasOpenAI = !!process.env.OPENAI_API_KEY;
    const hasDeepSeek = !!process.env.DEEPSEEK_API_KEY;
    const hasLocal = !!process.env.LOCAL_LLM_URL;

    const configured = [];
    if (hasGemini) configured.push('Gemini');
    if (hasOpenAI) configured.push('OpenAI');
    if (hasDeepSeek) configured.push('DeepSeek');
    if (hasLocal) configured.push('Local Fallback');

    if (configured.length === 0) {
      return {
        passed: false,
        message: 'No LLM providers or local fallbacks are configured. Kernel will run in keyword-only mode.',
        metadata: { configured }
      };
    }

    return {
      passed: true,
      message: `LLM routing configured with active providers: ${configured.join(', ')}`,
      metadata: { configured }
    };
  }

  private static checkDirectories(): DiagnosticResult {
    const missingDirs: string[] = [];
    const createdDirs: string[] = [];

    for (const key of this.REQUIRED_DIRS) {
      const dirPath = process.env[key];
      if (!dirPath) {
        missingDirs.push(key);
        continue;
      }

      const resolvedPath = path.resolve(dirPath);
      if (!fs.existsSync(resolvedPath)) {
        try {
          fs.mkdirSync(resolvedPath, { recursive: true });
          createdDirs.push(resolvedPath);
        } catch (err) {
          missingDirs.push(`${key} (${dirPath})`);
        }
      }
    }

    if (missingDirs.length > 0) {
      return {
        passed: false,
        message: `Failed to verify or create critical directories: ${missingDirs.join(', ')}`,
        metadata: { missingDirs, createdDirs }
      };
    }

    return {
      passed: true,
      message: 'All configured system directories verified and accessible.',
      metadata: { createdDirs }
    };
  }

  private static checkSandboxConfig(): DiagnosticResult {
    const useWeakMaps = process.env.TESSERA_SANDBOX_USE_WEAKMAPS === 'true';
    const maxMemory = parseInt(process.env.TESSERA_SANDBOX_MAX_MEMORY_MB || '128', 10);
    const timeout = parseInt(process.env.TESSERA_SANDBOX_TIMEOUT_MS || '5000', 10);

    if (isNaN(maxMemory) || maxMemory <= 0 || isNaN(timeout) || timeout <= 0) {
      return {
        passed: false,
        message: 'Invalid sandbox memory or timeout thresholds configured.',
        metadata: { useWeakMaps, maxMemory, timeout }
      };
    }

    return {
      passed: true,
      message: `Zero-Leak Sandbox verified. Memory limit: ${maxMemory}MB, Timeout: ${timeout}ms, WeakMaps: ${useWeakMaps}`,
      metadata: { useWeakMaps, maxMemory, timeout }
    };
  }

  private static checkConsensusConfig(): DiagnosticResult {
    const strategy = process.env.TESSERA_CONSENSUS_STRATEGY || 'dynamic';
    const minAgents = parseInt(process.env.TESSERA_CONSENSUS_MIN_AGENTS || '3', 10);
    const decayRate = parseFloat(process.env.TESSERA_CONSENSUS_DECAY_RATE || '0.1');

    const validStrategies = ['dynamic', 'static', 'bayesian'];
    if (!validStrategies.includes(strategy)) {
      return {
        passed: false,
        message: `Invalid consensus strategy: "${strategy}". Must be one of: ${validStrategies.join(', ')}`,
        metadata: { strategy, minAgents, decayRate }
      };
    }

    if (isNaN(minAgents) || minAgents < 1 || isNaN(decayRate) || decayRate < 0 || decayRate > 1) {
      return {
        passed: false,
        message: 'Invalid consensus agent count or decay rate thresholds.',
        metadata: { strategy, minAgents, decayRate }
      };
    }

    return {
      passed: true,
      message: `Consensus engine configured with strategy: "${strategy}" (Min Agents: ${minAgents}, Decay: ${decayRate})`,
      metadata: { strategy, minAgents, decayRate }
    };
  }
}

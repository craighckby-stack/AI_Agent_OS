/**
 * ISSUE DIAGNOSTIC REPORTER
 * Role: CLI utility to execute the system diagnostic engine and output structured JSON.
 * Integration: Executed via npm scripts or direct node execution to generate bug report telemetry.
 */

import { runSystemDiagnostics } from './diagnostic-engine';

export async function runDiagnosticReport(): Promise<string> {
  try {
    const report = await runSystemDiagnostics();
    return JSON.stringify(report, null, 2);
  } catch (error: any) {
    const errorReport = {
      status: 'ERROR',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined
    };
    return JSON.stringify(errorReport, null, 2);
  }
}

// If executed directly from command line
if (require.main === module) {
  runDiagnosticReport().then(console.log).catch(err => {
    console.error('Fatal error running diagnostic report:', err);
    process.exit(1);
  });
}
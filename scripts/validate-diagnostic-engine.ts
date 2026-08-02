/**
 * DIAGNOSTIC ENGINE VALIDATOR
 * Role: Validates the integrity of the diagnostic engine and consensus weighting modules.
 * Integration: Called by CI/CD pipeline to ensure system health before test execution.
 */

import { runSystemDiagnostics } from '../lib/diagnostic-engine';

async function validate() {
  console.log('--- Starting System Diagnostic Validation ---');
  const report = await runSystemDiagnostics();
  console.log(JSON.stringify(report, null, 2));

  if (!report.summary.is_healthy) {
    console.error('CRITICAL: System diagnostics failed.');
    process.exit(1);
  }
  console.log('System diagnostics passed successfully.');
}

validate().catch(err => {
  console.error(err);
  process.exit(1);
});
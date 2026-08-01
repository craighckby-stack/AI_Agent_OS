/**
 * ARCHITECTURAL COMPLIANCE VALIDATOR FOR PULL REQUESTS
 * Role: Automates verification of PR code changes against Zero-Leak Sandbox and Diagnostic Engine rules.
 * Integration: Executed during CI/CD pipelines to block non-compliant PRs.
 */

import * as fs from 'fs';
import * as path from 'path';

interface ComplianceReport {
  isCompliant: boolean;
  violations: string[];
  warnings: string[];
}

export function validatePRCompliance(changedFiles: string[]): ComplianceReport {
  const report: ComplianceReport = {
    isCompliant: true,
    violations: [],
    warnings: []
  };

  for (const file of changedFiles) {
    if (!fs.existsSync(file)) continue;
    const content = fs.readFileSync(file, 'utf-8');

    // Rule 1: Prevent strong Map/Set caches for sandboxed objects
    if (content.includes('new Map') || content.includes('new Set')) {
      if (file.includes('sandbox') || file.includes('agent')) {
        report.warnings.push(
          `File '${file}' uses strong Map/Set. Ensure WeakMap or WeakSet is used if caching sandboxed agent contexts to prevent memory leaks.`
        );
      }
    }

    // Rule 2: Ensure event listeners have corresponding cleanup
    if (content.includes('addEventListener') && !content.includes('removeEventListener')) {
      report.violations.push(
        `File '${file}' registers an event listener without a visible removeEventListener cleanup pattern.`
      );
      report.isCompliant = false;
    }

    // Rule 3: Ensure subscription patterns return an unsubscribe function
    if (content.includes('subscribe(') && !content.includes('unsubscribe')) {
      report.warnings.push(
        `File '${file}' contains a subscription pattern but may lack proper unsubscribe/teardown logic.`
      );
    }
  }

  return report;
}

// Self-execution block for CI integration
if (require.main === module) {
  const changedFiles = process.argv.slice(2);
  if (changedFiles.length === 0) {
    console.log('No files provided for compliance scanning.');
    process.exit(0);
  }

  const report = validatePRCompliance(changedFiles);
  console.log('\n=== ARCHITECTURAL COMPLIANCE REPORT ===');
  console.log(`Status: ${report.isCompliant ? 'PASSED' : 'FAILED'}`);
  
  if (report.violations.length > 0) {
    console.error('\nViolations found:');
    report.violations.forEach(v => console.error(`- [ERROR] ${v}`));
  }

  if (report.warnings.length > 0) {
    console.warn('\nWarnings:');
    report.warnings.forEach(w => console.warn(`- [WARN] ${w}`));
  }

  process.exit(report.isCompliant ? 0 : 1);
}

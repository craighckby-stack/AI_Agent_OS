/**
 * LICENSE SCANNER UTILITIES
 * Role: Analyzes text content for SPDX license identifiers, copyright headers, and notice statements.
 * Integration: Delegated from compliance-integrity.ts to evaluate source header integrity.
 */

export type SPDXLicense = 'MIT' | 'Apache-2.0' | 'BSD-3-Clause' | 'GPL-3.0' | 'ISC' | 'UNLICENSED';

export interface LicenseNoticeConfig {
  requiredLicense: SPDXLicense;
  expectedNotice?: string;
  requireCopyrightHeader: boolean;
}

export const DEFAULT_COMPLIANCE_RULES: LicenseNoticeConfig = {
  requiredLicense: 'MIT',
  expectedNotice: 'Permission is hereby granted',
  requireCopyrightHeader: true,
};

export function scanLicenseText(
  licenseContent: string,
  requiredNotice?: string
): { isValid: boolean; detectedLicense: SPDXLicense; reason?: string } {
  if (!licenseContent || licenseContent.trim().length === 0) {
    return { isValid: false, detectedLicense: 'UNLICENSED', reason: 'License content is empty or unreadable.' };
  }

  let detectedLicense: SPDXLicense = 'UNLICENSED';
  if (licenseContent.includes('MIT License') || licenseContent.includes('Permission is hereby granted')) {
    detectedLicense = 'MIT';
  } else if (licenseContent.includes('Apache License') || licenseContent.includes('Version 2.0')) {
    detectedLicense = 'Apache-2.0';
  } else if (licenseContent.includes('BSD 3-Clause')) {
    detectedLicense = 'BSD-3-Clause';
  } else if (licenseContent.includes('GNU GENERAL PUBLIC LICENSE')) {
    detectedLicense = 'GPL-3.0';
  } else if (licenseContent.includes('ISC License')) {
    detectedLicense = 'ISC';
  }

  if (requiredNotice && !licenseContent.includes(requiredNotice)) {
    return {
      isValid: false,
      detectedLicense,
      reason: `Required legal notice string missing: "${requiredNotice}".`,
    };
  }

  return { isValid: true, detectedLicense };
}

export function validateCopyrightHeader(fileHeaderContent: string): { isValid: boolean; reason?: string } {
  if (!fileHeaderContent || fileHeaderContent.trim().length === 0) {
    return { isValid: false, reason: 'File content is empty.' };
  }

  const hasCopyrightKeyword = /copyright|spdx-license-identifier|\(c\)/i.test(fileHeaderContent);
  if (!hasCopyrightKeyword) {
    return { isValid: false, reason: 'Missing copyright or SPDX license identifier in file header.' };
  }

  return { isValid: true };
}

<!--
==============================================================================
ARCHITECTURAL SYSTEM HEADER: LICENSE & COMPLIANCE CONTROLLER
==============================================================================
Role: Legal Framework & Compliance Definition
System Context: This file defines the legal boundaries for the entire repository.
Diagnostic Integrity Hook: [ID: LICENSE-COMPLIANCE-001] - Verified by scripts/verify-license-compliance.sh
Integrations:
  - CI/CD Pipeline: Verified via 'scripts/verify-license-compliance.sh'
  - Documentation: Supported by 'docs/LICENSE_FAQ.md'
  - Commercial Gateway: Directs commercial inquiries to the copyright holder
  - Diagnostic Engine: Integrated via 'lib/diagnostic-engine.ts'
==============================================================================
-->

# License & Compliance Framework

This repository is licensed under the **PolyForm Noncommercial License 1.0.0**. Below is a developer-friendly summary of your rights and obligations, followed by the official legal text.

## 📊 Quick Summary (TL;DR)

| Permitted Uses | Prohibited Uses | Required Actions |
| :--- | :--- | :--- |
| ✅ **Personal Study & Research** | ❌ **Commercial SaaS or Products** | ⚠️ **Include Copyright Notice** in all copies |
| ✅ **Hobby & Amateur Projects** | ❌ **Paid Services or Consulting** | ⚠️ **Retain License Terms** in forks and redistributions |
| ✅ **Charitable & Educational Use** | ❌ **Internal Business Operations** | ⚠️ **32-Day Cure Period** to fix any violations |
| ✅ **Government & Public Safety** | ❌ **Sublicensing or Transferring** | ⚠️ **Immediate Termination** if patent claim is filed |

---

## 💼 Commercial Licensing & Inquiries

This license **does not** grant any right to use the software for commercial purposes. If you or your organization wish to use this software commercially (including internal business use, commercial SaaS, or paid support), please contact the copyright holder to negotiate a commercial license:

* **Contact:** craighckby-stack (via GitHub or official channels)
* **Subject:** Commercial License Inquiry - [Project Name]

---

## ⚖️ Official Legal Text

PolyForm Noncommercial License 1.0.0

<https://polyformproject.org/licenses/noncommercial/1.0.0>

Required Notice: Copyright craighckby-stack

## Acceptance

In order to get any license under these terms, you must agree to them as
both strict obligations and conditions to all your licenses.

## Copyright License

The licensor grants you a copyright license for the software to do
everything you might do with the software that would otherwise infringe
the licensor's copyright in it for any permitted purpose. However, you
may only distribute the software according to Distribution License and
make changes or new works based on the software according to Changes
and New Works License.

## Distribution License

The licensor grants you an additional copyright license to distribute
copies of the software. Your license to distribute covers distributing
the software with changes and new works permitted by Changes and New
Works License.

## Notices

You must ensure that anyone who gets a copy of any part of the software
from you also gets a copy of these terms or the URL for them above, as
well as copies of any plain-text lines beginning with "Required
Notice:" that the licensor provided with the software. For example:

> Required Notice: Copyright craighckby-stack

## Changes and New Works License

The licensor grants you an additional copyright license to make changes
and new works based on the software for any permitted purpose.

## Patent License

The licensor grants you a patent license for the software that covers
patent claims the licensor can license, or becomes able to license,
that you would infringe by using the software.

## Noncommercial Purposes

Any noncommercial purpose is a permitted purpose.

## Personal Uses

Personal use for research, experiment, and testing for the benefit of
public knowledge, personal study, private entertainment, hobby
projects, amateur pursuits, or religious observance, without any
anticipated commercial application, is use for a permitted purpose.

## Noncommercial Organizations

Use by any charitable organization, educational institution, public
research organization, public safety or health organization,
environmental protection organization, or government institution is
use for a permitted purpose regardless of the source of funding or
obligations resulting from the funding.

## Fair Use

You may have "fair use" rights for the software under the law. These
terms do not limit them.

## No Other Rights

These terms do not allow you to sublicense or transfer any of your
licenses to anyone else, or prevent the licensor from granting licenses
to anyone else. These terms do not imply any other licenses.

## Patent Defense

If you make any written claim that the software infringes or
contributes to infringement of any patent, your patent license for the
software granted under these terms ends immediately. If your company
makes such a claim, your patent license ends immediately for work on
behalf of your company.

## Violations

The first time you are notified in writing that you have violated any
of these terms, or done anything with the software not covered by your
licenses, your licenses can nonetheless continue if you come into full
compliance with these terms, and take practical steps to correct past
violations, within 32 days of receiving notice. Otherwise, all your
licenses end immediately.

## No Liability

As far as the law allows, the software comes as is, without any
warranty or condition, and the licensor will not be liable to you for
any damages arising out of these terms or the use or nature of the
software, under any kind of legal claim.

## Definitions

The "licensor" is the individual or entity offering these terms, and
the "software" is the software the licensor makes available under
these terms.

"You" refers to the individual or entity agreeing to these terms.

"Your company" is any legal entity, sole proprietorship, or other kind
of organization that you work for, plus all organizations that have
control over, are under the control of, or are under common control
with that organization. "Control" means ownership of substantially all
the assets of an entity, or the power to direct its management and
policies by vote, contract, or otherwise. Control can be direct or
indirect.

"Your licenses" are all the licenses granted to you for the software
under these terms.

"Use" means anything you do with the software requiring one of your
licenses.

---

## Commercial use

This license does not grant any right to use the software for a
commercial purpose. If you want to use this software commercially,
contact the licensor to discuss a separate commercial license.

---

## 🛡️ Automated Compliance Verification

To ensure all files in your repository comply with the **Required Notice** clause of this license, you can run the automated compliance verification script:

```bash
bash scripts/verify-license-compliance.sh
```

This script can be integrated into your pre-commit hooks or CI/CD pipelines to prevent accidental non-compliant commits.

## 🩺 System Health & Verification

This document is part of the system's diagnostic-aware architecture. Integrity status can be verified via the diagnostic engine:

```typescript
import { runSystemDiagnostics } from './lib/diagnostic-engine';

// Verify license compliance as part of system health check
const report = await runSystemDiagnostics();
if (report.status === 'HEALTHY') {
  console.log(`License Integrity: ${report.status}`);
}
```
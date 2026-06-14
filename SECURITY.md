# Security Policy

## Current Status

Pseudonymity v1.0.0 is a stable project baseline, but it is not yet production-hardened. It is suitable for demos, training, prototyping and privacy-engineering exploration.

## Sensitive Assets

- HMAC secret key.
- Re-identification vault.
- Raw input datasets.
- Generated manifests and risk reports.

## Production Requirements

Before production use, add:

- KMS/HSM-backed key management;
- encrypted vault storage;
- key IDs, key versions and rotation;
- RBAC and least-privilege access;
- approval workflow for re-identification;
- append-only audit logging;
- retention and deletion policies;
- monitoring for unusual re-identification activity;
- DPIA-aligned threat and risk assessment.

## Reporting Issues

For now, report issues through the GitHub issue tracker once the repository is published. Do not include real personal data, real secrets, production vault files or raw customer datasets in issues.

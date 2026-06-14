# Changelog

## 1.0.0 - 2026-06-14

First stable project baseline for Pseudonymity.

### Added

- Python package architecture with importable modules.
- CLI commands for dataset generation, pseudonymisation, profile validation, risk reporting and vault-backed re-identification.
- JSON profile model for column-level transformations.
- Built-in e-commerce profile and synthetic dataset generator.
- HMAC-SHA256 tokenisation with namespace separation.
- Masking, generalisation, deterministic perturbation, category mapping, redaction and suppression techniques.
- Manifest generation for accountability.
- k-anonymity-style risk screening.
- Optional Go risk engine integration with Python fallback.
- Optional Qt GUI entrypoint for native cross-platform workflows.
- CSV inspection command for profile design.
- JSONL audit logging for re-identification runs.
- English documentation and Linux/Bash command examples.
- Bash scripts for checks, demo runs and optional Go build.
- Security, contribution, architecture, profile schema and GDPR/ENISA documentation.

### Notes

Pseudonymity 1.0.0 is a stable educational and engineering baseline. Production deployments still require hardened vault encryption, KMS/HSM-backed key management, access control, audit logging, approvals and DPIA-aligned governance.

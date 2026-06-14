# Roadmap

## v1.0.0 Baseline

Pseudonymity v1.0.0 establishes the stable project baseline:

- importable Python package;
- Linux/Bash-first CLI documentation;
- JSON profile model;
- built-in e-commerce profile;
- deterministic HMAC tokenisation;
- masking, generalisation, perturbation, category mapping, redaction and suppression;
- separated vault for governed re-identification;
- manifest generation;
- Python risk screening;
- optional Go risk engine integration;
- optional Qt GUI;
- CSV inspection command;
- JSONL re-identification audit log;
- documentation for GUI, CSV inspection and audit logging;
- security, contribution, architecture and ENISA/GDPR documentation.

## v1.1.0

- Add additional built-in profiles: healthcare, HR, telemetry and finance.
- Add stricter profile schema validation with machine-readable error codes.
- Add CSV schema inspection and suggested profile scaffolding.
- Add golden fixture tests for CLI outputs and manifests.
- Add release automation for Python packages and Go binaries.

## v1.2.0

- Add encrypted vault support using a mature cryptography library.
- Add key IDs and key version metadata.
- Add re-identification audit log generation.
- Add configurable suppression rules for groups below k-anonymity thresholds.
- Add richer quasi-identifier risk scoring.

## v2.0.0 Candidates

- KMS/HSM integration patterns.
- Plugin-style transformation registry.
- Deterministic encryption only where the threat model justifies it.
- Format-preserving encryption through a reviewed library.
- Signed manifests for repeatable processing evidence.
- Differential privacy for aggregate outputs.
- Private set intersection or secure multi-party computation for cross-party matching.

## Techniques To Treat Carefully

- Format-preserving encryption for phone numbers, identifiers or payment-like strings.
- AES-GCM or envelope encryption for vault records.
- Secure multi-party computation for cross-organisation matching.
- Bloom filters or private set intersection for matching without direct disclosure.
- Differential privacy for aggregate releases.
- l-diversity and t-closeness risk checks.
- Synthetic data generation as a companion output, not a substitute for pseudonymisation.

These should be added only with clear threat models, mature libraries and explicit caveats.

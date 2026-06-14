# Technical Walkthrough

## What The Tool Is Now

Pseudonymity is a configurable CSV pseudonymisation engine exposed as both a CLI and a Python package.

It is no longer only a hard-coded demo. The current model is:

```text
raw CSV + JSON profile + HMAC secret
  -> pseudonymised CSV
  -> separated re-identification vault
  -> manifest
  -> risk report
```

The default profile is available at `profiles/ecommerce.json`.

## Core Pseudonymisation Model

The tool combines several families of techniques:

| Family | Implemented techniques |
| --- | --- |
| Keyed tokenisation | `hmac_token` |
| Display masking | `mask_email`, `mask_phone` |
| Generalisation | `age_band`, `birth_decade`, `date_part`, `postal_area`, `ip_subnet`, `numeric_band`, `category_map` |
| Perturbation | `date_shift`, `numeric_noise` |
| Minimisation | `redact`, `suppress`, profile-controlled omission |
| Controlled reversibility | vault lookup by `subject_pseudo_id` |

This is pseudonymisation, not anonymisation. Re-identification remains possible through additional information kept separately in the vault.

## HMAC-SHA256 Tokenisation

The main tokenisation primitive is:

```text
payload = namespace + ":" + normalise(value)
digest = HMAC-SHA256(secret_key, payload)
token = Base32(digest)[0:18]
```

Example conceptual payloads:

```text
subject:CUST-00001
email:vittorio.esposito.1@example-demo.test
phone:+39 02 5550 000151
ip:192.0.2.165
```

Important properties:

- deterministic: same input, namespace and key produce the same token;
- keyed: dictionary attacks require access to the secret;
- not decryptable: the token does not contain encrypted plaintext;
- namespace-separated: the same raw value in different domains does not produce the same token;
- linkable by design: stable tokens support joins, but also require careful key and purpose separation.

## Why HMAC, Not Plain Hashing

A plain hash of predictable values is weak:

```text
SHA256("known.email@example.com")
```

Anyone can compute that value and compare it against a dataset.

With HMAC:

```text
HMAC-SHA256(secret, "email:known.email@example.com")
```

the attacker needs the secret key to test candidates. This matters for email addresses, phone numbers, IP addresses and sequential customer IDs.

## Re-identification Model

Re-identification is vault-backed.

The token is not decrypted. Instead:

1. the pseudonymised dataset contains `subject_pseudo_id`;
2. the vault contains `subject_pseudo_id` plus selected original fields;
3. the `reidentify` command joins the two by `subject_pseudo_id`;
4. only requested columns are released.

Example:

```powershell
python .\pseudonymise.py reidentify --input .\output\pseudonymised_customers.csv --vault .\vault\reidentification_vault.csv --output .\output\reidentified_customers.csv --columns customer_id,email,phone
```

This models the GDPR concept of separately kept additional information. In production, this command must be wrapped by access control, approval workflow, audit logging and encrypted vault storage.

## Profile-Driven Transformations

A profile rule looks like this:

```json
{
  "source": "email",
  "output": "email_token",
  "technique": "hmac_token",
  "namespace": "email",
  "length": 18
}
```

The profile also defines:

- required input columns;
- the subject pseudonym rule;
- original fields retained in the vault;
- output columns;
- quasi-identifier groups for risk screening.

This gives the project an extensible architecture: adding a new dataset should normally require a new profile, not code changes.

## Software Modularity

The Python package is split by responsibility:

| Module | Responsibility |
| --- | --- |
| `pseudonymity.cli` | CLI parsing and command orchestration. |
| `pseudonymity.engine` | Main pseudonymisation pipeline. |
| `pseudonymity.techniques` | Column-level transformations. |
| `pseudonymity.crypto` | HMAC tokenisation and secret loading. |
| `pseudonymity.profiles` | Built-in profile, profile loading and validation. |
| `pseudonymity.datasets` | Synthetic datasets. |
| `pseudonymity.risk` | Python risk engine and optional Go integration. |
| `pseudonymity.vault` | Vault-backed re-identification. |
| `pseudonymity.io` | CSV/JSON utilities. |

The old `pseudonymise.py` file remains only as a backward-compatible shim.

## Go Risk Engine Integration

The optional Go component lives in `go/pseudonymity-risk`.

It can be compiled into `tools/pseudonymity-risk` and invoked from Python with:

```powershell
python .\pseudonymise.py risk --engine go --go-risk-binary .\tools\pseudonymity-risk --input .\output\pseudonymised_customers.csv --profile .\profiles\ecommerce.json
```

When `--engine auto` is used, Pseudonymity calls the Go binary if available and falls back to the Python implementation otherwise.

## Qt GUI

Pseudonymity also ships an optional native Qt GUI.

```powershell
python .\pseudonymise.py gui
```

The GUI provides tabs for:

- running the full demo;
- pseudonymising an existing CSV;
- re-identifying selected columns through the vault;
- writing a JSONL audit entry for re-identification;
- inspecting a CSV before designing a profile.

The GUI is intentionally a thin layer over the same library functions used by the CLI.

## CSV Inspection And Audit Logging

The `inspect` command helps profile authors review a CSV before designing transformations:

```powershell
python .\pseudonymise.py inspect --input .\data\sample_customers.csv --output .\output\inspection_report.json
```

The `reidentify` command can append a JSONL audit entry:

```powershell
python .\pseudonymise.py reidentify --input .\output\test1.csv --vault .\vault\reidentification_vault.csv --output .\output\test1_reid.csv --columns customer_id,email,phone --audit-log .\output\reidentification_audit.jsonl --reason "support-case-123"
```

## Current Example Dataset

The generated dataset includes:

- direct identifiers: name, email, phone, address;
- indirect/quasi-identifiers: date of birth, postal code, region, IP, signup date;
- analytic fields: plan, purchase category, amount, support tickets, churn score;
- governance/demo fields: marketing consent, preferred channel, loyalty points;
- synthetic special-category-style field: diagnosis code.

The diagnosis code is fake and included only to demonstrate stronger handling requirements.

## Residual Risk Report

The tool computes screening checks over configured quasi-identifier sets.

For each set it reports:

- number of equivalence classes;
- minimum and maximum group size;
- unique groups;
- estimated singling-out rate;
- examples of unique groups.

This is not a complete DPIA or anonymisation proof. It is a practical signal that pseudonymised datasets may still be linkable or single out individuals.

## Production Hardening Still Needed

The current project is a strong prototype, not a certified production platform.

Before production use, add:

- encrypted vault storage;
- KMS/HSM key management;
- key IDs and key rotation;
- policy-based access control;
- re-identification approvals;
- append-only audit logging;
- suppression rules for small groups;
- mature risk modelling;
- retention and secure deletion controls.

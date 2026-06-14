# Concepts

Pseudonymity is built around a simple idea: pseudonymisation is not just a token generator. It is a controlled data-processing workflow.

## Pseudonymisation

Pseudonymisation reduces direct attribution by replacing, transforming or removing identifying fields. In Pseudonymity, this can mean:

- replacing identifiers with HMAC tokens;
- masking display values;
- generalising dates, postcodes, IP addresses or categories;
- perturbing dates and numeric values;
- suppressing or redacting fields;
- keeping selected analytical fields when the profile says they are needed.

The result can still be personal data. If a subject can be re-identified through a vault, key, external dataset or reasonable inference, GDPR obligations still apply.

## Tokenisation

The main tokenisation primitive is HMAC-SHA256:

```text
token = Base32(HMAC-SHA256(secret, namespace + ":" + normalised_value))[0:18]
```

This is deterministic and keyed. The same value with the same namespace and key gives the same token, which supports joins and deduplication. The key prevents simple dictionary attacks that would affect plain hashes.

The token is not encrypted plaintext. There is no decryption operation for an HMAC token.

## Re-identification

Pseudonymity uses vault-backed re-identification.

The analytical dataset contains `subject_pseudo_id`. The vault contains `subject_pseudo_id` plus selected original fields. Re-identification is a lookup:

```text
subject_pseudo_id -> original fields in vault
```

This makes recovery explicit and auditable. It also creates a clear security boundary: the vault is a high-risk asset and must be protected.

## Quasi-identifiers

Removing names and emails is not enough. Fields like age band, region, postcode, rare category, signup date and transaction patterns may single out a person when combined.

Pseudonymity profiles therefore treat quasi-identifiers explicitly and risk reports screen configured combinations for small groups.

## Profiles

A profile is the processing policy. It defines:

- required input columns;
- how the subject pseudonym is generated;
- which original fields go into the vault;
- which transformations produce the analytical output;
- which output fields are checked as quasi-identifier sets.

Profiles are deliberately human-readable JSON so they can be reviewed by privacy, security, legal and engineering stakeholders.

## Manifest

The manifest is the accountability artifact. It records:

- input, output and vault locations;
- profile name and description;
- techniques used;
- field treatment rules;
- key source metadata;
- reference date for age bands.

It does not record the secret key.

## Risk Report

The risk report computes k-anonymity-style screening checks over configured quasi-identifier sets. It reports group counts, minimum group size, unique groups and examples of unique combinations.

This is not a complete anonymisation proof or DPIA. It is an engineering signal used to identify combinations that deserve review.

## GUI

The Qt GUI exists for the same reason the CLI exists: to make the workflow repeatable. It is not a separate implementation. It calls the same Python library functions as the CLI.

The GUI is useful when:

- demonstrating the tool in a seminar;
- reviewing a profile with non-developer stakeholders;
- selecting local files interactively;
- running a controlled re-identification with an audit reason;
- inspecting a CSV before writing a profile.

## Production Boundary

Pseudonymity v1.0.0 is a stable project baseline, not a full production data protection platform. Production deployments should add encrypted vault storage, KMS/HSM key management, RBAC, approval workflows, central audit logging, retention policies and a DPIA-aligned governance process.

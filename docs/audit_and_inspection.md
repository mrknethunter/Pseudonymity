# Audit And Inspection

## CSV Inspection

Before writing or reviewing a profile, inspect the source dataset:

```powershell
python .\pseudonymise.py inspect --input .\data\sample_customers.csv --output .\output\inspection_report.json
```

The report includes:

- row count;
- column names;
- non-empty and empty counts;
- unique value count;
- uniqueness ratio;
- common sample values;
- privacy-relevant hints.

Column hints include:

- `direct_identifier_candidate`
- `quasi_identifier_candidate`
- `sensitive_candidate`
- `analytical_or_context_field`

These hints are not a legal classification. They are a starting point for privacy engineering review.

Inspection is intentionally conservative and heuristic. It looks at column names, uniqueness and representative values; it does not decide the legal nature of a field. A privacy engineer should use the report to start questions such as:

- Is this column directly identifying?
- Could this field become identifying when joined with another dataset?
- Does this field need to be in the analytical output?
- Should this field go to the vault, be generalised, be tokenised or be suppressed?

## Re-identification Audit Log

Write a JSONL audit entry when recovering values from the vault:

```powershell
python .\pseudonymise.py reidentify --input .\output\test1.csv --vault .\vault\reidentification_vault.csv --output .\output\test1_reid.csv --columns customer_id,email,phone --audit-log .\output\reidentification_audit.jsonl --reason "support-case-123"
```

Each JSONL entry records:

- timestamp;
- event type;
- input dataset;
- vault path;
- output dataset;
- row count;
- missing token count;
- token column;
- released columns;
- reason.

The audit log is append-only at file level, but it is not tamper-proof. Production deployments should use append-only storage, central logging or SIEM integration.

The reason field is deliberately free text. In real workflows, it should normally reference a ticket, case number, approval ID or data-subject request.

# Profile Schema

Profiles are JSON files that describe how Pseudonymity processes an input CSV.

## Top-Level Shape

```json
{
  "schema_version": "1.0",
  "name": "ecommerce-default",
  "description": "Human-readable description.",
  "required_columns": ["customer_id", "email"],
  "subject_id": {},
  "vault": {},
  "rules": [],
  "risk": {}
}
```

## `subject_id`

Defines the primary subject pseudonym.

```json
{
  "source": "customer_id",
  "output": "subject_pseudo_id",
  "technique": "hmac_token",
  "namespace": "subject",
  "length": 18
}
```

The current subject strategy is HMAC tokenisation. It is deterministic and not decryptable.

## `vault`

Defines the additional information retained for controlled re-identification.

```json
{
  "token_column": "subject_pseudo_id",
  "include_original_fields": ["customer_id", "email", "phone"]
}
```

Fields not listed here cannot be recovered by `reidentify` unless they are also present somewhere else.

## `rules`

Each rule maps one input field to one output field.

```json
{
  "source": "email",
  "output": "email_token",
  "technique": "hmac_token",
  "namespace": "email",
  "length": 18
}
```

Supported techniques:

- `hmac_token`
- `mask_email`
- `mask_phone`
- `email_domain`
- `birth_decade`
- `age_band`
- `postal_area`
- `ip_subnet`
- `date_part`
- `date_shift`
- `numeric_band`
- `numeric_noise`
- `category_map`
- `keep`
- `redact`
- `suppress`

## `risk`

Defines quasi-identifier groups used for screening.

```json
{
  "quasi_identifier_sets": [
    ["region", "age_band"],
    ["region", "age_band", "postal_area"]
  ]
}
```

These checks are not a proof of anonymisation. They are practical signals for singling-out and linkage risk.

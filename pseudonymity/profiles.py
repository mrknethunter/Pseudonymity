"""Built-in profiles and profile helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "date_of_birth",
    "street_address",
    "city",
    "region",
    "postal_code",
    "last_login_ip",
    "signup_date",
    "subscription_plan",
    "purchase_category",
    "purchase_amount_eur",
    "support_tickets",
    "churn_risk_score",
    "loyalty_points",
    "preferred_channel",
    "marketing_consent",
    "diagnosis_code",
]

VAULT_COLUMNS = [
    "subject_pseudo_id",
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "date_of_birth",
    "street_address",
    "city",
    "region",
    "postal_code",
    "last_login_ip",
    "signup_date",
    "purchase_amount_eur",
    "churn_risk_score",
    "loyalty_points",
    "diagnosis_code",
]

DEFAULT_PROFILE: dict[str, Any] = {
    "schema_version": "1.0",
    "name": "ecommerce-default",
    "description": "E-commerce sample profile with direct, indirect and quasi-identifier treatment.",
    "required_columns": REQUIRED_COLUMNS,
    "subject_id": {
        "source": "customer_id",
        "output": "subject_pseudo_id",
        "technique": "hmac_token",
        "namespace": "subject",
        "length": 18,
    },
    "vault": {
        "token_column": "subject_pseudo_id",
        "include_original_fields": VAULT_COLUMNS[1:],
    },
    "rules": [
        {"source": "email", "output": "email_token", "technique": "hmac_token", "namespace": "email", "length": 18},
        {"source": "email", "output": "email_masked", "technique": "mask_email"},
        {"source": "phone", "output": "phone_token", "technique": "hmac_token", "namespace": "phone", "length": 18},
        {"source": "phone", "output": "phone_masked", "technique": "mask_phone", "visible_digits": 2},
        {"source": "last_login_ip", "output": "ip_token", "technique": "hmac_token", "namespace": "ip", "length": 18},
        {"source": "email", "output": "email_domain", "technique": "email_domain"},
        {"source": "date_of_birth", "output": "birth_year", "technique": "date_part", "part": "year"},
        {"source": "date_of_birth", "output": "birth_decade", "technique": "birth_decade"},
        {"source": "date_of_birth", "output": "age_band", "technique": "age_band"},
        {"source": "postal_code", "output": "postal_area", "technique": "postal_area", "digits": 3},
        {"source": "region", "output": "region", "technique": "keep"},
        {"source": "last_login_ip", "output": "ip_subnet_24", "technique": "ip_subnet", "prefix": 24},
        {"source": "signup_date", "output": "signup_month", "technique": "date_part", "part": "month"},
        {"source": "signup_date", "output": "signup_date_shifted", "technique": "date_shift", "max_days": 21},
        {"source": "subscription_plan", "output": "subscription_plan", "technique": "keep"},
        {"source": "purchase_category", "output": "purchase_category", "technique": "keep"},
        {
            "source": "purchase_amount_eur",
            "output": "purchase_amount_band",
            "technique": "numeric_band",
            "bands": [0, 50, 100, 250, 500, 1000],
            "unit": "EUR",
        },
        {
            "source": "purchase_amount_eur",
            "output": "purchase_amount_eur_noisy",
            "technique": "numeric_noise",
            "scale": 5.0,
            "decimals": 2,
        },
        {"source": "support_tickets", "output": "support_tickets", "technique": "keep"},
        {
            "source": "churn_risk_score",
            "output": "churn_risk_score_noisy",
            "technique": "numeric_noise",
            "scale": 0.03,
            "decimals": 2,
            "min": 0,
            "max": 1,
        },
        {
            "source": "loyalty_points",
            "output": "loyalty_points_band",
            "technique": "numeric_band",
            "bands": [0, 100, 500, 1000, 2500, 5000, 10000],
            "unit": "pts",
        },
        {"source": "preferred_channel", "output": "preferred_channel", "technique": "keep"},
        {"source": "marketing_consent", "output": "marketing_consent", "technique": "keep"},
        {
            "source": "diagnosis_code",
            "output": "diagnosis_group",
            "technique": "category_map",
            "mapping": {
                "I10": "cardio",
                "E11": "metabolic",
                "J45": "respiratory",
                "M54": "musculoskeletal",
                "F41": "mental-health",
                "NONE": "none",
            },
            "default": "other",
        },
    ],
    "risk": {
        "quasi_identifier_sets": [
            ["region", "age_band"],
            ["region", "age_band", "postal_area"],
            ["region", "birth_decade", "postal_area", "purchase_category"],
            ["region", "age_band", "diagnosis_group", "purchase_amount_band"],
        ]
    },
}


def load_profile(profile_path: Path | None = None) -> dict[str, Any]:
    if profile_path and profile_path.exists():
        return json.loads(profile_path.read_text(encoding="utf-8"))
    if profile_path and not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    return DEFAULT_PROFILE


def profile_output_columns(profile: dict[str, Any]) -> list[str]:
    subject_output = profile["subject_id"]["output"]
    outputs = [subject_output]
    for rule in profile.get("rules", []):
        output = rule["output"]
        if output not in outputs:
            outputs.append(output)
    return outputs


def profile_vault_columns(profile: dict[str, Any]) -> list[str]:
    token_column = profile.get("vault", {}).get("token_column", profile["subject_id"]["output"])
    fields = [token_column]
    for field in profile.get("vault", {}).get("include_original_fields", []):
        if field not in fields:
            fields.append(field)
    return fields


def validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if profile.get("schema_version") not in {"1.0", None}:
        errors.append(f"Unsupported schema_version '{profile.get('schema_version')}'.")
    if "subject_id" not in profile:
        errors.append("Missing subject_id section.")
    else:
        for key in ["source", "output", "technique"]:
            if key not in profile["subject_id"]:
                errors.append(f"subject_id is missing {key}.")
        if profile["subject_id"].get("technique") != "hmac_token":
            errors.append("subject_id.technique must currently be hmac_token.")
    if "rules" not in profile or not isinstance(profile["rules"], list):
        errors.append("Missing rules list.")
    required_columns = set(profile.get("required_columns", []))
    if not required_columns:
        errors.append("required_columns must not be empty.")
    known_techniques = {
        "age_band",
        "birth_decade",
        "category_map",
        "date_part",
        "date_shift",
        "email_domain",
        "hmac_token",
        "ip_subnet",
        "keep",
        "mask_email",
        "mask_phone",
        "numeric_band",
        "numeric_noise",
        "postal_area",
        "redact",
        "suppress",
    }
    outputs: set[str] = set()
    for index, rule in enumerate(profile.get("rules", []), start=1):
        for key in ["source", "output", "technique"]:
            if key not in rule:
                errors.append(f"Rule {index} is missing {key}.")
        source = rule.get("source")
        output = rule.get("output")
        technique = rule.get("technique")
        if source and required_columns and source not in required_columns:
            errors.append(f"Rule {index} source '{source}' is not listed in required_columns.")
        if output in outputs:
            errors.append(f"Rule {index} output '{output}' is duplicated.")
        if output:
            outputs.add(output)
        if technique and technique not in known_techniques:
            errors.append(f"Rule {index} uses unsupported technique '{technique}'.")
        if technique == "date_part" and rule.get("part") not in {"year", "month"}:
            errors.append(f"Rule {index} date_part must specify part 'year' or 'month'.")
        if technique == "numeric_band" and not rule.get("bands"):
            errors.append(f"Rule {index} numeric_band must specify bands.")
        if technique == "category_map" and not isinstance(rule.get("mapping"), dict):
            errors.append(f"Rule {index} category_map must specify a mapping object.")
    vault_fields = profile.get("vault", {}).get("include_original_fields", [])
    for field in vault_fields:
        if required_columns and field not in required_columns:
            errors.append(f"Vault field '{field}' is not listed in required_columns.")
    risk_outputs = set(outputs)
    if "subject_id" in profile and "output" in profile["subject_id"]:
        risk_outputs.add(profile["subject_id"]["output"])
    for set_index, qi_set in enumerate(profile.get("risk", {}).get("quasi_identifier_sets", []), start=1):
        for column in qi_set:
            if column not in risk_outputs:
                errors.append(f"Risk set {set_index} references unknown output column '{column}'.")
    return errors

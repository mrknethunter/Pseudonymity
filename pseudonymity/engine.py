"""Pseudonymisation engine."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from pseudonymity.crypto import hmac_token, load_or_create_secret
from pseudonymity.io import read_csv, write_csv, write_json
from pseudonymity.profiles import (
    DEFAULT_PROFILE,
    load_profile,
    profile_output_columns,
    profile_vault_columns,
)
from pseudonymity.risk import build_risk_report
from pseudonymity.techniques import apply_rule, parse_iso_date


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_reference_date(value: str | None) -> date:
    if value:
        return parse_iso_date(value)
    return datetime.now(timezone.utc).date()


def pseudonymise_row_with_profile(
    row: dict[str, str],
    key: bytes,
    reference_date: date,
    profile: dict[str, Any],
) -> tuple[dict[str, str], dict[str, str]]:
    subject_rule = profile["subject_id"]
    subject_token = hmac_token(
        row[subject_rule["source"]],
        key,
        subject_rule.get("namespace", "subject"),
        int(subject_rule.get("length", 18)),
    )
    subject_output = subject_rule["output"]

    pseudonymised = {subject_output: subject_token}
    for rule in profile.get("rules", []):
        pseudonymised[rule["output"]] = apply_rule(row, rule, key, reference_date, subject_token)

    vault = {profile.get("vault", {}).get("token_column", subject_output): subject_token}
    for field in profile.get("vault", {}).get("include_original_fields", []):
        vault[field] = row.get(field, "")
    return pseudonymised, vault


def pseudonymise_row(row: dict[str, str], key: bytes, reference_date: date) -> tuple[dict[str, str], dict[str, str]]:
    return pseudonymise_row_with_profile(row, key, reference_date, DEFAULT_PROFILE)


def build_manifest(
    input_path: Path,
    output_path: Path,
    vault_path: Path,
    rows: int,
    key_source: str,
    reference_date: date,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_profile = profile or DEFAULT_PROFILE
    techniques = sorted({rule["technique"] for rule in selected_profile.get("rules", [])})
    return {
        "created_at": utc_now_iso(),
        "project": "Pseudonymity",
        "scope": "pseudonymised data remains personal data under GDPR when re-identification is possible",
        "input": str(input_path),
        "output": str(output_path),
        "vault": str(vault_path),
        "rows": rows,
        "reference_date": reference_date.isoformat(),
        "key_source": key_source,
        "profile": {
            "name": selected_profile.get("name", "inline-profile"),
            "description": selected_profile.get("description", ""),
        },
        "techniques": techniques,
        "algorithm_notes": {
            "tokenisation": "HMAC-SHA256 with namespace separation and Base32 truncation",
            "vault_reidentification": "authorized lookup by subject pseudonym in a separated vault",
            "reversible_by_token_decryption": False,
            "reversible_by_governed_vault": True,
        },
        "field_treatment": {
            "subject_id": selected_profile["subject_id"],
            "rules": selected_profile.get("rules", []),
            "vault_original_fields": selected_profile.get("vault", {}).get("include_original_fields", []),
        },
    }


def pseudonymise_dataset(
    input_path: Path,
    output_path: Path,
    vault_path: Path,
    key_file: Path,
    secret_env: str,
    create_key: bool,
    manifest_path: Path,
    risk_report_path: Path,
    reference_date: date,
    profile_path: Path | None = None,
    risk_engine: str = "python",
    go_risk_binary: Path | None = None,
) -> dict[str, Any]:
    profile = load_profile(profile_path)
    key, key_source = load_or_create_secret(secret_env, key_file, create_key)
    rows = read_csv(input_path, profile.get("required_columns", []))

    pseudonymised_rows: list[dict[str, str]] = []
    vault_rows: list[dict[str, str]] = []
    for row in rows:
        pseudonymised, vault = pseudonymise_row_with_profile(row, key, reference_date, profile)
        pseudonymised_rows.append(pseudonymised)
        vault_rows.append(vault)

    output_columns = profile_output_columns(profile)
    vault_columns = profile_vault_columns(profile)
    write_csv(output_path, pseudonymised_rows, output_columns)
    write_csv(vault_path, vault_rows, vault_columns)

    manifest = build_manifest(input_path, output_path, vault_path, len(rows), key_source, reference_date, profile)
    write_json(manifest_path, manifest)

    risk_report = build_risk_report(
        rows=pseudonymised_rows,
        csv_path=output_path,
        quasi_identifier_sets=profile.get("risk", {}).get("quasi_identifier_sets", []),
        profile_name=profile.get("name", "inline-profile"),
        engine=risk_engine,
        go_binary=go_risk_binary,
    )
    risk_report["created_at"] = utc_now_iso()
    write_json(risk_report_path, risk_report)

    return {
        "rows": len(rows),
        "input": str(input_path),
        "output": str(output_path),
        "vault": str(vault_path),
        "manifest": str(manifest_path),
        "risk_report": str(risk_report_path),
        "risk_engine": risk_report.get("engine", risk_engine),
        "key_source": key_source,
        "profile": profile.get("name", "inline-profile"),
    }

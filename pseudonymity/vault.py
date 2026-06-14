"""Vault-backed re-identification."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pseudonymity.io import ensure_parent, read_csv, write_csv


def append_reidentification_audit(
    audit_log_path: Path,
    result: dict[str, Any],
    token_column: str,
    columns: list[str] | None,
    reason: str | None,
) -> None:
    ensure_parent(audit_log_path)
    entry = {
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "event": "reidentify",
        "input": result["input"],
        "vault": result["vault"],
        "output": result["output"],
        "rows": result["rows"],
        "missing_tokens": result["missing_tokens"],
        "token_column": token_column,
        "released_columns": columns or "all",
        "reason": reason or "",
    }
    with audit_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def reidentify_dataset(
    pseudonymised_path: Path,
    vault_path: Path,
    output_path: Path,
    token_column: str = "subject_pseudo_id",
    columns: list[str] | None = None,
    audit_log_path: Path | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    pseudo_rows = read_csv(pseudonymised_path, [token_column])
    vault_rows = read_csv(vault_path, [token_column])
    vault_index = {row[token_column]: row for row in vault_rows}

    selected_columns = columns or list(vault_rows[0].keys())
    output_columns = list(dict.fromkeys([token_column] + selected_columns))
    output_rows: list[dict[str, str]] = []
    missing_tokens = 0
    for row in pseudo_rows:
        token = row[token_column]
        vault_row = vault_index.get(token)
        if not vault_row:
            missing_tokens += 1
            continue
        output_rows.append({column: vault_row.get(column, row.get(column, "")) for column in output_columns})

    write_csv(output_path, output_rows, output_columns)
    result = {
        "input": str(pseudonymised_path),
        "vault": str(vault_path),
        "output": str(output_path),
        "rows": len(output_rows),
        "missing_tokens": missing_tokens,
    }
    if audit_log_path:
        append_reidentification_audit(audit_log_path, result, token_column, columns, reason)
    return result

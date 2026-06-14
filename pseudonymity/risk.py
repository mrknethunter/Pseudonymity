"""Risk screening helpers and optional Go engine integration."""

from __future__ import annotations

import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from pseudonymity.constants import DEFAULT_GO_RISK_BINARY
from pseudonymity.io import read_csv


def k_anonymity(rows: list[dict[str, str]], columns: list[str]) -> dict[str, Any]:
    available_columns = [column for column in columns if rows and column in rows[0]]
    if not rows or len(available_columns) != len(columns):
        return {"columns": columns, "groups": 0, "minimum_group_size": 0, "unique_groups": 0, "skipped": True}

    groups = Counter(tuple(row[column] for column in columns) for row in rows)
    group_sizes = list(groups.values())
    unique_examples = [
        dict(zip(columns, key))
        for key, count in groups.items()
        if count == 1
    ][:10]

    return {
        "columns": columns,
        "groups": len(groups),
        "minimum_group_size": min(group_sizes),
        "maximum_group_size": max(group_sizes),
        "unique_groups": sum(1 for size in group_sizes if size == 1),
        "estimated_singling_out_rate": round(sum(1 for size in group_sizes if size == 1) / len(rows), 4),
        "unique_group_examples": unique_examples,
    }


def build_python_risk_report(
    rows: list[dict[str, str]],
    quasi_identifier_sets: list[list[str]],
    profile_name: str,
) -> dict[str, Any]:
    return {
        "engine": "python",
        "rows": len(rows),
        "profile": profile_name,
        "note": "k-anonymity here is a screening signal, not a full re-identification risk assessment.",
        "checks": [k_anonymity(rows, columns) for columns in quasi_identifier_sets],
    }


def resolve_go_binary(go_binary: Path | None = None) -> Path | None:
    env_binary = os.environ.get("PSEUDONYMITY_RISK_GO")
    candidates = [go_binary, Path(env_binary) if env_binary else None, DEFAULT_GO_RISK_BINARY]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return None


def build_go_risk_report(
    csv_path: Path,
    quasi_identifier_sets: list[list[str]],
    profile_name: str,
    go_binary: Path | None = None,
) -> dict[str, Any]:
    binary = resolve_go_binary(go_binary)
    if not binary:
        raise FileNotFoundError(
            "Go risk engine binary not found. Build go/pseudonymity-risk and place it at "
            f"{DEFAULT_GO_RISK_BINARY}, or set PSEUDONYMITY_RISK_GO."
        )
    payload = json.dumps(quasi_identifier_sets)
    completed = subprocess.run(
        [str(binary), "--input", str(csv_path), "--sets", payload, "--profile", profile_name],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def build_risk_report(
    rows: list[dict[str, str]],
    csv_path: Path,
    quasi_identifier_sets: list[list[str]],
    profile_name: str,
    engine: str = "python",
    go_binary: Path | None = None,
) -> dict[str, Any]:
    if engine not in {"python", "go", "auto"}:
        raise ValueError("risk engine must be one of: python, go, auto")
    if engine == "python":
        return build_python_risk_report(rows, quasi_identifier_sets, profile_name)
    if engine == "go":
        return build_go_risk_report(csv_path, quasi_identifier_sets, profile_name, go_binary)
    if resolve_go_binary(go_binary):
        return build_go_risk_report(csv_path, quasi_identifier_sets, profile_name, go_binary)
    report = build_python_risk_report(rows, quasi_identifier_sets, profile_name)
    report["engine"] = "python-fallback"
    return report


def build_risk_report_from_csv(
    csv_path: Path,
    quasi_identifier_sets: list[list[str]],
    profile_name: str = "ad-hoc",
    engine: str = "python",
    go_binary: Path | None = None,
) -> dict[str, Any]:
    rows = read_csv(csv_path)
    return build_risk_report(rows, csv_path, quasi_identifier_sets, profile_name, engine, go_binary)

"""CSV inspection helpers for profile design."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from pseudonymity.io import read_csv


DIRECT_IDENTIFIER_HINTS = ("id", "name", "email", "phone", "address", "ip")
QUASI_IDENTIFIER_HINTS = ("date", "birth", "age", "postal", "zip", "city", "region", "gender")
SENSITIVE_HINTS = ("diagnosis", "health", "medical", "religion", "politic", "union", "biometric")


def classify_column(name: str) -> list[str]:
    lowered = name.lower()
    classes: list[str] = []
    if any(hint in lowered for hint in DIRECT_IDENTIFIER_HINTS):
        classes.append("direct_identifier_candidate")
    if any(hint in lowered for hint in QUASI_IDENTIFIER_HINTS):
        classes.append("quasi_identifier_candidate")
    if any(hint in lowered for hint in SENSITIVE_HINTS):
        classes.append("sensitive_candidate")
    if not classes:
        classes.append("analytical_or_context_field")
    return classes


def inspect_csv(path: Path, sample_values: int = 5) -> dict[str, Any]:
    rows = read_csv(path)
    if not rows:
        return {"input": str(path), "rows": 0, "columns": []}

    columns = list(rows[0].keys())
    column_reports: list[dict[str, Any]] = []
    for column in columns:
        values = [row.get(column, "") for row in rows]
        non_empty = [value for value in values if value != ""]
        unique_values = set(non_empty)
        common = Counter(non_empty).most_common(sample_values)
        column_reports.append(
            {
                "name": column,
                "classes": classify_column(column),
                "non_empty": len(non_empty),
                "empty": len(values) - len(non_empty),
                "unique": len(unique_values),
                "uniqueness_ratio": round(len(unique_values) / len(non_empty), 4) if non_empty else 0,
                "sample_values": [value for value, _count in common],
            }
        )

    return {
        "input": str(path),
        "rows": len(rows),
        "columns": column_reports,
    }

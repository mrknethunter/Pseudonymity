"""Command-line interface for Pseudonymity."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pseudonymity.constants import (
    DEFAULT_PROFILE_PATH,
    KEY_FILE,
    MANIFEST_FILE,
    PSEUDONYMISED_DATASET,
    RAW_DATASET,
    REIDENTIFIED_DATASET,
    RISK_REPORT_FILE,
    VAULT_DATASET,
)
from pseudonymity.datasets import generate_sample_dataset
from pseudonymity.engine import parse_reference_date, pseudonymise_dataset
from pseudonymity.inspect import inspect_csv
from pseudonymity.io import write_json
from pseudonymity.profiles import DEFAULT_PROFILE, load_profile, validate_profile
from pseudonymity.risk import build_risk_report_from_csv
from pseudonymity.vault import reidentify_dataset


def add_common_pseudonymise_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", type=Path, default=RAW_DATASET, help="Raw CSV input path.")
    parser.add_argument("--output", type=Path, default=PSEUDONYMISED_DATASET, help="Pseudonymised CSV output path.")
    parser.add_argument("--vault", type=Path, default=VAULT_DATASET, help="Separated re-identification vault CSV path.")
    parser.add_argument("--key-file", type=Path, default=KEY_FILE, help="Demo HMAC key file path.")
    parser.add_argument("--secret-env", default="PSEUDONYMITY_SECRET", help="Environment variable containing the HMAC key.")
    parser.add_argument("--create-key", action="store_true", help="Create a demo key file if no key exists.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_FILE, help="Manifest JSON output path.")
    parser.add_argument("--risk-report", type=Path, default=RISK_REPORT_FILE, help="Risk report JSON output path.")
    parser.add_argument("--profile", type=Path, help="JSON profile describing column-level transformations.")
    parser.add_argument("--risk-engine", choices=["python", "go", "auto"], default="python", help="Risk engine to use.")
    parser.add_argument("--go-risk-binary", type=Path, help="Optional path to the compiled Go risk engine.")
    parser.add_argument(
        "--reference-date",
        help="Reference date for age bands in YYYY-MM-DD format. Defaults to today in UTC.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pseudonymity: configurable data pseudonymisation toolkit.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Create a synthetic raw dataset.")
    generate.add_argument("--output", type=Path, default=RAW_DATASET, help="Synthetic CSV output path.")
    generate.add_argument("--rows", type=int, default=100, help="Number of synthetic rows to create.")
    generate.add_argument("--seed", type=int, default=20260614, help="Random seed for repeatability.")

    pseudonymise = subparsers.add_parser("pseudonymise", help="Pseudonymise an existing raw CSV.")
    add_common_pseudonymise_args(pseudonymise)

    demo = subparsers.add_parser("demo", help="Generate sample data and pseudonymise it.")
    demo.add_argument("--rows", type=int, default=100, help="Number of synthetic rows to create.")
    demo.add_argument("--seed", type=int, default=20260614, help="Random seed for repeatability.")
    add_common_pseudonymise_args(demo)

    reidentify = subparsers.add_parser("reidentify", help="Re-identify pseudonymised rows through a separated vault.")
    reidentify.add_argument("--input", type=Path, default=PSEUDONYMISED_DATASET, help="Pseudonymised CSV input path.")
    reidentify.add_argument("--vault", type=Path, default=VAULT_DATASET, help="Separated vault CSV path.")
    reidentify.add_argument("--output", type=Path, default=REIDENTIFIED_DATASET, help="Re-identified CSV output path.")
    reidentify.add_argument("--token-column", default="subject_pseudo_id", help="Token column used to join with the vault.")
    reidentify.add_argument("--columns", help="Comma-separated vault columns to release. Defaults to all vault columns.")
    reidentify.add_argument("--audit-log", type=Path, help="Append a JSONL audit entry for the re-identification run.")
    reidentify.add_argument("--reason", help="Human-readable reason for the re-identification run.")

    inspect = subparsers.add_parser("inspect", help="Inspect a CSV and suggest privacy-relevant column classes.")
    inspect.add_argument("--input", type=Path, required=True, help="CSV input path.")
    inspect.add_argument("--output", type=Path, help="Optional JSON report output path.")
    inspect.add_argument("--sample-values", type=int, default=5, help="Number of common sample values per column.")

    risk = subparsers.add_parser("risk", help="Build a risk report for an existing pseudonymised CSV.")
    risk.add_argument("--input", type=Path, default=PSEUDONYMISED_DATASET, help="Pseudonymised CSV input path.")
    risk.add_argument("--profile", type=Path, default=DEFAULT_PROFILE_PATH, help="Profile containing quasi-identifier sets.")
    risk.add_argument("--output", type=Path, default=RISK_REPORT_FILE, help="Risk report JSON output path.")
    risk.add_argument("--engine", choices=["python", "go", "auto"], default="python", help="Risk engine to use.")
    risk.add_argument("--go-risk-binary", type=Path, help="Optional path to the compiled Go risk engine.")

    profile = subparsers.add_parser("write-profile", help="Write the built-in profile as JSON.")
    profile.add_argument("--output", type=Path, default=DEFAULT_PROFILE_PATH, help="Profile JSON output path.")

    validate = subparsers.add_parser("validate-profile", help="Validate a Pseudonymity profile.")
    validate.add_argument("--profile", type=Path, default=DEFAULT_PROFILE_PATH, help="Profile JSON path.")

    subparsers.add_parser("gui", help="Open the optional Qt graphical interface.")

    return parser


def print_result(title: str, result: dict[str, Any]) -> None:
    print(title)
    for key, value in result.items():
        print(f"- {key}: {value}")


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "generate":
        generate_sample_dataset(args.output, args.rows, args.seed)
        print(f"Created synthetic dataset: {args.output} ({args.rows} rows)")
        return 0

    if args.command == "write-profile":
        write_json(args.output, DEFAULT_PROFILE)
        print(f"Wrote profile: {args.output}")
        return 0

    if args.command == "validate-profile":
        errors = validate_profile(load_profile(args.profile))
        if errors:
            print("Profile validation failed")
            for error in errors:
                print(f"- {error}")
            return 2
        print(f"Profile is valid: {args.profile}")
        return 0

    if args.command == "risk":
        profile = load_profile(args.profile)
        report = build_risk_report_from_csv(
            csv_path=args.input,
            quasi_identifier_sets=profile.get("risk", {}).get("quasi_identifier_sets", []),
            profile_name=profile.get("name", "inline-profile"),
            engine=args.engine,
            go_binary=args.go_risk_binary,
        )
        write_json(args.output, report)
        print_result("Risk report completed", {"output": args.output, "engine": report.get("engine")})
        return 0

    if args.command == "inspect":
        report = inspect_csv(args.input, args.sample_values)
        if args.output:
            write_json(args.output, report)
            print_result("Inspection completed", {"input": args.input, "output": args.output, "columns": len(report["columns"])})
        else:
            print_result("Inspection completed", {"input": args.input, "rows": report["rows"], "columns": len(report["columns"])})
            for column in report["columns"]:
                print(f"- {column['name']}: {', '.join(column['classes'])}; unique={column['unique']}")
        return 0

    if args.command == "reidentify":
        columns = [column.strip() for column in args.columns.split(",")] if args.columns else None
        result = reidentify_dataset(
            args.input,
            args.vault,
            args.output,
            args.token_column,
            columns,
            audit_log_path=args.audit_log,
            reason=args.reason,
        )
        print_result("Re-identification completed", result)
        return 0

    if args.command == "gui":
        from pseudonymity.gui import run_gui

        return run_gui()

    if args.command == "demo":
        generate_sample_dataset(args.input, args.rows, args.seed)
        args.create_key = True

    reference_date = parse_reference_date(args.reference_date)
    result = pseudonymise_dataset(
        input_path=args.input,
        output_path=args.output,
        vault_path=args.vault,
        key_file=args.key_file,
        secret_env=args.secret_env,
        create_key=args.create_key,
        manifest_path=args.manifest,
        risk_report_path=args.risk_report,
        reference_date=reference_date,
        profile_path=args.profile,
        risk_engine=args.risk_engine,
        go_risk_binary=args.go_risk_binary,
    )

    print_result("Pseudonymisation completed", result)
    return 0

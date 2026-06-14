"""Pseudonymity public Python API."""

from pseudonymity.datasets import generate_sample_dataset
from pseudonymity.engine import pseudonymise_dataset
from pseudonymity.inspect import inspect_csv
from pseudonymity.profiles import DEFAULT_PROFILE, load_profile
from pseudonymity.risk import build_risk_report, k_anonymity
from pseudonymity.vault import reidentify_dataset

__all__ = [
    "DEFAULT_PROFILE",
    "build_risk_report",
    "generate_sample_dataset",
    "inspect_csv",
    "k_anonymity",
    "load_profile",
    "pseudonymise_dataset",
    "reidentify_dataset",
]

__version__ = "1.0.0"

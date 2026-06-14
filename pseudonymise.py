#!/usr/bin/env python3
"""Backward-compatible CLI shim for Pseudonymity.

Prefer `python -m pseudonymity.cli ...` or the installed `pseudonymity`
console script. This module re-exports the public API used by earlier demo
tests and scripts.
"""

from pseudonymity import *  # noqa: F401,F403
from pseudonymity.cli import main
from pseudonymity.engine import parse_reference_date, pseudonymise_row

if __name__ == "__main__":
    raise SystemExit(main())

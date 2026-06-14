#!/usr/bin/env bash
set -euo pipefail

python -m unittest discover -s tests
python -m compileall .
python -m pseudonymity validate-profile --profile profiles/ecommerce.json

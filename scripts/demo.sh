#!/usr/bin/env bash
set -euo pipefail

python -m pseudonymity write-profile --output profiles/ecommerce.json
python -m pseudonymity demo \
  --rows 120 \
  --reference-date 2026-06-14 \
  --profile profiles/ecommerce.json \
  --risk-engine auto
python -m pseudonymity reidentify \
  --input output/pseudonymised_customers.csv \
  --vault vault/reidentification_vault.csv \
  --output output/reidentified_customers.csv \
  --columns customer_id,email,phone

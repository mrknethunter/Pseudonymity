"""Default paths used by the Pseudonymity CLI."""

from pathlib import Path

RAW_DATASET = Path("data/sample_customers.csv")
PSEUDONYMISED_DATASET = Path("output/pseudonymised_customers.csv")
REIDENTIFIED_DATASET = Path("output/reidentified_customers.csv")
VAULT_DATASET = Path("vault/reidentification_vault.csv")
KEY_FILE = Path("vault/demo_hmac_key.hex")
MANIFEST_FILE = Path("output/pseudonymisation_manifest.json")
RISK_REPORT_FILE = Path("output/risk_report.json")
DEFAULT_PROFILE_PATH = Path("profiles/ecommerce.json")
DEFAULT_GO_RISK_BINARY = Path("tools/pseudonymity-risk")

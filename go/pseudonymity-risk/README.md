# Pseudonymity Go Risk Engine

Small optional Go component used by the Python CLI for k-anonymity-style risk screening.

Build:

```powershell
mkdir -p ../../tools
go build -o ../../tools/pseudonymity-risk .
```

Use from Python by either placing the binary at `tools/pseudonymity-risk` or setting:

```powershell
export PSEUDONYMITY_RISK_GO="/path/to/pseudonymity-risk"
```

The main Python CLI works without this binary and falls back to its built-in Python risk engine when `--risk-engine auto` is used.

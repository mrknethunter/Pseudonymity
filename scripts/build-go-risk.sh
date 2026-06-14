#!/usr/bin/env bash
set -euo pipefail

mkdir -p tools
go build -o tools/pseudonymity-risk ./go/pseudonymity-risk

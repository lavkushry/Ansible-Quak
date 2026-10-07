#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 &>/dev/null; then
    python3 "$SCRIPT_DIR/check-fqcn.py"
else
    echo "python3 required for AST-based FQCN analysis."
    exit 1
fi

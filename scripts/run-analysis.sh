#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
mkdir -p reports
python3 scripts/analyze.py --output reports

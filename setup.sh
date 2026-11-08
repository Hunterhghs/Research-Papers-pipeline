#!/usr/bin/env bash
# One-time setup: creates .venv and installs the pipeline's Python dependencies.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
"$PY" -m venv .venv
.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install -r requirements.txt -q
echo "Setup complete. Try:  ./hh qa _features"
echo "Optional: install LibreOffice to render DOCX previews (--docx-preview)."

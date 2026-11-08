#!/usr/bin/env bash
# Convenience wrapper: ./hh make <slug>   (uses .venv if present)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$DIR/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"
cd "$DIR" && exec "$PY" -m hhreport "$@"

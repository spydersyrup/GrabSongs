#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ -f "./.venv/bin/python" ]; then
    PYTHON_BIN="./.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

echo "Starting GrabSongs..."
exec "$PYTHON_BIN" app.py "$@"

#!/bin/sh
# Make Please use the Python version pinned in .python-version (via uv).
# Please builds with its own restricted PATH, so it ignores the python3 on
# your PATH; it has to be given the interpreter's absolute path instead.
set -eu
cd "$(dirname "$0")/.."
uv python install
printf '[Plugin "python"]\nDefaultInterpreter = %s\n' "$(uv python find)" > .plzconfig.local
echo "Please will use: $(uv python find)"

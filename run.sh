#!/usr/bin/env sh
cd "$(dirname "$0")" || exit 1

if [ ! -x ".venv/bin/python" ]; then
    echo "run setup.sh first"
    exit 1
fi

exec .venv/bin/python -m escoba "$@"

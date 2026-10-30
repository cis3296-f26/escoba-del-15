#!/usr/bin/env sh
cd "$(dirname "$0")" || exit 1

rm -rf .venv build dist .pytest_cache

find . -type d -name __pycache__ -prune -exec rm -rf {} +

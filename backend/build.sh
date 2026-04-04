#!/bin/sh
set -e

echo "==> Installing Poetry"
curl -sSL https://install.python-poetry.org | python3

export PATH="$HOME/.local/bin:$PATH"

echo "==> Installing dependencies"
poetry install --no-interaction --no-root
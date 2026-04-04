#!/bin/sh
set -e

echo "==> Installing Poetry"

export POETRY_HOME="/tmp/poetry"
curl -sSL https://install.python-poetry.org | python3

export PATH="$POETRY_HOME/bin:$PATH"

echo "==> Installing dependencies"
poetry install --no-interaction --no-root
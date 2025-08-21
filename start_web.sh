#!/bin/sh

echo "==> Rodando migrations Alembic"
alembic upgrade head

echo "==> Iniciando FastAPI com Uvicorn"
uvicorn app.main:app --host=0.0.0.0 --port=10000
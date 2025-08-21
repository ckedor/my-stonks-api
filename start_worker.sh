#!/bin/sh
celery -A app.worker.celery_app worker \
  --loglevel=info \
  --pool=solo \
  --without-heartbeat \
  --without-mingle \
  --without-gossip \
  -B

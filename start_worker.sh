#!/bin/sh
celery -A app.main_celery.celery_app worker \
  --loglevel=info \
  --pool=solo \
  --without-heartbeat \
  --without-mingle \
  --without-gossip \
  -B

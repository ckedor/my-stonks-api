# app/entrypoints/worker/celery_app.py
from celery import Celery

from app.config.settings import settings

from .scheduler import beat_schedule

celery_app = Celery("my-stonks")

celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL
celery_app.conf.timezone = "America/Sao_Paulo"
celery_app.conf.enable_utc = False

celery_app.conf.beat_schedule = beat_schedule

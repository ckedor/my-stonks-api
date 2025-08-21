from celery import Celery
from celery.schedules import crontab

import app.infrastructure.db.models
import app.users.models
from app.config.settings import settings

celery_app = Celery("my-stonks")
celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL
celery_app.conf.timezone = "America/Sao_Paulo"
celery_app.conf.enable_utc = False

import app.worker.tasks

celery_app.conf.beat_schedule = {
    "consolidate-indexes-3x-day": {
        "task": "consolidate_indexes_history",
        "schedule": crontab(hour="5,13,21", minute=0),
    },
    "consolidate-portfolios-3x-day": {
        "task": "consolidate_all_portfolios",
        "schedule": crontab(hour="5,13,21", minute=5),
    },
    "consolidate-fiis-dividends-1x-day": {
        "task": "consolidate_fiis_dividends",
        "schedule": crontab(hour="4", minute=30),
    },
}

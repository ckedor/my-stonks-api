from celery.schedules import crontab

beat_schedule = {
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

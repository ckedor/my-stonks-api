import app.infra.db.models  # noqa: F401
import app.users.models  # noqa: F401
import app.worker.tasks  # noqa: F401
from app.entrypoints.worker.celery_app import celery_app

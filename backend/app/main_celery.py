import app.infra.db.models  # noqa: F401
import app.modules.market_data.tasks  # noqa: F401
import app.modules.portfolio.tasks  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.entrypoints.worker.celery_app import celery_app

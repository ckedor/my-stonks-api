# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.router import router as main_router
from app.config.logger import logging
from app.config.settings import settings
from app.infrastructure.middlewares.demo_user_middleware import DemoUserMiddleware
from app.users.views import setup_user_views
from app.worker.celery_app import celery_app

logger = logging.getLogger('uvicorn')

app = FastAPI(
    title='My Stonks API',
    description='API for portfolio consolidation',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(DemoUserMiddleware)

app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

setup_user_views(app)
app.include_router(main_router)

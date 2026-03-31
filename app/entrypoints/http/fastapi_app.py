# app/entrypoints/http/app.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config.logger import logger
from app.config.settings import settings
from app.entrypoints.http.router import router as main_router
from app.modules.users.views import setup_user_views


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.entrypoints.worker.task_runner import run_task
    from app.modules.market_data.tasks.consolidate_indexes_history import (
        consolidate_indexes_history,
    )

    logger.info("🚀 Disparando consolidate_indexes_history no startup")
    run_task(consolidate_indexes_history)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title='My Stonks API',
        description='API for portfolio consolidation',
        version='1.0.0',
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

    setup_user_views(app)
    
    app.include_router(main_router)
        
    return app

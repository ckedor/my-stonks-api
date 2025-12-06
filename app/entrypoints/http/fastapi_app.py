# app/entrypoints/http/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config.settings import settings
from app.entrypoints.http.router import router as main_router
from app.users.views import setup_user_views


def create_app() -> FastAPI:
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

    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

    setup_user_views(app)
    
    app.include_router(main_router)
        
    return app

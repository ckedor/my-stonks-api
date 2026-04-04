"""
Asset Module

Handles asset management, asset types, fixed income, and events.

Structure:
- api/: FastAPI routes and Pydantic schemas
- service/: Business logic layer
"""

from app.modules.asset.api.routes import router

__all__ = ['router']

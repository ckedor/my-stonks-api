"""
Brokers Module

Handles broker management operations.

Structure:
- api/: FastAPI routes and Pydantic schemas
- service/: Business logic layer
"""

from app.modules.brokers.api.routes import router

__all__ = ['router']

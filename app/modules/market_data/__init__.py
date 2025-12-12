"""
Market Data Module

Handles market indexes, exchange rates (USD/BRL), and asset price quotes.

Structure:
- api/: FastAPI routes and Pydantic schemas
- service/: Business logic layer
- repositories/: Database access layer
- tasks/: Celery background tasks
- domain/: Domain models and business rules (if needed)
"""

from app.modules.market_data.api.routes import router

__all__ = ['router']

"""
Portfolio Module

Handles portfolio management, positions, transactions, dividends, and income tax calculations.

Structure:
- api/: FastAPI routes and Pydantic schemas (multiple sub-routers)
- service/: Business logic layer
"""

from app.modules.portfolio.api.router import router

__all__ = ['router']

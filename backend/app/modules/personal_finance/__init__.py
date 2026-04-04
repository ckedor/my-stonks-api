"""
Personal Finance Module

Handles personal expense tracking, income management, and financial summaries.

Structure:
- api/: FastAPI routes and Pydantic schemas
- service/: Business logic layer
"""

from app.modules.personal_finance.api.routes import router

__all__ = ['router']

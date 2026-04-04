---
description: "Use when writing or editing Python backend code: FastAPI routes, services, repositories, Celery tasks, Pydantic schemas."
applyTo: "backend/**/*.py"
---
# Backend Python Conventions

## Route Handlers
- Always `async def`.
- Inject session via `Depends(get_session)`, auth via `Depends(current_active_user)`.
- Instantiate service inside handler: `service = MyService(session)`.
- Use `Query()` for query params with defaults. Use Pydantic schemas for request bodies.

## Services
- Receive `session` in `__init__`, create repositories there.
- Keep business logic here — not in routes or repos.
- Raise `HTTPException` for error responses.
- For dual-currency data: `suffix = '_usd' if currency == 'USD' else ''`, then `getattr(model, f'field{suffix}')`.

## Repositories
- Async SQLAlchemy queries, return DataFrames (`pd.DataFrame`) or ORM models.
- Use `_build_portfolio_position_query` base query pattern for position-related queries.

## Formatting
- Black (line-length 120), isort, Ruff. Pre-commit handles this automatically.

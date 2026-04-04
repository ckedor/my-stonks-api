# My Stonks – Copilot Instructions

## Language

Always respond in **English** unless the user writes in another language — then match their language.

## Project Overview

**My Stonks** is a portfolio consolidation platform for Brazilian investors. It tracks stocks (BR & US), FIIs, crypto, fixed income, and pension assets with multi-currency (BRL/USD) support.

## Tech Stack

### Backend (`/backend`)
- **Python 3.12+**, FastAPI, async/await throughout
- **Database**: PostgreSQL 14 (async via asyncpg + SQLAlchemy async)
- **Migrations**: Alembic (`app/infra/db/alembic/`)
- **Task queue**: Celery + Redis
- **Data processing**: Pandas, NumPy
- **Auth**: fastapi-users, JWT, Argon2
- **Formatting**: Black, isort, Ruff

### Frontend (`/frontend`)
- **React 19** + **TypeScript 5** (strict mode)
- **Build**: Vite
- **UI**: MUI (Material UI) + Emotion
- **State**: Zustand (with persist middleware to localStorage)
- **Caching**: Dexie (IndexedDB) via `useCachedData` hook
- **HTTP**: Axios with JWT interceptor
- **Charts**: Recharts, lightweight-charts, visx
- **Lint**: ESLint flat config

## Architecture

### Backend module structure
```
modules/{name}/
├── api/
│   ├── router.py          # FastAPI sub-router
│   └── {feature}/
│       ├── router.py
│       └── schemas.py     # Pydantic models
├── service/               # Business logic
├── repositories/          # Data access (SQLAlchemy queries)
├── domain/                # Domain models/logic (optional)
└── tasks/                 # Celery tasks
```

### Frontend structure
```
src/
├── components/            # Reusable components
│   ├── charts/            # Chart components
│   └── ui/                # Atomic UI (AppTable, AppCard, etc.)
├── pages/                 # Route pages (portfolio/, login/, admin/)
├── stores/                # Zustand stores (portfolio/, currency, auth)
├── hooks/                 # Custom hooks (useCachedData, useCurrency)
├── api/                   # Pure API functions (no state side-effects)
├── actions/               # Sync actions (bridge API → stores with caching)
├── lib/                   # Utilities (api.ts axios instance, formatters)
└── types/                 # TypeScript interfaces
```

## Key Patterns

### Backend

- **Dependency injection**: Use `Depends(get_session)` for DB sessions, `Depends(current_active_user)` for auth.
- **Service instantiation**: Create service in route handler — `service = MyService(session)`. Services receive the session in `__init__`.
- **Repository layer**: Services use repositories for DB queries. Repos return DataFrames (Pandas) or ORM models.
- **Dual-currency columns**: Position table has paired columns (`price`/`price_usd`, `acc_return`/`acc_return_usd`, etc.). Select with `suffix = '_usd' if currency == 'USD' else ''`.
- **Error handling**: Raise `HTTPException` directly in services/routes.
- **Caching**: `RedisService` for hot data (patrimony, returns). `@cached` decorator where applicable.
- **Celery tasks**: Located in `modules/{module}/tasks/`, invoked via `run_task(task_function, *args)`.

### Frontend

- **Data fetching** (page-level): `useCachedData<T>(cacheKey, fetcher, { enabled })` — reads IndexedDB first, then background-fetches.
- **Global data sync**: `usePortfolioSync()` in MainLayout watches currency/portfolio changes and re-syncs all stores.
- **Currency**: `useCurrency()` returns `{ currency, symbol, locale, format, toggleCurrency }`. Always use `format(value)` for monetary display. Include `currency` in cache keys and API params.
- **Zustand stores**: Thin stores (state + setters). Persist with `persist()` middleware when needed.
- **API functions**: Pure functions in `src/api/` — return data only, no store mutations. Actions in `src/actions/` bridge API → stores.
- **Component naming**: `{Feature}Form.tsx`, `{Feature}Table.tsx`, `{Feature}Chart.tsx`, `{Feature}PieChart.tsx`.
- **Atomic UI**: `AppTable`, `AppCard`, `AppPieChart`, `AppBarChart` in `components/ui/` — reusable building blocks.

## Testing

### Backend
- Tests in `/backend/tests/` using pytest + httpx `AsyncClient`.
- Separate test DB on port 5434; Alembic migrations run once per session.
- `mock_redis` fixture stubs all Redis calls.
- Reference tables preserved between tests; other tables truncated.

### Frontend
- No test setup currently.

## Commands

| Action | Command |
|--------|---------|
| Backend dev server | `cd backend && uvicorn app.main_fastapi:app --reload` |
| Frontend dev server | `cd frontend && npm run dev` |
| Start DB | `cd backend && docker-compose up -d db` |
| Start Redis | `cd backend && docker-compose up -d redis` |
| Run backend tests | `cd backend && pytest` |
| Frontend build | `cd frontend && npm run build` |
| DB migrations | `cd backend && alembic upgrade head` |
| Celery worker | `cd backend && celery -A app.main_celery worker` |
| Celery beat | `cd backend && celery -A app.main_celery beat` |

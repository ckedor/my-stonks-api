---
description: "Use when writing or editing backend tests with pytest."
applyTo: "backend/tests/**/*.py"
---
# Backend Testing Conventions

- Use `pytest.mark.asyncio` for async tests.
- HTTP client: `client` fixture (httpx `AsyncClient`).
- Auth: seed user is `seed@user.com`. Login via `POST /auth/login` with form data.
- DB: test database on port 5434. Alembic migrations run once per session.
- Redis: `mock_redis` fixture stubs all `RedisService` calls in-memory.
- Reference tables (currency, asset_type, etc.) are preserved; other tables truncated between tests.
- Arrange-Act-Assert pattern. Use descriptive test names: `test_{action}_should_{expected_result}`.

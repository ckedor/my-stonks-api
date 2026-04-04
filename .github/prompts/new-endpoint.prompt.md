---
description: "Create a new FastAPI endpoint with service, repository, and Pydantic schema following project conventions."
agent: "agent"
argument-hint: "Describe the endpoint (e.g., GET /portfolio/{id}/summary)"
---
Create a new backend endpoint following these steps:

1. **Router**: Add the route in the appropriate `modules/{module}/api/{feature}/router.py`. Use `async def`, inject `session=Depends(get_session)` and auth if needed.
2. **Schema**: Create Pydantic request/response models in `schemas.py` next to the router.
3. **Service**: Add the business logic method in the corresponding service class. Instantiate the service in the router handler.
4. **Repository** (if new query needed): Add the data access method in the repository. Return DataFrame or ORM model.

Follow existing patterns in the codebase. Include `currency: str = Query('BRL')` if the endpoint returns monetary data.

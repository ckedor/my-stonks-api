from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class DemoUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        response = await call_next(request)

        try:
            user = getattr(request.state, 'user', None)
            if user and isinstance(user, dict):
                if user.get("email") == "user@demo.com" and request.method in {"POST", "PUT", "DELETE"}:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Demo user is not allowed to modify resources."}
                    )
        except Exception:
            pass

        return response

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

type Remaining = dict[str, int] | None


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """Add rate-limit metadata set by request dependencies to responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)
        remaining: Remaining = getattr(request.state, "rate_limit_remaining", None)
        if remaining:
            for scope, value in remaining.items():
                response.headers[f"X-RateLimit-Remaining-{scope}"] = str(value)
        return response

"""Security and monitoring middleware for FastAPI application."""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    def __init__(self, app: ASGIApp, is_production: bool = False):
        super().__init__(app)
        self.is_production = is_production

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS header (only in production with HTTPS)
        if self.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # React needs eval
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses with timing."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log successful response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                }
            )

            # Add timing header
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {exc.__class__.__name__}: {exc} ({duration:.3f}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_seconds": duration,
                    "exception": str(exc),
                    "exception_type": exc.__class__.__name__,
                },
                exc_info=True,
            )
            raise


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size to prevent memory exhaustion attacks."""

    def __init__(self, app: ASGIApp, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        if "content-length" in request.headers:
            content_length = int(request.headers["content-length"])
            if content_length > self.max_size:
                logger.warning(
                    f"Request body too large: {content_length} bytes (max: {self.max_size})",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "content_length": content_length,
                        "max_size": self.max_size,
                    }
                )
                return Response(
                    content=f'{{"detail":"Request body too large. Maximum size: {self.max_size} bytes"}}',
                    status_code=413,
                    media_type="application/json",
                )

        return await call_next(request)

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from chat_store.core.logger import get_logger, LoggingContext

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses with correlation IDs."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID if not provided
        request_id = request.headers.get("X-Request-ID") or str(time.time_ns())
        
        # Extract user ID from various sources
        user_id = None
        if hasattr(request.state, 'user_id'):
            user_id = request.state.user_id
        elif request.headers.get("X-User-ID"):
            user_id = request.headers.get("X-User-ID")
        
        # Set up logging context
        with LoggingContext(request_id=request_id, user_id=user_id):
            # Log request
            logger.info(
                "request_started",
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params),
                user_agent=request.headers.get("user-agent"),
                client_ip=self._get_client_ip(request),
                content_length=request.headers.get("content-length"),
            )
            
            start_time = time.time()
            
            try:
                # Process request
                response = await call_next(request)
                
                # Log successful response
                duration = time.time() - start_time
                logger.info(
                    "request_completed",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_seconds=duration,
                    content_length=response.headers.get("content-length"),
                )
                
                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id
                
                return response
                
            except Exception as exc:
                # Log error
                duration = time.time() - start_time
                logger.error(
                    "request_failed",
                    method=request.method,
                    path=request.url.path,
                    duration_seconds=duration,
                    error=str(exc),
                    error_type=type(exc).__name__,
                )
                
                # Return error response with request ID
                return JSONResponse(
                    status_code=500,
                    content={
                        "detail": "Internal server error",
                        "request_id": request_id
                    },
                    headers={"X-Request-ID": request_id}
                )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class DatabaseQueryLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging database queries."""
    
    async def dispatch(self, request: Request, call_next):
        # This would integrate with SQLAlchemy event listeners
        # For now, we'll just pass through
        response = await call_next(request)
        return response
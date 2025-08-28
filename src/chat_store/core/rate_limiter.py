from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

from chat_store.core.config import config
from chat_store.core.logger import get_logger

logger = get_logger(__name__)

# Initialize the rate limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour"],
    storage_uri=str(config.redis.REDIS_URI),
    headers_enabled=True,
    strategy="fixed-window"
)


def setup_rate_limiter(app: FastAPI):
    """Setup rate limiting for the FastAPI application."""
    if not config.RATE_LIMITER_ENABLED:
        logger.info("rate_limiter_disabled")
        return
    
    # Add the limiter to the app
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info(
        "rate_limiter_enabled",
        max_requests=config.RATE_LIMITER_MAX_REQUESTS,
        timeframe=config.RATE_LIMITER_TIMEFRAME
    )


def get_rate_limit_string(endpoint_type: str) -> Optional[str]:
    """Get rate limit string for specific endpoint type."""
    if not config.RATE_LIMITER_ENABLED:
        return None
    
    rate_limits = {
        "create_session": config.RATE_LIMIT_CREATE_SESSION,
        "list_sessions": config.RATE_LIMIT_LIST_SESSIONS,
        "create_message": config.RATE_LIMIT_CREATE_MESSAGE,
        "get_messages": config.RATE_LIMIT_GET_MESSAGES,
        "resume_message": config.RATE_LIMIT_RESUME_MESSAGE,
        "update_session": config.RATE_LIMIT_UPDATE_SESSION,
        "delete_session": config.RATE_LIMIT_DELETE_SESSION,
        "toggle_favorite": config.RATE_LIMIT_TOGGLE_FAVORITE,
    }
    
    return rate_limits.get(endpoint_type)

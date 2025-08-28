from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from chat_store.api.v1.api import api_router
from chat_store.core.config import config
from chat_store.core.logger import setup_logging, get_logger
from chat_store.core.middleware import LoggingMiddleware
from chat_store.core.rate_limiter import setup_rate_limiter
from chat_store.db.init_db import init_db

# Import models to ensure SQLAlchemy mapper configuration
from chat_store.models import message, session  # noqa: F401

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    logger.info("application_startup", service="chat-store", version="1.0.0")
    yield
    logger.info("application_shutdown", service="chat-store")

app = FastAPI(
    title="RAG Chat Storage Microservice",
    description="A scalable backend microservice for managing chat sessions in a RAG chatbot system",
    version="1.0.0",
    openapi_url=f"{config.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Setup rate limiting
setup_rate_limiter(app)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=config.API_V1_STR)

start_time = datetime.now()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions globally."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


@app.get("/health")
async def health():
    """A simple, fast liveness probe."""
    current_time = datetime.now()
    uptime = current_time - start_time

    days = uptime.days
    seconds = uptime.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime_str = f"{days}d {hours}hrs {minutes}mins {seconds}s"

    logger.debug("health_check_requested", uptime_seconds=uptime.total_seconds())

    return JSONResponse(
        content={
            "status": "OK",
            "start_time": start_time.isoformat(),
            "current_time": current_time.isoformat(),
            "uptime": uptime_str,
        },
        status_code=200
    )
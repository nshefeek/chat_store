import logging
import sys
import uuid
from typing import Optional
import structlog
from contextvars import ContextVar, Token
import time

# Context variable for request correlation
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def setup_logging(log_level: str = "INFO", enable_access_log: bool = False):
    """
    Set up enhanced structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_access_log: Whether to enable uvicorn access logs
    """
    
    def add_app_info(logger, method_name, event_dict):
        """Add application-specific information to logs."""
        event_dict["app"] = "chat-store"
        event_dict["version"] = "1.0.0"
        event_dict["environment"] = "production"
        return event_dict
    
    def add_request_context(logger, method_name, event_dict):
        """Add request context information to logs."""
        request_id = request_id_var.get()
        user_id = user_id_var.get()
        
        if request_id:
            event_dict["request_id"] = request_id
        if user_id:
            event_dict["user_id"] = user_id
            
        return event_dict
    
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_app_info,
        add_request_context,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processor=structlog.processors.JSONRenderer(),
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Configure uvicorn access logs
    if not enable_access_log:
        logging.getLogger("uvicorn.access").disabled = True
    else:
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_access_logger.handlers.clear()
        uvicorn_access_logger.addHandler(handler)
        uvicorn_access_logger.setLevel(getattr(logging, log_level.upper()))

    # Configure database query logging
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


def get_logger(module_name: str) -> structlog.BoundLogger:
    """Get a structured logger instance for the given module."""
    return structlog.get_logger(module_name)


class LoggingContext:
    """Context manager for setting request context variables."""
    
    def __init__(self, request_id: Optional[str] = None, user_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.request_token: Optional[Token[Optional[str]]] = None
        self.user_token: Optional[Token[Optional[str]]] = None
    
    def __enter__(self):
        self.request_token = request_id_var.set(self.request_id)
        if self.user_id:
            self.user_token = user_id_var.set(self.user_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.request_token is not None:
            request_id_var.reset(self.request_token)
        if self.user_token is not None:
            user_id_var.reset(self.user_token)


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, logger: structlog.BoundLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(
            "operation_started",
            operation=self.operation,
            **self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            
            if exc_type is not None:
                self.logger.error(
                    "operation_failed",
                    operation=self.operation,
                    duration_seconds=duration,
                    error=str(exc_val),
                    error_type=exc_type.__name__,
                    **self.context
                )
            else:
                self.logger.info(
                    "operation_completed",
                    operation=self.operation,
                    duration_seconds=duration,
                    **self.context
                )
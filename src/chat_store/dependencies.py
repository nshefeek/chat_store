from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat_store.db.base import get_db
from chat_store.repositories.session_repository import SessionRepository
from chat_store.repositories.message_repository import MessageRepository
from chat_store.services.session_service import SessionService
from chat_store.services.message_service import MessageService
from chat_store.core.rate_limiter import limiter


def get_session_repository(db: AsyncSession = Depends(get_db)) -> SessionRepository:
    """Dependency to get SessionRepository instance."""
    return SessionRepository(db)


def get_message_repository(db: AsyncSession = Depends(get_db)) -> MessageRepository:
    """Dependency to get MessageRepository instance."""
    return MessageRepository(db)


def get_session_service(
    repository: SessionRepository = Depends(get_session_repository)
) -> SessionService:
    """Dependency to get SessionService instance."""
    return SessionService(repository)


def get_message_service(
    message_repository: MessageRepository = Depends(get_message_repository),
    session_repository: SessionRepository = Depends(get_session_repository)
) -> MessageService:
    """Dependency to get MessageService instance."""
    return MessageService(message_repository, session_repository)


# Export the limiter for use in endpoints
__all__ = [
    "get_session_repository",
    "get_message_repository", 
    "get_session_service",
    "get_message_service",
    "limiter"
]
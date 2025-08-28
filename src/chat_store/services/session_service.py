from typing import List, Optional, Tuple
from uuid import UUID

from chat_store.repositories.session_repository import SessionRepository
from chat_store.models.session import Session
from chat_store.schemas.session import SessionCreate
from chat_store.core.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    """Service layer for session business logic."""
    
    def __init__(self, repository: SessionRepository):
        self.repository = repository
    
    async def create_session(self, session_data: SessionCreate) -> Session:
        """Create a new session with business validation."""
        session = Session(**session_data.dict())
        created_session = await self.repository.create(session)
        
        logger.info(
            "session_created",
            session_id=str(created_session.id),
            user_id=str(created_session.user_id),
            session_name=created_session.name
        )
        
        return created_session
    
    async def get_user_sessions(self, user_id: UUID, skip: int = 0, limit: int = 100) -> Tuple[List[Session], int]:
        """Get paginated sessions for a user."""
        sessions = await self.repository.list_by_user(user_id, skip, limit)
        total = await self.repository.count_by_user(user_id)
        
        logger.debug(
            "user_sessions_retrieved",
            user_id=str(user_id),
            count=len(sessions),
            total=total,
            skip=skip,
            limit=limit
        )
        
        return sessions, total
    
    async def get_session_by_id(self, session_id: UUID) -> Optional[Session]:
        """Get a single session by ID."""
        session = await self.repository.get_by_id(session_id)
        
        if session:
            logger.debug("session_retrieved", session_id=str(session_id))
        else:
            logger.warning("session_not_found", session_id=str(session_id))
        
        return session
    
    async def update_session_name(self, session_id: UUID, name: str) -> Optional[Session]:
        """Update session name with validation."""
        if not name or not name.strip():
            logger.warning("invalid_session_name", session_id=str(session_id), name=name)
            return None
        
        updated_session = await self.repository.update(session_id, name=name.strip())
        
        if updated_session:
            logger.info(
                "session_name_updated",
                session_id=str(session_id),
                new_name=name.strip()
            )
        
        return updated_session
    
    async def toggle_favorite(self, session_id: UUID, is_favorite: bool) -> Optional[Session]:
        """Toggle favorite status for a session."""
        updated_session = await self.repository.update(session_id, is_favorite=is_favorite)
        
        if updated_session:
            logger.info(
                "session_favorite_toggled",
                session_id=str(session_id),
                is_favorite=is_favorite
            )
        
        return updated_session
    
    async def delete_session(self, session_id: UUID) -> bool:
        """Delete a session with cascade."""
        success = await self.repository.delete(session_id)
        
        if success:
            logger.info("session_deleted", session_id=str(session_id))
        else:
            logger.warning("session_delete_failed", session_id=str(session_id))
        
        return success
    
    async def session_exists(self, session_id: UUID) -> bool:
        """Check if a session exists."""
        return await self.repository.exists(session_id)
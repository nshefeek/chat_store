from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from chat_store.models.session import Session
from chat_store.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository for Session data access operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
    
    async def create(self, session: Session) -> Session:
        """Create a new session."""
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Session]:
        """List sessions for a specific user with pagination."""
        query = select(Session).where(Session.user_id == user_id)
        query = query.order_by(
            Session.is_favorite.desc(),
            Session.updated_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_by_user(self, user_id: UUID) -> int:
        """Count total sessions for a user."""
        query = select(func.count()).where(Session.user_id == user_id)
        return await self.db.scalar(query) or 0
    
    async def list(self, **filters) -> List[Session]:
        """List sessions with optional filters."""
        query = select(Session)
        
        if 'user_id' in filters:
            query = query.where(Session.user_id == filters['user_id'])
        if 'is_favorite' in filters:
            query = query.where(Session.is_favorite == filters['is_favorite'])
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, session_id: UUID, **kwargs) -> Optional[Session]:
        """Update session by ID."""
        session = await self.get_by_id(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            await self.db.commit()
            await self.db.refresh(session)
        return session
    
    async def delete(self, session_id: UUID) -> bool:
        """Delete session by ID."""
        session = await self.get_by_id(session_id)
        if session:
            await self.db.delete(session)
            await self.db.commit()
            return True
        return False
    
    async def exists(self, session_id: UUID) -> bool:
        """Check if session exists."""
        result = await self.db.execute(
            select(Session.id).where(Session.id == session_id)
        )
        return result.scalar_one_or_none() is not None
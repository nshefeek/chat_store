from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from chat_store.models.message import Message
from chat_store.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message data access operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
    
    async def create(self, message: Message) -> Message:
        """Create a new message."""
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """Get message by ID."""
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_session(self, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        """List messages for a specific session in chronological order."""
        query = select(Message).where(Message.session_id == session_id)
        query = query.order_by(Message.timestamp.asc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_by_session(self, session_id: UUID) -> int:
        """Count total messages for a session."""
        query = select(func.count()).where(Message.session_id == session_id)
        return await self.db.scalar(query) or 0
    
    async def get_latest_by_session(self, session_id: UUID) -> Optional[Message]:
        """Get the latest message for a session."""
        query = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.timestamp.desc())
            .limit(1)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list(self, **filters) -> List[Message]:
        """List messages with optional filters."""
        query = select(Message)
        
        if 'session_id' in filters:
            query = query.where(Message.session_id == filters['session_id'])
        if 'sender' in filters:
            query = query.where(Message.sender == filters['sender'])
        if 'status' in filters:
            query = query.where(Message.status == filters['status'])
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, message_id: UUID, **kwargs) -> Optional[Message]:
        """Update message by ID."""
        message = await self.get_by_id(message_id)
        if message:
            for key, value in kwargs.items():
                if hasattr(message, key):
                    setattr(message, key, value)
            await self.db.commit()
            await self.db.refresh(message)
        return message
    
    async def delete(self, message_id: UUID) -> bool:
        """Delete message by ID."""
        message = await self.get_by_id(message_id)
        if message:
            await self.db.delete(message)
            await self.db.commit()
            return True
        return False
    
    async def exists(self, message_id: UUID) -> bool:
        """Check if message exists."""
        result = await self.db.execute(
            select(Message.id).where(Message.id == message_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def exists_in_session(self, session_id: UUID) -> bool:
        """Check if any messages exist for a session."""
        result = await self.db.execute(
            select(Message.id).where(Message.session_id == session_id).limit(1)
        )
        return result.scalar_one_or_none() is not None
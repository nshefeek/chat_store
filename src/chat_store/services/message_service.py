from typing import List, Optional, Tuple
from uuid import UUID

from chat_store.repositories.message_repository import MessageRepository
from chat_store.repositories.session_repository import SessionRepository
from chat_store.models.message import Message, MessageStatus
from chat_store.schemas.message import MessageCreate, ResumeResponse
from chat_store.core.logger import get_logger

logger = get_logger(__name__)


class MessageService:
    """Service layer for message business logic."""
    
    def __init__(self, message_repository: MessageRepository, session_repository: SessionRepository):
        self.message_repository = message_repository
        self.session_repository = session_repository
    
    async def create_message(self, session_id: UUID, message_data: MessageCreate) -> Message:
        """Create a new message with session validation."""
        # Validate session exists
        session_exists = await self.session_repository.exists(session_id)
        if not session_exists:
            logger.warning(
                "session_not_found",
                session_id=str(session_id),
                action="create_message"
            )
            raise ValueError(f"Session {session_id} not found")
        
        message_data_dict = message_data.model_dump(exclude_unset=True)
        message_data_dict['session_id'] = session_id
        message = Message(**message_data_dict)
        created_message = await self.message_repository.create(message)
        
        logger.info(
            "message_created",
            message_id=str(created_message.id),
            session_id=str(created_message.session_id),
            sender=created_message.sender.value,
            content_length=len(created_message.content)
        )
        
        return created_message
    
    async def get_session_messages(self, session_id: UUID, skip: int = 0, limit: int = 100) -> Tuple[List[Message], int]:
        """Get paginated messages for a session."""
        # Validate session exists
        session_exists = await self.session_repository.exists(session_id)
        if not session_exists:
            logger.warning(
                "session_not_found",
                session_id=str(session_id),
                action="get_session_messages"
            )
            raise ValueError(f"Session {session_id} not found")
        
        messages = await self.message_repository.list_by_session(session_id, skip, limit)
        total = await self.message_repository.count_by_session(session_id)
        
        logger.debug(
            "session_messages_retrieved",
            session_id=str(session_id),
            count=len(messages),
            total=total,
            skip=skip,
            limit=limit
        )
        
        return messages, total
    
    async def get_message_by_id(self, message_id: UUID) -> Optional[Message]:
        """Get a single message by ID."""
        message = await self.message_repository.get_by_id(message_id)
        
        if message:
            logger.debug("message_retrieved", message_id=str(message_id))
        else:
            logger.warning("message_not_found", message_id=str(message_id))
        
        return message
    
    async def resume_failed_message(self, session_id: UUID) -> ResumeResponse:
        """Resume a failed or pending message."""
        # Validate session exists
        session_exists = await self.session_repository.exists(session_id)
        if not session_exists:
            logger.warning(
                "session_not_found",
                session_id=str(session_id),
                action="resume_failed_message"
            )
            raise ValueError(f"Session {session_id} not found")
        
        # Get the latest message
        latest_message = await self.message_repository.get_latest_by_session(session_id)
        
        if not latest_message:
            logger.warning(
                "no_messages_found",
                session_id=str(session_id),
                action="resume_failed_message"
            )
            raise ValueError(f"No messages found for session {session_id}")
        
        # Check if message is resumable
        if latest_message.status not in [MessageStatus.PENDING, MessageStatus.FAILED]:
            logger.warning(
                "message_not_resumable",
                session_id=str(session_id),
                message_id=str(latest_message.id),
                status=latest_message.status.value
            )
            raise ValueError("Latest message is not in a resumable state")
        
        # Reset status to pending
        updated_message = await self.message_repository.update(
            latest_message.id,
            status=MessageStatus.PENDING,
            error_message=None
        )
        
        if updated_message:
            logger.info(
                "message_resumed",
                session_id=str(session_id),
                message_id=str(updated_message.id)
            )
        
        return ResumeResponse(
            message_id=updated_message.id,
            status=updated_message.status
        )
    
    async def update_message_status(self, message_id: UUID, status: MessageStatus, error_message: Optional[str] = None) -> Optional[Message]:
        """Update message status."""
        updated_message = await self.message_repository.update(
            message_id,
            status=status,
            error_message=error_message
        )
        
        if updated_message:
            logger.info(
                "message_status_updated",
                message_id=str(message_id),
                status=status.value,
                error_message=error_message
            )
        
        return updated_message
    
    async def delete_message(self, message_id: UUID) -> bool:
        """Delete a message."""
        success = await self.message_repository.delete(message_id)
        
        if success:
            logger.info("message_deleted", message_id=str(message_id))
        else:
            logger.warning("message_delete_failed", message_id=str(message_id))
        
        return success
    
    async def session_has_messages(self, session_id: UUID) -> bool:
        """Check if a session has any messages."""
        return await self.message_repository.exists_in_session(session_id)
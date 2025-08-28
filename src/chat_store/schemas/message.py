from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer

from chat_store.models.message import MessageStatus, Sender


class MessageBase(BaseModel):
    sender: Sender = Field(..., description="Message sender (user or ai)")
    content: str = Field(..., description="Message content", min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = Field(None, description="RAG context data")


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, description="Updated message content")
    status: Optional[MessageStatus] = Field(None, description="Message status")
    partial_content: Optional[str] = Field(None, description="Partial response content")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class MessageInDBBase(BaseModel):
    id: UUID
    session_id: UUID
    sender: Sender
    content: str
    context: Optional[Dict[str, Any]]
    status: MessageStatus
    partial_content: Optional[str]
    error_message: Optional[str]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    @field_serializer('id')
    def serialize_id(self, value: UUID, _info) -> str:
        return str(value)

    @field_serializer('session_id')
    def serialize_session_id(self, value: UUID, _info) -> str:
        return str(value)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime, _info) -> str:
        return value.isoformat()

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat()

    @field_serializer('updated_at')
    def serialize_updated_at(self, value: datetime, _info) -> str:
        return value.isoformat()


class Message(MessageInDBBase):
    pass


class MessageList(BaseModel):
    messages: list[Message]
    total: int


class ResumeResponse(BaseModel):
    message_id: UUID
    status: MessageStatus
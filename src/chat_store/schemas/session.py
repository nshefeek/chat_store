from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer


class SessionBase(BaseModel):
    name: Optional[str] = Field(None, description="Session name")
    is_favorite: Optional[bool] = Field(False, description="Whether session is favorited")


class SessionCreate(SessionBase):
    user_id: UUID = Field(..., description="User ID")
    name: Optional[str] = Field("New Chat", description="Session name")

    @field_serializer('user_id')
    def serialize_user_id(self, value: UUID, _info) -> str:
        return str(value)


class SessionUpdate(SessionBase):
    name: Optional[str] = Field(None, description="Session name")


class SessionInDBBase(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    is_favorite: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('id')
    def serialize_id(self, value: UUID, _info) -> str:
        return str(value)

    @field_serializer('user_id')
    def serialize_user_id(self, value: UUID, _info) -> str:
        return str(value)

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat()

    @field_serializer('updated_at')
    def serialize_updated_at(self, value: datetime, _info) -> str:
        return value.isoformat()


class Session(SessionInDBBase):
    pass


class SessionList(BaseModel):
    sessions: list[Session]
    total: int
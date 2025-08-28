from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, Response

from chat_store.services.session_service import SessionService
from chat_store.services.message_service import MessageService
from chat_store.schemas.session import SessionCreate, SessionUpdate, Session, SessionList
from chat_store.schemas.message import MessageCreate, Message, MessageList, ResumeResponse
from chat_store.services.auth import verify_api_key
from chat_store.dependencies import get_session_service, get_message_service
from chat_store.core.rate_limiter import limiter

router = APIRouter()


@router.post("/", response_model=Session, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_session(
    request: Request,
    response: Response,
    session_in: SessionCreate,
    service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Create a new chat session."""
    return await service.create_session(session_in)


@router.get("/", response_model=SessionList)
@limiter.limit("30/minute")
async def list_sessions(
    request: Request,
    response: Response,
    user_id: UUID = Query(..., description="User ID"),
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit N items"),
    service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """List sessions for a specific user with pagination."""
    sessions, total = await service.get_user_sessions(user_id, skip, limit)
    return SessionList(sessions=sessions, total=total)


@router.put("/{session_id}", response_model=Session)
@limiter.limit("20/minute")
async def update_session(
    request: Request,
    response: Response,
    session_id: UUID,
    session_in: SessionUpdate,
    service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Update session details."""
    if session_in.name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required for update"
        )
    
    updated_session = await service.update_session_name(session_id, session_in.name)
    if not updated_session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    return updated_session


@router.patch("/{session_id}/favorite", response_model=Session)
@limiter.limit("20/minute")
async def toggle_favorite(
    request: Request,
    response: Response,
    session_id: UUID,
    is_favorite: bool = Query(..., description="Favorite status"),
    service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Toggle favorite status for a session."""
    updated_session = await service.toggle_favorite(session_id, is_favorite)
    if not updated_session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    return updated_session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_session(
    request: Request,
    response: Response,
    session_id: UUID,
    service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Delete a session and all its messages."""
    success = await service.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

# Messages

@router.post("/{session_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
@limiter.limit("50/minute")
async def create_session_message(
    request: Request,
    response: Response,
    session_id: UUID,
    message_in: MessageCreate,
    message_service: MessageService = Depends(get_message_service),
    session_service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Create a new message in a specific session."""
    session_exists = await session_service.session_exists(session_id)
    if not session_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    try:
        return await message_service.create_message(session_id, message_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{session_id}/messages", response_model=MessageList)
@limiter.limit("100/minute")
async def list_session_messages(
    request: Request,
    response: Response,
    session_id: UUID,
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit N items"),
    message_service: MessageService = Depends(get_message_service),
    session_service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Get paginated messages for a specific session with advanced filtering."""
    session_exists = await session_service.session_exists(session_id)
    if not session_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    try:
        messages, total = await message_service.get_session_messages(session_id, skip, limit)
        return MessageList(messages=messages, total=total)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get("/{session_id}/messages/{message_id}", response_model=Message)
@limiter.limit("100/minute")
async def get_session_message(
    request: Request,
    response: Response,
    session_id: UUID,
    message_id: UUID,
    message_service: MessageService = Depends(get_message_service),
    session_service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Get a specific message from a session."""
    session_exists = await session_service.session_exists(session_id)
    if not session_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    message = await message_service.get_message_by_id(message_id)
    if not message or message.session_id != session_id:
        raise HTTPException(
            status_code=404,
            detail=f"Message {message_id} not found in session {session_id}"
        )
    
    return message


@router.post("/{session_id}/messages/{message_id}/resume", response_model=ResumeResponse)
@limiter.limit("5/minute")
async def resume_session_message(
    request: Request,
    response: Response,
    session_id: UUID,
    message_id: UUID,
    message_service: MessageService = Depends(get_message_service),
    session_service: SessionService = Depends(get_session_service),
    api_key: str = Depends(verify_api_key)
):
    """Resume a failed or pending message in a specific session."""
    session_exists = await session_service.session_exists(session_id)
    if not session_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    message = await message_service.get_message_by_id(message_id)
    if not message or message.session_id != session_id:
        raise HTTPException(
            status_code=404,
            detail=f"Message {message_id} not found in session {session_id}"
        )
    
    try:
        return await message_service.resume_failed_message(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
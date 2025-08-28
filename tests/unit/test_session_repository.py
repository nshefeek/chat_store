import pytest_asyncio
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from chat_store.repositories.session_repository import SessionRepository
from chat_store.models.session import Session


class TestSessionRepository:
    """Unit tests for SessionRepository."""

    @pytest_asyncio.fixture
    async def repository(self, db_session: AsyncSession) -> SessionRepository:
        """Create a session repository instance."""
        return SessionRepository(db_session)

    @pytest_asyncio.fixture
    async def test_session(self, db_session: AsyncSession) -> Session:
        """Create a test session."""
        session = Session(
            user_id="a6ee4dde-c95d-4644-a842-13d4fadea71e",
            name="Test Session",
            is_favorite=False
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        return session

    async def test_create_session(self, repository: SessionRepository):
        """Test creating a new session."""
        session = Session(
            user_id="a6ee4dde-c95d-4644-a842-13d4fadea71e",
            name="New Test Session",
            is_favorite=True
        )
        
        created = await repository.create(session)
        
        assert created.id is not None
        assert created.user_id == "a6ee4dde-c95d-4644-a842-13d4fadea71e"
        assert created.name == "New Test Session"
        assert created.is_favorite is True
        assert isinstance(created.created_at, datetime)
        assert isinstance(created.updated_at, datetime)

    async def test_get_by_id(self, repository: SessionRepository, test_session: Session):
        """Test getting session by ID."""
        retrieved = await repository.get_by_id(test_session.id)
        
        assert retrieved is not None
        assert retrieved.id == test_session.id
        assert retrieved.user_id == test_session.user_id

    async def test_get_by_id_not_found(self, repository: SessionRepository):
        """Test getting non-existent session."""
        fake_id = UUID("12345678-1234-1234-1234-123456789abc")
        retrieved = await repository.get_by_id(fake_id)
        
        assert retrieved is None

    async def test_list_by_user(self, repository: SessionRepository, db_session: AsyncSession):
        """Test listing sessions by user."""
        # Create multiple sessions for the same user
        sessions = [
            Session(user_id="user-1", name="Session 1", is_favorite=True),
            Session(user_id="user-1", name="Session 2", is_favorite=False),
            Session(user_id="user-2", name="Session 3", is_favorite=False),
        ]
        
        for session in sessions:
            db_session.add(session)
        await db_session.commit()
        
        # Test listing for user-1
        user1_sessions = await repository.list_by_user("user-1")
        assert len(user1_sessions) == 2
        assert all(s.user_id == "user-1" for s in user1_sessions)

    async def test_list_by_user_with_pagination(self, repository: SessionRepository, db_session: AsyncSession):
        """Test listing sessions with pagination."""
        # Create 5 sessions
        for i in range(5):
            session = Session(user_id="a6ee4dde-c95d-4644-a842-13d4fadea71e", name=f"Session {i}")
            db_session.add(session)
        await db_session.commit()
        
        # Test pagination
        sessions = await repository.list_by_user("user-1", skip=2, limit=2)
        assert len(sessions) == 2

    async def test_count_by_user(self, repository: SessionRepository, db_session: AsyncSession):
        """Test counting sessions by user."""
        # Create sessions
        sessions = [
            Session(user_id="a6ee4dde-c95d-4644-a842-13d4fadea71e", name="Session 1"),
            Session(user_id="b6ee4dde-c95d-4644-a842-13d4fadea71e", name="Session 2"),
            Session(user_id="c6ee4dde-c95d-4644-a842-13d4fadea71e", name="Session 3"),
        ]
        
        for session in sessions:
            db_session.add(session)
        await db_session.commit()
        
        count = await repository.count_by_user("user-1")
        assert count == 2

    async def test_update_session(self, repository: SessionRepository, test_session: Session):
        """Test updating session."""
        updated = await repository.update(
            test_session.id,
            name="Updated Name",
            is_favorite=True
        )
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.is_favorite is True

    async def test_update_nonexistent_session(self, repository: SessionRepository):
        """Test updating non-existent session."""
        fake_id = UUID("12345678-1234-1234-1234-123456789abc")
        updated = await repository.update(fake_id, name="New Name")
        
        assert updated is None

    async def test_delete_session(self, repository: SessionRepository, test_session: Session):
        """Test deleting session."""
        success = await repository.delete(test_session.id)
        assert success is True
        
        # Verify it's deleted
        retrieved = await repository.get_by_id(test_session.id)
        assert retrieved is None

    async def test_delete_nonexistent_session(self, repository: SessionRepository):
        """Test deleting non-existent session."""
        fake_id = UUID("12345678-1234-1234-1234-123456789abc")
        success = await repository.delete(fake_id)
        assert success is False

    async def test_exists(self, repository: SessionRepository, test_session: Session):
        """Test checking if session exists."""
        exists = await repository.exists(test_session.id)
        assert exists is True

    async def test_exists_false(self, repository: SessionRepository):
        """Test checking if non-existent session exists."""
        fake_id = UUID("12345678-1234-1234-1234-123456789abc")
        exists = await repository.exists(fake_id)
        assert exists is False
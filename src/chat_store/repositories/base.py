from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository interface for data access operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @abstractmethod
    async def create(self, obj: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def list(self, **filters) -> List[T]:
        """List entities with optional filters."""
        pass
    
    @abstractmethod
    async def update(self, id: Any, **kwargs) -> Optional[T]:
        """Update entity by ID."""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        pass
from chat_store.db.base import engine, Base
from chat_store.core.logger import get_logger, PerformanceTimer

# Import models to ensure they're registered with SQLAlchemy
from chat_store.models import Message, Session  # noqa: F401

logger = get_logger(__name__)


async def init_db():
    with PerformanceTimer(logger, "database_initialization"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("database_initialized", tables=list(Base.metadata.tables.keys()))
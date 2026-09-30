from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Base class for all business logic services."""

    def __init__(self, db: AsyncSession):
        self.db = db

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

class BaseService:
    """Base class for all business logic services."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

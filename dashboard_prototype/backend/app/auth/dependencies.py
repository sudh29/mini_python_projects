"""
Auth dependencies — JWT token validation + tenant scoping.

For the prototype, we support both:
  1. API-key auth (X-API-Key header) — for programmatic access
  2. JWT Bearer token — for UI sessions

All endpoints automatically get the current user's client_id for tenant isolation.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.client import Client, User, UserRole

# ── Password Hashing ─────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Bearer Scheme ─────────────────────────────────────────────────
bearer_scheme = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    user_id: str
    client_id: str
    role: str
    username: str


class CurrentUser(BaseModel):
    """Injected into route handlers via Depends()."""
    user_id: str
    client_id: str
    role: UserRole
    username: str


# ── Token Creation ───────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ── Auth Dependency ──────────────────────────────────────────────
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)] = None,
    x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None,
) -> CurrentUser:
    """
    Resolve the current user from either:
      - JWT Bearer token (UI sessions)
      - X-API-Key header (programmatic / dev access)
    """

    # ── Try JWT first ────────────────────────────────────────────
    if credentials and credentials.credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return CurrentUser(
                user_id=payload["user_id"],
                client_id=payload["client_id"],
                role=UserRole(payload["role"]),
                username=payload["username"],
            )
        except (JWTError, KeyError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    # ── Fallback to API Key ──────────────────────────────────────
    if x_api_key:
        result = await db.execute(
            select(Client).where(Client.api_key == x_api_key, Client.is_active == True)
        )
        client = result.scalar_one_or_none()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        # API key users get admin role by default
        return CurrentUser(
            user_id="api-key-user",
            client_id=client.id,
            role=UserRole.ADMIN,
            username=f"apikey@{client.name}",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ── Role Guard ───────────────────────────────────────────────────
def require_role(required: UserRole):
    """Dependency factory — ensures user has the required role."""
    async def _check(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if user.role == UserRole.ADMIN:
            return user  # Admin can do everything
        if user.role != required:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required.value}' required",
            )
        return user
    return _check

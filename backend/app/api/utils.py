from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import User as TokenUser
from backend.app.api.deps import get_current_user
from backend.app.core.config import settings
from backend.app.db.database import get_session
from backend.app.db import models


def to_user_out(entity: models.User) -> dict[str, Optional[str]]:
    return {
        "id": entity.id,
        "name": entity.name,
        "phone": entity.phone,
        "email": entity.email,
        "role": entity.role,
        "unit_no": entity.unit_no,
    }


async def resolve_user(token_user: TokenUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> models.User:
    statement = select(models.User).where(models.User.id == int(token_user.id))
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def create_access_token(user: models.User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user.id), "role": user.role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

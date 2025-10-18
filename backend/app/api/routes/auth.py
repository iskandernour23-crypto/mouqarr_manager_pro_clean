from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api import schemas
from backend.app.api.utils import create_access_token, resolve_user, to_user_out
from backend.app.db import models
from backend.app.db.database import get_session

router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
async def login(payload: schemas.LoginRequest, session: AsyncSession = Depends(get_session)) -> schemas.TokenResponse:
    identifier = payload.identifier.strip()
    statement = select(models.User).where(
        or_(
            models.User.email == identifier,
            models.User.phone == identifier,
            models.User.name == identifier,
        )
    )
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user)
    return schemas.TokenResponse(access_token=token, user=schemas.UserOut(**to_user_out(user)))


@router.get("/me", response_model=schemas.UserOut)
async def me(current_user: models.User = Depends(resolve_user)) -> schemas.UserOut:
    return schemas.UserOut(**to_user_out(current_user))

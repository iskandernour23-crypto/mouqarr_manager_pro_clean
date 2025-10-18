from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api import schemas
from backend.app.api.utils import resolve_user
from backend.app.db import models
from backend.app.db.database import get_session

router = APIRouter()


@router.get("/", response_model=List[schemas.NotificationOut])
async def list_notifications(
    session: AsyncSession = Depends(get_session),
    user: models.User = Depends(resolve_user),
) -> List[schemas.NotificationOut]:
    statement = select(models.Notification).where(models.Notification.user_id == user.id)
    result = await session.execute(statement)
    records = result.scalars().all()
    return [schemas.NotificationOut.from_orm(record) for record in records]


@router.post("/{notification_id}/read", response_model=schemas.NotificationOut)
async def mark_read(
    notification_id: int,
    session: AsyncSession = Depends(get_session),
    user: models.User = Depends(resolve_user),
) -> schemas.NotificationOut:
    statement = select(models.Notification).where(models.Notification.id == notification_id)
    result = await session.execute(statement)
    notification = result.scalar_one_or_none()
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notification.read = True
    await session.flush()
    return schemas.NotificationOut.from_orm(notification)

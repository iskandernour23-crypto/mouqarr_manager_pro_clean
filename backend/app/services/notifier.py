from __future__ import annotations

from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db import models


async def create_notification(
    session: AsyncSession,
    user_id: int,
    title: str,
    body: str,
    channel: str = "in_app",
) -> models.Notification:
    record = models.Notification(user_id=user_id, title=title, body=body, channel=channel)
    session.add(record)
    await session.flush()
    return record


async def notify_users(
    session: AsyncSession,
    users: Iterable[models.User],
    title: str,
    body: str,
    channel: str = "in_app",
) -> None:
    for user in users:
        await create_notification(session, user_id=user.id, title=title, body=body, channel=channel)

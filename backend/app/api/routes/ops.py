from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api import permissions, schemas
from backend.app.db import models
from backend.app.db.database import get_session
from backend.app.services import reminders

router = APIRouter()


@router.post("/run-reminders", response_model=schemas.ReminderRunResult)
async def run_reminders(
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.ReminderRunResult:
    result = await reminders.run(session)
    return result

from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.schemas.actions import ActionExecuteRequest, ActionExecuteResponse
from backend.app.ai.services.tools import registry
from backend.app.api.deps import User, get_current_user
from backend.app.db.database import get_session
from backend.app.db.models import AIInteraction

router = APIRouter()


@router.post("/actions/execute", response_model=ActionExecuteResponse)
async def execute_action(
    payload: ActionExecuteRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ActionExecuteResponse:
    result = await registry.invoke(payload.name, payload.params, user)
    log_entry = AIInteraction(
        user_id=user.id,
        role="tool",
        content=json.dumps(result, ensure_ascii=False),
        tool_name=payload.name,
    )
    session.add(log_entry)
    await session.flush()
    return ActionExecuteResponse(name=payload.name, result=result)

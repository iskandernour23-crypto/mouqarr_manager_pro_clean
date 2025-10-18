from __future__ import annotations

import asyncio
import logging
import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.ai.routers.chat import router as chat_router
from backend.app.ai.routers.actions import router as actions_router
from backend.app.ai.routers.suggest import router as suggest_router
from backend.app.api.routes import api_router
from backend.app.core.config import settings
from backend.app.db.database import AsyncSessionLocal
from backend.app.services import reminders

app = FastAPI(title=f"{settings.app_name} AI Gateway")

logger = logging.getLogger("reminders")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(chat_router, prefix="/ai", tags=["ai-chat"])
app.include_router(actions_router, prefix="/ai", tags=["ai-actions"])
app.include_router(suggest_router, prefix="/ai", tags=["ai-suggest"])


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


async def _reminder_worker(interval_hours: int = 6) -> None:
    while True:
        async with AsyncSessionLocal() as session:
            try:
                result = await reminders.run(session)
                await session.commit()
                logger.info(
                    "reminder-run",
                    extra={
                        "overdue": result.overdue_invoices,
                        "warranties": len(result.expiring_warranties),
                        "subscriptions": len(result.expiring_subscriptions),
                    },
                )
            except Exception as exc:  # pragma: no cover - background safety
                await session.rollback()
                logger.exception("reminder worker failure: %s", exc)
        await asyncio.sleep(interval_hours * 3600)


@app.on_event("startup")
async def start_background_tasks() -> None:
    app.state.reminder_task = asyncio.create_task(_reminder_worker())


@app.on_event("shutdown")
async def stop_background_tasks() -> None:
    task = getattr(app.state, "reminder_task", None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

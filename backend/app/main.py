from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.ai.routers.chat import router as chat_router
from backend.app.ai.routers.actions import router as actions_router
from backend.app.ai.routers.suggest import router as suggest_router
from backend.app.core.config import settings

app = FastAPI(title=f"{settings.app_name} AI Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/ai", tags=["ai-chat"])
app.include_router(actions_router, prefix="/ai", tags=["ai-actions"])
app.include_router(suggest_router, prefix="/ai", tags=["ai-suggest"])


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
